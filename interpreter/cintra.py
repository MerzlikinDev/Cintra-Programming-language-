# Cintra GPL python interpreter
# I had known that my language interpreter - transpiler (13.10.2026)
import importlib
stack = {}
skip = 0 
taken = 0
is_module = False
if_last = False
is_python = False

# goal : make something that can parse line without split, cuz now "i=1" != "i = 1" (i will fix it mb) 

def better_than_split(line: str) -> list[str]:
    char = 0
    res = []
    while char < len(line):
        if line[char].isspace():
            char += 1
            continue
        if line[char] in ('"', "'"):
            quote = line[char]
            token = quote
            char += 1
            while char < len(line) and line[char] != quote:
                token += line[char]
                char += 1
            if char < len(line):
                token += quote
                char += 1
            res.append(token)
            continue
        predicate1 = line[char].isalpha()
        predicate2 = line[char].isdigit()
        token = line[char]
        if char < len(line) - 1 and line[char] == "/" and line[char + 1] == "/":
            break
        while char + 1 < len(line) and ((line[char + 1].isalpha() == predicate1 and line[char+1].isdigit() == predicate2 or line[char+1] in ("_", ".")) or line[char] in( "_", "\\")):
            if line[char+1].isspace():
                break
            token += line[char + 1]
            char += 1
            if line[char] not in (".", "_"):
                predicate1 = line[char].isalpha()
                predicate2 = line[char].isdigit()
        res.append(token)
        char += 1

    return res


def _cintra_input(name: str):
    value = input()
    if name in stack:
        try:
            return type(stack[name])(value)
        except Exception:
            return value
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    return value


def translate_block(lines: list, in_class: bool = False) -> str:
    result = []
    indent = 0
    i = 0
    while i < len(lines):
        raw = lines[i]
        line = raw.strip().rstrip(";").rstrip()
        if not line or line.startswith("//"):
            i += 1
            continue
        tokens = better_than_split(line)
        tokens = [i for i in tokens if i != ";"]
        if not tokens:
            i += 1
            continue
        kw = tokens[0]

        if kw in ("if", "если"):
            cond = " ".join(tokens[1:]).rstrip(":").replace("&&", "and").replace("||", "or")
            result.append("    " * indent + f"if {cond}:")
            indent += 1

        elif kw.rstrip(":") in ("else", "иначе"):
            indent -= 1
            result.append("    " * indent + "else:")
            indent += 1

        elif kw in ("endif", "конецесли"):
            indent -= 1

        elif kw in ("while", "пока"):
            cond = " ".join(tokens[1:]).rstrip(":").replace("&&", "and").replace("||", "or")
            result.append("    " * indent + f"while {cond}:")
            indent += 1

        elif kw in ("whileend", "покаконец"):
            indent -= 1

        elif kw in ("func", "функция"):
            header = " ".join(tokens[1:]).rstrip(":").strip()
            if "(" in header:
                name = header.split("(")[0].strip()
                inner = header[header.index("(") + 1:header.rindex(")")]
                args = [a.strip() for a in inner.split(",") if a.strip()]
            else:
                parts = header.split()
                name = parts[0] if parts else ""
                args = parts[1:]
            body_lines = []
            depth = 0
            j = i + 1
            while j < len(lines):
                t2 = better_than_split(lines[j].strip().rstrip(";").rstrip())
                if t2:
                    if t2[0] in ("func", "функция"):
                        depth += 1
                    elif t2[0] in ("funcend", "конецфункции"):
                        if depth == 0:
                            break
                        depth -= 1
                body_lines.append(lines[j])
                j += 1

            if in_class and not (args and args[0] == "self"):
                all_args = ["self"] + args
            else:
                all_args = args
            result.append("    " * indent + f'def {name}({", ".join(all_args)}):')
            indent += 1
            inner_code = translate_block(body_lines)
            if inner_code.strip():
                for bl in inner_code.splitlines():
                    result.append("    " * indent + bl)
            else:
                result.append("    " * indent + "pass")
            indent -= 1
            i = j

        elif kw in ("funcend", "конецфункции"):
            pass
        elif kw in ("struct", "class", "класс", "структура"):
            header = " ".join(tokens[1:]).rstrip(":").strip()
            parts = header.split()
            name = parts[0] if parts else ""
            parent = parts[1] if len(parts) > 1 else ""
            body_lines = []
            depth = 0
            j = i + 1
            end_kws = ("structend", "classend", "конецструктуры", "конецкласса")
            while j < len(lines):
                t2 = better_than_split(lines[j].strip().rstrip(";").rstrip())
                if t2:
                    if t2[0] in ("struct", "class", "класс", "структура"):
                        depth += 1
                    elif t2[0] in end_kws:
                        if depth == 0:
                            break
                        depth -= 1
                body_lines.append(lines[j])
                j += 1

            base = f"({parent})" if parent else ""
            result.append("    " * indent + f"class {name}{base}:")
            indent += 1
            inner_code = translate_block(body_lines, in_class=True)
            if inner_code.strip():
                for bl in inner_code.splitlines():
                    result.append("    " * indent + bl)
            else:
                result.append("    " * indent + "pass")
            indent -= 1
            i = j

        elif kw in ("structend", "classend", "конецструктуры", "конецкласса"):
            pass

        elif kw in ("out", "вывести"):
            rest = tokens[1:]
            if rest and rest[0] in ("call", "вызвать"):
                expr = f'{rest[1]}({", ".join(rest[2:])})'
            else:
                expr = " ".join(rest)
            result.append("    " * indent + f"print({expr})")

        elif kw in ("in", "ввести"):
            name = tokens[1]
            result.append("    " * indent + f'{name} = _cintra_input("{name}")')

        elif kw in ("out_type", "вывести_тип"):
            expr = " ".join(tokens[1:])
            result.append("    " * indent + f"print(type({expr}))")

        elif kw in ("call", "вызвать"):
            name = tokens[1]
            args = ", ".join(tokens[2:])
            result.append("    " * indent + f"{name}({args})")

        elif kw in ("return", "вернуть"):
            rest = tokens[1:]
            if rest and rest[0] in ("call", "вызвать"):
                expr = f'{rest[1]}({", ".join(rest[2:])})'
            else:
                expr = " ".join(rest)
            result.append("    " * indent + f"return {expr}")

        elif kw in ("var", "let", "переменная"):
            name = tokens[1]
            # tokens[2] is "="
            rest = tokens[3:]
            if rest and rest[0] in ("call", "вызвать"):
                value = f'{rest[1]}({", ".join(rest[2:])})'
            else:
                value = " ".join(rest)
            result.append("    " * indent + f"{name} = {value}")

        elif kw in ("push", "добавить"):
            name = tokens[1]
            rest = tokens[2:]
            if rest and rest[0] in ("call", "вызвать"):
                value = f'{rest[1]}({", ".join(rest[2:])})'
            else:
                value = " ".join(rest)
            result.append("    " * indent + f"{name}.append({value})")
        elif kw in ("delete", "удалить"):
            result.append("   " * indent + f"del {tokens[1]}[{tokens[2]}]")
        elif kw in ("clear", "очистить"):
            result.append("    " * indent + f'{tokens[1]} = []')
        elif kw in ("lambda", "лямбда"):
            all_string = " ".join(tokens[1:])
            if ":" not in all_string:
                result.append("    " * indent + f"# bad lambda: {all_string}")
            else:
                head, expr = all_string.split(":", 1)
                parts = head.split()
                lname = parts[0] if parts else "_lambda"
                largs = parts[1:] if len(parts) > 1 else []
                expr = expr.strip()
                if not expr.startswith("return"):
                    expr = "return " + expr
                result.append("    " * indent + f"def {lname}({', '.join(largs)}): {expr}")

        elif kw in ("include", "подключить"):
            result.append("    " * indent + f"import {tokens[1]}")

        elif kw in ("lib", "библиотека"):
            path = tokens[1]
            with open(path) as f:
                included = translate_block(f.readlines())
            for il in included.splitlines():
                result.append("    " * indent + il)
            result.append("    " * indent + 'print("module on cintra included")')
        elif kw in ("pythonblock", "блокпитона"):
            j = i + 1
            while j < len(lines):
                t = better_than_split(lines[j].strip())
                if t and t[0] in ("pythonend", "конецпитона"):
                    break
                result.append("    " * indent + lines[j].rstrip())
                j += 1
            i = j

        elif kw in ("pythonend", "конецпитона"):
            pass
        else:
            result.append("    " * indent + " ".join(tokens))

        i += 1

    return "\n".join(result)


def run_code(file_name: str = "to_compile", to_file=True) -> int:
    global stack
    stack["_cintra_input"] = _cintra_input
    with open(file_name) as f:
        lines = f.readlines()
    code = translate_block(lines)
    if to_file: # thank u/sausix from reddit.
        with open(file_name + ".py", "w") as out:
            out.write(code)
    try:
        exec(code, stack)
    except Exception as e:
        print(f"ERROR: {e}")
        return 1
    print("Program have been done with exit code 0.")
    return 0

file_name = input("Enter file name: ")
run_code(file_name)
