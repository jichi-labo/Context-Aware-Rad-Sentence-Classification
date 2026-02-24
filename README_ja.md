# 合成データを用いた放射線レポートの文脈考慮型文分類

[English README](README.md)

本リポジトリは以下の論文で使用した合成データ・アノテーションスクリプト・学習済み分類モデルを提供します。

**"Context-Aware Sentence Classification of Radiology Reports Using Synthetic Data: Development and Validation Study"**

## 1. 合成放射線レポート

`data/generated_reports.jsonl` には、OpenAI API 経由で GPT-4.1 を用いて生成した合成日本語放射線レポートが格納されています。

生成に使用したプロンプトは `scripts/report_generate_prompts.py` で再現できます:

```bash
# 1件のプロンプト生成
python scripts/report_generate_prompts.py

# 5件生成（システムプロンプト表示付き）
python scripts/report_generate_prompts.py --num 5 --show-system-prompt
```

## 2. 文レベルのアノテーション

生成されたレポートの各文に、以下の4ラベルのいずれかを付与しています:

| ラベル | 名称 | 説明 |
|--------|------|------|
| 0 | Background | 画像所見に直接関係しない情報 |
| 1 | Positive finding | 新規の異常所見 |
| 2 | Negative finding | 異常がないことの記述 |
| 3 | Continuation | 前文を修飾・補足する記述 |

`scripts/report_annotate_with_api.py` に、GPT-4.1-mini を用いた自動アノテーションの再現コードを掲載しています:

アノテーション済みの結果は `data/annotated/`（train / validation / test）にすでに格納しています。以下は、ご自身で実行する場合の参考としてください:

```bash
python scripts/report_annotate_with_api.py \
  --input data/generated_reports.jsonl \
  --output data/annotated/output.jsonl \
  --skip-existing
```

### データ形式

```json
{
  "finding_lines": ["比較画像なし。", "膵体部に径18mm大の..."],
  "sentence_class": "{\"比較画像なし。\": 0, \"膵体部に径18mm大の...\": 1}"
}
```

## 3. 学習済み分類モデル

アノテーション済みデータを用いてファインチューニングした軽量分類モデルも公開しています。

| # | モデル | 説明 |
|---|--------|------|
| 0 | BERT base Japanese v3 | 日本語 Wikipedia で事前学習 |
| 1 | JMedRoBERTa-base | 日本語医学文献で事前学習 |
| 2 | ModernBERT-Ja-130M | 最新の BERT アーキテクチャ |

### モデルのダウンロード

モデルは Google Drive で配布しています（合計約 1.4 GB）:

1. `models.zip` をダウンロード: [Google Drive](https://drive.google.com/file/d/19ULWvQZluLUUirFCBk-LWzhztbvMpLCX/view)
2. 解凍して配置:

```bash
unzip models.zip
```

### 推論デモ

`scripts/report_classification_inference.py` で単一症例を推論し、正解ラベルと比較できます:

```bash
python scripts/report_classification_inference.py <model_id (0-2)> <case_index>
```

例:

```bash
python scripts/report_classification_inference.py 0 0
```

出力:

```
Model : tohoku-nlp_bert-base-japanese-v3
Case  : #0  (15 sentences)
================================================================================
[o] GT= 0(Background    ) Pred= 0(Background    ) prob=[0.99 0.00 0.00 0.00]
    前回2024年2月に同部位の単純CTが施行されています。
[o] GT= 0(Background    ) Pred= 0(Background    ) prob=[1.00 0.00 0.00 0.00]
    臨床情報：膀胱癌治療後の経過観察、治療効果判定目的に撮像。
[o] GT= 2(Neg_finding   ) Pred= 2(Neg_finding   ) prob=[0.00 0.00 1.00 0.00]
    【腹部】膀胱壁は全周性肥厚像は明らかでなく、内腔に腫瘤性病変を明瞭に認めません。
[o] GT= 3(Continuation  ) Pred= 3(Continuation  ) prob=[0.00 0.00 0.01 0.98]
    前回と比較し、膀胱壁の所見に大きな変化を認めません。
...
================================================================================
Accuracy: 15/15 (100.0%)
```

## インストール

### Docker（推奨）

```bash
docker build -t radiology-classification .
docker run --gpus all -it -v $(pwd):/workspace radiology-classification
```

### 手動インストール

```bash
pip install -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cu121
```

## 引用

本データやコードを使用する場合は、以下の論文を引用してください:

```bibtex
@article{kikuchi2025context,
  title={Context-Aware Sentence Classification of Radiology Reports Using Synthetic Data: Development and Validation Study},
  author={Kikuchi, Tomohiro and Yamagishi, Yosuke and Yamamoto, Kohei and Akashi, Toshiaki and Mori, Harushi and Makimoto, Hisaki and Kohro, Takahide},
  journal={JMIR Preprints},
  year={2025},
  doi={10.2196/preprints.86365},
  url={https://preprints.jmir.org/preprint/86365}
}
```

## ライセンス

本リポジトリの各コンポーネントには異なるライセンスが適用されます。

### データ・スクリプト

合成レポート（`data/`）およびスクリプト（`scripts/`）は **CC BY 4.0** で提供します。

### 学習済みモデル

各モデルは、ファインチューニング元のベースモデルのライセンスを継承します。

| モデル | ベースモデルのライセンス |
|--------|------------------------|
| BERT base Japanese v3 | Apache License 2.0 |
| JMedRoBERTa-base | CC BY-NC-SA 4.0 |
| ModernBERT-Ja-130M | MIT License |

