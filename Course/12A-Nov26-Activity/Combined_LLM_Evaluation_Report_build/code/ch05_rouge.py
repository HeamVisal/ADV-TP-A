"""Chapter 5 code, extracted from Combined_LLM_Evaluation_Report.md.

Edit the report, then run: python tools/build_report.py code
"""

from itertools import combinations

from rouge_score import rouge_scorer


def fmt(score):
    return f"P={score.precision:.4f} R={score.recall:.4f} F1={score.fmeasure:.4f}"


scorer = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"])
# RougeScorer.score(target, prediction): the REFERENCE comes first.
for ref, cand in [
    ("the weather is cold outside", "the weather is cold"),
    ("the cat sat on the mat", "the cat rested on the mat"),
]:
    for name, s in scorer.score(ref, cand).items():
        print(f"{cand!r:30} {name:7} {fmt(s)}")

# ROUGE-L versus ROUGE-Lsum: sentences are separated by newlines.
ref = "heavy rain closed the schools today"
cand = "the schools closed today\nheavy rain fell"
for name in ["rougeL", "rougeLsum"]:
    s = rouge_scorer.RougeScorer([name]).score(ref, cand)[name]
    print(f"{name:9} {fmt(s)}")


def skip_bigrams(tokens):
    """Ordered pairs (earlier word, later word), any gap allowed."""
    return set(combinations(tokens, 2))  # teaching version: no repeated words


def rouge_s(ref, cand, with_unigrams=False):
    r_units, c_units = skip_bigrams(ref.split()), skip_bigrams(cand.split())
    if with_unigrams:  # ROUGE-SU also counts single words
        r_units |= {(w,) for w in ref.split()}
        c_units |= {(w,) for w in cand.split()}
    hits = len(r_units & c_units)
    p, r = hits / len(c_units), hits / len(r_units)
    f = 0.0 if hits == 0 else 2 * p * r / (p + r)
    return round(p, 4), round(r, 4), round(f, 4)


print("ROUGE-S  the cat sat / the cat slept:", rouge_s("the cat sat", "the cat slept"))
print("ROUGE-SU A B C / C B A:", rouge_s("A B C", "C B A", with_unigrams=True))


def wlcs(x, y, f=lambda k: k**2):
    """Weighted LCS (Lin, 2004): consecutive matches earn extra credit."""
    m, n = len(x), len(y)
    c = [[0.0] * (n + 1) for _ in range(m + 1)]
    w = [[0] * (n + 1) for _ in range(m + 1)]  # current run length
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if x[i - 1] == y[j - 1]:
                k = w[i - 1][j - 1]
                c[i][j] = c[i - 1][j - 1] + f(k + 1) - f(k)
                w[i][j] = k + 1
            else:
                c[i][j] = max(c[i - 1][j], c[i][j - 1])
    return c[m][n]


ref = list("ABCDEFG")
for cand in ["A B C D H I K", "A H B K C I D"]:
    score = wlcs(ref, cand.split())
    recall = (score / len(ref) ** 2) ** 0.5  # inverse of f(k) = k^2
    print(f"ROUGE-W recall for {cand!r}: WLCS={score:.0f}, R={recall:.4f}")


# The default tokenizer keeps only a-z and 0-9, so Khmer text disappears.
khmer = "ខ្ញុំ ចូលចិត្ត អាន សៀវភៅ"
print(
    "Default tokenizer, identical Khmer texts:",
    fmt(rouge_scorer.RougeScorer(["rouge1"]).score(khmer, khmer)["rouge1"]),
)


class WhitespaceTokenizer:
    """Use only for text that is already segmented into words."""

    def tokenize(self, text):
        return text.split()


custom = rouge_scorer.RougeScorer(["rouge1"], tokenizer=WhitespaceTokenizer())
print(
    "Whitespace tokenizer, identical Khmer texts:",
    fmt(custom.score(khmer, khmer)["rouge1"]),
)
