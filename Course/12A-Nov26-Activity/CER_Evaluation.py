"""Group 9: Character Error Rate (CER).

Python source version of CER_Evaluation.ipynb.
Run with: conda run -n Py311-TF python CER_Evaluation.py
Dependency: jiwer (tested with version 4.0.0).

This script runs local examples and scores previously collected answers.
It does not contact AI services or train models. See the notebook for the
full explanations, experiment limitations, and source links.

Text rules: preserve case, spaces, punctuation, and Unicode code points.
Reject empty references; allow empty predictions.
"""


# %% D. Build the CER calculation in Python
# Corresponds to notebook cell 6.
import sys
from importlib import metadata

print("Python:", sys.version.split()[0])
print("Interpreter:", sys.executable)

try:
    print("JiWER:", metadata.version("jiwer"))
except metadata.PackageNotFoundError:
    print("JiWER is not installed. See the setup cell in Section E.")


# %% D2. Look at two text values
# Corresponds to notebook cell 8.
example_reference = "plant"
example_prediction = "blat"

print("Reference:", repr(example_reference))
print("Prediction:", repr(example_prediction))
print("Reference length:", len(example_reference))
print("Prediction length:", len(example_prediction))


# %% D3. Find the smallest number of character changes
# Corresponds to notebook cell 10.
def character_distance(reference, prediction):
    """Return the minimum character edits between two strings."""
    # Creating each prediction prefix from empty text needs insertions.
    previous_row = list(range(len(prediction) + 1))

    for i, reference_char in enumerate(reference, start=1):
        # Removing this reference prefix to make empty text needs i deletions.
        current_row = [i]

        for j, prediction_char in enumerate(prediction, start=1):
            replacement_cost = 0 if reference_char == prediction_char else 1

            deletion = previous_row[j] + 1
            insertion = current_row[j - 1] + 1
            substitution = previous_row[j - 1] + replacement_cost

            current_row.append(min(deletion, insertion, substitution))

        previous_row = current_row

    return previous_row[-1]


example_errors = character_distance(example_reference, example_prediction)
print("Minimum character changes:", example_errors)
print("Expected: 2 — one substitution and one deletion.")


# %% D4. Turn the error count into CER
# Corresponds to notebook cell 12.
def calculate_cer(reference, prediction):
    """Return CER as a ratio; reject non-text inputs and empty references."""
    if not isinstance(reference, str):
        raise TypeError("Reference must be text.")
    if not isinstance(prediction, str):
        raise TypeError("Prediction must be text.")
    if len(reference) == 0:
        raise ValueError("Reference must contain at least one character.")

    errors = character_distance(reference, prediction)
    return errors / len(reference)


example_score = calculate_cer(example_reference, example_prediction)
print("CER as a number:", example_score)
print(f"CER as a percentage: {example_score:.2%}")
print("Expected: 0.4 and 40.00%")


# %% E. Check the calculation
# Corresponds to notebook cell 14.
# Each row: reference, prediction, expected minimum error count.
check_cases = [
    ("cat", "cat", 0),
    ("cat", "cut", 1),
    ("cat", "ct", 1),
    ("cat", "cart", 1),
    ("plant", "blat", 2),
    ("cat", "chats", 2),
    ("cat", "", 3),
    ("a", "abcd", 3),
    ("cat", "Cat", 1),
    ("cat", "cat!", 1),
    ("cat", " cat", 1),
    ("cat", "cat ", 1),
    ("a cat", "acat", 1),
]

for ref, pred, expected_errors in check_cases:
    errors = character_distance(ref, pred)
    score = calculate_cer(ref, pred)
    assert errors == expected_errors, (ref, pred, errors, expected_errors)
    assert abs(score - expected_errors / len(ref)) < 1e-12
    print(f"{ref!r} → {pred!r}: errors={errors}, CER={score:.2%} — PASS")

print(f"\nKnown-answer checks passed: {len(check_cases)}/{len(check_cases)}")


# %% E2. Check invalid inputs
# Corresponds to notebook cell 16.
invalid_cases = [
    ("", "cat", ValueError),
    ("", "", ValueError),
    (123, "cat", TypeError),
    ("cat", None, TypeError),
]

for ref, pred, expected_exception in invalid_cases:
    try:
        calculate_cer(ref, pred)
    except expected_exception as error:
        print(f"{ref!r}, {pred!r}: PASS — {error}")
    else:
        raise AssertionError("The function should have rejected this input.")


# %% E3. Check against JiWER
# Corresponds to notebook cell 18.
# Run this line only if JiWER is missing from the selected kernel.

import jiwer

print("JiWER version:", metadata.version("jiwer"))

# No Strip(), lowercase conversion, or punctuation removal.
character_rules = jiwer.Compose([
    jiwer.ReduceToListOfListOfChars(),
])


def inspect_character_errors(reference, prediction):
    """Return JiWER counts using the same input rules as our CER function."""
    calculate_cer(reference, prediction)  # Apply our input checks first.
    return jiwer.process_characters(
        reference,
        prediction,
        reference_transform=character_rules,
        hypothesis_transform=character_rules,
    )


for ref, pred, expected_errors in check_cases:
    result = inspect_character_errors(ref, pred)
    our_score = calculate_cer(ref, pred)
    library_errors = result.substitutions + result.deletions + result.insertions
    assert library_errors == expected_errors
    assert abs(our_score - result.cer) < 1e-12

print(f"JiWER comparison checks passed: {len(check_cases)}/{len(check_cases)}")


# %% E4. Display the three error counts
# Corresponds to notebook cell 20.
for ref, pred in [("plant", "blat"), ("cat", "chats")]:
    result = inspect_character_errors(ref, pred)
    print(f"\nReference: {ref!r} | Prediction: {pred!r}")
    print("Substitutions:", result.substitutions)
    print("Deletions:", result.deletions)
    print("Insertions:", result.insertions)
    print("Reference characters:", len(ref))
    print(f"CER: {result.cer:.2%}")


# %% F. Compare real answers from two LLMs
# Corresponds to notebook cell 22.
# Prepared inputs and references. These are not model predictions.
evaluation_tasks = [
    {"id": 1, "input": "The cat is sleping.",
     "reference": "The cat is sleeping."},
    {"id": 2, "input": "I drink watter every day.",
     "reference": "I drink water every day."},
    {"id": 3, "input": "She goes to schol.",
     "reference": "She goes to school."},
    {"id": 4, "input": "Please close the dor.",
     "reference": "Please close the door."},
    {"id": 5, "input": "We are learning Pythn.",
     "reference": "We are learning Python."},
]

tasks_by_id = {task["id"]: task for task in evaluation_tasks}
assert len(tasks_by_id) == len(evaluation_tasks), "Task IDs must be unique."

prompt_instruction = (
    "Correct the spelling mistakes in the sentence below. "
    "Keep the wording, capitalization, and punctuation unchanged "
    "except where needed to fix spelling. "
    "Return only the corrected sentence, without explanations."
)

for task in evaluation_tasks:
    task["prompt"] = prompt_instruction + "\n\n" + task["input"]

# Show the prompts for the two tested tasks, without their references.
for task_id in [1, 2]:
    print(f"\n=== PROMPT FOR TASK {task_id} ===")
    print(tasks_by_id[task_id]["prompt"])


# %% F2. Store the collected answers
# Corresponds to notebook cell 24.
model_results = [
    {"task_id": 1, "model": "Claude — Sonnet 5.5 Medium",
     "answer": "The cat is sleeping."},
    {"task_id": 1, "model": "Gemini — Auto",
     "answer": "The cat is sleeping."},
    {"task_id": 2, "model": "Claude — Sonnet 5.5 Medium",
     "answer": "I drink water every day."},
    {"task_id": 2, "model": "Gemini — Auto",
     "answer": "I drink water every day."},
]

# Check that no answer is missing, unknown, or recorded twice.
expected_models = {"Claude — Sonnet 5.5 Medium", "Gemini — Auto"}
expected_pairs = {
    (model_name, task_id)
    for model_name in expected_models
    for task_id in [1, 2]
}
recorded_pairs = {(row["model"], row["task_id"]) for row in model_results}
assert len(recorded_pairs) == len(model_results), "Duplicate answer records found."
assert recorded_pairs == expected_pairs, "Missing or unexpected answer records."

for row in model_results:
    assert isinstance(row["answer"], str), "Each answer must be text."
    print(f"Task {row['task_id']} | {row['model']} | {row['answer']!r}")

print("\nCollected answers:", len(model_results))
print("Tested tasks: 1 and 2. Untested tasks: 3, 4, and 5.")


# %% F3. Calculate each answer's score
# Corresponds to notebook cell 26.
scored_results = []

for row in model_results:
    ref = tasks_by_id[row["task_id"]]["reference"]
    pred = row["answer"]
    details = inspect_character_errors(ref, pred)
    score = calculate_cer(ref, pred)
    assert abs(score - details.cer) < 1e-12

    scored_results.append({
        **row,
        "reference": ref,
        "substitutions": details.substitutions,
        "deletions": details.deletions,
        "insertions": details.insertions,
        "errors": details.substitutions + details.deletions + details.insertions,
        "reference_characters": len(ref),
        "cer": score,
    })

# Show the actual texts before the score table.
for row in scored_results:
    print(f"\nTask {row['task_id']} — {row['model']}")
    print("Reference:", repr(row["reference"]))
    print("Answer:   ", repr(row["answer"]))

lines = [
    "| Task | Model | S | D | I | Reference characters | CER |",
    "|---|---|---|---|---|---|---|",
]
for row in scored_results:
    lines.append(
        f"| {row['task_id']} | {row['model']} | "
        f"{row['substitutions']} | {row['deletions']} | "
        f"{row['insertions']} | {row['reference_characters']} | "
        f"{row['cer']:.2%} |"
    )

print("\n".join(lines))


# %% F4. Calculate overall CER for each service
# Corresponds to notebook cell 28.
model_summary = {}

for row in scored_results:
    model_name = row["model"]
    if model_name not in model_summary:
        model_summary[model_name] = {
            "tasks": 0,
            "errors": 0,
            "reference_characters": 0,
        }

    totals = model_summary[model_name]
    totals["tasks"] += 1
    totals["errors"] += row["errors"]
    totals["reference_characters"] += row["reference_characters"]

lines = [
    "| Model | Tested tasks | Total errors | Reference characters | Overall CER |",
    "|---|---|---|---|---|",
]
for model_name, totals in sorted(model_summary.items()):
    totals["cer"] = totals["errors"] / totals["reference_characters"]
    lines.append(
        f"| {model_name} | {totals['tasks']} | {totals['errors']} | "
        f"{totals['reference_characters']} | {totals['cer']:.2%} |"
    )

print("\n".join(lines))

# Confirm the expected result for the stored experiment.
for totals in model_summary.values():
    assert totals["tasks"] == 2
    assert totals["reference_characters"] == 44
    assert totals["errors"] == 0
    assert totals["cer"] == 0
print("Stored experiment checks passed.")


# %% G. Strengths, limits, and conclusion
# Corresponds to notebook cell 31.
fact_reference = "The card is valid for 4 years."
fact_prediction = "The card is valid for 5 years."

print("Reference:", fact_reference)
print("Prediction:", fact_prediction)
print("Character errors:", character_distance(fact_reference, fact_prediction))
print(f"CER: {calculate_cer(fact_reference, fact_prediction):.2%}")
print("The text is close, but the stated number of years is wrong.")
