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

    async def test_json_float_is_rejected_to_prevent_implicit_rounding(self):
        response = await self.request(
            "POST",
            "/api/solve",
            json={
                "objective": [0.1],
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
