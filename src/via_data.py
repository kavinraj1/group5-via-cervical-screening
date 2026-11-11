"""Load the Jhpiego + IARC VIA images into one labelled table.

Labels follow the expert VIA reading: Negative / Positive / Suspicious of cancer.
`refer` is the screening target: 1 if Positive or Suspicious of cancer.
"""
import os

import numpy as np
import pandas as pd
from PIL import Image

CLASSES = ["Negative", "Positive", "Suspicious of cancer"]


def _longest_run(mask):
    best, start, best_span = 0, None, (0, len(mask))
    for i, v in enumerate(list(mask) + [False]):
        if v and start is None:
            start = i
        elif not v and start is not None:
            if i - start > best:
                best, best_span = i - start, (start, i)
            start = None
    return best_span


def crop_flashcard(img, inset=0.02):
    """Cut the cervix photo out of a scanned Jhpiego flashcard page.

    The photo sits in the top half of the page; the logo and text are excluded
    by searching only there and keeping the largest block of non-white rows.
    """
    img = img.convert("RGB")
    a = np.asarray(img).astype(np.int16)
    top = a[: a.shape[0] // 2]
    spread = top.max(axis=2) - top.min(axis=2)
    ink = (spread > 30) | (top.mean(axis=2) < 170)
    r0, r1 = _longest_run(ink.mean(axis=1) > 0.25)
    c0, c1 = _longest_run(ink[r0:r1].mean(axis=0) > 0.5)
    dy, dx = int((r1 - r0) * inset), int((c1 - c0) * inset)
    return img.crop((c0 + dx, r0 + dy, c1 - dx, r1 - dy))


def load_table(root, jhpiego_labels_csv):
    """root: folder containing IARCImageBankVIA/ and via/."""
    iarc = os.path.join(root, "IARCImageBankVIA")
    meta = pd.read_excel(os.path.join(iarc, "Cases Meta data.xlsx"))
    imgs = pd.read_excel(os.path.join(iarc, "Cases - Images.xlsx"))
    after = imgs[imgs["Type"] == "After application of acetic acid"]
    after = after.drop_duplicates("CaseNumber")
    case_dirs = {}
    for d in os.listdir(iarc):
        p = os.path.join(iarc, d)
        if os.path.isdir(p):
            for f in os.listdir(p):
                case_dirs[f] = p
    rows = []
    for _, r in after.merge(meta, on="CaseNumber").iterrows():
        if r["File"] in case_dirs:
            rows.append(dict(source="IARC", id=f"IARC-{r['CaseNumber']:03d}",
                             path=os.path.join(case_dirs[r["File"]], r["File"]),
                             via=r["VIA"], histology=r["Histology findings"]))
    jh = pd.read_csv(jhpiego_labels_csv)
    for _, r in jh.iterrows():
        rows.append(dict(source="Jhpiego", id=f"JH-{r['card']:03d}",
                         path=os.path.join(root, "via", r["file"]),
                         via=r["via"], histology=None))
    df = pd.DataFrame(rows)
    df = df[df["via"].isin(CLASSES)].reset_index(drop=True)
    df["label"] = df["via"].map(CLASSES.index)
    df["refer"] = (df["label"] > 0).astype(int)
    return df


def open_image(row):
    img = Image.open(row["path"])
    return crop_flashcard(img) if row["source"] == "Jhpiego" else img.convert("RGB")
