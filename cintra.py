# Cintra GPL python interpreter
import importlib
stack = {}
skip = 0 
taken = 0

def understand_line(line, count_of_lines):
    global stack, taken, skip
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
    if line[0] == "else" or line[0] == "иначе":
        if taken == 1:
            skip = 1
        return 0
    if line[0] == "endif" or line[0] == "конецесли":
        taken = 0
        return 0

    if line[0] == "out" or line[0] == "вывести":
        print(eval(" ".join(line[1:]), {}, stack))
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
    if line[0] == "include" or line[0] == "вывести":
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
        if len(first) >= 2:
            exec("def" + " " + first[0] + "("+(" ,".join(first[1:]))+")" + ":" + expression, stack)
        else:
            exec("def" + " " + first[0] + "()" + ":" + expression, stack)
        return 0
    if line[0] in ("call", "вызвать"):
        full_line = line[1:]
        if len(full_line) == 1:
            exec(f'{stack[line[1]]()}', stack)
        else:
            args = [eval(a, {}, stack) for a in line[2:]]
            stack[line[1]](*args)
        return 0
    if line[0] in ("var", "переменная"):
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


def run_block(body, body_nums):
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


def run_code(file_name: str = "to_compile"):
    global stack, taken, skip
    with open(file_name, 'r') as file:
        count_of_lines = 0

        while True:
            raw = file.readline()
            if raw == "":
                print("Program have been done with exit code 0.")
                return 0

            count_of_lines += 1
            line = raw.split()
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
                elif line[0] in ("else", "иначе") and skip == 1:
                    skip = 0
                continue
            if line[0] in ("lambda", "лямбда"):
                understand_line(line, count_of_lines)
                continue
            if line[0] in ("call", "вызвать"):
                understand_line(line, count_of_lines)
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
                    l2 = raw2.split()
                    if not l2:
                        continue
                    if l2[0] in ("while", "конец"):
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
