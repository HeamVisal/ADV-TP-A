"""Chapter 7 code, extracted from Combined_LLM_Evaluation_Report.md.

Edit the report, then run: python tools/build_report.py code
"""

from bert_score import score
from transformers import AutoTokenizer

CONFIG = {"model_type": "bert-base-uncased", "num_layers": 9}  # Group 7

# Group 7, Example 1 (paraphrasing). Outputs copied from the slides.
ref = (
    "Artificial intelligence accelerates scientific discovery by "
    "analyzing massive datasets quickly."
)
cands = [
    "AI accelerates scientific discovery by rapidly analyzing vast datasets.",
    ref,
]  # SmolLM2 copied the reference
P, R, F = score(cands, [ref] * len(cands), **CONFIG)
for name, p, r, f in zip(["Qwen2.5-0.5B", "SmolLM2-135M"], P, R, F):
    print(f"Ex1 {name:13} P={p:.4f} R={r:.4f} F1={f:.4f}")

# Group 7, Example 2 (summary with missing details).
ref2 = "The city opened a new public library with free Wi-Fi and study rooms."
cands2 = [
    (
        "The city has launched a new public library that provides free "
        "Wi-Fi and study spaces for residents."
    ),
    "The city opened a new public library.",
]
P, R, F = score(cands2, [ref2] * 2, **CONFIG)
for name, p, r, f in zip(["Qwen2.5-0.5B", "SmolLM2-135M"], P, R, F):
    print(f"Ex2 {name:13} P={p:.4f} R={r:.4f} F1={f:.4f}")


# Teaching examples: similar wording, different meaning.
refs = [
    "The boy is happy",
    "The dog chased the cat",
    "The medicine is safe for children.",
    "The train leaves at 9 a.m.",
]
hyps = [
    "The kid feels joyful",
    "The cat chased the dog",
    "The medicine is not safe for children.",
    "The train leaves at 5 p.m.",
]
_, _, F_raw = score(hyps, refs, **CONFIG)
_, _, F_res = score(hyps, refs, lang="en", rescale_with_baseline=True, **CONFIG)
for h, raw, res in zip(hyps, F_raw, F_res):
    print(f"{h!r:42} raw F1={raw:.4f} rescaled F1={res:.4f}")

(_, _, _), config_hash = score(hyps[:1], refs[:1], return_hash=True, **CONFIG)
print("Hash:", config_hash)


# Language support: look at how each model's tokenizer splits Khmer text.
# bert-score uses bert-base-multilingual-cased by default for lang="km".
khmer = "ខ្ញុំចូលចិត្តអានសៀវភៅ"  # "I like reading books"
for name in ["bert-base-multilingual-cased", "xlm-roberta-base"]:
    tokenizer = AutoTokenizer.from_pretrained(name)
    print(name, tokenizer.tokenize(khmer))
