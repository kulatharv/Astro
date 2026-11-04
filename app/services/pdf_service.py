"""PDF Report generation service for Kundali and Horoscope charts using in-memory buffers."""

import io


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
            textColor=colors.HexColor("#4F46E5"),
            spaceAfter=12,
        )
        heading_style = ParagraphStyle(
            "Heading2Custom",
            parent=styles["Heading2"],
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#1F2937"),
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
                p.get("name", ""),
                p.get("sign", ""),
                p.get("degree", ""),
                str(p.get("house", "")),
                p.get("nakshatra", ""),
                str(p.get("pada", "")),
                p.get("navamsa", ""),
                p.get("strength", "Neutral"),
            ])

        t = Table(table_data, colWidths=[65, 70, 75, 45, 80, 40, 80, 85])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4F46E5")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E5E7EB")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F9FAFB")]),
        ]))
        story.append(t)
        story.append(Spacer(1, 14))

        # Yogas
        story.append(Paragraph("Active Vedic Yogas & Planetary Combinations", heading_style))
        yogas = chart.get("yogas", [])
        active_yogas = [y for y in yogas if y.get("present")]
        if active_yogas:
            for y in active_yogas[:6]:
                story.append(Paragraph(f"• <b>{y.get('name')}</b> ({y.get('strength', 'Medium')}): {y.get('description', '')}", normal_style))
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

    except ImportError:
        text_content = f"AstroLogic AI Kundali Report\nLagna: {chart.get('lagna')}\n"
        buffer.write(text_content.encode("utf-8"))
        buffer.seek(0)
        return buffer


# Backward-compatibility alias
generate_kundali_pdf = generate_kundali_pdf_buffer
