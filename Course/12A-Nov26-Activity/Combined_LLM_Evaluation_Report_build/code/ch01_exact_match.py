"""Chapter 1 code, extracted from Combined_LLM_Evaluation_Report.md.

Edit the report, then run: python tools/build_report.py code
"""

import re
import string


def normalize_answer(text):
    """SQuAD v1.1-style cleanup: lowercase, remove punctuation,
    remove English articles (a, an, the), and tidy whitespace."""
    text = text.lower()
    # string.punctuation holds ASCII punctuation only, e.g. "!" and ".".
    text = "".join(ch for ch in text if ch not in set(string.punctuation))
    text = re.sub(r"\b(a|an|the)\b", " ", text)
    return " ".join(text.split())  # split() + join() collapses all spaces


def exact_match(prediction, references, normalize=False):
    """Return 1 if the prediction equals ANY acceptable reference, else 0."""
    if isinstance(references, str):  # allow one reference or a list
        references = [references]
    if normalize:
        prediction = normalize_answer(prediction)
        references = [normalize_answer(ref) for ref in references]
    return int(any(prediction == ref for ref in references))


def dataset_em(predictions, references, normalize=False):
    """Average EM over a dataset. references[i] may be a string or a list."""
    if len(predictions) != len(references):
        raise ValueError("predictions and references must have equal length")
    if not predictions:
        raise ValueError("the dataset must not be empty")
    scores = [exact_match(p, r, normalize) for p, r in zip(predictions, references)]
    return sum(scores) / len(scores)


refs = ["Paris", "4", "Jupiter", "H2O", "Phnom Penh"]
preds = ["Paris", "4", "Jupiter", "Water", "Phnom Penh"]
print("Example 1 strict EM:", dataset_em(preds, refs))
print("Multiple references:", exact_match("four", ["4", "four"]))
print(repr(normalize_answer("ភ្នំពេញ។")))

pairs = [
    ("Paris", "paris"),
    ("Phnom Penh", "Phnom Penh!"),
    ("The United States", "United States"),
    ("Phnom Penh", "The answer is Phnom Penh"),
]
for ref, pred in pairs:
    print(
        f"{pred!r:28} raw={exact_match(pred, ref)} "
        f"normalized={exact_match(pred, ref, normalize=True)}"
    )
