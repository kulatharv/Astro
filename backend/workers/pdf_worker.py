"""PDF Report generation service for Kundali and Horoscope charts using in-memory buffers."""

import io


def _create_fallback_pdf(chart: dict) -> io.BytesIO:
    """Generate a valid, standards-compliant minimal PDF in pure Python without external dependencies."""
    buf = io.BytesIO()
    lagna = chart.get('lagna', 'Unknown')
    dasha = chart.get('mahadasha', 'Unknown')
    tithi = chart.get('tithi_name', 'Unknown')
    nakshatra = chart.get('nakshatra', 'Unknown')
    planets = chart.get('planets', [])

    text_lines = [
        "AstroLogic AI - Vedic Kundali Report",
        "=====================================",
        f"Ascendant (Lagna): {lagna} | Nakshatra: {nakshatra}",
        f"Current Mahadasha: {dasha} | Tithi: {tithi}",
        "",
        "Planetary Positions:",
        "--------------------",
    ]
    for p in planets:
        text_lines.append(
            f"  {p.get('name', '')}: {p.get('sign', '')} ({p.get('degree', '')}) in House {p.get('house', '')} [{p.get('strength', 'Neutral')}]"
        )

    # Build PDF stream
    content_stream = "BT\n/F1 12 Tf\n40 750 Td\n18 TL\n"
    for line in text_lines:
        safe_line = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        content_stream += f"({safe_line}) '\n"
    content_stream += "ET\n"

    stream_bytes = content_stream.encode("latin-1", "replace")
    stream_len = len(stream_bytes)

    objects = [
        b"%PDF-1.4\n",
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n",
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n",
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n",
        f"4 0 obj\n<< /Length {stream_len} >>\nstream\n".encode("ascii") + stream_bytes + b"\nendstream\nendobj\n",
        b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n",
    ]

    offsets = []
    current_offset = 0
    for obj in objects:
        if obj.startswith(b"%PDF"):
            current_offset += len(obj)
            continue
        offsets.append(current_offset)
        current_offset += len(obj)

    xref_pos = current_offset
    xref = f"xref\n0 {len(offsets) + 1}\n0000000000 65535 f \n".encode("ascii")
    for off in offsets:
        xref += f"{off:010d} 00000 n \n".encode("ascii")

    trailer = f"trailer\n<< /Size {len(offsets) + 1} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n".encode("ascii")

    for obj in objects:
        buf.write(obj)
    buf.write(xref)
    buf.write(trailer)
    buf.seek(0)
    return buf


def generate_kundali_pdf_buffer(chart: dict) -> io.BytesIO:
    """Generate a clean, structured Vedic Kundali PDF report in an isolated BytesIO buffer."""
    buffer = io.BytesIO()

    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36,
        )
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "ReportTitle",
            parent=styles["Title"],
            fontSize=20,
            leading=24,
            textColor=colors.HexColor("#821C17"),
            spaceAfter=12,
        )
        heading_style = ParagraphStyle(
            "Heading2Custom",
            parent=styles["Heading2"],
            fontSize=12,
            leading=16,
            textColor=colors.HexColor("#421A10"),
            spaceBefore=10,
            spaceAfter=6,
        )
        normal_style = styles["Normal"]

        story = []

        # Title
        story.append(Paragraph("AstroLogic AI — Vedic Kundali Report", title_style))
        story.append(
            Paragraph(
                f"<b>Ascendant (Lagna):</b> {chart.get('lagna', 'Unknown')} ({chart.get('lagna_degree', '')}) &nbsp;|&nbsp; "
                f"<b>Nakshatra:</b> {chart.get('lagna_nakshatra', '')} (Pada {chart.get('lagna_pada', 1)})",
                normal_style,
            )
        )
        story.append(
            Paragraph(
                f"<b>Current Mahadasha:</b> {chart.get('mahadasha', '')} &nbsp;|&nbsp; "
                f"<b>Dasha Balance:</b> {chart.get('dasha_balance', '')}",
                normal_style,
            )
        )
        story.append(Spacer(1, 14))

        # Planetary Positions Table
        story.append(Paragraph("Planetary Longitudes & Dignities", heading_style))
        table_data = [["Planet", "Sign", "Degree", "House", "Nakshatra", "Pada", "Navamsa (D9)", "Dignity"]]

        for p in chart.get("planets", []):
            table_data.append([
                str(p.get("name", "")),
                str(p.get("sign", "")),
                str(p.get("degree", "")),
                str(p.get("house", "")),
                str(p.get("nakshatra", "")),
                str(p.get("pada", "")),
                str(p.get("navamsa", "")),
                str(p.get("strength", "Neutral")),
            ])

        t = Table(table_data, colWidths=[65, 70, 75, 45, 80, 40, 80, 85])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#821C17")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#F9DAB5")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#FCEBD2")]),
        ]))
        story.append(t)
        story.append(Spacer(1, 14))

        # Yogas
        story.append(Paragraph("Active Vedic Yogas & Planetary Combinations", heading_style))
        yogas = chart.get("yogas", [])
        active_yogas = [y for y in yogas if y.get("present")]
        if active_yogas:
            for y in active_yogas[:6]:
                story.append(Paragraph(f"• <b>{y.get('name')}</b> ({y.get('strength', 'Active')}): {y.get('description', '')}", normal_style))
        else:
            story.append(Paragraph("No dominant special yogas detected in primary placements.", normal_style))

        story.append(Spacer(1, 10))

        # Doshas
        story.append(Paragraph("Dosha Analysis & Vedic Guidance", heading_style))
        doshas = chart.get("doshas", [])
        active_doshas = [d for d in doshas if d.get("present")]
        if active_doshas:
            for d in active_doshas:
                story.append(Paragraph(f"• <b>{d.get('name')}</b> (Severity: {d.get('severity', 'Medium')}): {d.get('description', '')}", normal_style))
        else:
            story.append(Paragraph("No severe doshas (Manglik, Sade Sati, Kaal Sarp) detected in natal chart.", normal_style))

        doc.build(story)
        buffer.seek(0)
        return buffer

    except Exception:
        return _create_fallback_pdf(chart)


# Backward-compatibility alias
generate_kundali_pdf = generate_kundali_pdf_buffer
