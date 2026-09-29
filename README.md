# Cintra GPL — Python Interpreter

Cintra GPL is a simple general-purpose interpreted language implemented in Python.  
The interpreter reads a program file line by line, stores variables in a global dictionary, evaluates expressions using Python `eval`, and supports conditions, loops, input/output, comments, and Python module imports.

## Features

- Dynamically typed variables.
- Assignment and compound operators: `=`, `+=`, `-=`, `*=`, `/=`, `%=`, `**=`, `//=`.
- Conditionals: `if`, `else`, `endif`.
- Loops: `while`, `whileend`.
- Input/output: `in`, `out`, `out_type`.
- Comments: lines starting with `//`.
- Import Python modules via `include`.
- Expressions use Python-like syntax.
- Indentation does not affect execution.
- Nested `while` and `if` are supported.

## Requirements

- Python 3.x
- No external dependencies.

## Running

1. Save the interpreter as, for example, `cintra.py`.
2. Create a file named `to_compile` with Cintra GPL code.
3. Run:

```bash
python cintra.py
