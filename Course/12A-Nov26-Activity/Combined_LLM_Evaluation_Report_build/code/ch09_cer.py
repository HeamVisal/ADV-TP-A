"""Chapter 9 code, extracted from Combined_LLM_Evaluation_Report.md.

Edit the report, then run: python tools/build_report.py code
"""

import unicodedata

import jiwer
import regex  # third-party module; supports \X (grapheme clusters)


def character_distance(reference, prediction):
    """Minimum character edits (Levenshtein distance), two-row version."""
    previous_row = list(range(len(prediction) + 1))
    for i, reference_char in enumerate(reference, start=1):
        current_row = [i]
        for j, prediction_char in enumerate(prediction, start=1):
            replacement_cost = 0 if reference_char == prediction_char else 1
            current_row.append(
                min(
                    previous_row[j] + 1,  # deletion
                    current_row[j - 1] + 1,  # insertion
                    previous_row[j - 1] + replacement_cost,
                )
            )
        previous_row = current_row
    return previous_row[-1]


def calculate_cer(reference, prediction):
    """CER as a ratio; empty references are rejected (Group 9's rule)."""
    if not isinstance(reference, str) or not isinstance(prediction, str):
        raise TypeError("Both inputs must be text.")
    if len(reference) == 0:
        raise ValueError("Reference must contain at least one character.")
    return character_distance(reference, prediction) / len(reference)


def edit_table(reference, prediction):
    """Full table D[i][j] for teaching (Table 9.4)."""
    table = [[0] * (len(prediction) + 1) for _ in range(len(reference) + 1)]
    for i in range(len(reference) + 1):
        table[i][0] = i
    for j in range(len(prediction) + 1):
        table[0][j] = j
    for i in range(1, len(reference) + 1):
        for j in range(1, len(prediction) + 1):
            cost = 0 if reference[i - 1] == prediction[j - 1] else 1
            table[i][j] = min(
                table[i - 1][j] + 1, table[i][j - 1] + 1, table[i - 1][j - 1] + cost
            )
    return table


for row in edit_table("plant", "blat"):
    print(row)

for ref, pred in [
    ("cat", "cut"),
    ("cat", "cart"),
    ("plant", "blat"),
    ("kitten", "sitting"),
    ("a", "abcd"),
    ("The card is valid for 4 years.", "The card is valid for 5 years."),
]:
    print(f"{ref!r:34} -> {pred!r:34} CER={calculate_cer(ref, pred):.2%}")


# Group 9's stored answers (Claude and Gemini gave identical answers).
tasks = {
    "The cat is sleeping.": "The cat is sleeping.",
    "I drink water every day.": "I drink water every day.",
}
errors = sum(character_distance(r, p) for r, p in tasks.items())
chars = sum(len(r) for r in tasks)
print(f"Overall: {errors} errors / {chars} characters = {errors / chars:.2%}")

# Code points versus visible clusters in Khmer.
word = "សួស្តី"
print("Code points:", len(word), [f"U+{ord(c):04X}" for c in word])
print("Grapheme clusters (\\X):", regex.findall(r"\X", word))

# The same visible letter can be stored in two ways.
composed, decomposed = "é", "é"
print("Raw CER:", calculate_cer(composed, decomposed))
print(
    "CER after NFC:",
    calculate_cer(
        unicodedata.normalize("NFC", composed), unicodedata.normalize("NFC", decomposed)
    ),
)

# jiwer's default cleanup differs from Group 9's rules.
print("jiwer default strips outer spaces:", jiwer.cer("cat", " cat"))
detail = jiwer.process_characters("plant", "blat")
print("jiwer S/D/I:", detail.substitutions, detail.deletions, detail.insertions)
