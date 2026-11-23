import unittest
from fractions import Fraction

import httpx

from app.main import app


class SolverApiTests(unittest.IsolatedAsyncioTestCase):
    async def request(self, method, path, **kwargs):
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://testserver",
        ) as client:
            return await client.request(method, path, **kwargs)

    async def test_big_m_endpoint_returns_exact_results_and_iterations(self):
        response = await self.request(
            "POST",
            "/api/solve",
            json={
                "objective": [3, 2],
                "constraints": [
                    {"coefficients": [1, 1], "sense": "<=", "rhs": 4},
                    {"coefficients": [1, 0], "sense": "<=", "rhs": 2},
                    {"coefficients": [0, 1], "sense": "<=", "rhs": 3},
                ],
                "direction": "max",
                "method": "big_m",
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "optimal")
        self.assertEqual(payload["objective_value"], "10")
        self.assertEqual(payload["solution"], {"x1": "2", "x2": "2"})
        self.assertEqual(payload["iterations"][-1]["objective_value"], "10")
        self.assertEqual(Fraction(payload["solution"]["x1"]), Fraction(2))
        self.assertIsNotNone(payload["standard_form"])
        self.assertTrue(payload["graphical"]["applicable"])
        self.assertTrue(payload["sensitivity"]["applicable"])
        self.assertEqual(len(payload["constraint_results"]), 3)

    async def test_direct_mode_returns_solution_without_iterations(self):
        response = await self.request(
            "POST",
            "/api/solve",
            json={
                "objective": [50, 80],
                "constraints": [
                    {"coefficients": [2, 1], "sense": "<=", "rhs": 100},
                    {"coefficients": [1, 3], "sense": "<=", "rhs": 90},
                    {"coefficients": [0, 1], "sense": "<=", "rhs": 40},
                ],
                "direction": "max",
                "method": "big_m",
                "mode": "direct",
            },
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["mode"], "direct")
        self.assertEqual(payload["objective_value"], "3380")
        self.assertEqual(payload["iterations"], [])

    async def test_revised_simplex_preserves_fractional_input(self):
        response = await self.request(
            "POST",
            "/api/solve",
            json={
                "objective": ["0.1"],
                "constraints": [
                    {"coefficients": [1], "sense": "<=", "rhs": "0.3"}
                ],
                "method": "revised_simplex",
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["objective_value"], "3/100")
        self.assertEqual(payload["solution"], {"x1": "3/10"})
        self.assertFalse(payload["graphical"]["applicable"])

    async def test_compare_endpoint_runs_both_methods(self):
        response = await self.request(
            "POST",
            "/api/compare",
            json={
                "objective": [4, 1],
                "constraints": [
                    {"coefficients": [3, 1], "sense": "=", "rhs": 3},
                    {"coefficients": [4, 3], "sense": ">=", "rhs": 6},
                    {"coefficients": [-1, -2], "sense": ">=", "rhs": -4},
                ],
                "direction": "min",
            },
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["comparison"]["same_status"])
        self.assertTrue(payload["comparison"]["same_objective_value"])
        self.assertEqual(payload["big_m"]["objective_value"], "17/5")
        self.assertEqual(payload["revised_simplex"]["objective_value"], "17/5")

    async def test_export_pdf_endpoint_returns_valid_pdf(self):
        response = await self.request(
            "POST",
            "/api/export/pdf",
            json={
                "objective": [50, 80],
                "constraints": [
                    {"coefficients": [2, 1], "sense": "<=", "rhs": 100},
                    {"coefficients": [1, 3], "sense": "<=", "rhs": 90},
                ],
                "direction": "max",
                "method": "big_m",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "application/pdf")
        self.assertTrue(response.content.startswith(b"%PDF-1.4"))

    async def test_inconsistent_constraint_dimensions_return_422(self):
        response = await self.request(
            "POST",
            "/api/solve",
            json={
                "objective": [1, 2],
                "constraints": [
                    {"coefficients": [1], "sense": "<=", "rhs": 3}
                ],
            },
        )

        self.assertEqual(response.status_code, 422)

    async def test_json_float_and_empty_string_are_rejected(self):
        for bad_val in (0.1, "", "1/0"):
            response = await self.request(
                "POST",
                "/api/solve",
                json={
                    "objective": [bad_val],
                    "constraints": [
                        {"coefficients": [1], "sense": "<=", "rhs": 1}
                    ],
                },
            )
            self.assertEqual(response.status_code, 422)

    async def test_health_endpoint(self):
        response = await self.request("GET", "/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})


if __name__ == "__main__":
    unittest.main()
