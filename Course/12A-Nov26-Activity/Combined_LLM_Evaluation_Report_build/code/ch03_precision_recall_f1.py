"""Chapter 3 code, extracted from Combined_LLM_Evaluation_Report.md.

Edit the report, then run: python tools/build_report.py code
"""

import re
from collections import Counter

from sklearn.metrics import (
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
    precision_score,
    recall_score,
)

# Example from Group 3's code slide: 1 = Positive (the positive class).
y_true = [1, 1, 1, 1, 0, 0, 0, 0, 0, 0]
y_pred = [1, 1, 1, 0, 1, 0, 0, 0, 0, 0]
print("Precision:", precision_score(y_true, y_pred))  # pos_label=1 by default
print("Recall   :", recall_score(y_true, y_pred))
print("F1       :", f1_score(y_true, y_pred))
# labels=[0, 1] fixes the row/column order: rows = actual, columns = predicted.
print(confusion_matrix(y_true, y_pred, labels=[0, 1]))


# Undefined case: the model never predicts Positive, so TP + FP = 0.
never_positive = [0] * 10
print(
    "Precision, zero_division=0 :",
    precision_score(y_true, never_positive, zero_division=0),
)


# Multiclass teaching example (Example 3.4).
gold = ["pos", "pos", "pos", "pos", "pos", "pos", "neg", "neg", "neg", "neu"]
pred = ["pos", "pos", "pos", "pos", "pos", "neg", "neg", "neg", "pos", "pos"]
labels = ["pos", "neg", "neu"]
p, r, f, support = precision_recall_fscore_support(
    gold, pred, labels=labels, zero_division=0
)
for name, *vals in zip(labels, p, r, f, support):
    print(f"{name}: P={vals[0]:.4f} R={vals[1]:.4f} F1={vals[2]:.4f} support={vals[3]}")
for avg in ["macro", "micro", "weighted"]:
    print(
        avg, round(f1_score(gold, pred, labels=labels, average=avg, zero_division=0), 4)
    )


def token_f1(prediction, reference):
    """SQuAD-style word-overlap F1 (lowercased, punctuation removed)."""
    pred = re.findall(r"\w+", prediction.lower())
    ref = re.findall(r"\w+", reference.lower())
    common = sum((Counter(pred) & Counter(ref)).values())  # shared words
    if common == 0:
        return 0.0
    precision, recall = common / len(pred), common / len(ref)
    return 2 * precision * recall / (precision + recall)


print("Token F1:", round(token_f1("Mekong River delta", "Mekong River"), 4))
