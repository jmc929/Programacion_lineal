from fastapi import APIRouter
from fastapi.responses import Response

from ..schemas import CompareResponse, ProblemRequest, SolveResponse
from ..services import compare_methods, export_solution_pdf, solve_problem


router = APIRouter(prefix="/api")


@router.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}


@router.post("/solve", response_model=SolveResponse, tags=["solver"])
def solve(request: ProblemRequest) -> SolveResponse:
    return solve_problem(request)


@router.post("/compare", response_model=CompareResponse, tags=["solver"])
def compare(request: ProblemRequest) -> CompareResponse:
    return compare_methods(request)


@router.post("/export/pdf", tags=["export"])
def export_pdf(request: ProblemRequest) -> Response:
    pdf_bytes = export_solution_pdf(request)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": 'attachment; filename="solucion_programacion_lineal.pdf"'
        },
    )
