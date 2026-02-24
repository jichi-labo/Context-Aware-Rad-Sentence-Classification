#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Automatic annotation of radiology reports into 4 categories using GPT-4.1-mini.

This script takes a JSONL file containing radiology reports with finding_lines
and annotates each sentence into one of 4 categories:
- Label 0: Background information (not related to image findings)
- Label 1: Positive findings (new abnormalities in context)
- Label 2: Negative findings (absence of abnormalities)
- Label 3: Continuation (modifying previous sentences, not standalone findings)
"""

import os
import json
import time
import argparse
from getpass import getpass
from openai import OpenAI

# System prompt for classification
SYSTEM_PROMPT = """
あなたは放射線画像に特化したテキスト分類モデルです。
入力：キー「finding_lines」に格納された画像所見文のリスト
タスク：各文を順に評価し、以下の基準でラベルを割り当ててください。
0 - 画像所見に関連しない文章（背景情報など）
1 - 文脈中に新たに登場する別個の*陽性*の画像所見を記述した文章。（迷ったらこれ）
2 - 文脈中に新たに登場する別個の*陰性*の画像所見を記述した文章。（※１の要素もある場合は１を優先）
3 - これよりも前の文を修飾しているもの、かつ単独では画像所見として成立しない文章（例：前述の病変の性状説明、所見の変化、など）

出力：元の文章をキー、ラベルを値とする JSON オブジェクトのみを返してください。元の文章を改変してはいけません。

例）
入力
finding_lines = [
"比較画像なし。",
"膵体部に径18mm大の境界明瞭な強く造影される内部均一な腫瘤を認めます。",
"腫瘤は動脈相で著明な早期造影効果を示し、門脈相でやや等信号、後期像で等低信号となります。",
"撮像範囲内の他臓器に明らかな異常なし。",
"骨に退行性変化を認めますが、転移はありません。",
]
出力
{
"比較画像なし。": 0,
"膵体部に径18mm大の境界明瞭な強く造影される内部均一な腫瘤を認めます。": 1,
"腫瘤は動脈相で著明な早期造影効果を示し、門脈相でやや等信号、後期像で等低信号となります。": 3,
"周囲への浸潤はありません。": 3,
"撮像範囲内の他臓器に明らかな異常なし。": 2,
"骨に退行性変化を認めますが、転移はありません。": 1
}
"""


def main():
    parser = argparse.ArgumentParser(
        description="Annotate radiology reports with sentence-level labels using GPT-4.1-mini"
    )
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Path to input JSONL file with finding_lines"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Path to output JSONL file (default: overwrites input file)"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=10,
        help="Number of entries to process before saving progress (default: 10)"
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip entries that already have sentence_class field"
    )
    args = parser.parse_args()

    # Setup OpenAI API
    if "OPENAI_API_KEY" not in os.environ:
        os.environ["OPENAI_API_KEY"] = getpass("Enter your OpenAI API key: ")
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Determine output path
    output_path = args.output if args.output else args.input

    # Load all entries
    with open(args.input, "r", encoding="utf-8") as f:
        entries = [json.loads(line) for line in f if line.strip()]

    total = len(entries)
    print(f"Total entries: {total}")

    # Process each entry
    processed_count = 0
    skipped_count = 0

    for idx, entry in enumerate(entries, start=1):
        # Skip if already processed (when --skip-existing is set)
        if args.skip_existing and "sentence_class" in entry:
            skipped_count += 1
            print(f"[{idx}/{total}] Skipped (already processed)")
            continue

        finding_lines = entry.get("finding_lines", [])
        if not finding_lines:
            print(f"[{idx}/{total}] Skipped (no finding_lines)")
            continue

        user_prompt = f"finding_lines = {json.dumps(finding_lines, ensure_ascii=False)}"

        try:
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0
            )
            entry["sentence_class"] = response.choices[0].message.content
            processed_count += 1
            print(f"[{idx}/{total}] Processed")

        except Exception as e:
            print(f"[Error at {idx}] {e}")
            break

        # Save progress periodically
        if idx % args.batch_size == 0:
            with open(output_path, "w", encoding="utf-8") as fw:
                for ent in entries:
                    fw.write(json.dumps(ent, ensure_ascii=False) + "\n")
            print(f"✅ Saved progress up to entry {idx}/{total}")

        time.sleep(0.2)  # Rate limiting

    # Final save
    with open(output_path, "w", encoding="utf-8") as fw:
        for ent in entries:
            fw.write(json.dumps(ent, ensure_ascii=False) + "\n")

    print(f"\n✅ Completed:")
    print(f"  - Total entries: {total}")
    print(f"  - Processed: {processed_count}")
    print(f"  - Skipped: {skipped_count}")
    print(f"  - Output: {output_path}")


if __name__ == "__main__":
    main()
