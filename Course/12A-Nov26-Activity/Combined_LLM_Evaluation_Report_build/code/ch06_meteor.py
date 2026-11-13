"""Chapter 6 code, extracted from Combined_LLM_Evaluation_Report.md.

Edit the report, then run: python tools/build_report.py code
"""

import re

from nltk.translate.meteor_score import meteor_score

examples = [
    ("the cat sleeps", "the cat sleeps"),  # Group 6, Example 1
    ("the cat sleeps", "sleeps cat the"),  # Group 6, Example 2
    (
        "Machine learning helps computers learn from data.",
        "Machine learning helps computers learn from data.",
    ),
    (
        "Machine learning helps computers learn from data.",
        "Computers learn from data with machine learning.",
    ),
    ("the student is happy", "the pupil is glad"),
    ("the cats are sleeping", "the cat is sleeping"),
]
for ref, hyp in examples:
    # NLTK needs token lists, not strings. Here we split on spaces,
    # so "data." stays one token including its full stop.
    score = meteor_score([ref.split()], hyp.split())
    print(f"{hyp!r:52} {score:.4f}")


def words(text):
    """Separate punctuation from words: 'data.' -> 'data', '.'"""
    return re.findall(r"\w+|[^\w\s]", text)


ref = "Machine learning helps computers learn from data."
hyp = "Computers learn from data with machine learning."
print("Split on spaces     :", round(meteor_score([ref.split()], hyp.split()), 4))
print("Punctuation split   :", round(meteor_score([words(ref)], words(hyp)), 4))

try:
    meteor_score(["the cat sleeps"], "the cat sleeps")  # raw strings
except TypeError as error:
    print("TypeError:", str(error)[:60], "...")
