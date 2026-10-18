# TP1 Homework: Python Fundamentals, PEP 8, and Debugging

- **Subject:** Advanced Programming
- **Lecturer:** Mr.VANN Visal
- **Institution:** Institute of Technology of Cambodia (ITC)

This lesson covered basic Python concepts, clean coding with PEP 8, and how to
find and fix errors. The following summary explains the main points and includes
short examples to show how they apply in practice.

## 1. Introduction

- **Function:** A reusable block of code that performs a specific task. A function
  can receive input through parameters and return a result. For example, a
  `calculate_total(price, quantity)` function could calculate the cost of several
  items without repeating the calculation throughout a program.
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
  the dotted name `utilities.math_helpers`.
- **Constant:** A named value intended to stay unchanged while the program runs.
  Python relies on a naming convention for ordinary constants rather than
  preventing reassignment. For example, `PASS_MARK = 50` communicates that this
  value should be treated as fixed.

The following example shows the relationship between a class, an object, and a
method:

```python
class Student:
    def greet(self):
        return "Hello, welcome to class!"


student = Student()
print(student.greet())
```

Here, `Student` is the class, `student` refers to an instance, and `greet()` is an
instance method. Calling it through `student` passes that object as `self`.

## 2. PEP 8 Rules

[PEP 8](https://peps.python.org/pep-0008/) is Python's style guide. It provides
conventions that help programmers write consistent, readable code that is easier
to review and maintain.

| Rule | Guidance |
| --- | --- |
| Indentation | Use four spaces per indentation level. Keep indentation consistent and avoid mixing tabs and spaces. |
| Line length | Limit code lines to 79 characters. Wrap comments and docstrings at 72 characters. |
| Imports | Place imports near the top, after module comments or docstrings. Put separate module imports on separate lines, grouping standard library, third-party, and local imports with blank lines between groups. |
| Naming | Use `snake_case` for variables, functions, and methods; `UPPER_CASE` for constants; and `PascalCase` for classes. |
| Whitespace | Add spaces around assignment and comparison operators and after commas. Avoid unnecessary spaces just inside parentheses or brackets. |
| Blank lines | Separate top-level functions and classes with two blank lines, and methods within a class with one blank line. |

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

## 3. Debugging

Debugging is the process of finding the cause of an error and correcting it.
Problems can include invalid syntax, exceptions during execution, or logic that
produces an incorrect result even though the program runs.

A useful debugging process is:

1. **Reproduce the problem.** Run the program with the input that caused the
   unexpected behavior.
2. **Read the error message.** For an exception, the last line identifies the
   error type and message. The traceback shows the relevant calls and locations.
3. **Inspect the code and data.** Check the reported line, variable names, values,
   data types, indentation, and conditions. Temporary output or a debugger can
   help reveal what the program is doing.
4. **Fix the cause.** Make a focused correction based on what caused the failure.
5. **Test again.** Repeat the original case and try other inputs to check that the
   correction works without introducing another problem.

For example, calculating `sum(scores) / len(scores)` when `scores` is empty
causes a `ZeroDivisionError`. Checking for an empty list handles that case:

```python
scores = []

if scores:
    average_score = sum(scores) / len(scores)
    print(average_score)
else:
    print("No scores are available.")
```

Testing both an empty list and a list containing scores checks the two possible
paths through this code.

## 4. Tips and Tricks for Clean Code

1. **Choose meaningful names.** Names such as `student_score` and
   `calculate_average` explain the purpose of data and actions. Clear names make
   code easier for other people to understand.
2. **Avoid unnecessary repetition.** Move repeated logic into a reusable function
   when appropriate. This makes changes easier because the shared logic can be
   updated in one place.
3. **Apply PEP 8 consistently.** Check indentation, names, spacing, and line
   lengths as you write. Configure your editor to insert four spaces and display
   a line-length guide.
4. **Write helpful comments.** Explain the reason for a decision or clarify a
   difficult part of the code. Keep comments accurate when the code changes.
5. **Avoid scattering hardcoded values.** Give meaningful names to values that
   may need to change. For example, using `PASS_MARK` throughout a program makes
   the grading threshold easier to understand and update.
6. **Test regularly.** Check small parts of the program as they are written. Use
   ordinary inputs and relevant boundary cases, such as an empty list or a score
   exactly equal to the pass mark.
7. **Debug systematically.** Use error messages and inspect values to understand
   the cause of a problem. Make small changes and rerun the failing case to check
   each correction.
8. **Keep the code simple.** Break a large problem into smaller steps and give
   each function a clear task. Straightforward code is easier to explain, test,
   and maintain.

## 5. References

- Class notes from the Advanced Programming lesson.
- [PEP 8: Style Guide for Python Code](https://peps.python.org/pep-0008/)
- [Python Tutorial: Classes](https://docs.python.org/3/tutorial/classes.html)
- [Python Tutorial: Modules and Packages](https://docs.python.org/3/tutorial/modules.html)
- [Python Tutorial: Errors and Exceptions](https://docs.python.org/3/tutorial/errors.html)
