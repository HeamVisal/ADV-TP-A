"""Chapter 10 code, extracted from Combined_LLM_Evaluation_Report.md.

Edit the report, then run: python tools/build_report.py code
"""

import re

import jiwer
import sacrebleu
from bert_score import score as bertscore
from nltk.translate.meteor_score import meteor_score
from rouge_score import rouge_scorer

reference = "The medicine is safe for children."
candidates = {
    "A exact copy": "The medicine is safe for children.",
    "B paraphrase": "Children can take this medicine safely.",
    "C negation": "The medicine is not safe for children.",
    "D lowercase": "the medicine is safe for children",
}

rouge = rouge_scorer.RougeScorer(["rougeL"])


def words(text):
    """Split words and punctuation for METEOR: "children." -> children, ."""
    return re.findall(r"\w+|[^\w\s]", text)


_, _, bert_f1 = bertscore(
    list(candidates.values()),
    [reference] * len(candidates),
    model_type="bert-base-uncased",
    num_layers=9,
)


print("cand          EM  BLEU   ROUGE-L METEOR BERT-F1  WER    CER")
for (name, cand), bf1 in zip(candidates.items(), bert_f1):
    em = int(cand == reference)
    bleu = sacrebleu.sentence_bleu(cand, [reference]).score
    rl = rouge.score(reference, cand)["rougeL"].fmeasure
    met = meteor_score([words(reference)], words(cand))
    wer = jiwer.wer(reference, cand)
    cer = jiwer.cer(reference, cand)
    print(
        f"{name:13} {em}  {bleu:6.2f} {rl:7.4f} {met:6.4f} {bf1:7.4f} "
        f"{wer:6.4f} {cer:6.4f}"
    )
