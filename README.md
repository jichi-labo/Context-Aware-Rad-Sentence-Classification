# Context-Aware Sentence Classification of Radiology Reports Using Synthetic Data

[日本語版 README はこちら](README_ja.md)

This repository provides the synthetic data, annotation scripts, and fine-tuned classification models used in the paper:

**"Context-Aware Sentence Classification of Radiology Reports Using Synthetic Data: Development and Validation Study"**

## 1. Synthetic Radiology Reports

The `data/generated_reports.jsonl` contains synthetic Japanese radiology reports generated using GPT-4.1 via the OpenAI API.

The prompts used for generation can be reproduced with `scripts/report_generate_prompts.py`:

```bash
# Generate a single prompt
python scripts/report_generate_prompts.py

# Generate multiple prompts with system prompt
python scripts/report_generate_prompts.py --num 5 --show-system-prompt
```

## 2. Sentence-Level Annotation

Each sentence in the generated reports is annotated with one of 4 labels:

| Label | Name | Description |
|-------|------|-------------|
| 0 | Background | Information not directly related to image findings |
| 1 | Positive finding | New abnormalities observed |
| 2 | Negative finding | Absence of abnormalities |
| 3 | Continuation | Modifying or supplementing a previous sentence |

`scripts/report_annotate_with_api.py` provides reproducible code for automatic annotation using GPT-4.1-mini:

The annotated results are already provided in `data/annotated/` (train / validation / test splits). The script is provided as a reference if you wish to run the annotation yourself:

```bash
python scripts/report_annotate_with_api.py \
  --input data/generated_reports.jsonl \
  --output data/annotated/output.jsonl \
  --skip-existing
```

### Data Format

```json
{
  "finding_lines": ["比較画像なし。", "膵体部に径18mm大の..."],
  "sentence_class": "{\"比較画像なし。\": 0, \"膵体部に径18mm大の...\": 1}"
}
```

## 3. Fine-Tuned Classification Models

We also provide lightweight classification models fine-tuned on the annotated data.

| # | Model | Description |
|---|-------|-------------|
| 0 | BERT base Japanese v3 | Pre-trained on Japanese Wikipedia |
| 1 | JMedRoBERTa-base | Pre-trained on Japanese medical literature |
| 2 | ModernBERT-Ja-130M | Modern BERT architecture |

### Download Models

The models are hosted on Google Drive (~1.4 GB total):

1. Download `models.zip` from [Google Drive](https://drive.google.com/file/d/19ULWvQZluLUUirFCBk-LWzhztbvMpLCX/view)
2. Extract and place in the repository:

```bash
unzip models.zip
```

### Inference Demo

`scripts/report_classification_inference.py` runs inference on a single test case and compares the prediction with the ground truth:

```bash
python scripts/report_classification_inference.py <model_id (0-2)> <case_index>
```

Example:

```bash
python scripts/report_classification_inference.py 0 0
```

Output:

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

## Installation

### Using Docker (Recommended)

```bash
docker build -t radiology-classification .
docker run --gpus all -it -v $(pwd):/workspace radiology-classification
```

### Manual Installation

```bash
pip install -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cu121
```

## Citation

If you use this data or code, please cite our paper:

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

## License

Different components of this repository are subject to different licenses.

### Data and Scripts

The synthetic reports (`data/`) and scripts (`scripts/`) are licensed under **CC BY 4.0**.

### Fine-Tuned Models

Each model inherits the license of its base pre-trained model.

| Model | Base Model License |
|-------|--------------------|
| BERT base Japanese v3 | Apache License 2.0 |
| JMedRoBERTa-base | CC BY-NC-SA 4.0 |
| ModernBERT-Ja-130M | MIT License |

## Acknowledgements

This research was supported by:
- Accreditation Organization for Management of Radiologic Imaging (AOMRI) Research Grant 2025
- Cross-ministerial Strategic Innovation Promotion Program (SIP) on "Integrated Health Care System" Grant Number JPJ012425

We thank the departments of radiology that provided the J-MID database.

