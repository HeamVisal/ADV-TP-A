"""Chapter 4 code, extracted from Combined_LLM_Evaluation_Report.md.

Edit the report, then run: python tools/build_report.py code
"""

import math
from collections import Counter

import sacrebleu
from nltk.translate.bleu_score import SmoothingFunction, sentence_bleu


def ngrams(tokens, n):
    """All runs of n consecutive tokens, counted."""
    return Counter(tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1))


def simple_bleu(candidate, references, max_n=4):
    """Sentence BLEU with uniform weights and no smoothing (Papineni et al.)."""
    cand = candidate.split()
    refs = [r.split() for r in references]
    log_sum = 0.0
    for n in range(1, max_n + 1):
        cand_counts = ngrams(cand, n)
        # Clipping: a candidate n-gram earns credit at most as many times
        # as it appears in any single reference.
        max_ref = Counter()
        for ref in refs:
            for gram, count in ngrams(ref, n).items():
                max_ref[gram] = max(max_ref[gram], count)
        clipped = sum(min(c, max_ref[g]) for g, c in cand_counts.items())
        total = max(sum(cand_counts.values()), 1)
        print(f"  p{n} = {clipped}/{total}")
        if clipped == 0:
            return 0.0  # log(0) is undefined, so unsmoothed BLEU is 0
        log_sum += (1 / max_n) * math.log(clipped / total)
    c = len(cand)
    # Effective reference length: the reference length closest to c.
    r = min((abs(len(ref) - c), len(ref)) for ref in refs)[1]
    bp = 1.0 if c > r else math.exp(1 - r / c)
    print(f"  c={c}, r={r}, BP={bp:.4f}")
    return bp * math.exp(log_sum)


ref = "the cat is on the mat"
cand = "the cat is on mat"
print("BLEU-2 (own):", round(simple_bleu(cand, [ref], max_n=2), 4))
print("BLEU-4 (own):", round(simple_bleu(cand, [ref], max_n=4), 4))
print("BLEU-4 (sacreBLEU):", sacrebleu.sentence_bleu(cand, [ref]))

# Clipping example: a repeated word.
print(
    "Clipped unigram precision:",
    sentence_bleu([ref.split()], ["the"] * 7, weights=(1,)),
)


# A paraphrase with no matching bigram: three tools, three answers.
para = "the feline is asleep"
print("Own, unsmoothed :", simple_bleu(para, ["the cat is sleeping"]))
print(
    "NLTK method1    :",
    round(
        sentence_bleu(
            [["the", "cat", "is", "sleeping"]],
            para.split(),
            smoothing_function=SmoothingFunction().method1,
        ),
        4,
    ),
)
print(
    "sacreBLEU (exp) :",
    round(sacrebleu.sentence_bleu(para, ["the cat is sleeping"]).score, 2),
)

# Corpus BLEU versus the average of sentence BLEU scores.
hyps = ["the cat is on the mat", "a dog runs"]
refs = ["the cat is on the mat", "the dog is running in the park"]
bleu = sacrebleu.BLEU()
corpus = bleu.corpus_score(hyps, [refs])  # [refs] = one reference set
sentence_scores = [sacrebleu.sentence_bleu(h, [r]).score for h, r in zip(hyps, refs)]
print("Corpus BLEU:", round(corpus.score, 2))
print(
    "Sentence BLEU:",
    [round(s, 2) for s in sentence_scores],
    "average:",
    round(sum(sentence_scores) / 2, 2),
)
print("Signature:", bleu.get_signature())
