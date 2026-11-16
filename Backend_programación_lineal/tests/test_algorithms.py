import unittest
from fractions import Fraction

from app.algorithms.big_m import solve_big_m
from app.algorithms.revised_simplex import solve_revised_simplex


SOLVERS = (solve_big_m, solve_revised_simplex)


class SimplexSolverTests(unittest.TestCase):
    def test_exact_maximization_with_less_equal_constraints(self):
        for solver in SOLVERS:
            with self.subTest(solver=solver.__name__):
                result = solver(
                    [3, 2],
                    [[1, 1], [1, 0], [0, 1]],
                    [4, 2, 3],
                    ["<=", "<=", "<="],
                )
                self.assertEqual(result["status"], "optimal")
                self.assertEqual(result["objective_value"], Fraction(10))
                self.assertEqual(
                    result["solution"],
                    {"x1": Fraction(2), "x2": Fraction(2)},
                )
                self.assertIsInstance(
                    result["iterations"][-1]["objective_value"], Fraction
                )

    def test_minimization_with_negative_rhs_and_artificial_variables(self):
        for solver in SOLVERS:
            with self.subTest(solver=solver.__name__):
                result = solver(
                    [1, 1],
                    [[1, 1], [1, -1]],
                    [4, -1],
                    [">=", "="],
                    direction="min",
                )
                self.assertEqual(result["status"], "optimal")
                self.assertEqual(result["objective_value"], Fraction(4))
                self.assertEqual(
                    result["solution"],
                    {"x1": Fraction(3, 2), "x2": Fraction(5, 2)},
                )

    def test_decimal_strings_remain_exact(self):
        for solver in SOLVERS:
            with self.subTest(solver=solver.__name__):
                result = solver(["0.1"], [[1]], ["0.3"], ["<="])
                self.assertEqual(result["status"], "optimal")
                self.assertEqual(result["solution"]["x1"], Fraction(3, 10))
                self.assertEqual(result["objective_value"], Fraction(3, 100))

    def test_infeasible_problem(self):
        for solver in SOLVERS:
            with self.subTest(solver=solver.__name__):
                result = solver(
                    [1],
                    [[1], [1]],
                    [2, 1],
                    [">=", "<="],
                )
                self.assertEqual(result["status"], "infeasible")
                self.assertIsNone(result["objective_value"])

    def test_unbounded_problem_without_constraints(self):
        for solver in SOLVERS:
            with self.subTest(solver=solver.__name__):
                result = solver([1], [], [], [])
                self.assertEqual(result["status"], "unbounded")

    def test_revised_simplex_removes_redundant_equality(self):
        result = solve_revised_simplex(
            [1],
            [[1], [0]],
            [2, 0],
            ["=", "="],
        )
        self.assertEqual(result["status"], "optimal")
        self.assertEqual(result["objective_value"], Fraction(2))
        self.assertEqual(result["solution"], {"x1": Fraction(2)})


if __name__ == "__main__":
    unittest.main()
