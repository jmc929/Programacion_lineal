import importlib.util
import os
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
                self.assertTrue(result["special_cases"]["is_infeasible"])
                self.assertFalse(result["sensitivity"]["applicable"])

    def test_unbounded_problem_without_constraints(self):
        for solver in SOLVERS:
            with self.subTest(solver=solver.__name__):
                result = solver([1], [], [], [])
                self.assertEqual(result["status"], "unbounded")
                self.assertTrue(result["special_cases"]["is_unbounded"])

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

    # ------------------------------------------------------------------
    # Los 7 problemas de evaluación del enunciado del proyecto
    # ------------------------------------------------------------------
    def test_eval_problem_1_standard_redundant_graphical_and_sensitivity(self):
        for solver in SOLVERS:
            with self.subTest(solver=solver.__name__):
                r = solver(
                    [50, 80],
                    [[2, 1], [1, 3], [0, 1]],
                    [100, 90, 40],
                    ["<=", "<=", "<="],
                    direction="max",
                )
                self.assertEqual(r["status"], "optimal")
                self.assertEqual(r["objective_value"], Fraction(3380))
                self.assertEqual(r["solution"], {"x1": Fraction(42), "x2": Fraction(16)})
                # Holguras: R1=0, R2=0, R3=24
                slacks = [c["slack_or_surplus"] for c in r["constraint_results"]]
                self.assertEqual(slacks, [Fraction(0), Fraction(0), Fraction(24)])
                # Método gráfico 2D
                self.assertTrue(r["graphical"]["applicable"])
                self.assertEqual(r["graphical"]["region_type"], "bounded")
                self.assertEqual(len(r["graphical"]["vertices"]), 4)
                # Sensibilidad
                sens = r["sensitivity"]
                self.assertTrue(sens["applicable"])
                self.assertEqual(
                    [o["min_value"] for o in sens["objective_ranges"]],
                    [Fraction(80, 3), Fraction(25)],
                )
                self.assertEqual(
                    [o["max_value"] for o in sens["objective_ranges"]],
                    [Fraction(160), Fraction(150)],
                )
                self.assertEqual(
                    [rh["shadow_price"] for rh in sens["rhs_ranges"]],
                    [Fraction(14), Fraction(22), Fraction(0)],
                )
                self.assertEqual(
                    [(rh["min_value"], rh["max_value"]) for rh in sens["rhs_ranges"]],
                    [(Fraction(30), Fraction(180)), (Fraction(50), Fraction(150)), (Fraction(16), None)],
                )

    def test_eval_problem_2_minimization_equality_ge_negative_rhs(self):
        for solver in SOLVERS:
            with self.subTest(solver=solver.__name__):
                r = solver(
                    [4, 1],
                    [[3, 1], [4, 3], [-1, -2]],
                    [3, 6, -4],
                    ["=", ">=", ">="],
                    direction="min",
                )
                self.assertEqual(r["status"], "optimal")
                self.assertEqual(r["objective_value"], Fraction(17, 5))
                self.assertEqual(
                    r["solution"],
                    {"x1": Fraction(2, 5), "x2": Fraction(9, 5)},
                )
                self.assertEqual(r["graphical"]["region_type"], "segment")
                self.assertEqual(
                    [rh["shadow_price"] for rh in r["sensitivity"]["rhs_ranges"]],
                    [Fraction(7, 5), Fraction(0), Fraction(1, 5)],
                )

    def test_eval_problem_3_three_variables_graphical_not_applicable(self):
        for solver in SOLVERS:
            with self.subTest(solver=solver.__name__):
                r = solver(
                    [3, 2, 5],
                    [[1, 2, 1], [3, 0, 2], [1, 4, 0]],
                    [430, 460, 420],
                    ["<=", "<=", "<="],
                    direction="max",
                )
                self.assertEqual(r["status"], "optimal")
                self.assertEqual(r["objective_value"], Fraction(1350))
                self.assertEqual(
                    r["solution"],
                    {"x1": Fraction(0), "x2": Fraction(100), "x3": Fraction(230)},
                )
                self.assertFalse(r["graphical"]["applicable"])
                self.assertEqual(
                    [o["reduced_cost"] for o in r["sensitivity"]["objective_ranges"]],
                    [Fraction(-4), Fraction(0), Fraction(0)],
                )

    def test_eval_problem_4_infeasible(self):
        for solver in SOLVERS:
            with self.subTest(solver=solver.__name__):
                r = solver([1, 1], [[1, 1], [1, 1]], [2, 5], ["<=", ">="], direction="max")
                self.assertEqual(r["status"], "infeasible")
                self.assertTrue(r["special_cases"]["is_infeasible"])
                self.assertEqual(r["graphical"]["region_type"], "empty")

    def test_eval_problem_5_unbounded(self):
        for solver in SOLVERS:
            with self.subTest(solver=solver.__name__):
                r = solver([1, 1], [[1, -1], [-1, 1]], [1, 2], ["<=", "<="], direction="max")
                self.assertEqual(r["status"], "unbounded")
                self.assertTrue(r["special_cases"]["is_unbounded"])
                self.assertEqual(r["graphical"]["region_type"], "unbounded")

    def test_eval_problem_6_multiple_optimal_solutions(self):
        for solver in SOLVERS:
            with self.subTest(solver=solver.__name__):
                r = solver([2, 4], [[1, 2], [1, 1]], [5, 4], ["<=", "<="], direction="max")
                self.assertEqual(r["status"], "optimal")
                self.assertEqual(r["objective_value"], Fraction(10))
                self.assertTrue(r["special_cases"]["has_multiple_optima"])
                self.assertGreaterEqual(len(r["special_cases"]["alternative_solutions"]), 1)
                self.assertEqual(len(r["graphical"]["optimal_segment"]), 2)

    def test_eval_problem_7_degeneracy(self):
        for solver in SOLVERS:
            with self.subTest(solver=solver.__name__):
                r = solver([3, 9], [[1, 4], [1, 2]], [8, 4], ["<=", "<="], direction="max")
                self.assertEqual(r["status"], "optimal")
                self.assertEqual(r["objective_value"], Fraction(18))
                self.assertEqual(r["solution"], {"x1": Fraction(0), "x2": Fraction(2)})
                self.assertTrue(r["special_cases"]["is_degenerate"])
                self.assertIn("s1", r["special_cases"]["degenerate_variables"])

    def test_step_by_step_artifacts_present(self):
        r_bm = solve_big_m([50, 80], [[2, 1], [1, 3]], [100, 90], ["<=", "<="])
        it0 = r_bm["iterations"][0]
        self.assertIsNotNone(it0["tableau"])
        self.assertIsNotNone(it0["pivot"])
        self.assertTrue(len(it0["ratio_test"]) == 2)
        self.assertTrue(it0["entering_reason"])
        self.assertTrue(it0["leaving_reason"])

        r_rs = solve_revised_simplex([50, 80], [[2, 1], [1, 3]], [100, 90], ["<=", "<="])
        it0_rs = r_rs["iterations"][0]
        self.assertIsNotNone(it0_rs["inverse_basis"])
        self.assertIsNotNone(it0_rs["dual_values"])
        self.assertIsNotNone(it0_rs["pivot"])
        self.assertTrue(len(it0_rs["ratio_test"]) == 2)

    def test_pure_python_pdf_generator(self):
        pdf_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "app", "services", "pdf_export.py")
        )
        spec = importlib.util.spec_from_file_location("pdf_export", pdf_path)
        pdf_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(pdf_mod)

        r = solve_big_m([50, 80], [[2, 1], [1, 3]], [100, 90], ["<=", "<="])
        minimal_dict = {
            "status": "optimal",
            "method": "big_m",
            "objective_value": "3380",
            "solution": {"x1": "42", "x2": "16"},
            "iterations": [],
            "standard_form": r["standard_form"],
            "constraint_results": [],
            "special_cases": {"messages": []},
            "sensitivity": {"applicable": False, "message": "N/A"},
            "graphical": r["graphical"],
        }
        pdf_bytes = pdf_mod.generate_solution_pdf(minimal_dict)
        self.assertTrue(pdf_bytes.startswith(b"%PDF-1.4"))
        self.assertIn(b"%%EOF", pdf_bytes)


if __name__ == "__main__":
    unittest.main()
