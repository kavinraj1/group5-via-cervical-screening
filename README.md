# Group 5: offline AI for VIA cervical cancer screening

EN.580.649 AI/ML for Global Health, Johns Hopkins, Fall 2026
Caroline Kelley · Kavinraj Srirangarayan Rangaraj · Luiza Brunelli · Maggie Ma

A phone app that works offline in low-resource clinics. A health worker takes a photo of the cervix after acetic acid (VIA), and the model:

1. **Classifies** it as negative, precancerous, or suspected cancer.
2. **Segments** it by outlining the acetowhite lesion.

## Plan (agreed Nov 4)

| Step | What |
|---|---|
| 1 | **EfficientNet-B3** backbone (ImageNet-pretrained) with a classification head and a segmentation head |
| 2 | **Prune** it: delete the filters that contribute least, fine-tune, repeat while it still meets the target |
| 3 | If it is still too big or loses too much accuracy: **distill** into a smaller student (MobileNetV3) |
| 4 | int8 quantization → TFLite → offline Android app |

**Accuracy target:** sensitivity ≥ 73% at ≥ 87% specificity (from the literature review in the preliminary notebook).

![Pruning step by step](docs/figures/pruning_neurons_flowchart.png)

## Repo layout

| Path | What |
|---|---|
| `notebooks/Group5_VIA_Team_Notebook.ipynb` | Shared team notebook: data setup from the *Finalized Dataset* folder, then B3 pruning, distillation and bigger-model experiments (5-fold CV) |
| `notebooks/VIA_Accuracy_Target_preliminary.ipynb` | Kavin's preliminary experiments (EfficientNet-B0, MobileNetV3, 5-fold CV) |
| `src/via_data.py` | Loads the IARC + Jhpiego images into one labelled table |
| `labels/jhpiego_labels.csv` | VIA labels for the 115 Jhpiego flashcards |
| `docs/figures/` | Pruning / distillation explainers |

## Getting started

1. Open a notebook in Colab:
   - Team notebook: [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/kavinraj1/group5-via-cervical-screening/blob/main/notebooks/Group5_VIA_Team_Notebook.ipynb)
   - Preliminary results: [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/kavinraj1/group5-via-cervical-screening/blob/main/notebooks/VIA_Accuracy_Target_preliminary.ipynb)
2. **Runtime > Change runtime type > T4 GPU.**
3. Add the team Drive folder to your own Drive once: in Google Drive, open the **AI ML Final Project** folder menu > **Organise > Add shortcut > My Drive**.
4. Run the cells in order and sign in to Google Drive when asked.

## Data is not in this repo

This repo is **public**. The VIA images and spreadsheets stay in the team Drive folder (**AI ML Final Project**; sources are listed in the *Finalized Dataset* doc).

- Never commit images, `.xlsx` files, model checkpoints, or notebooks with outputs that show patient photos or case rows.
- Before committing a notebook: **Edit > Clear all outputs**, then save.
- Put results worth keeping (metrics, plots without patient images) in the README or a short markdown cell.

## Working together

1. Work in Colab as usual.
2. To save your work here: in Colab, **File > Save a copy in GitHub**, pick this repo, and use a branch named after you (e.g. `caroline/segmentation`).
3. Open a pull request so the others can see what changed, then merge into `main`.

Keep each pull request to one thing (one experiment or one fix) and use short conventional commit messages, e.g. `feat: add segmentation head` or `fix: data path for team folder`.

## Preliminary results (Nov 2, EfficientNet-B0 / MobileNetV3, 300 images, 5-fold CV)

| Model | AUC (95% CI) | Sensitivity at 86.7% specificity | 3-class accuracy |
|---|---|---|---|
| Frozen EfficientNet-B0 + logistic regression | 0.773 | 0.46 | 0.673 |
| Fine-tuned EfficientNet-B0 | 0.842 (0.80–0.88) | 0.61 | 0.720 |
| Fine-tuned MobileNetV3-Large | 0.856 (0.81–0.90) | 0.64 | 0.730 |
| Average of the two | 0.862 | 0.61 | 0.733 |

None of these meet the target yet; the move to EfficientNet-B3 is meant to close that gap.

## Results so far (Nov 11, 300 images, 5-fold CV)

| Model | Params | AUC | Sensitivity at 86.7% specificity | 3-class accuracy |
|---|---|---|---|---|
| EfficientNet-B3 | 10.7M | 0.879–0.885 | 0.69–0.73 | 0.750–0.763 |
| B3 pruned 20% (uniform) | 6.7M | 0.796 | 0.49 | 0.673 |
| MobileNetV3-L distilled from B3 | 4.2M | 0.858 | 0.68 | 0.730 |
| EfficientNet-B4 | 17.6M | 0.852 | 0.69 | 0.733 |
| EfficientNetV2-S | 20.2M | 0.874 | 0.72 | 0.767 |
| **Average of B3 + V2-S** | 30.9M | **0.899** | **0.74** | **0.770** |

- Pruning B3 loses accuracy at every level, and bigger single models don't beat B3 on 300 images.
- Averaging B3 and V2-S meets the target and fits a 4 GB phone (~62 MB at float16, roughly 3–8 s per photo). Next: distil it into a single B3 and compare.
- B3 ranges come from separate runs of the same recipe; differences of ~0.02 AUC or a few points of sensitivity are within run-to-run noise.
