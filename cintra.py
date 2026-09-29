# Cintra GPL python interpreter
import importlib
stack = {}
skip = 0 
taken = 0

def understand_line(line, count_of_lines):
    global stack, taken, skip
    if line[0] == "if":
        cond = " ".join(line[1:]).rstrip(":")
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
    if line[0] == "else":
        if taken == 1:
            skip = 1
        return 0
    if line[0] == "endif":
        taken = 0
        return 0

    if line[0] == "out":
        print(eval(" ".join(line[1:]), {}, stack))
        return 0
    if line[0] == "in":
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
    if line[0] == "include":
        importlib.import_module(line[1])
        return 0
    if line[0] == "out_type":
        print(type(eval(" ".join(line[1:]), {}, stack)))
        return 0
    if " ".join(line).startswith("//"):
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
            if l[0] == "if":
                skip += 1
            elif l[0] == "endif":
                skip -= 1
                if skip == 0:
                    taken = 0
            elif l[0] == "while":
                skip += 1
            elif l[0] == "whileend":
                skip -= 1
            elif l[0] == "else" and skip == 1:
                skip = 0
            i += 1
            continue
        if l[0] == "while":
            cond = " ".join(l[1:]).rstrip(":")
            depth = 0
            j = i + 1
            while j < len(body):
                if body[j][0] == "while":
                    depth += 1
                elif body[j][0] == "whileend":
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
        if l[0] == "whileend":
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
                if line[0] == "if":
                    skip += 1
                elif line[0] == "endif":
                    skip -= 1
                    if skip == 0:
                        taken = 0
                elif line[0] == "while":
                    skip += 1
                elif line[0] == "whileend":
                    skip -= 1
                elif line[0] == "else" and skip == 1:
                    skip = 0
                continue

            if line[0] == "while":
                cond = " ".join(line[1:]).rstrip(":")
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
                    if l2[0] == "while":
                        depth += 1
                    elif l2[0] == "whileend":
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


run_code()
