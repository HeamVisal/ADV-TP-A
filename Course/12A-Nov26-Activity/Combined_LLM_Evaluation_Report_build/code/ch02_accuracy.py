"""Chapter 2 code, extracted from Combined_LLM_Evaluation_Report.md.

Edit the report, then run: python tools/build_report.py code
"""

from sklearn.metrics import accuracy_score, balanced_accuracy_score


def calculate_accuracy(predictions, references):
    """Correct predictions divided by all predictions."""
    if len(predictions) != len(references) or not references:
        raise ValueError("need two non-empty lists of equal length")
    correct = sum(p == r for p, r in zip(predictions, references))
    return correct / len(references)


refs = ["Positive", "Negative", "Positive"]
preds = ["Positive", "Positive", "Positive"]
print("Own function :", calculate_accuracy(preds, refs))
print("scikit-learn :", accuracy_score(refs, preds))  # (y_true, y_pred)
print(f"As a percentage: {accuracy_score(refs, preds):.1%}")

# Recount of Group 2's reported experiment table (Example 2.4).
gold = ["Positive", "Negative", "Positive", "Positive", "Negative"]
gemini = ["Positive", "Negative", "Positive", "Positive", "Positive"]
llama = ["Positive", "Negative", "Negative", "Positive", "Negative"]
print(
    "Group 2 table - Gemini 1.5:",
    accuracy_score(gold, gemini),
    "Llama 3:",
    accuracy_score(gold, llama),
)


y_true = [0] * 95 + [1] * 5  # 95 negative, 5 positive
always_negative = [0] * 100  # majority-class baseline
print("Majority baseline accuracy:", accuracy_score(y_true, always_negative))
print("Balanced accuracy        :", balanced_accuracy_score(y_true, always_negative))
