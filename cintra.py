# Cintra GPL interpreter
def run_code(file_name: str = "to_compile"):
    with open(file_name, 'r') as file:
        stack = {}
        count_of_lines = 0
        skip = 0 
        taken = 0

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
                elif line[0] == "else" and skip == 1:
                    skip = 0
                continue

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
                continue

            if line[0] == "else":
                if taken == 1:
                    skip = 1
                continue

            if line[0] == "endif":
                taken = 0
                continue

            if line[0] == "out":
                print(eval(" ".join(line[1:]), {}, stack))
                continue
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
                continue
            if len(line) < 3:
                print(f"BAD KEYWORDS on line {count_of_lines}")
                return 1
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
                else:
                    print(f"BAD KEYWORDS on line {count_of_lines}")
                    return 1
            except Exception as e:
                print(f"BAD KEYWORDS on line {count_of_lines}: {e}")
                return 1


run_code()
