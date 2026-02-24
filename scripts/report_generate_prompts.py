#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Generate user prompts for synthetic radiology report generation.

This script generates randomized prompts that can be used with GPT-4.1
to create diverse Japanese radiology reports.
"""

import random

# Parameter pools for prompt generation
experience_levels = ["若手", "中堅", "熟練", "今回の読影分野のプロフェッショナル", "一般的な能力"]
reader_styles = ["簡潔", "丁寧", "できるだけ長い記載","箇条書き形式", "専門用語の多用", "わかりやすさ重視", "(頭部)、(胸部)、(腹部)のように部位ごとに分けての詳細な自然文での記載"]
patient_sexes = ["男性", "女性"]
patient_ages = ["小児", "成人", "高齢者"]
patient_ages_weights = [0.1, 0.5, 0.4]

modalities = ["単純CT", "造影CT", "単純MRI", "造影MRI", "X線", "PET-CT", "PET-CT以外の適切な核医学"]
modalities_weights = [0.3, 0.25, 0.2, 0.15, 0.05, 0.04, 0.01]


sites = ["脾臓", "腎臓", "胆嚢・胆管", "肝臓", "胃", "膵臓", "副腎", "肺", "気管", "甲状腺",
         "腸管", "膀胱", "骨盤臓器", "骨", "心臓", "血管", "関節", "脊髄", "脳"]

quality = ["良好", "適切", "一部で不十分"]
quality_weights = [0.7, 0.299, 0.001]

exam_reasons = [
    "検診異常の精査", "症状の精査・スクリーニング", "術後フォローアップ",
    "治療効果判定", "外傷後の評価", "偶発所見フォロー", "手術前評価"
]

disease_categories = [
    "腫瘍性病変", "炎症性・感染性病変", "血管性病変",
    "先天性・発達異常", "変性疾患", "外傷性病変"
]

range_notes = [
    "局所だけでなく、撮像範囲全体の所見を詳細に記載してください",
    "今回の撮像範囲に含まれる他部位の要点も記載してください",
    "該当部分以外の記載は最小限にしてください",
    "全体としてよくかけていますが、まれに誤字・脱字、変換ミスに気づかないことがあります"
]
range_notes_weights = [0.45, 0.30, 0.20, 0.05]

first_lines = [
    "には前回検査があったことを書きましょう",
    "には実施した検査種の明記、比較した画像検査を記載してください",
    "には実施した検査種を記載してください",
    "には比較した画像検査の有無を記載してください",
]

second_lines = [
    "2行目には臨床情報の要約を記載してください。",
    "2行目には検査の目的を記載してください。",
    ""
]
second_lines_weights = [0.5, 0.1, 0.4]

add_notes = [
    "",
    "その他には気になる所見はありませんでした。",
    "検査目的の他に重要な異常所見をみつけました。",
    "検査目的の他にはあまり重要ではないものの複数の異常所見がありました。",
    "検査目的の他にはあまり重要ではないものの別の異常所見がありました。",
]

lesion_patterns = [
    "{ctg}の1つに特徴的な所見がありました、具体的な疾患を絞り込むことができました",
    "{ctg}の1つと診断できる特徴的な所見がありました",
    "{ctg}を疑う異常所見がったものの、鑑別に挙げるにとどめました",
    "{ctg}を中心に複数の鑑別診断を考慮する異常所見がありましたが、特定の疾患は絞りきれませんでした",
    "common diseaseの1つを第一に考えました",
    "比較的稀ではありますが特定の疾患を考えました",
    "非常に稀な疾患を疑う所見がありました",
    "具体的な疾患名までは絞れませんでしたが、{ctg}の可能性を考慮しました",
    "読影の結果、異常所見はないと考えました",
]

# Prompt template
prompt_template = """
あなたは{reader_experience}の放射線科医で、レポート作成は{reader_style}を好みます。
現在、{patient_age}歳の{patient_sex}の検査を読影しています。
検査理由は{site}の{exam_reason}で{modality}が行われました。検査範囲は適切で、画質は{quality}です。
{lesion_note}。{add_note}
所見の1行目{first_line}。{second_line}
なお、{range_note}。
""".strip()


def generate_lesion_note():
    """Generate a lesion description by selecting a random disease category and pattern."""
    ctg = random.choice(disease_categories)
    pattern = random.choice(lesion_patterns)
    return pattern.format(ctg=ctg)


def generate_prompt():
    """Generate a randomized user prompt for radiology report generation."""
    data = {
        "reader_experience": random.choice(experience_levels),
        "reader_style": random.choice(reader_styles),
        "patient_age": random.choices(patient_ages, weights=patient_ages_weights, k=1)[0],
        "patient_sex": random.choice(patient_sexes),
        "modality": random.choices(modalities, weights=modalities_weights, k=1)[0],
        "quality": random.choices(quality, weights=quality_weights, k=1)[0],
        "site": random.choice(sites),
        "lesion_note": generate_lesion_note(),
        "exam_reason": random.choice(exam_reasons),
        "disease_category": random.choice(disease_categories),
        "range_note": random.choices(range_notes, weights=range_notes_weights, k=1)[0],
        "first_line": random.choice(first_lines),
        "second_line": random.choices(second_lines, weights=second_lines_weights, k=1)[0],
        "add_note": random.choice(add_notes),
    }

    return prompt_template.format(**data)


def get_system_prompt():
    """Return the system prompt for GPT-4.1."""
    return """下記の状況から実際の臨床場面を設定してください。
経過や状況、解剖部位、特定の疾患を具体的に設定することがとても重要です。
そしてとても具体的で実際にありうる日本語の画像診断レポートを作成してください。
所見と診断をJson形式で出力してください。keyは'診断'と'所見'としてください。
valueはリスト型としてください。改行する場合は改行コードではなく、リストの次の要素として記入してください。"""


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate prompts for synthetic radiology report generation"
    )
    parser.add_argument(
        "--num",
        type=int,
        default=1,
        help="Number of prompts to generate (default: 1)"
    )
    parser.add_argument(
        "--show-system-prompt",
        action="store_true",
        help="Show the system prompt"
    )
    args = parser.parse_args()

    if args.show_system_prompt:
        print("=== System Prompt ===")
        print(get_system_prompt())
        print("\n")

    for i in range(args.num):
        if args.num > 1:
            print(f"=== Prompt {i+1}/{args.num} ===")
        print(generate_prompt())
        if i < args.num - 1:
            print("\n" + "="*50 + "\n")
