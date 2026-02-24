#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
単一症例の推論結果とアノテーション結果を並べて表示するスクリプト。

Usage:
    python for_publish/scripts/report_classification_inference.py <model_id> <case_index>

    model_id:    0 = tohoku-nlp_bert-base-japanese-v3
                 1 = alabnii_jmedroberta-base-sentencepiece
                 2 = sbintuitions_modernbert-ja-130m
    case_index:  test.jsonl の行番号（0始まり）
"""

import os
import sys
import json
import warnings
warnings.filterwarnings('ignore')

import torch
from torch.nn.functional import softmax
from transformers import AutoTokenizer, AutoModelForSequenceClassification

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
DATA_PATH = os.path.join(BASE_DIR, "data", "annotated", "test.jsonl")
MODEL_BASE_DIR = os.path.join(BASE_DIR, "models")

MODELS = [
    "tohoku-nlp_bert-base-japanese-v3",
    "alabnii_jmedroberta-base-sentencepiece",
    "sbintuitions_modernbert-ja-130m",
]

LABEL_NAMES = {0: "Background", 1: "Pos_finding", 2: "Neg_finding", 3: "Continuation"}


def load_case(index):
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i == index:
                return json.loads(line)
    return None


def predict(model, tokenizer, texts, device):
    inputs = tokenizer(texts, padding=True, truncation=True, max_length=512, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        logits = model(**inputs).logits
        probs = softmax(logits, dim=-1)
        preds = torch.argmax(logits, dim=-1)
    return preds.cpu().numpy(), probs.cpu().numpy()


def main():
    if len(sys.argv) != 3:
        print("Usage: python report_classification_inference.py <model_id (0-2)> <case_index>")
        print("  Models:")
        for i, m in enumerate(MODELS):
            print(f"    {i}: {m}")
        sys.exit(1)

    model_id = int(sys.argv[1])
    case_index = int(sys.argv[2])

    if model_id not in (0, 1, 2):
        print(f"Error: model_id must be 0, 1, or 2")
        sys.exit(1)

    model_name = MODELS[model_id]
    case = load_case(case_index)
    if case is None:
        print(f"Error: case index {case_index} not found")
        sys.exit(1)

    sentence_class = json.loads(case['sentence_class'])
    sentences = list(sentence_class.keys())
    gt_labels = list(sentence_class.values())

    print(f"Model : {model_name}")
    print(f"Case  : #{case_index}  ({len(sentences)} sentences)")
    print(f"{'='*80}")

    # モデルロード
    model_path = os.path.join(MODEL_BASE_DIR, model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSequenceClassification.from_pretrained(model_path)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)
    model.eval()

    preds, probs = predict(model, tokenizer, sentences, device)

    # 結果表示
    correct = 0
    for i, (sentence, gt) in enumerate(zip(sentences, gt_labels)):
        pred_label = int(preds[i])
        match = "o" if pred_label == gt else "x"
        if pred_label == gt:
            correct += 1

        prob_str = " ".join(f"{p:.2f}" for p in probs[i])
        gt_name = LABEL_NAMES.get(gt, str(gt))
        pred_name = LABEL_NAMES.get(pred_label, str(pred_label))

        print(f"[{match}] GT={gt:>2}({gt_name:<14s}) Pred={pred_label:>2}({pred_name:<14s}) prob=[{prob_str}]")
        print(f"    {sentence}")

    print(f"{'='*80}")
    print(f"Accuracy: {correct}/{len(sentences)} ({correct/len(sentences)*100:.1f}%)")


if __name__ == "__main__":
    main()
