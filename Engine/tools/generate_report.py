#!/usr/bin/env python3
"""
SIRR Report Generator — Produces a professional PDF reading from engine output.
Usage: python generate_report.py [output.json] [report.pdf]
Requires: pip install reportlab
"""

import json
import sys
import os
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch, mm
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate, Frame
from reportlab.lib.units import cm


DEEP_NAVY    = HexColor("#0B1D3A")
GOLD         = HexColor("#C9A84C")
WARM_GRAY    = HexColor("#4A4A4A")
LIGHT_GRAY   = HexColor("#E8E8E8")
SOFT_CREAM   = HexColor("#FAF8F0")
ACCENT_BLUE  = HexColor("#2E5C8A")
ACCENT_RED   = HexColor("#8B2E2E")
MUTED_GREEN  = HexColor("#2E6B4F")
TABLE_HEAD   = HexColor("#1A2F4A")
TABLE_ALT    = HexColor("#F4F1E8")
DIVIDER      = HexColor("#C9A84C")


class SIRRDocTemplate(BaseDocTemplate):
    def __init__(self, filename, **kwargs):
        self.profile_subject = kwargs.pop('profile_subject', 'SIRR')
        super().__init__(filename, **kwargs)
        frame = Frame(
            self.leftMargin, self.bottomMargin,
            self.width, self.height,
            id='normal'
        )
        template = PageTemplate(id='main', frames=frame, onPage=self._draw_footer)
        self.addPageTemplates([template])

    def _draw_footer(self, canvas_obj, doc):
        canvas_obj.saveState()
        canvas_obj.setFont("Helvetica", 7)
        canvas_obj.setFillColor(HexColor("#999999"))
        canvas_obj.drawString(
            doc.leftMargin, 0.4 * inch,
            f"SIRR Report — {self.profile_subject}"
        )
        canvas_obj.drawRightString(
            doc.pagesize[0] - doc.rightMargin, 0.4 * inch,
            f"Page {doc.page}"
        )
        canvas_obj.setStrokeColor(LIGHT_GRAY)
        canvas_obj.setLineWidth(0.5)
        canvas_obj.line(
            doc.leftMargin,
            doc.pagesize[1] - doc.topMargin + 12,
            doc.pagesize[0] - doc.rightMargin,
            doc.pagesize[1] - doc.topMargin + 12
        )
        canvas_obj.restoreState()


def build_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle('CoverTitle', fontName='Helvetica-Bold', fontSize=36, textColor=DEEP_NAVY, alignment=TA_CENTER, spaceAfter=6))
    styles.add(ParagraphStyle('CoverArabic', fontName='Helvetica', fontSize=20, textColor=GOLD, alignment=TA_CENTER, spaceAfter=30))
    styles.add(ParagraphStyle('CoverSub', fontName='Helvetica', fontSize=12, textColor=WARM_GRAY, alignment=TA_CENTER, spaceAfter=4))
    styles.add(ParagraphStyle('CoverTag', fontName='Helvetica-Oblique', fontSize=10, textColor=ACCENT_BLUE, alignment=TA_CENTER, spaceAfter=8))
    styles.add(ParagraphStyle('SectionHead', fontName='Helvetica-Bold', fontSize=18, textColor=DEEP_NAVY, spaceBefore=24, spaceAfter=10, borderPadding=(0, 0, 4, 0)))
    styles.add(ParagraphStyle('SubHead', fontName='Helvetica-Bold', fontSize=13, textColor=ACCENT_BLUE, spaceBefore=14, spaceAfter=6))
    styles.add(ParagraphStyle('SubHead2', fontName='Helvetica-Bold', fontSize=11, textColor=WARM_GRAY, spaceBefore=10, spaceAfter=4))
    styles.add(ParagraphStyle('Body', fontName='Helvetica', fontSize=9.5, textColor=WARM_GRAY, leading=14, alignment=TA_JUSTIFY, spaceAfter=6))
    styles.add(ParagraphStyle('BodySmall', fontName='Helvetica', fontSize=8.5, textColor=WARM_GRAY, leading=12, spaceAfter=4))
    styles.add(ParagraphStyle('Callout', fontName='Helvetica-Oblique', fontSize=10, textColor=ACCENT_BLUE, leading=14, alignment=TA_CENTER, spaceBefore=8, spaceAfter=8, leftIndent=36, rightIndent=36))
    styles.add(ParagraphStyle('ThreadTitle', fontName='Helvetica-Bold', fontSize=11, textColor=DEEP_NAVY, spaceBefore=10, spaceAfter=3))
    styles.add(ParagraphStyle('Tension', fontName='Helvetica-Oblique', fontSize=9, textColor=ACCENT_RED, leading=12, leftIndent=18, spaceAfter=4))
    styles.add(ParagraphStyle('ClusterTitle', fontName='Helvetica-Bold', fontSize=10, textColor=MUTED_GREEN, spaceBefore=10, spaceAfter=3))
    styles.add(ParagraphStyle('Principle', fontName='Helvetica', fontSize=9, textColor=WARM_GRAY, leading=13, leftIndent=12, spaceBefore=2, spaceAfter=4, bulletIndent=0, bulletFontName='Helvetica-Bold'))
    styles.add(ParagraphStyle('ModuleTitle', fontName='Helvetica-Bold', fontSize=9.5, textColor=DEEP_NAVY, spaceBefore=8, spaceAfter=2))
    styles.add(ParagraphStyle('Disclaimer', fontName='Helvetica-Oblique', fontSize=7.5, textColor=HexColor("#999999"), leading=10, alignment=TA_CENTER, spaceBefore=12, spaceAfter=4))
    return styles


def build_cover(data, styles):
    elements = []
    profile = data['profile']
    results = data['results']
    synth = data['synthesis']
    elements.append(Spacer(1, 1.8 * inch))
    elements.append(Paragraph("S I R R", styles['CoverTitle']))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph("Systems Integration Resonance Recognition", styles['CoverSub']))
    elements.append(Spacer(1, 0.6 * inch))
    elements.append(HRFlowable(width="40%", thickness=1.5, color=GOLD, spaceBefore=0, spaceAfter=20, hAlign='CENTER'))
    elements.append(Paragraph(profile['subject'], ParagraphStyle('name', fontName='Helvetica-Bold', fontSize=22, textColor=DEEP_NAVY, alignment=TA_CENTER, spaceAfter=4)))
    elements.append(Paragraph(profile.get('arabic', ''), styles['CoverArabic']))
    elements.append(Paragraph(f"Born {profile['dob']}  ·  {profile.get('location', '')}", styles['CoverSub']))
    elements.append(Spacer(1, 0.5 * inch))
    n_modules = len(results)
    n_conv = synth.get('convergence_count', 0)
    n_sig = synth.get('significant_count', 0)
    elements.append(Paragraph(f"{n_modules} Computation Modules  ·  15+ Traditions  ·  {n_conv} Convergences  ·  {n_sig} Significant", styles['CoverTag']))
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(Paragraph(f"Generated {datetime.now().strftime('%B %d, %Y')}", styles['CoverSub']))
    elements.append(Spacer(1, 0.8 * inch))
    elements.append(Paragraph("This report presents structural reflections across many traditions. All outputs are deterministic computations, not predictions. No prophecy. No destiny claims. Agency is always yours.", styles['Disclaimer']))
    elements.append(PageBreak())
    return elements


def build_core_numbers(data, styles):
    elements = []
    narr = data['narrative']
    cn = narr['core_numbers']
    elements.append(Paragraph("Core Number Grid", styles['SectionHead']))
    elements.append(HRFlowable(width="100%", thickness=1, color=GOLD, spaceBefore=0, spaceAfter=12))
    numbers = [
        ("Life Path", str(cn['life_path']), "Your fundamental operating frequency"),
        ("Expression", str(cn['expression']), "Master Number — amplified output capacity"),
        ("Soul Urge", str(cn['soul_urge']), "Inner structural drive"),
        ("Personality", str(cn['personality']), "External analytical filter"),
        ("Birthday", str(cn['birthday']), "Adaptive range and motion"),
        ("Abjad First", str(cn.get('abjad_first', '—')), "Arabic name numerical root"),
    ]
    table_data = [["Position", "Value", "Function"]]
    for name, val, desc in numbers:
        table_data.append([name, val, desc])
    t = Table(table_data, colWidths=[1.6*inch, 0.8*inch, 4.0*inch])
    t.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'), ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('TEXTCOLOR', (0, 0), (-1, 0), white), ('BACKGROUND', (0, 0), (-1, 0), TABLE_HEAD),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'), ('FONTNAME', (1, 1), (1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, -1), 9.5), ('FONTSIZE', (1, 1), (1, -1), 16),
        ('TEXTCOLOR', (1, 1), (1, -1), DEEP_NAVY), ('TEXTCOLOR', (0, 1), (0, -1), WARM_GRAY),
        ('TEXTCOLOR', (2, 1), (2, -1), WARM_GRAY), ('FONTSIZE', (2, 1), (2, -1), 8.5),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, TABLE_ALT]),
        ('TOPPADDING', (0, 0), (-1, -1), 8), ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10), ('GRID', (0, 0), (-1, -1), 0.5, LIGHT_GRAY),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 18))
    natal = next((r for r in data['results'] if r['id'] == 'natal_chart'), None)
    if natal:
        d = natal['data']
        elements.append(Paragraph("Natal Positions", styles['SubHead']))
        big3 = []
        planets = d.get('planets', {})
        for body in ['Sun', 'Moon']:
            if body in planets:
                p = planets[body]
                big3.append(f"{body}: {p.get('sign', '?')} {p.get('longitude', 0):.1f}°")
        asc = d.get('houses', {}).get('1')
        if asc is not None:
            big3.append(f"Ascendant: {asc:.1f}°")
        if big3:
            elements.append(Paragraph("  ·  ".join(big3), styles['Body']))
        elements.append(Spacer(1, 12))
    return elements


def build_convergence(data, styles):
    """Convergence Analysis page.

    Under §X.3 strict-no-counts (Decision 2, 2026-05-03), the inline
    counts row, Top Convergences table, Secondary Resonances list, and
    Monte Carlo baseline footer are retired. The page now surfaces the
    dominant root concept (Option γ analog for PDF) plus the headline
    callout. Engineering signals (system_count, group_count, percentile)
    remain in the synthesis JSON for non-customer-facing audit use.
    """
    elements = []
    narr = data['narrative']
    cs = narr.get('convergence_summary', {})
    elements.append(Paragraph("Convergence Analysis", styles['SectionHead']))
    elements.append(HRFlowable(width="100%", thickness=1, color=GOLD, spaceBefore=0, spaceAfter=12))
    mr = narr.get('mirror_reading', {})
    headline = mr.get('headline', '')
    if headline:
        elements.append(Paragraph(f'"{headline}"', styles['Callout']))
        elements.append(Spacer(1, 8))
    dominant_root = cs.get('dominant_root', '?')
    if dominant_root != '?':
        elements.append(Paragraph(
            f"<b>Dominant Root:</b> {dominant_root}",
            styles['Body']))
        elements.append(Spacer(1, 8))
    secondary = cs.get('secondary', [])
    if secondary:
        elements.append(Paragraph("Secondary Patterns", styles['SubHead2']))
        sec_text = ", ".join(f"Root {s['root']}" for s in secondary[:6])
        elements.append(Paragraph(sec_text, styles['BodySmall']))
        elements.append(Spacer(1, 8))
    elements.append(PageBreak())
    return elements


def build_mirror_reading(data, styles):
    elements = []
    mr = data['narrative'].get('mirror_reading', {})
    elements.append(Paragraph("Mirror Reading", styles['SectionHead']))
    elements.append(HRFlowable(width="100%", thickness=1, color=GOLD, spaceBefore=0, spaceAfter=12))
    elements.append(Paragraph("Structural Threads", styles['SubHead']))
    for i, thread in enumerate(mr.get('threads', []), 1):
        elements.append(Paragraph(f"{i}. {thread['title']}", styles['ThreadTitle']))
        elements.append(Paragraph(thread.get('capacity_statement', ''), styles['Body']))
        for tension in thread.get('tensions', []):
            elements.append(Paragraph(f"Tension: {tension}", styles['Tension']))
    elements.append(Spacer(1, 12))
    clusters = mr.get('cross_tradition_clusters', [])
    if clusters:
        elements.append(Paragraph("Cross-Tradition Convergences", styles['SubHead']))
        elements.append(Paragraph("When traditions that genuinely differ in computation method point to the same theme, the signal carries extra weight.", styles['BodySmall']))
        elements.append(Spacer(1, 6))
        for cluster in clusters:
            elements.append(Paragraph(cluster['title'], styles['ClusterTitle']))
            elements.append(Paragraph(cluster.get('description', ''), styles['Body']))
            ind_note = cluster.get('independence_note', '')
            if ind_note:
                elements.append(Paragraph(f"Independence: {ind_note}", styles['BodySmall']))
    elements.append(Spacer(1, 12))
    elem = mr.get('elemental_summary', {})
    if elem:
        elements.append(Paragraph("Elemental Profile", styles['SubHead']))
        elements.append(Paragraph(f"<b>Primary:</b> {elem.get('primary_element', '?')} ({elem.get('primary_temperament', '?')})  ·  <b>Secondary:</b> {elem.get('secondary_element', '?')}  ·  <b>Blend:</b> {elem.get('blend', '?')}", styles['Body']))
        desc = elem.get('description', '')
        if desc:
            elements.append(Paragraph(desc, styles['Body']))
    elements.append(Spacer(1, 12))
    principles = mr.get('integration_principles', [])
    if principles:
        elements.append(Paragraph("Integration Principles", styles['SubHead']))
        for p in principles:
            elements.append(Paragraph(f"• {p}", styles['Principle']))
    uncertainties = mr.get('uncertainties', [])
    if uncertainties:
        elements.append(Spacer(1, 10))
        elements.append(Paragraph("Confidence Notes", styles['SubHead2']))
        for u in uncertainties:
            status_color = MUTED_GREEN if u.get('status') == 'CONFIDENT' else ACCENT_RED
            elements.append(Paragraph(f"<font color='{status_color.hexval()}'><b>{u.get('status', '?')}</b></font> — {u.get('item', '')}: {u.get('reason', '')}", styles['BodySmall']))
    elements.append(PageBreak())
    return elements


def build_module_pages(data, styles):
    elements = []
    results = data['results']
    elements.append(Paragraph("Module Highlights", styles['SectionHead']))
    elements.append(HRFlowable(width="100%", thickness=1, color=GOLD, spaceBefore=0, spaceAfter=12))
    elements.append(Paragraph(f"Selected interpretations from {len(results)} computation modules across 15+ civilizational traditions. Each module computes independently — convergence emerges at the synthesis layer.", styles['Body']))
    elements.append(Spacer(1, 8))
    tradition_groups = {
        "Islamic / Arabic": ["abjad_kabir", "abjad_saghir", "abjad_wusta", "abjad_maghribi", "elemental_letters", "luminous_dark", "solar_lunar", "wafq", "hijri", "manazil", "geomancy", "taksir", "bast_kasr", "istikhara_adad", "zakat_huruf", "jafr", "buduh", "persian_abjad", "tasyir"],
        "Western Numerology": ["attitude", "bridges", "challenges", "chaldean", "compound", "cornerstone", "essence", "hidden_passion", "karmic_debt", "life_purpose", "maturity", "personal_year", "pinnacles", "subconscious_self", "enneagram_dob", "steiner_cycles", "latin_ordinal"],
        "Western Astrology": ["decan", "dwad", "profection", "sabian", "firdaria", "temperament", "natal_chart", "house_system", "aspects", "essential_dignities", "sect", "arabic_parts", "declinations", "midpoints", "harmonic_charts", "solar_arc", "solar_return", "progressions", "fixed_stars"],
        "Hellenistic": ["antiscia", "reception", "zodiacal_releasing", "dorothean_chronocrators", "almuten"],
        "Vedic": ["nakshatra", "vedic_tithi", "vedic_yoga", "vimshottari", "yogini_dasha", "ashtottari_dasha", "shadbala", "ashtakavarga", "shodashavarga", "kalachakra_dasha"],
        "Chinese": ["bazi_pillars", "bazi_growth", "bazi_daymaster", "bazi_luck_pillars", "bazi_hidden_stems", "bazi_ten_gods", "bazi_combos", "bazi_shensha", "chinese_zodiac", "flying_star", "nayin", "nine_star_ki", "lo_shu_grid", "iching", "bazhai", "meihua", "zi_wei_dou_shu"],
        "Tarot": ["tarot_birth", "tarot_year", "tarot_name", "cardology"],
        "Hebrew / Kabbalistic": ["hebrew_gematria", "hebrew_calendar", "atbash", "albam", "avgad", "notarikon", "tree_of_life"],
        "Gematria Systems": ["greek_isopsephy", "coptic_isopsephy", "armenian_gematria", "georgian_gematria", "agrippan", "thelemic_gematria", "trithemius", "mandaean_gematria"],
        "Calendar / Cycle": ["julian", "biorhythm", "day_ruler", "planetary_hours", "god_of_day"],
        "Celtic / Norse / Egyptian": ["celtic_tree", "ogham", "birth_rune", "egyptian_decan"],
        "Mesoamerican": ["mayan", "dreamspell", "tonalpohualli"],
        "African": ["ifa", "ethiopian_asmat", "akan_kra_din"],
        "Southeast Asian / Tibetan": ["pawukon", "primbon", "weton", "planetary_joy", "tibetan_mewa"],
        "Western Esoteric": ["rose_cross_sigil", "planetary_kameas", "ars_magna", "gd_correspondences"],
    }
    result_map = {r['id']: r for r in results}
    featured_ids = {"abjad_kabir", "elemental_letters", "manazil", "geomancy", "jafr", "chaldean", "essence", "pinnacles", "personal_year", "natal_chart", "firdaria", "essential_dignities", "sect", "nakshatra", "vimshottari", "vedic_tithi", "bazi_pillars", "bazi_daymaster", "chinese_zodiac", "nine_star_ki", "tarot_birth", "cardology", "hebrew_gematria", "hebrew_calendar", "tree_of_life", "mayan", "celtic_tree", "birth_rune", "ifa", "ethiopian_asmat", "tibetan_mewa", "pawukon", "zodiacal_releasing", "almuten"}
    for tradition, module_ids in tradition_groups.items():
        present = [mid for mid in module_ids if mid in result_map]
        if not present:
            continue
        elements.append(Paragraph(tradition, styles['SubHead']))
        for mid in present:
            r = result_map[mid]
            d = r.get('data', {})
            cert = r.get('certainty', 'UNKNOWN')
            key_vals = []
            for k, v in list(d.items())[:4]:
                if isinstance(v, (dict, list)):
                    continue
                val_str = str(v)
                if len(val_str) > 40:
                    val_str = val_str[:37] + "..."
                key_vals.append(f"{k}: {val_str}")
            compact = "  ·  ".join(key_vals) if key_vals else ""
            elements.append(Paragraph(f"<b>{r['name']}</b> <font color='#999999' size='7'>[{cert}]</font>", styles['ModuleTitle']))
            if compact:
                elements.append(Paragraph(compact, styles['BodySmall']))
            if mid in featured_ids:
                interp = r.get('interpretation', '')
                if interp:
                    if len(interp) > 500:
                        interp = interp[:497] + "..."
                    elements.append(Paragraph(interp, styles['Body']))
        elements.append(Spacer(1, 6))
    elements.append(PageBreak())
    return elements


def build_methodology(data, styles):
    elements = []
    elements.append(Paragraph("Methodology", styles['SectionHead']))
    elements.append(HRFlowable(width="100%", thickness=1, color=GOLD, spaceBefore=0, spaceAfter=12))
    elements.append(Paragraph("SIRR (Systems Integration Resonance Recognition) is a deterministic computation engine that analyzes a person's name and date of birth across multiple esoteric traditions. Each tradition computes using its own mapping tables, algorithms, and cultural frameworks. Some traditions share input structure (cognate-mapped letter values) and are flagged accordingly; others operate on disjoint inputs.", styles['Body']))
    elements.append(Paragraph("The synthesis engine surfaces patterns of agreement, divergence, and structural absence across the computed traditions. Where multiple traditions return the same value, that pattern is shown without claiming it as evidence; agreement may arise from shared computation, input dependency, archetypal recurrence, or coincidence.", styles['Body']))
    elements.append(Paragraph("Certainty Tags", styles['SubHead2']))
    cert_data = [["Tag", "Meaning"], ["COMPUTED_STRICT", "Pure math, fully deterministic"], ["LOOKUP_FIXED", "Fixed mapping table, deterministic"], ["APPROX", "Approximation, needs ephemeris for exactness"], ["NEEDS_EPHEMERIS", "Requires astronomical data (provided via pyswisseph)"]]
    ct = Table(cert_data, colWidths=[1.8*inch, 4.6*inch])
    ct.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'), ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('TEXTCOLOR', (0, 0), (-1, 0), white), ('BACKGROUND', (0, 0), (-1, 0), TABLE_HEAD),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'), ('TEXTCOLOR', (0, 1), (0, -1), ACCENT_BLUE),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, TABLE_ALT]),
        ('TOPPADDING', (0, 0), (-1, -1), 5), ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8), ('GRID', (0, 0), (-1, -1), 0.5, LIGHT_GRAY),
    ]))
    elements.append(ct)
    elements.append(Spacer(1, 16))
    elements.append(Paragraph("Constitutional Principles", styles['SubHead2']))
    for p in ["No prophecy — all outputs are structural reflections, never predictions or destiny claims.", "Agency protection — coercive language is never used. Your choices remain entirely yours.", "Contradiction transparency — when traditions conflict, the ledger logs it openly.", "Provenance — every output traces to its engine, inputs, and constants version."]:
        elements.append(Paragraph(f"• {p}", styles['Principle']))
    elements.append(Spacer(1, 20))
    profile = data['profile']
    elements.append(Paragraph("Technical Metadata", styles['SubHead2']))
    elements.append(Paragraph(f"Engine: SIRR v{data.get('constants_version', '?')}  ·  Modules: {len(data['results'])}  ·  Profile: {profile['subject']}  ·  Computed: {data['narrative'].get('generated_at', 'N/A')[:10]}  ·  Report: {datetime.now().strftime('%Y-%m-%d')}", styles['BodySmall']))
    elements.append(Spacer(1, 30))
    elements.append(Paragraph("SIRR is a personal computation engine. It does not collect data, connect to servers, or share information. All processing is local and offline.", styles['Disclaimer']))
    return elements


def generate_report(input_path, output_path):
    with open(input_path) as f:
        data = json.load(f)
    styles = build_styles()
    doc = SIRRDocTemplate(output_path, pagesize=letter, topMargin=0.75*inch, bottomMargin=0.65*inch, leftMargin=0.85*inch, rightMargin=0.85*inch, profile_subject=data['profile']['subject'])
    elements = []
    elements += build_cover(data, styles)
    elements += build_core_numbers(data, styles)
    elements += build_convergence(data, styles)
    elements += build_mirror_reading(data, styles)
    elements += build_module_pages(data, styles)
    elements += build_methodology(data, styles)
    doc.build(elements)
    print(f"Report generated: {output_path}")
    print(f"  Subject: {data['profile']['subject']}")
    print(f"  Modules: {len(data['results'])}")
    print(f"  Convergences: {data['synthesis'].get('convergence_count', '?')}")


if __name__ == "__main__":
    input_file = sys.argv[1] if len(sys.argv) > 1 else "output.json"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "sirr_report.pdf"
    generate_report(input_file, output_file)
