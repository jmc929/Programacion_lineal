from fastapi import APIRouter

from ..schemas import ProblemRequest, SolveResponse
from ..services import solve_problem


router = APIRouter(prefix="/api")


@router.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}


@router.post("/solve", response_model=SolveResponse, tags=["solver"])
def solve(request: ProblemRequest) -> SolveResponse:
    return solve_problem(request)
