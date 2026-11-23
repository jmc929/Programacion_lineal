from fractions import Fraction
import math

from .fractions import to_fraction
from .standard_form import format_fraction


def _dedupe_points(points: list[tuple[Fraction, Fraction]]) -> list[tuple[Fraction, Fraction]]:
    unique = []
    for pt in points:
        if pt not in unique:
            unique.append(pt)
    return unique


def _clip_polygon_halfplane(
    polygon: list[tuple[Fraction, Fraction]],
    a: Fraction,
    b: Fraction,
    rhs: Fraction,
    sense: str,
) -> list[tuple[Fraction, Fraction]]:
    """Clip a 2D convex polygon (exact Fractions) against a*x + b*y <= rhs (or >=)."""
    if not polygon:
        return []

    # Normalize to keep: a*x + b*y <= rhs
    if sense == ">=":
        a, b, rhs = -a, -b, -rhs

    def eval_fn(pt):
        return a * pt[0] + b * pt[1] - rhs

    # Handle degenerate 0D or 1D input
    if len(polygon) == 1:
        return polygon if eval_fn(polygon[0]) <= 0 else []

    if len(polygon) == 2:
        p1, p2 = polygon
        v1, v2 = eval_fn(p1), eval_fn(p2)
        if v1 <= 0 and v2 <= 0:
            return [p1, p2]
        if v1 > 0 and v2 > 0:
            return []
        t = v1 / (v1 - v2)
        inter = (p1[0] + t * (p2[0] - p1[0]), p1[1] + t * (p2[1] - p1[1]))
        if v1 <= 0:
            return _dedupe_points([p1, inter])
        return _dedupe_points([inter, p2])

    output = []
    n = len(polygon)
    for i in range(n):
        curr_pt = polygon[i]
        prev_pt = polygon[i - 1]
        curr_val = eval_fn(curr_pt)
        prev_val = eval_fn(prev_pt)
        curr_in = curr_val <= 0
        prev_in = prev_val <= 0

        if curr_in:
            if not prev_in:
                t = prev_val / (prev_val - curr_val)
                inter = (
                    prev_pt[0] + t * (curr_pt[0] - prev_pt[0]),
                    prev_pt[1] + t * (curr_pt[1] - prev_pt[1]),
                )
                output.append(inter)
            output.append(curr_pt)
        elif prev_in:
            t = prev_val / (prev_val - curr_val)
            inter = (
                prev_pt[0] + t * (curr_pt[0] - prev_pt[0]),
                prev_pt[1] + t * (curr_pt[1] - prev_pt[1]),
            )
            output.append(inter)

    return _dedupe_points(output)


def _clip_box_with_constraints(
    x_max: Fraction,
    y_max: Fraction,
    constraints: list[tuple[Fraction, Fraction, str, Fraction]],
) -> list[tuple[Fraction, Fraction]]:
    poly = [
        (Fraction(0), Fraction(0)),
        (x_max, Fraction(0)),
        (x_max, y_max),
        (Fraction(0), y_max),
    ]
    for a, b, sense, rhs in constraints:
        if a == 0 and b == 0:
            ok = (
                (Fraction(0) <= rhs)
                if sense == "<="
                else (Fraction(0) >= rhs)
                if sense == ">="
                else (Fraction(0) == rhs)
            )
            if not ok:
                return []
            continue
        if sense == "<=":
            poly = _clip_polygon_halfplane(poly, a, b, rhs, "<=")
        elif sense == ">=":
            poly = _clip_polygon_halfplane(poly, a, b, rhs, ">=")
        else:
            poly = _clip_polygon_halfplane(poly, a, b, rhs, "<=")
            poly = _clip_polygon_halfplane(poly, a, b, rhs, ">=")
        if not poly:
            return []
    return poly


def _clip_line_to_box(
    a: Fraction,
    b: Fraction,
    rhs: Fraction,
    x_max: Fraction,
    y_max: Fraction,
) -> list[tuple[Fraction, Fraction]]:
    """Intersect line a*x + b*y = rhs with bounding box [0, x_max] x [0, y_max]."""
    if a == 0 and b == 0:
        return []
    pts = []
    # x = 0
    if b != 0:
        y = rhs / b
        if 0 <= y <= y_max:
            pts.append((Fraction(0), y))
        # x = x_max
        y = (rhs - a * x_max) / b
        if 0 <= y <= y_max:
            pts.append((x_max, y))
    # y = 0
    if a != 0:
        x = rhs / a
        if 0 <= x <= x_max:
            pts.append((x, Fraction(0)))
        # y = y_max
        x = (rhs - b * y_max) / a
        if 0 <= x <= x_max:
            pts.append((x, y_max))

    pts = _dedupe_points(pts)
    if len(pts) > 2:
        # Pick the two farthest points along the line
        pts.sort()
        pts = [pts[0], pts[-1]]
    return pts


def _nice_bound(max_val: float) -> Fraction:
    if max_val <= 0:
        return Fraction(10)
    padded = max_val * 1.25
    magnitude = 10 ** math.floor(math.log10(padded))
    normalized = padded / magnitude
    if normalized <= 1.2:
        nice = 1.2
    elif normalized <= 1.5:
        nice = 1.5
    elif normalized <= 2:
        nice = 2
    elif normalized <= 2.5:
        nice = 2.5
    elif normalized <= 3:
        nice = 3
    elif normalized <= 4:
        nice = 4
    elif normalized <= 5:
        nice = 5
    elif normalized <= 6:
        nice = 6
    elif normalized <= 8:
        nice = 8
    else:
        nice = 10
    val = nice * magnitude
    # Convert cleanly to exact Fraction
    return to_fraction(round(val, 6))


def _format_2d_equation(a: Fraction, b: Fraction, sense: str, rhs: Fraction) -> str:
    sense_sym = {"<=": "≤", ">=": "≥", "=": "="}[sense]
    terms = []
    for coeff, name in ((a, "x1"), (b, "x2")):
        if coeff == 0:
            continue
        abs_c = abs(coeff)
        c_str = "" if abs_c == 1 else format_fraction(abs_c)
        if not terms:
            sign = "-" if coeff < 0 else ""
            terms.append(f"{sign}{c_str}{name}")
        else:
            sign = " - " if coeff < 0 else " + "
            terms.append(f"{sign}{c_str}{name}")
    lhs = "".join(terms) if terms else "0"
    return f"{lhs} {sense_sym} {format_fraction(rhs)}"


def _satisfies_all(
    pt: tuple[Fraction, Fraction],
    constraints: list[tuple[Fraction, Fraction, str, Fraction]],
) -> bool:
    x, y = pt
    if x < 0 or y < 0:
        return False
    for a, b, sense, rhs in constraints:
        val = a * x + b * y
        if sense == "<=" and val > rhs:
            return False
        if sense == ">=" and val < rhs:
            return False
        if sense == "=" and val != rhs:
            return False
    return True


def _point_dict(pt: tuple[Fraction, Fraction]) -> dict:
    return {
        "x1": format_fraction(pt[0]),
        "x2": format_fraction(pt[1]),
        "x1_float": float(pt[0]),
        "x2_float": float(pt[1]),
    }


def compute_graphical_method(
    objective: list,
    matrix: list,
    rhs: list,
    senses: list,
    direction: str,
    status: str,
    optimal_value: Fraction | None = None,
    optimal_solution: dict | None = None,
) -> dict:
    """Compute exact 2D graphical method data (feasible region, vertices, lines, isoprofit)."""
    n_vars = len(objective)
    if n_vars != 2:
        return {
            "applicable": False,
            "message": (
                f"El método gráfico solo aplica para problemas con 2 variables de decisión "
                f"(este modelo tiene {n_vars} {'variable' if n_vars == 1 else 'variables'})."
            ),
        }

    c1, c2 = to_fraction(objective[0]), to_fraction(objective[1])
    constraints = [
        (to_fraction(row[0]), to_fraction(row[1]), sense, to_fraction(b_val))
        for row, sense, b_val in zip(matrix, senses, rhs)
    ]

    # 1. Compute all exact feasible vertices from pairwise intersections of constraint lines + axes
    lines_for_intersections = [
        (Fraction(1), Fraction(0), Fraction(0)),  # x1 = 0
        (Fraction(0), Fraction(1), Fraction(0)),  # x2 = 0
    ] + [(a, b, r) for a, b, _, r in constraints if not (a == 0 and b == 0)]

    true_vertices = []
    for i in range(len(lines_for_intersections)):
        a1, b1, r1 = lines_for_intersections[i]
        for j in range(i + 1, len(lines_for_intersections)):
            a2, b2, r2 = lines_for_intersections[j]
            det = a1 * b2 - a2 * b1
            if det == 0:
                continue
            x = (r1 * b2 - r2 * b1) / det
            y = (a1 * r2 - a2 * r1) / det
            pt = (x, y)
            if _satisfies_all(pt, constraints):
                true_vertices.append(pt)

    true_vertices = _dedupe_points(true_vertices)

    # Order vertices counterclockwise around their centroid if >= 3
    if len(true_vertices) >= 3:
        cx = sum(float(p[0]) for p in true_vertices) / len(true_vertices)
        cy = sum(float(p[1]) for p in true_vertices) / len(true_vertices)
        true_vertices.sort(key=lambda p: math.atan2(float(p[1]) - cy, float(p[0]) - cx))
    else:
        true_vertices.sort()

    # 2. Choose viewing bounding box [0, x_max] x [0, y_max]
    x_candidates = [0.0]
    y_candidates = [0.0]
    for pt in true_vertices:
        x_candidates.append(float(pt[0]))
        y_candidates.append(float(pt[1]))
    for a, b, _, r in constraints:
        if a != 0:
            x_int = float(r / a)
            if x_int > 0:
                x_candidates.append(x_int)
        if b != 0:
            y_int = float(r / b)
            if y_int > 0:
                y_candidates.append(y_int)

    # Keep reasonable scale if an extreme intercept exists far away from all feasible vertices
    if true_vertices:
        max_vx = max(float(p[0]) for p in true_vertices)
        max_vy = max(float(p[1]) for p in true_vertices)
        # Filter out absurdly far intercepts (> 4x max vertex) when vertices are positive
        x_ref = max(
            [max_vx] + [v for v in x_candidates if max_vx == 0 or v <= max_vx * 3.0]
        )
        y_ref = max(
            [max_vy] + [v for v in y_candidates if max_vy == 0 or v <= max_vy * 3.0]
        )
    else:
        x_ref = max(x_candidates)
        y_ref = max(y_candidates)

    if x_ref <= 0 and y_ref <= 0:
        x_ref = 10.0
        y_ref = 10.0
    elif x_ref <= 0:
        x_ref = y_ref
    elif y_ref <= 0:
        y_ref = x_ref

    x_max = _nice_bound(x_ref)
    y_max = _nice_bound(y_ref)
    # If unbounded (or all vertices on boundary), ensure extra room so rays are visible
    if status == "unbounded":
        x_max = _nice_bound(max(float(x_max), x_ref * 1.6 + 2.0))
        y_max = _nice_bound(max(float(y_max), y_ref * 1.6 + 2.0))

    # 3. Compute clipped feasible region polygon & detect bounded vs unbounded vs empty
    clipped_poly = _clip_box_with_constraints(x_max, y_max, constraints)
    larger_poly = _clip_box_with_constraints(x_max * 2, y_max * 2, constraints)

    is_region_unbounded = False
    if not clipped_poly and not larger_poly:
        region_type = "empty"
    else:
        # Check if feasible region grows when box doubles
        if set(larger_poly) != set(clipped_poly):
            is_region_unbounded = True
        if is_region_unbounded:
            region_type = "unbounded"
        elif len(clipped_poly) == 1:
            region_type = "point"
        elif len(clipped_poly) == 2:
            region_type = "segment"
        else:
            region_type = "bounded"

    # Order clipped polygon CCW if >= 3 points
    if len(clipped_poly) >= 3:
        cx = sum(float(p[0]) for p in clipped_poly) / len(clipped_poly)
        cy = sum(float(p[1]) for p in clipped_poly) / len(clipped_poly)
        clipped_poly.sort(key=lambda p: math.atan2(float(p[1]) - cy, float(p[0]) - cx))

    # 4. Build vertices list with Z values and optimal flags
    vertices_info = []
    optimal_vertices = []
    for pt in true_vertices:
        z_val = c1 * pt[0] + c2 * pt[1]
        is_opt = status == "optimal" and optimal_value is not None and z_val == optimal_value
        entry = {
            "x1": format_fraction(pt[0]),
            "x2": format_fraction(pt[1]),
            "x1_float": float(pt[0]),
            "x2_float": float(pt[1]),
            "z": format_fraction(z_val),
            "z_float": float(z_val),
            "is_optimal": is_opt,
        }
        vertices_info.append(entry)
        if is_opt:
            optimal_vertices.append(entry)

    # 5. Constraint lines clipped to the viewing box
    constraint_lines = []
    for idx, (a, b, sense, r) in enumerate(constraints, start=1):
        seg = _clip_line_to_box(a, b, r, x_max, y_max)
        constraint_lines.append(
            {
                "index": idx,
                "label": f"R{idx}",
                "equation": _format_2d_equation(a, b, sense, r),
                "sense": sense,
                "points": [_point_dict(p) for p in seg],
            }
        )

    # 6. Isoprofit / isocost line at optimal Z*
    objective_line = None
    if status == "optimal" and optimal_value is not None and not (c1 == 0 and c2 == 0):
        iso_pts = _clip_line_to_box(c1, c2, optimal_value, x_max, y_max)
        if len(iso_pts) >= 2:
            objective_line = {
                "label": f"Z* = {format_fraction(optimal_value)}",
                "equation": _format_2d_equation(c1, c2, "=", optimal_value),
                "points": [_point_dict(p) for p in iso_pts],
            }

    # Optimal segment if multiple optimal vertices exist
    optimal_segment = []
    if len(optimal_vertices) >= 2:
        optimal_segment = [optimal_vertices[0], optimal_vertices[-1]]

    region_messages = {
        "bounded": "Región factible acotada (polígono convexo cerrado).",
        "unbounded": (
            "Región factible no acotada (se extiende indefinidamente en el primer cuadrante)."
            if status != "unbounded"
            else "Región factible no acotada y la función objetivo crece/decrece indefinidamente (problema no acotado)."
        ),
        "empty": "Región factible vacía: las restricciones no tienen ningún punto en común (problema infactible).",
        "segment": "Región factible unidimensional (segmento de recta debido a una restricción de igualdad).",
        "point": "Región factible formada por un único punto factible.",
    }

    return {
        "applicable": True,
        "message": region_messages[region_type],
        "region_type": region_type,
        "bounds": {
            "x_min": 0.0,
            "x_max": float(x_max),
            "y_min": 0.0,
            "y_max": float(y_max),
        },
        "feasible_polygon": [_point_dict(p) for p in clipped_poly],
        "vertices": vertices_info,
        "constraint_lines": constraint_lines,
        "objective_line": objective_line,
        "optimal_segment": optimal_segment,
    }
