"""Pure-Python PDF 1.4 generator for Linear Programming step-by-step reports.

Generates a genuine, multi-page, standards-compliant PDF document without
requiring third-party PDF libraries. Includes:
- Problem formulation and standard form
- Optimal solution, slacks/surpluses, and special cases
- Every simplex iteration (Tableau / B^-1, reduced costs, minimum ratio test, pivot, justifications)
- Sensitivity analysis tables and interpretations
- Vector 2D graphical method plot when n = 2
"""

from __future__ import annotations

import textwrap
from typing import Any


PAGE_W = 612.0  # Letter width (pt)
PAGE_H = 792.0  # Letter height (pt)
MARGIN_X = 44.0
MARGIN_TOP = 50.0
MARGIN_BOTTOM = 48.0
CONTENT_W = PAGE_W - 2 * MARGIN_X


_UNICODE_REPLACEMENTS = {
    "≤": "<=",
    "≥": ">=",
    "∞": "inf",
    "−": "-",
    "–": "-",
    "—": "-",
    "·": "*",
    "×": "x",
    "⁻¹": "^-1",
    "¹": "^1",
    "²": "^2",
    "³": "^3",
    "₁": "1",
    "₂": "2",
    "₃": "3",
    "₄": "4",
    "₅": "5",
    "c̄": "c_bar",
    "✓": "[OK]",
    "✗": "[X]",
    "⚠": "[!]",
    "→": "->",
    "↓": "->",
    "↑": "<-",
    "•": "-",
}


def _sanitize_text(text: str) -> str:
    s = str(text)
    for src, dst in _UNICODE_REPLACEMENTS.items():
        s = s.replace(src, dst)
    # Encode to cp1252 (WinAnsi) safely
    return s.encode("cp1252", errors="replace").decode("cp1252")


def _pdf_escape(text: str) -> str:
    clean = _sanitize_text(text)
    clean = clean.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    return clean


def _format_big_m_dict(val: Any) -> str:
    if isinstance(val, dict) and "m_coefficient" in val:
        m = val["m_coefficient"]
        c = val["constant"]
        if m == "0":
            return c
        if m == "1":
            m_str = "M"
        elif m == "-1":
            m_str = "-M"
        else:
            m_str = f"{m}M"
        if c == "0":
            return m_str
        if c.startswith("-"):
            return f"{m_str} - {c[1:]}"
        return f"{m_str} + {c}"
    return str(val)


class _SimplePDFBuilder:
    """Minimal multi-page PDF 1.4 canvas with Helvetica, Helvetica-Bold, and Courier."""

    def __init__(self):
        self.pages: list[list[str]] = []
        self.y = PAGE_H - MARGIN_TOP
        self._new_page()

    def _new_page(self):
        self.pages.append([])
        self.y = PAGE_H - MARGIN_TOP

    def _emit(self, cmd: str):
        self.pages[-1].append(cmd)

    def ensure_space(self, height: float):
        if self.y - height < MARGIN_BOTTOM:
            self._new_page()

    def add_spacer(self, pts: float = 8.0):
        self.y -= pts
        if self.y < MARGIN_BOTTOM:
            self._new_page()

    def add_banner(self, title: str, subtitle: str):
        box_h = 48.0
        self.ensure_space(box_h + 10)
        y_bottom = self.y - box_h
        # Indigo banner background
        self._emit("0.31 0.27 0.90 rg")
        self._emit(f"{MARGIN_X:.1f} {y_bottom:.1f} {CONTENT_W:.1f} {box_h:.1f} re f")
        self._emit("1 1 1 rg")
        self._emit(
            f"BT /F2 15 Tf {MARGIN_X + 14:.1f} {self.y - 22:.1f} Td ({_pdf_escape(title)}) Tj ET"
        )
        self._emit(
            f"BT /F1 9.5 Tf {MARGIN_X + 14:.1f} {self.y - 38:.1f} Td ({_pdf_escape(subtitle)}) Tj ET"
        )
        self._emit("0.06 0.09 0.16 rg")
        self.y = y_bottom - 14.0

    def add_section_heading(self, title: str):
        self.ensure_space(28.0)
        self.y -= 4.0
        self._emit("0.31 0.27 0.90 rg")
        self._emit(
            f"BT /F2 12 Tf {MARGIN_X:.1f} {self.y:.1f} Td ({_pdf_escape(title)}) Tj ET"
        )
        self.y -= 5.0
        self._emit("0.88 0.91 0.94 RG 0.8 w")
        self._emit(f"{MARGIN_X:.1f} {self.y:.1f} m {PAGE_W - MARGIN_X:.1f} {self.y:.1f} l S")
        self._emit("0.06 0.09 0.16 rg")
        self.y -= 12.0

    def add_subheading(self, title: str):
        self.ensure_space(20.0)
        self._emit("0.15 0.22 0.35 rg")
        self._emit(
            f"BT /F2 10 Tf {MARGIN_X:.1f} {self.y:.1f} Td ({_pdf_escape(title)}) Tj ET"
        )
        self._emit("0.06 0.09 0.16 rg")
        self.y -= 14.0

    def add_paragraph(
        self,
        text: str,
        font: str = "F1",
        size: float = 9.0,
        indent: float = 0.0,
        color: tuple[float, float, float] = (0.12, 0.16, 0.24),
        leading: float | None = None,
    ):
        line_h = leading if leading is not None else (size + 3.5)
        avail_w = CONTENT_W - indent
        # Approximate average char width
        char_w = size * (0.60 if font == "F3" else 0.50)
        max_chars = max(20, int(avail_w / char_w))
        lines = []
        for raw_line in str(text).splitlines() or [""]:
            wrapped = textwrap.wrap(raw_line, width=max_chars) or [""]
            lines.extend(wrapped)

        r, g, b = color
        for line in lines:
            self.ensure_space(line_h + 2)
            self._emit(f"{r:.2f} {g:.2f} {b:.2f} rg")
            self._emit(
                f"BT /{font} {size:.1f} Tf {MARGIN_X + indent:.1f} {self.y:.1f} Td ({_pdf_escape(line)}) Tj ET"
            )
            self.y -= line_h

    def add_table(
        self,
        headers: list[str],
        rows: list[list[str]],
        col_widths: list[float] | None = None,
        font_size: float = 7.8,
        highlight_row: int | None = None,
        highlight_col: int | None = None,
    ):
        if not headers:
            return
        n_cols = len(headers)
        if col_widths is None:
            col_widths = [CONTENT_W / n_cols] * n_cols
        else:
            total = sum(col_widths)
            col_widths = [w * CONTENT_W / total for w in col_widths]

        row_h = max(14.5, font_size + 7.0)

        def draw_header():
            self.ensure_space(row_h * 2 + 4)
            y_bot = self.y - row_h
            self._emit("0.94 0.96 0.98 rg")
            self._emit(f"{MARGIN_X:.1f} {y_bot:.1f} {CONTENT_W:.1f} {row_h:.1f} re f")
            self._emit("0.82 0.85 0.90 RG 0.5 w")
            self._emit(f"{MARGIN_X:.1f} {y_bot:.1f} {CONTENT_W:.1f} {row_h:.1f} re S")
            x = MARGIN_X
            self._emit("0.15 0.22 0.35 rg")
            for idx, h in enumerate(headers):
                max_c = max(3, int((col_widths[idx] - 6) / (font_size * 0.55)))
                cell = _sanitize_text(h)
                if len(cell) > max_c:
                    cell = cell[: max_c - 1] + "."
                self._emit(
                    f"BT /F2 {font_size:.1f} Tf {x + 3:.1f} {y_bot + 4.2:.1f} Td ({_pdf_escape(cell)}) Tj ET"
                )
                x += col_widths[idx]
            self.y = y_bot

        draw_header()
        for r_idx, row in enumerate(rows):
            if self.y - row_h < MARGIN_BOTTOM:
                self._new_page()
                draw_header()
            y_bot = self.y - row_h
            if highlight_row is not None and r_idx == highlight_row:
                self._emit("0.93 0.95 1.00 rg")
                self._emit(f"{MARGIN_X:.1f} {y_bot:.1f} {CONTENT_W:.1f} {row_h:.1f} re f")
            elif r_idx % 2 == 1:
                self._emit("0.985 0.99 0.995 rg")
                self._emit(f"{MARGIN_X:.1f} {y_bot:.1f} {CONTENT_W:.1f} {row_h:.1f} re f")

            self._emit("0.88 0.90 0.94 RG 0.4 w")
            self._emit(f"{MARGIN_X:.1f} {y_bot:.1f} {CONTENT_W:.1f} {row_h:.1f} re S")

            x = MARGIN_X
            for c_idx, raw_val in enumerate(row):
                if (
                    highlight_row is not None
                    and highlight_col is not None
                    and r_idx == highlight_row
                    and c_idx == highlight_col
                ):
                    self._emit("0.80 0.85 1.00 rg")
                    self._emit(f"{x:.1f} {y_bot:.1f} {col_widths[c_idx]:.1f} {row_h:.1f} re f")

                max_c = max(3, int((col_widths[c_idx] - 6) / (font_size * 0.56)))
                cell = _sanitize_text(raw_val)
                if len(cell) > max_c:
                    cell = cell[: max_c - 1] + "."
                font_name = "F2" if c_idx == 0 else "F3"
                self._emit("0.08 0.12 0.20 rg")
                self._emit(
                    f"BT /{font_name} {font_size:.1f} Tf {x + 3:.1f} {y_bot + 4.2:.1f} Td ({_pdf_escape(cell)}) Tj ET"
                )
                x += col_widths[c_idx]
            self.y = y_bot
        self.y -= 8.0

    def add_graphical_plot(self, graphical: dict):
        """Draw a crisp 2D vector plot of the graphical method directly into the PDF."""
        plot_w = 340.0
        plot_h = 230.0
        self.ensure_space(plot_h + 45.0)

        bounds = graphical.get("bounds") or {}
        x_max = max(float(bounds.get("x_max", 10.0)), 1e-6)
        y_max = max(float(bounds.get("y_max", 10.0)), 1e-6)

        ox = MARGIN_X + 42.0
        oy = self.y - plot_h - 10.0

        def map_pt(x: float, y: float) -> tuple[float, float]:
            px = ox + (x / x_max) * plot_w
            py = oy + (y / y_max) * plot_h
            return px, py

        # Background frame
        self._emit("0.985 0.99 1.00 rg")
        self._emit(f"{ox:.1f} {oy:.1f} {plot_w:.1f} {plot_h:.1f} re f")

        # Grid lines (5 divisions)
        self._emit("0.90 0.92 0.95 RG 0.4 w")
        for step in range(6):
            gx = ox + (step / 5.0) * plot_w
            gy = oy + (step / 5.0) * plot_h
            self._emit(f"{gx:.1f} {oy:.1f} m {gx:.1f} {oy + plot_h:.1f} l S")
            self._emit(f"{ox:.1f} {gy:.1f} m {ox + plot_w:.1f} {gy:.1f} l S")
            # Tick labels
            x_val = (step / 5.0) * x_max
            y_val = (step / 5.0) * y_max
            self._emit("0.35 0.40 0.50 rg")
            self._emit(
                f"BT /F1 7 Tf {gx - 8:.1f} {oy - 11:.1f} Td ({_pdf_escape(f'{x_val:.1f}')}) Tj ET"
            )
            self._emit(
                f"BT /F1 7 Tf {ox - 28:.1f} {gy - 2.5:.1f} Td ({_pdf_escape(f'{y_val:.1f}')}) Tj ET"
            )

        # Feasible polygon shaded
        poly = graphical.get("feasible_polygon") or []
        if len(poly) >= 3:
            self._emit("0.82 0.86 0.99 rg")
            p0 = map_pt(poly[0]["x1_float"], poly[0]["x2_float"])
            self._emit(f"{p0[0]:.1f} {p0[1]:.1f} m")
            for p in poly[1:]:
                px, py = map_pt(p["x1_float"], p["x2_float"])
                self._emit(f"{px:.1f} {py:.1f} l")
            self._emit("h f")
        elif len(poly) == 2:
            self._emit("0.31 0.27 0.90 RG 2.2 w")
            p0 = map_pt(poly[0]["x1_float"], poly[0]["x2_float"])
            p1 = map_pt(poly[1]["x1_float"], poly[1]["x2_float"])
            self._emit(f"{p0[0]:.1f} {p0[1]:.1f} m {p1[0]:.1f} {p1[1]:.1f} l S")

        # Constraint lines
        palette = [
            (0.20, 0.40, 0.85),
            (0.08, 0.62, 0.45),
            (0.85, 0.42, 0.10),
            (0.65, 0.22, 0.78),
            (0.80, 0.18, 0.30),
        ]
        for idx, line in enumerate(graphical.get("constraint_lines") or []):
            pts = line.get("points") or []
            if len(pts) < 2:
                continue
            r, g, b = palette[idx % len(palette)]
            self._emit(f"{r:.2f} {g:.2f} {b:.2f} RG 1.2 w")
            p0 = map_pt(pts[0]["x1_float"], pts[0]["x2_float"])
            p1 = map_pt(pts[1]["x1_float"], pts[1]["x2_float"])
            self._emit(f"{p0[0]:.1f} {p0[1]:.1f} m {p1[0]:.1f} {p1[1]:.1f} l S")
            mx = (p0[0] + p1[0]) / 2.0 + 3.0
            my = (p0[1] + p1[1]) / 2.0 + 3.0
            self._emit(f"{r:.2f} {g:.2f} {b:.2f} rg")
            self._emit(
                f"BT /F2 7.5 Tf {mx:.1f} {my:.1f} Td ({_pdf_escape(line['label'])}) Tj ET"
            )

        # Isoprofit line
        obj_line = graphical.get("objective_line")
        if obj_line and len(obj_line.get("points") or []) >= 2:
            pts = obj_line["points"]
            p0 = map_pt(pts[0]["x1_float"], pts[0]["x2_float"])
            p1 = map_pt(pts[1]["x1_float"], pts[1]["x2_float"])
            self._emit("0.88 0.15 0.25 RG 1.4 w [4 3] 0 d")
            self._emit(f"{p0[0]:.1f} {p0[1]:.1f} m {p1[0]:.1f} {p1[1]:.1f} l S [] 0 d")

        # Axes
        self._emit("0.10 0.14 0.22 RG 1.1 w")
        self._emit(f"{ox:.1f} {oy:.1f} m {ox + plot_w:.1f} {oy:.1f} l S")
        self._emit(f"{ox:.1f} {oy:.1f} m {ox:.1f} {oy + plot_h:.1f} l S")
        self._emit("0.10 0.14 0.22 rg")
        self._emit(f"BT /F2 8.5 Tf {ox + plot_w + 5:.1f} {oy - 2:.1f} Td (x1) Tj ET")
        self._emit(f"BT /F2 8.5 Tf {ox - 6:.1f} {oy + plot_h + 6:.1f} Td (x2) Tj ET")

        # Vertices
        for v in graphical.get("vertices") or []:
            px, py = map_pt(v["x1_float"], v["x2_float"])
            if v.get("is_optimal"):
                self._emit("0.04 0.58 0.36 rg")
                rad = 3.8
            else:
                self._emit("0.15 0.20 0.35 rg")
                rad = 2.6
            self._emit(
                f"{px - rad:.1f} {py - rad:.1f} {rad * 2:.1f} {rad * 2:.1f} re f"
            )
            lbl = f"({v['x1']}, {v['x2']}) Z={v['z']}"
            self._emit(
                f"BT /F1 6.8 Tf {px + 5:.1f} {py + 3:.1f} Td ({_pdf_escape(lbl)}) Tj ET"
            )

        self.y = oy - 24.0

    def build_bytes(self) -> bytes:
        total_pages = len(self.pages)
        # Add footer page numbers to every page
        for idx, page_cmds in enumerate(self.pages, start=1):
            footer = f"Optimizacion Lineal Exacta - Pagina {idx} de {total_pages}"
            page_cmds.append("0.45 0.50 0.58 rg")
            page_cmds.append(
                f"BT /F1 8 Tf {MARGIN_X:.1f} 24.0 Td ({_pdf_escape(footer)}) Tj ET"
            )

        # Objects:
        # 1: Catalog
        # 2: Pages
        # 3: Font F1 (Helvetica)
        # 4: Font F2 (Helvetica-Bold)
        # 5: Font F3 (Courier)
        # For each page i: (6 + 2*i) = Page object, (7 + 2*i) = Content stream
        objects: list[bytes] = []

        page_obj_nums = [6 + 2 * i for i in range(total_pages)]
        kids_str = " ".join(f"{n} 0 R" for n in page_obj_nums)

        objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")
        objects.append(
            f"<< /Type /Pages /Kids [{kids_str}] /Count {total_pages} >>".encode("ascii")
        )
        objects.append(
            b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>"
        )
        objects.append(
            b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>"
        )
        objects.append(
            b"<< /Type /Font /Subtype /Type1 /BaseFont /Courier /Encoding /WinAnsiEncoding >>"
        )

        for i, page_cmds in enumerate(self.pages):
            page_num = 6 + 2 * i
            stream_num = page_num + 1
            stream_data = ("\n".join(page_cmds) + "\n").encode("cp1252", errors="replace")
            page_dict = (
                f"<< /Type /Page /Parent 2 0 R "
                f"/MediaBox [0 0 {PAGE_W:.0f} {PAGE_H:.0f}] "
                f"/Resources << /Font << /F1 3 0 R /F2 4 0 R /F3 5 0 R >> >> "
                f"/Contents {stream_num} 0 R >>"
            ).encode("ascii")
            stream_obj = (
                f"<< /Length {len(stream_data)} >>\nstream\n".encode("ascii")
                + stream_data
                + b"endstream"
            )
            objects.append(page_dict)
            objects.append(stream_obj)

        out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        offsets = [0]
        for obj_id, obj_body in enumerate(objects, start=1):
            offsets.append(len(out))
            out.extend(f"{obj_id} 0 obj\n".encode("ascii"))
            out.extend(obj_body)
            out.extend(b"\nendobj\n")

        xref_pos = len(out)
        out.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
        out.extend(b"0000000000 65535 f \n")
        for off in offsets[1:]:
            out.extend(f"{off:010d} 00000 n \n".encode("ascii"))

        out.extend(
            (
                f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
                f"startxref\n{xref_pos}\n%%EOF\n"
            ).encode("ascii")
        )
        return bytes(out)


def generate_solution_pdf(result_dict: dict) -> bytes:
    """Render a full SolveResponse dict (model_dump) into a downloadable PDF."""
    pdf = _SimplePDFBuilder()

    method_label = (
        "Método de la Gran M (Tableau Simplex)"
        if result_dict.get("method") == "big_m"
        else "Método Simplex Revisado (Dos Fases)"
    )
    pdf.add_banner(
        "Reporte de Programación Lineal - Solución Paso a Paso",
        f"{method_label} | Aritmética Racional Exacta (Fracciones)",
    )

    # 1. Formulación y Forma Estándar
    sf = result_dict.get("standard_form") or {}
    pdf.add_section_heading("1. Formulación y Forma Estándar")
    pdf.add_paragraph(f"Función objetivo original: {sf.get('original_objective', '')}", font="F2")
    pdf.add_paragraph(f"Función objetivo estándar: {sf.get('standard_objective', '')}", font="F3", size=8.5)
    if sf.get("objective_note"):
        pdf.add_paragraph(sf["objective_note"], indent=8.0, size=8.5)
    pdf.add_paragraph(
        f"Base inicial factible: {', '.join(sf.get('initial_basis') or [])}",
        font="F2",
        size=8.5,
    )
    pdf.add_spacer(4)
    sf_rows = [
        [
            f"R{c['index']}",
            c["original_equation"],
            c["standard_equation"],
            c["note"],
        ]
        for c in (sf.get("constraints") or [])
    ]
    if sf_rows:
        pdf.add_table(
            ["Restr.", "Original", "Forma Estándar", "Transformación"],
            sf_rows,
            col_widths=[0.08, 0.24, 0.30, 0.38],
            font_size=7.4,
        )

    # 2. Solución Óptima y Casos Especiales
    pdf.add_section_heading("2. Resultado y Solución Óptima")
    status_labels = {
        "optimal": "Solución Óptima Encontrada",
        "infeasible": "Problema Infactible (Sin Solución)",
        "unbounded": "Problema No Acotado",
        "iteration_limit": "Límite de Iteraciones Alcanzado",
    }
    status = result_dict.get("status", "")
    pdf.add_paragraph(f"Estado: {status_labels.get(status, status)}", font="F2", size=10.0)

    if status == "optimal":
        pdf.add_paragraph(
            f"Valor Óptimo Z* = {result_dict.get('objective_value')}",
            font="F2",
            size=11.0,
            color=(0.02, 0.45, 0.30),
        )
        sol = result_dict.get("solution") or {}
        sol_str = "  |  ".join(f"{k} = {v}" for k, v in sol.items())
        pdf.add_paragraph(f"Variables de decisión: {sol_str}", font="F3", size=9.0)

        c_results = result_dict.get("constraint_results") or []
        if c_results:
            pdf.add_spacer(4)
            pdf.add_subheading("Holguras y Excesos por Restriccion:")
            c_rows = [
                [
                    f"R{cr['constraint_index']}",
                    cr["lhs_value"],
                    cr["sense"],
                    cr["rhs_value"],
                    f"{cr['slack_or_surplus']} ({cr['type']})",
                    "Activa" if cr["is_binding"] else "No activa",
                ]
                for cr in c_results
            ]
            pdf.add_table(
                ["Restr.", "Eval. LHS", "Sentido", "RHS", "Holgura/Exceso", "Estado"],
                c_rows,
                col_widths=[0.10, 0.16, 0.10, 0.14, 0.30, 0.20],
                font_size=7.8,
            )

    special = result_dict.get("special_cases") or {}
    for msg in special.get("messages") or []:
        pdf.add_paragraph(f"Aviso: {msg}", font="F2", size=8.5, color=(0.65, 0.25, 0.05))

    # 3. Iteraciones Paso a Paso
    iterations = result_dict.get("iterations") or []
    if iterations:
        pdf.add_section_heading(f"3. Proceso Paso a Paso ({len(iterations)} iteraciones)")
        for it in iterations:
            phase_txt = f" (Fase {it['phase']})" if it.get("phase") else ""
            pdf.add_subheading(
                f"Iteracion {it['iteration']}{phase_txt}  |  Base: [{', '.join(it['basic_variables'])}]  |  Z = {it['objective_value']}"
            )
            if it.get("entering_reason"):
                pdf.add_paragraph(f"- Entrante / Criterio: {it['entering_reason']}", indent=6.0, size=8.2)
            if it.get("leaving_reason"):
                pdf.add_paragraph(f"- Saliente / Razon minima: {it['leaving_reason']}", indent=6.0, size=8.2)
            if it.get("pivot"):
                pv = it["pivot"]
                pdf.add_paragraph(
                    f"- Elemento pivote: {pv['value']} (fila {pv['row'] + 1}: {pv['row_variable']}, columna: {pv['col_variable']})",
                    indent=6.0,
                    size=8.2,
                    font="F2",
                )

            # Tableau (Big M)
            if it.get("tableau") is not None:
                vnames = it.get("variable_names") or []
                headers = ["Base"] + vnames + ["RHS"]
                rows = []
                for r_i, row_vals in enumerate(it["tableau"]):
                    b_name = it["basic_variables"][r_i] if r_i < len(it["basic_variables"]) else f"F{r_i+1}"
                    rows.append([b_name] + list(row_vals))
                # Append Cj - Zj row
                rc = it.get("reduced_costs") or {}
                rc_row = ["Cj-Zj"] + [_format_big_m_dict(rc.get(vn, "0")) for vn in vnames]
                bm_z = _format_big_m_dict(it.get("big_m_objective") or it.get("objective_value"))
                rc_row.append(bm_z)
                rows.append(rc_row)
                pv = it.get("pivot")
                pdf.add_table(
                    headers,
                    rows,
                    font_size=7.0 if len(headers) > 8 else 7.6,
                    highlight_row=pv["row"] if pv else None,
                    highlight_col=(pv["col"] + 1) if pv else None,
                )

            # Inverse Basis B^-1 & Reduced Costs (Revised Simplex)
            if it.get("inverse_basis") is not None:
                b_inv = it["inverse_basis"]
                if b_inv:
                    headers = ["Base"] + [f"B^-1[{j+1}]" for j in range(len(b_inv[0]))] + ["x_B"]
                    rows = [
                        [it["basic_variables"][r_i]] + list(row_vals) + [it["basic_values"][r_i]]
                        for r_i, row_vals in enumerate(b_inv)
                    ]
                    pdf.add_table(headers, rows, font_size=7.6)
                rc = it.get("reduced_costs") or {}
                if rc:
                    rc_line = "  |  ".join(f"{k}: {_format_big_m_dict(v)}" for k, v in rc.items())
                    pdf.add_paragraph(f"Costos reducidos: {rc_line}", font="F3", size=7.8, indent=6.0)

            # Ratio test table if present
            rt = it.get("ratio_test") or []
            if rt:
                rt_rows = [
                    [
                        entry["basic_variable"],
                        entry["rhs"],
                        entry["pivot_column_value"],
                        entry["ratio"] if entry["ratio"] is not None else "No aplica (<= 0)",
                        "MINIMA (Sale)" if entry["is_minimum"] else ("Elegible" if entry["eligible"] else "-"),
                    ]
                    for entry in rt
                ]
                pdf.add_table(
                    ["Var. Basica", "RHS (b_i)", "Col. Pivote", "Razon (b_i / a_ij)", "Decision"],
                    rt_rows,
                    col_widths=[0.16, 0.16, 0.16, 0.26, 0.26],
                    font_size=7.4,
                )

    # 4. Método Gráfico
    graphical = result_dict.get("graphical") or {}
    pdf.add_section_heading("4. Metodo Grafico")
    if not graphical.get("applicable"):
        pdf.add_paragraph(graphical.get("message", "El metodo grafico no aplica para este problema."))
    else:
        pdf.add_paragraph(graphical.get("message", ""))
        pdf.add_graphical_plot(graphical)
        verts = graphical.get("vertices") or []
        if verts:
            v_rows = [
                [
                    f"V{i}",
                    f"({v['x1']}, {v['x2']})",
                    v["z"],
                    "OPTIMO" if v["is_optimal"] else "",
                ]
                for i, v in enumerate(verts, start=1)
            ]
            pdf.add_table(
                ["Vertice", "Coordenadas (x1, x2)", "Valor Z", "Estado"],
                v_rows,
                col_widths=[0.15, 0.35, 0.25, 0.25],
                font_size=8.0,
            )

    # 5. Análisis de Sensibilidad
    sens = result_dict.get("sensitivity") or {}
    pdf.add_section_heading("5. Analisis de Sensibilidad")
    if not sens.get("applicable"):
        pdf.add_paragraph(sens.get("message", "No aplica analisis de sensibilidad."))
    else:
        obj_ranges = sens.get("objective_ranges") or []
        if obj_ranges:
            pdf.add_subheading("Rangos de Coeficientes de la Funcion Objetivo y Costos Reducidos:")
            o_rows = [
                [
                    o["variable"],
                    o["optimal_value"],
                    o["reduced_cost"],
                    o["current_coefficient"],
                    o["min_value"] if o["min_value"] is not None else "-inf",
                    o["max_value"] if o["max_value"] is not None else "+inf",
                ]
                for o in obj_ranges
            ]
            pdf.add_table(
                ["Var.", "Valor Opt.", "Costo Red.", "Coef. Actual", "Minimo", "Maximo"],
                o_rows,
                font_size=7.8,
            )
            for o in obj_ranges:
                pdf.add_paragraph(f"- {o['interpretation']}", indent=6.0, size=8.0)
            pdf.add_spacer(4)

        rhs_ranges = sens.get("rhs_ranges") or []
        if rhs_ranges:
            pdf.add_subheading("Precios Sombra y Rangos del Lado Derecho (RHS):")
            r_rows = [
                [
                    f"R{r['constraint_index']}",
                    r["slack_or_surplus"],
                    r["shadow_price"],
                    r["current_rhs"],
                    r["min_value"] if r["min_value"] is not None else "-inf",
                    r["max_value"] if r["max_value"] is not None else "+inf",
                ]
                for r in rhs_ranges
            ]
            pdf.add_table(
                ["Restr.", "Holg./Exc.", "Precio Sombra", "RHS Actual", "Minimo", "Maximo"],
                r_rows,
                font_size=7.8,
            )
            for r in rhs_ranges:
                pdf.add_paragraph(f"- {r['interpretation']}", indent=6.0, size=8.0)

        for note in sens.get("notes") or []:
            pdf.add_paragraph(note, font="F2", size=8.0, color=(0.55, 0.25, 0.05))

    return pdf.build_bytes()
