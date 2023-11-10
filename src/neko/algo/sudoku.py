from z3 import Int, And, Distinct, Solver, Not, sat

type Instance = list[list[int]]


def solve(instance: Instance, number_of_solutions: int = 1, N=9, MI=3, MJ=3) -> list[Instance]:
    """
    Sudoku solver using z3
    The number of solutions is one by default
    """
    x = [[Int(f"x_{i+1}_{j+1}") for j in range(N)] for i in range(N)]

    c_cell_range = [And(1 <= x[i][j], x[i][j] <= N) for i in range(N) for j in range(N)]
    c_row_distinct = [Distinct(x[i]) for i in range(N)]
    c_col_distinct = [Distinct([x[i][j] for i in range(N)]) for j in range(N)]
    c_subgrid_distinct = [
        Distinct([x[ii * MI + i][jj * MJ + j] for i in range(MI) for j in range(MJ)])
        for ii in range(MJ)
        for jj in range(MI)
    ]

    c_sudoku = c_cell_range + c_row_distinct + c_col_distinct + c_subgrid_distinct

    c_instance = [True if instance[i][j] == 0 else x[i][j] == instance[i][j] for i in range(N) for j in range(N)]

    s = Solver()
    s.add(c_sudoku + c_instance)

    solutions = []
    for _ in range(number_of_solutions):
        if s.check() == sat:
            m = s.model()
            solution = [[m.evaluate(x[i][j]).as_long() for j in range(N)] for i in range(N)]
            solutions.append(solution)
            c_solution = And([x[i][j] == m.evaluate(x[i][j]) for i in range(N) for j in range(N)])
            s.add(Not(c_solution))
        else:
            break
    return solutions
