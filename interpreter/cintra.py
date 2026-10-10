# Cintra GPL python interpreter
import importlib
stack = {}
skip = 0 
taken = 0
is_module = False
if_last = False


# goal : make something that can parse line without split, cuz now "i=1" != "i = 1" (i will fix it mb) 

def better_than_split(line: str) -> list[str]:
    char = 0
    res = []
    while char < len(line):
        if line[char].isspace():
            char += 1
            continue
        predicate1 = line[char].isalpha()
        predicate2 = line[char].isdigit()
        token = line[char]
        while char + 1 < len(line) and (line[char + 1].isalpha() == predicate1 and line[char+1].isdigit() == predicate2 or line[char+1] in ("_", ".")):
            if line[char+1].isspace():
                break
            token += line[char + 1]
            char += 1
            
        res.append(token)
        char += 1
        
    return res



def translate_block(lines: list) -> str:
    result = []
    indent = 0
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("//"):
            continue
        tokens = better_than_split(line)
        if not tokens:
            continue
        kw = tokens[0]

        if kw in ("if", "если"):
            cond = " ".join(tokens[1:]).rstrip(":")
            cond = cond.replace("&&", "and").replace("||", "or")
            result.append("    " * indent + f"if {cond}:")
            indent += 1

        elif kw.rstrip(":") in ("else", "иначе"):
            indent -= 1
            result.append("    " * indent + "else:")
            indent += 1

        elif kw in ("endif", "конецесли"):
            indent -= 1

        elif kw in ("while", "пока"):
            cond = " ".join(tokens[1:]).rstrip(":")
            cond = cond.replace("&&", "and").replace("||", "or")
            result.append("    " * indent + f"while {cond}:")
            indent += 1

        elif kw in ("whileend", "покаконец"):
            indent -= 1

        else:
            translated = parser_of_expressions(line)
            if translated:
                result.append("    " * indent + translated)

    return "\n".join(result)

def parser_of_expressions(line: str) -> str: # parse line in lambda /function
    global stack
    line = better_than_split(line)
    if not line:
        return ""
    if line[0] in ("out", "вывести"):
        return f'print({" ".join(line[1:])})'
    if line[0] in ("in", "ввести"):
        return f'{line[1]} = input()'
    if line[0] in ("out_type", "вывести_тип"):
        return f'print({type(line[1])})'
    if line[0] in ("call", "вызвать"):
        func = line[1]
        args = ", ".join(line[2:])
        return f'{func}({args})'
    if line[0] in ("return", "вернуть"):
        return f'return {parser_of_expressions(" ".join(line[1:]))}'
    if line[0] in ("out_type", "вывести_тип"):
        return f'print({type(stack[line[1]])})'
    if line[0] in ("var", "let", "переменная"):
        return f'{line[1]} = {" ".join(line[3:])}'
    if line[0] in ("if", "если"):
        return f'if {" ".join(line[1:])}'
    if line[0] in ("push", "добавить"):
        return f'{line[1]}.append({eval(line[2], {}, stack)})'
    else:
        return " ".join(line)





# Goal: make big functions, not lambdas. 
# kinda like 'func' and 'funcend'


class Function:
    def __init__(self, name, args):
        if isinstance(args, str):
            self.args = args.rstrip(":").split()
        else:
            self.args = list(args)
        self.name = name
        self.body_lines = []

    def add_line(self, raw_line):
        self.body_lines.append(raw_line)

    def end_of_init(self):
        body = translate_block(self.body_lines)
        if body.strip():
            body = "\n".join("    " + line for line in body.splitlines())
        else:
            body = "    pass"
        code = f'def {self.name}({", ".join(self.args)}):\n{body}'
        exec(code, stack)


def understand_line(line: list, count_of_lines: int) -> int:
    global stack, taken, skip, is_module
    if line[0] == "if" or line[0] == "если":
        cond = " ".join(line[1:]).rstrip(":").replace("&&", "and").replace("||", "or")
        try:
            result = eval(cond, {}, stack)
        except Exception as e:
            print(f"BAD CONDITION on line {count_of_lines}: {e}")
            return 1
        if result:
            taken = 1
        else:
            skip = 1
        return 0
    if line[0].rstrip(":") == "else" or line[0].rstrip(":") == "иначе":
        if taken == 1:
            skip = 1
        return 0
    if line[0] == "endif" or line[0] == "конецесли":
        taken = 0
        return 0

    if line[0] == "out" or line[0] == "вывести":
        print(eval(parser_of_expressions(" ".join(line[1:])), {}, stack))
        return 0
    if line[0] in ("in", "ввести"):
        var = line[1]
        try:
            if var in stack:
                stack[var] = type(stack[var])(input())
            else:
                stack[var] = input()
                
        except Exception as e:
            print(f"BAD INPUT on line {count_of_lines}: {e}")
            return 1
        return 0
    if line[0] == "include" or line[0] == "подключить":
        importlib.import_module(line[1])
        return 0
    if line[0] == "out_type" or line[0] == "вывести_тип":
        print(type(eval(" ".join(line[1:]), {}, stack)))
        return 0
    if " ".join(line).startswith("//"):
        return 0
    # lambda functions are in beta now
    if line[0] in ("lambda", "лямбда"):
        all_string = " ".join(line[1:])
        first = all_string.split(":")[0].split()
        expression = all_string.split(":")[1]
        expression = parser_of_expressions(expression)
        if len(first) >= 2:
            exec("def" + " " + first[0] + "("+(" ,".join(first[1:]))+")" + ":" + expression, stack)
        else:
            exec("def" + " " + first[0] + "()" + ":" + expression, stack)
        return 0
    if line[0] in ("call", "вызвать"):
        full_line = line[1:]
        if len(full_line) == 1:
            stack[line[1]]()
        else:
            args = [eval(a, {}, stack) for a in line[2:]]
            stack[line[1]](*args)
        return 0
    if line[0] in ("push", "добавить"):
        stack[line[1]].append(eval(line[2], {}, stack))
        return 0
    if line[0] in ("var", "let", "переменная"):
        stack[line[1]] = eval(" ".join(line[3:]), {}, stack)
        return 0
    try:
        name, op_tok = line[0], line[1]
        expr = " ".join(line[2:])
        if op_tok == "=":
            stack[name] = eval(expr, {}, stack)
        elif op_tok == "*=":
            stack[name] *= eval(expr, {}, stack)
        elif op_tok == "+=":
            stack[name] += eval(expr, {}, stack)
        elif op_tok == "-=":
            stack[name] -= eval(expr, {}, stack)
        elif op_tok == "/=":
            stack[name] /= eval(expr, {}, stack)
        elif op_tok == "%=":
            stack[name] %= eval(expr, {}, stack)
        elif op_tok == "**=":
            stack[name] **= eval(expr, {}, stack)
        elif op_tok == "//=":
            stack[name] //= eval(expr, {}, stack)
        else:
            print(f"BAD KEYWORDS on line {count_of_lines}")
            return 1
    except Exception as e:
        print(f"BAD KEYWORDS on line {count_of_lines}: {e}")
        return 1


def run_block(body: list, body_nums: int) -> int:
    global skip, taken
    i = 0
    while i < len(body):
        l = body[i]
        if skip > 0:
            if l[0] in ("if", "если"):
                skip += 1
            elif l[0] in ("endif", "конецесли"):
                skip -= 1
                if skip == 0:
                    taken = 0
            elif l[0] in ("while", "пока"):
                skip += 1
            elif l[0] in ("whileend", "покаконец"):
                skip -= 1
            elif l[0] in ("else", "иначе") and skip == 1:
                skip = 0
            i += 1
            continue
        if l[0] in ("while", "пока"):
            cond = " ".join(l[1:]).rstrip(":").replace("&&", "and").replace("||", "or")
            depth = 0
            j = i + 1
            while j < len(body):
                if body[j][0] in ("while", "пока"):
                    depth += 1
                elif body[j][0] in ("whileend", "покаконец"):
                    if depth == 0:
                        break
                    depth -= 1
                j += 1
            if j >= len(body):
                print("MISSING whileend")
                return 1
            sub_body = body[i+1:j]
            sub_nums = body_nums[i+1:j]
            while eval(cond, {}, stack):
                if run_block(sub_body, sub_nums):
                    return 1
            i = j + 1
            continue
        if l[0] in ("whileend", "покаконец"):
            print("UNEXPECTED whileend")
            return 1
        if understand_line(l, body_nums[i]):
            return 1
        i += 1
    return 0


def run_code(file_name: str = "to_compile") -> int:
    global stack, taken, skip, is_module
    with open(file_name, 'r') as file:
        count_of_lines = 0

        while True:
            raw = file.readline()
            if raw == "" and is_module == False:
                print("Program have been done with exit code 0.")
                return 0
            elif raw == "" and is_module == True:
                print("module on cintra included")
                is_module = False
                return 0
            count_of_lines += 1
            line = better_than_split(raw)
            if not line:
                continue

            if skip > 0:
                if line[0] in ("if", "если"):
                    skip += 1
                elif line[0] in ("endif", "конецесли"):
                    skip -= 1
                    if skip == 0:
                        taken = 0
                elif line[0] in ("while", "пока"):
                    skip += 1
                elif line[0] in ("whileend", "покаконец"):
                    skip -= 1
                elif line[0].rstrip(":") in ("else", "иначе") and skip == 1:
                    skip = 0
                continue
            else:
                if line[0] not in ("else", "if", "while", "func"):
                    line = better_than_split(" ".join(line).rstrip(";"))
            if line[0] in ("lambda", "лямбда"):
                understand_line(line, count_of_lines)
                continue
            if line[0] in ("call", "вызвать"):
                understand_line(line, count_of_lines)
                continue
            if line[0] in ("cintrafile", "файлцинтра"):
                is_module = True
                run_code(f'{line[1]}')
                continue
            if line[0] in ('func', 'функция'):
                header = " ".join(line[1:]).rstrip(":").strip()
                if "(" in header:
                    name = header.split("(")[0].strip()
                    inner = header[header.index("(")+1:header.rindex(")")]
                    args = [a.strip() for a in inner.split(",") if a.strip()]
                else:
                    parts = header.split()
                    name = parts[0] if parts else ""
                    args = parts[1:]
                function = Function(name, args)
                while True:
                    raw = file.readline()
                    if raw == "":
                        print("MISSING funcend")
                        return 1
                    count_of_lines += 1
                    l = better_than_split(raw)
                    if not l:
                        continue
                    if l[0] in ("funcend", "конецфункции"):
                        break
                    function.add_line(raw)
                function.end_of_init()
                continue
            if line[0] in ("push", "добавить"):
                stack[line[1]].append(eval(line[2], {}, stack))
                continue
            if line[0] in ("while", "пока"):
                cond = " ".join(line[1:]).rstrip(":").replace("&&", "and").replace("||", "or")
                body = []
                body_nums = []
                depth = 0
                while True:
                    raw2 = file.readline()
                    if raw2 == "":
                        print("MISSING whileend")
                        return 1
                    count_of_lines += 1
                    l2 = better_than_split(raw2)
                    if not l2:
                        continue
                    if l2[0] in ("while", "пока"):
                        depth += 1
                    elif l2[0] in ("whileend", "покаконец"):
                        if depth == 0:
                            break
                        depth -= 1
                    body.append(l2)
                    body_nums.append(count_of_lines)

                while eval(cond, {}, stack):
                    if run_block(body, body_nums):
                        return 1
                continue

            if understand_line(line, count_of_lines):
                return 1

file_name = input("Enter file name: ")
run_code(file_name)
