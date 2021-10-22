from z3 import *

Instance = list[list[int]]


def solve(instance: Instance, number_of_solutions: int = 1) -> list[Instance]:
    """
    Sudoku solver using z3
    解の個数はデフォルトで一つ
    """
    N = 9
    M = 3
    x = [[Int(f"x_{i+1}_{j+1}") for j in range(N)] for i in range(N)]

    # 入る数字の条件
    c_cell_range = [And(1 <= x[i][j], x[i][j] <= N) for i in range(N) for j in range(N)]
    # 行の条件
    c_row_distinct = [Distinct(x[i]) for i in range(N)]
    # 列の条件
    c_col_distinct = [Distinct([x[i][j] for i in range(N)]) for j in range(N)]
    # スクエアの条件
    c_square_distinct = [Distinct([x[ii * M + i][jj * M + j] for i in range(M) for j in range(M)]) for ii in range(M) for jj in range(M)]

    c_sudoku = c_cell_range + c_row_distinct + c_col_distinct + c_square_distinct

    c_instance = [True if instance[i][j] == 0 else x[i][j] == instance[i][j] for i in range(N) for j in range(N)]

    s = Solver()
    s.add(c_sudoku + c_instance)

    solutions = []
    for _ in range(number_of_solutions):
        if s.check() == sat:
            m = s.model()
            solution = [[m.evaluate(x[i][j]) for j in range(N)] for i in range(N)]
            solutions.append(solution)
            c_solution = And([x[i][j] == m.evaluate(x[i][j]) for i in range(N) for j in range(N)])
            s.add(Not(c_solution))
        else:
            break
    return solutions
