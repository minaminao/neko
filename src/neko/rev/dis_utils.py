import dis
import io
import re


def dis_code(code, n_extend=100, rich_info=False) -> str:
    """
    普通にコードオブジェクトをdis.dis(code)してもエラーが出る場合に使う。
    例: IndexError: tuple index out of range
    """
    dis_result = io.StringIO()
    names = tuple(list(code.co_names) + ["_unknown_name"] * n_extend)
    varnames = tuple(list(code.co_varnames) + ["_unknown_varname"] * n_extend)
    consts = tuple(list(code.co_consts) + ["_unknown_const"] * n_extend)
    cell_names = tuple(list(code.co_cellvars + code.co_freevars) + ["_unknown_cell_name"] * n_extend)
    # linestarts = dict(dis.findlinestarts(code))
    lasti = -1
    dis._disassemble_bytes(code.co_code, lasti, varnames, names, consts, cell_names, file=dis_result)
    dis_result = dis_result.getvalue()

    if rich_info:
        dis_result = add_rich_info(dis_result)

    return dis_result


def add_rich_info(dis_result):
    """
    二項演算や関数・メソッド呼び出しなどの詳細情報を追加する。
    情報は`#`で始まる。
    linestartsがない結果のみパースが対応。
    JUMPなどで狂う場合がある。
    """
    lines = dis_result.split("\n")
    result = ""
    names = []
    info_index_in_line = 0
    for line in lines:
        additional_info = ""

        name = re.search(r"\(.+\)", line)
        if name is not None:
            name = name.group(0)[1:-1]
            if not name.startswith("to "):
                names.append(name)
            info_index_in_line = line.index("(")

        v = list(filter(None, line.split(" ")))
        if len(v) == 0:
            continue
        if v[0] == ">>":
            v = v[1:]
        instruction_name = v[1]

        # 2オペランド命令
        x = None
        if instruction_name == "BINARY_POWER":
            x = f"{names[-2]} ** {names[-1]}"
        elif instruction_name == "BINARY_MULTIPLY":
            x = f"{names[-2]} * {names[-1]}"
        elif instruction_name == "BINARY_MATRIX_MULTIPLY":
            x = f"{names[-2]} @ {names[-1]}"
        elif instruction_name == "BINARY_FLOOR_DIVIDE":
            x = f"{names[-2]} // {names[-1]}"
        elif instruction_name == "BINARY_TRUE_DIVIDE":
            x = f"{names[-2]} / {names[-1]}"
        elif instruction_name == "BINARY_MODULO":
            x = f"{names[-2]} % {names[-1]}"
        elif instruction_name == "BINARY_ADD":
            x = f"{names[-2]} + {names[-1]}"
        elif instruction_name == "BINARY_SUBTRACT":
            x = f"{names[-2]} - {names[-1]}"
        elif instruction_name == "BINARY_SUBSCR":
            x = f"{names[-2]}[{names[-1]}]"
        elif instruction_name == "BINARY_LSHIFT":
            x = f"{names[-2]} << {names[-1]}"
        elif instruction_name == "BINARY_RSHIFT":
            x = f"{names[-2]} >> {names[-1]}"
        elif instruction_name == "BINARY_AND":
            x = f"{names[-2]} & {names[-1]}"
        elif instruction_name == "BINARY_XOR":
            x = f"{names[-2]} ^ {names[-1]}"
        elif instruction_name == "BINARY_OR":
            x = f"{names[-2]} | {names[-1]}"
        if x is not None:
            names.pop()
            names.pop()
            names.append(x)
            additional_info += x

        if instruction_name == "CALL_FUNCTION":
            argc = int(v[2])
            args = []
            for _ in range(argc):
                args.append(names.pop())
            function_name = names.pop()
            args = ", ".join(args)
            x = f"{function_name}({args})"
            names.append(x)
            additional_info += x
        if instruction_name == "CALL_METHOD":
            argc = int(v[2])
            args = []
            for _ in range(argc):
                args.append(names.pop())
            method_name = names.pop()
            object_name = names.pop()
            args = ", ".join(args)
            x = f"{object_name}.{method_name}({args})"
            names.append(x)
            additional_info += x
        if instruction_name == "COMPARE_OP":
            op = names.pop()
            x = f"{names[-2]} {op} {names[-1]}"
            names.pop()
            names.pop()
            names.append(x)
            additional_info += x

        if additional_info == "":
            result += line + "\n"
        else:
            result += line + " " * max(1, info_index_in_line - len(line)) + f"# {additional_info}" + "\n"

    return result
