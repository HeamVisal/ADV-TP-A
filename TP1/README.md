# APDS TP1: Lecture Summary

- **Course:** Advanced Programming for Data Science (APDS)
- **Department:** Applied Mathematics and Statistics (AMS)
- **Lecturer:** Mr.VANN Visal
- **Institution:** Institute of Technology of Cambodia (ITC)
- **Lecture date:** October 13, 2026

This lesson covered Python's main building blocks, clean code, PEP 8, debugging,
and tools for maintaining a consistent coding style. The summary follows the
lecture's three main topics and includes short examples of the ideas in practice.

## 1. Introduction

- **Function:** A reusable block of code that performs a specific task. A function
  can receive input through parameters and return a result. For example, a
  `calculate_total(price, quantity)` function could calculate the cost of several
  items without repeating the calculation throughout a program. A function that
  finishes without an explicit return value returns `None`.
- **Variable:** A name that refers to a value or object. Variables let us access
  and work with data, and we can assign a different value to the same name later.
  For example, `student_score = 75` associates the name `student_score` with `75`.
- **Method:** A function associated with a class or an object. An instance method
  describes an action an object can perform and receives that object through its
  first parameter, conventionally named `self`.
- **Class:** A blueprint for creating objects that share a structure and behavior.
  It can define attributes for data and methods for actions. An object created
  from a class is called an instance of that class.
- **Module:** A Python source file containing code, such as functions, classes,
  and variables, that other files can import and reuse. For example,
  `math_helpers.py` could contain calculation functions.
- **Package:** A way to organize related modules together. For example, a package
  named `utilities` could contain a module named `math_helpers`, imported using
  the dotted name `utilities.math_helpers`. Regular packages use an `__init__.py`
  file; namespace packages can omit it.
- **Constant:** A named value intended to stay unchanged while the program runs.
  Python relies on a naming convention for ordinary constants rather than
  preventing reassignment. For example, `PASS_MARK = 50` communicates that this
  value should be treated as fixed.

The following example shows the relationship between a class, an object, and a
method:

```python
class Student:
    """Represent a student in a simple example."""

    def greet(self):
        """Return a greeting for the student."""
        return "Hello, welcome to class!"


student = Student()
print(student.greet())
```

Here, `Student` is the class, `student` refers to an instance, and `greet()` is an
instance method. Calling it through `student` passes that object as `self`.

## 2. Clean Code, PEP 8, and Debugging

### 2.1 Clean Code Principles

Clean code communicates its purpose clearly and is easy to maintain. The main
practices discussed in the lesson were:

- **Use descriptive names.** Prefer names such as `student_score` and
  `calculate_average` when they explain the data or operation. Short names are
  useful when their meaning is clear from a small context.
- **Give functions a clear responsibility.** Break a long function into smaller
  helpers when it mixes unrelated tasks. This makes each part easier to
  understand and test independently.
- **Reuse shared logic.** Move repeated calculations or operations into functions
  so a correction can be made in one place.
- **Name values that may need to change.** A constant such as `PASS_MARK` makes a
  grading threshold easier to recognize and update than repeated literal values.
- **Use comments to explain decisions.** Describe the reason behind a difficult
  step and keep the explanation accurate when the code changes.
- **Document reusable code.** A docstring is a string literal used as the first
  statement in a module, class, or function. Summarize its purpose and explain
  relevant inputs, outputs, and expected errors.
  [PEP 257](https://peps.python.org/pep-0257/) recommends triple double quotes, a
  clear opening sentence, and a period.
- **Keep control flow simple.** An early return, also called a guard clause, can
  handle a special case before the main calculation and reduce unnecessary
  nesting.

For example, this function documents its result and handles an empty list before
performing the calculation:

```python
def calculate_average(scores):
    """Return the mean score, or None if no scores are available."""
    if not scores:
        return None
    return sum(scores) / len(scores)


print(calculate_average([60, 80, 100]))
print(calculate_average([]))
```

The outputs are `80.0` and `None`. The early return prevents division by zero for
an empty list, while the main calculation remains easy to follow.

### 2.2 PEP 8 Guidelines

[PEP 8](https://peps.python.org/pep-0008/) is Python's style guide. It provides
conventions that help programmers write consistent, readable code that is easier
to review and maintain. Apply the project's agreed conventions consistently.

| Rule | Guidance |
| --- | --- |
| Indentation | Use four spaces per level in new code. For continuation lines, align wrapped elements or use a clear hanging indent. |
| Line length | Normally limit code lines to 79 characters, and comments and docstrings to 72. |
| Imports | Place imports after module comments or docstrings and before constants. Group standard library, third-party, and local imports, separated by blank lines. Avoid wildcard imports. |
| Naming | Use `snake_case` for variables, functions, and methods; `UPPER_CASE` for constants; and `PascalCase` for classes. |
| Whitespace | Space assignment and comparison operators, and keep arithmetic readable. Avoid extra spaces inside delimiters or before a function call's `(`. |
| Commas and colons | Write `[60, 80]` and `{"score": 80}`. Slice notation differs: `scores[1:3]`. |
| Blank lines | Use two between top-level functions or classes, and one between methods. |
| Wrapped expressions | Prefer parentheses for wrapping. For new code, prefer breaks before binary operators. |
| Quotes | Use string quotes consistently; docstrings conventionally use triple double quotes. |

Import separate modules on separate lines, such as `import math` followed by
`import logging`. Importing several names from one module, such as
`from math import ceil, floor`, is also valid.

For default parameters, write `port=8080` without an annotation and
`port: int = 8080` with one. Keyword arguments use `connect(port=8080)`.

For example:

```python
PASS_MARK = 50


def has_passed(score):
    return score >= PASS_MARK


student_score = 75
print(has_passed(student_score))
```

This example uses clear names, a constant, four-space indentation, and consistent
spacing. It prints `True` because the student's score meets the pass mark.

### 2.3 Useful Python Idioms

- **Check for a missing value with identity:** use `result is None` or
  `result is not None`.
- **Check empty collections directly:** use `if not scores:` for an empty list,
  and `if scores:` when it contains items. Empty strings, tuples, and dictionaries
  are also false in a condition.
- **Use boolean values directly:** when `has_passed` is a boolean, write
  `if has_passed:` or `if not has_passed:` without comparing it to `True` or
  `False`.

### 2.4 Debugging and Error Handling

Debugging is the process of finding the cause of an error and correcting it.
Problems can include invalid syntax, exceptions during execution, or logic that
produces an incorrect result even though the program runs.

For example, `TypeError` can indicate incompatible types, `KeyError` a missing
dictionary key, and `IndexError` an invalid sequence index.

A useful debugging process is:

1. **Reproduce the problem.** Run the program with the input that caused the
   unexpected behavior.
2. **Read the error message.** For an exception, the last line identifies the
   error type and message. The traceback shows the relevant calls and locations.
3. **Narrow down the cause.** Check the reported line, variable values, types, and
   conditions. Run a small function independently with known inputs to check its
   behavior before returning to the complete program.
4. **Fix the cause.** Make a focused correction based on what caused the failure.
5. **Test again.** Repeat the original case and try other inputs to check that the
   correction works without introducing another problem.

Useful techniques include:

- **Temporary output:** `print()` can quickly show a value while investigating a
  small problem. Remove temporary output when it is no longer useful.
- **Logging:** Python's [logging module](https://docs.python.org/3/howto/logging.html)
  records events at levels such as
  `DEBUG`, `INFO`, `WARNING`, `ERROR`, and `CRITICAL`. Configure the logging level
  to control which messages appear without removing the logging calls.
- **Breakpoints:** `breakpoint()` normally opens Python's `pdb` debugger at that
  point. This lets us inspect variables and step through execution.
- **Specific exception handling:** catch expected exceptions by name. A bare
  `except:` also catches events such as `KeyboardInterrupt` and `SystemExit`, so
  it can hide problems or prevent an intended exit.

For example, converting text to an integer can raise `ValueError`. The following
code handles that expected input problem:

```python
raw_score = "eighty"

try:
    score = int(raw_score)
except ValueError:
    print("Enter a whole-number score.")
else:
    print(f"Score: {score}")
```

Test this example with both `"eighty"` and `"80"` to exercise the error and success
paths. Error handling defines how a program responds to an expected problem;
debugging helps identify and correct the cause of unexpected behavior.

## 3. Tips and Tricks to Help Code Follow PEP 8

### 3.1 Daily Coding Habits

1. Configure the editor to insert four spaces and show a line-length guide.
2. Use formatting and lint feedback regularly, rather than leaving all style
   corrections until the end of an activity.
3. Review names, comments, and docstrings manually. Use complete sentences for
   prose comments, preserving an identifier's spelling when it starts a sentence.
4. Test small functions as they are written, including ordinary inputs, empty
   collections, and boundary values such as a score equal to the pass mark.
5. Rerun relevant examples or tests after changing the code to verify its behavior.

### 3.2 Formatting and Linting with Ruff

[Ruff](https://docs.astral.sh/ruff/) provides a
[formatter](https://docs.astral.sh/ruff/formatter/) for code layout and a
[linter](https://docs.astral.sh/ruff/linter/) for detecting issues under enabled
rules. Install it in an activated Python virtual environment:

```bash
python -m pip install ruff
```

| Command | Purpose |
| --- | --- |
| `ruff check .` | Report lint issues in the current project. |
| `ruff check --fix .` | Apply available safe fixes for enabled rules. |
| `ruff format .` | Format the code. |
| `ruff format --check .` | Check formatting without changing files. |

Ruff's [default configuration](https://docs.astral.sh/ruff/configuration/) uses a
line length of 88 characters. To use the 79-character convention in a Python
project, an example `pyproject.toml` configuration is:

```toml
[tool.ruff]
line-length = 79

[tool.ruff.lint]
extend-select = ["I", "N", "E501"]
```

Here, `I` enables import-sorting checks, `N` enables naming checks, and `E501`
checks for long lines. Import sorting is handled by lint rules; the formatter
handles layout. Formatting attempts to wrap lines, but some still require manual
editing. Review reported issues and check the meaning of names, comments, and
docstrings yourself.

### 3.3 Editor Integration

An [editor integration](https://docs.astral.sh/ruff/editors/setup/), such as the
Ruff extension for VS Code, can show lint diagnostics while editing and run the
formatter on save. Use the same project configuration in the editor and the
command line so the results stay consistent.

## 4. References

- Personal class notes and a classmate's lecture summary for TP1.
- [PEP 8: Style Guide for Python Code](https://peps.python.org/pep-0008/)
- [PEP 257: Docstring Conventions](https://peps.python.org/pep-0257/)
- [Python Tutorial: Classes](https://docs.python.org/3/tutorial/classes.html)
- [Python Tutorial: Modules and Packages](https://docs.python.org/3/tutorial/modules.html)
- [Python Tutorial: Errors and Exceptions](https://docs.python.org/3/tutorial/errors.html)
- [Python Logging HOWTO](https://docs.python.org/3/howto/logging.html)
- [Python Built-in Functions: breakpoint](https://docs.python.org/3/library/functions.html#breakpoint)
- Ruff documentation: [Formatter](https://docs.astral.sh/ruff/formatter/), [Linter](https://docs.astral.sh/ruff/linter/), and [Configuration](https://docs.astral.sh/ruff/configuration/)
