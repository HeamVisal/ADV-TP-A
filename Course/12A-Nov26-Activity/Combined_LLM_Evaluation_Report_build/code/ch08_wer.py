"""Chapter 8 code, extracted from Combined_LLM_Evaluation_Report.md.

Edit the report, then run: python tools/build_report.py code
"""

import jiwer

pairs = [
    ("I love to read books", "I love to read book"),  # Group 8 ex. 1
    ("The weather is nice today", "weather is very nice today"),  # Group 8 ex. 2
    ("the cat sits on the mat", "the cat sit on the mat"),  # Group 8 code
    ("turn off the light", "turn of light"),  # Example 8.3
    ("yes", "yes yes yes"),  # above 100%
]
for ref, hyp in pairs:
    out = jiwer.process_words(ref, hyp)  # reference first, hypothesis second
    print(
        f"{hyp!r:30} S={out.substitutions} D={out.deletions} "
        f"I={out.insertions} WER={out.wer:.4f}"
    )

print(
    jiwer.visualize_alignment(
        jiwer.process_words("The weather is nice today", "weather is very nice today")
    )
)


# Two different minimum alignments exist here (2 S, or 1 D + 1 I);
# jiwer reports one of them. The total, 2 edits, is the same.
swap = jiwer.process_words("a b", "b a")
print("Swap:", swap.substitutions, swap.deletions, swap.insertions, swap.wer)

# Lists: total errors / total reference words (not an average of rates).
refs = ["a b c d", "e f"]
hyps = ["a b c d", "x y"]
print("Corpus WER:", round(jiwer.wer(refs, hyps), 4))

# Same cleanup applied to reference and hypothesis.
clean = jiwer.Compose(
    [
        jiwer.ToLowerCase(),
        jiwer.RemovePunctuation(),
        jiwer.RemoveMultipleSpaces(),
        jiwer.Strip(),
        jiwer.ReduceToListOfListOfWords(),
    ]
)
print("Raw WER    :", jiwer.wer("Turn off the lights.", "turn off the lights"))
print(
    "Cleaned WER:",
    jiwer.wer(
        "Turn off the lights.",
        "turn off the lights",
        reference_transform=clean,
        hypothesis_transform=clean,
    ),
)

# jiwer 4 edge case: an empty reference returns the number of insertions.
print("Empty reference:", jiwer.wer("", "a b"))
