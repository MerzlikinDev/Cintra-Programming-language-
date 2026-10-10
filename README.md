# Cintra GPL — Language Reference

A small line-based interpreted programming language written in Python. It supports bilingual keywords (English and Russian), variables, control flow, functions, lambdas, modules, and basic list operations.

## Table of Contents

1. Basics
2. Comments
3. Variables
4. Operators
5. Input / Output
6. Conditionals
7. Loops
8. Functions
9. Lambdas
10. Lists
11. Modules
12. Keyword Reference
13. Complete Example

## Basics

- Every statement is written on its own line.
- The interpreter is whitespace-insensitive — `i=1`, `i = 1`, and `i   =   1` are all valid.
- Keywords exist in English and Russian; you can mix them freely.
- Variables live in a shared global scope (referred to as the `stack`).
- File extension convention: none required.

Run a program:

    $ python cintra.py
    Enter file name: my_program.ctr

## Comments

Use `//` to start a comment. Full-line comments are ignored.

    // this is a comment

## Variables

Declare a variable using `var`, `let`, or `переменная`:

    var x = 10
    let name = "Alice"
    переменная pi = 3.14

You can also assign directly without a keyword:

    x = 10
    y = x + 5

### Assignment operators

| Operator | Meaning             |
|----------|---------------------|
| `=`      | assign              |
| `+=`     | add and assign      |
| `-=`     | subtract and assign |
| `*=`     | multiply and assign |
| `/=`     | divide and assign   |
| `//=`    | floor divide        |
| `%=`     | modulo and assign   |
| `**=`    | power and assign    |

Example:

    var n = 5
    n += 3      // n is now 8
    n *= 2      // n is now 16

## Operators

Inside conditions and expressions you can use:

- `&&` — logical AND (translated to `and`)
- `||` — logical OR (translated to `or`)
- `==`, `!=`, `<`, `>`, `<=`, `>=` — comparisons
- `+`, `-`, `*`, `/`, `//`, `%`, `**` — arithmetic

## Input / Output

### Print a value

    out "Hello, world!"
    вывести 42
    out x + y

### Read input

    in name
    ввести age

If the variable already exists, the interpreter tries to convert the input to the same type.

### Print a type

    out_type x
    вывести_тип y

## Conditionals

    if x > 10
        out "big"
    else
        out "small"
    endif

Russian form:

    если x > 10
        вывести "большое"
    иначе
        вывести "маленькое"
    конецесли

Rules:

- The `if` line accepts `:` at the end (optional).
- `else` / `иначе` is optional.
- `endif` / `конецесли` closes the block.

## Loops

Only `while` loops are supported.

    var i = 0
    while i < 5
        out i
        i += 1
    whileend

Russian form:

    пока i < 5
        вывести i
        i += 1
    покаконец

Loops can be nested. Each `while` must be matched with a `whileend`.

## Functions

Define a function with `func` / `функция` and close it with `funcend` / `конецфункции`.

    func greet(name)
        out "Hello, " + name
    funcend

    call greet("Alice")

Russian form:

    функция add(a, b)
        return a + b
    конецфункции

    вызвать add(2, 3)

### Return values

    return <expression>
    вернуть <expression>

### Calling

    call greet("Bob")
    вызвать add(1, 2)
    call no_args_func

## Lambdas

Lambdas are supported (beta) using `lambda` / `лямбда`.

Syntax:

    lambda <name> <args> : <expression>

Example:

    lambda double x : x * 2
    call double(5)

## Lists

Use `push` / `добавить` to append to a list.

    var items = []
    push items 10
    push items 20
    out items

The expression after the list name is evaluated before appending.

## Modules

### Import a Python module

    include math
    подключить math

### Run another Cintra file as a module

    cintrafile other_module
    файлцинтра другой_модуль

This executes the given file in module mode.

## Keyword Reference

| Concept          | English           | Russian            |
|------------------|-------------------|--------------------|
| If               | `if`              | `если`             |
| Else             | `else`            | `иначе`            |
| End if           | `endif`           | `конецесли`        |
| While            | `while`           | `пока`             |
| End while        | `whileend`        | `покаконец`        |
| Function         | `func`            | `функция`          |
| End function     | `funcend`         | `конецфункции`     |
| Return           | `return`          | `вернуть`          |
| Lambda           | `lambda`          | `лямбда`           |
| Call             | `call`            | `вызвать`          |
| Print            | `out`             | `вывести`          |
| Input            | `in`              | `ввести`           |
| Print type       | `out_type`        | `вывести_тип`      |
| Variable         | `var` / `let`     | `переменная`       |
| Push to list     | `push`            | `добавить`         |
| Include module   | `include`         | `подключить`       |
| Load Cintra file | `cintrafile`      | `файлцинтра`       |

## Complete Example

FizzBuzz in Cintra:

    // FizzBuzz in Cintra

    var i = 1
    while i <= 20
        if i % 15 == 0
            out "FizzBuzz"
        else
            if i % 3 == 0
                out "Fizz"
            else
                if i % 5 == 0
                    out "Buzz"
                else
                    out i
                endif
            endif
        endif
        i += 1
    whileend

Function + lambda example:

    // Function + lambda example

    func square(x)
        return x * x
    funcend

    lambda triple x : x * 3

    var n = 7
    call square(n)
    call triple(n)

## Notes & Limitations

- All variables share one global namespace.
- There is no block scoping.
- Indentation is not significant to the parser, but is required only for readability.
- Nested `if`/`else` inside loops works, but `else` handles only a single `if` scope.
- Lambdas must be defined before use.
- Type conversion on input is only attempted if the variable already exists.
