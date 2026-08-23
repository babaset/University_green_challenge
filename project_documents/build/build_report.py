"""Build the University Green Challenge project report as a polished PDF."""

from __future__ import annotations

import json
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Flowable,
    HRFlowable,
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "project_documents" / "University_Green_Challenge_Project_Report.pdf"
LOGO = ROOT / "green_challenge" / "assets" / "green_challenge_logo.png"
DATA = ROOT / "green_challenge_data.json"

GREEN = colors.HexColor("#116A43")
DARK_GREEN = colors.HexColor("#0B4B32")
LIGHT_GREEN = colors.HexColor("#E9F6EE")
MID_GREEN = colors.HexColor("#A7DDBA")
INK = colors.HexColor("#1C2B25")
MUTED = colors.HexColor("#5B6B62")
LINE = colors.HexColor("#D6E5DA")
GOLD = colors.HexColor("#B7791F")
RED = colors.HexColor("#B42318")
PALE = colors.HexColor("#F7FAF8")


class UMLDiagram(Flowable):
    """Compact UML class diagram generated from the project model and store."""

    def __init__(self):
        super().__init__()
        self.width = 516
        self.height = 330

    def wrap(self, available_width, available_height):
        return self.width, self.height

    def _box(self, canvas, x, y, w, h, title, lines, accent=GREEN):
        canvas.setStrokeColor(accent)
        canvas.setLineWidth(1.2)
        canvas.setFillColor(colors.white)
        canvas.roundRect(x, y, w, h, 7, stroke=1, fill=1)
        canvas.setFillColor(accent)
        canvas.roundRect(x, y + h - 25, w, 25, 7, stroke=0, fill=1)
        canvas.rect(x, y + h - 8, w, 8, stroke=0, fill=1)
        canvas.setFillColor(colors.white)
        canvas.setFont("Helvetica-Bold", 9)
        canvas.drawCentredString(x + w / 2, y + h - 16, title)
        canvas.setFillColor(INK)
        canvas.setFont("Helvetica", 7.2)
        line_y = y + h - 38
        for text in lines:
            canvas.drawString(x + 7, line_y, text)
            line_y -= 11

    def _arrow(self, canvas, x1, y1, x2, y2, label=""):
        canvas.setStrokeColor(MUTED)
        canvas.setFillColor(MUTED)
        canvas.setLineWidth(1)
        canvas.line(x1, y1, x2, y2)
        dx, dy = x2 - x1, y2 - y1
        length = max((dx * dx + dy * dy) ** 0.5, 1)
        ux, uy = dx / length, dy / length
        px, py = -uy, ux
        tipx, tipy = x2, y2
        canvas.line(tipx, tipy, tipx - 7 * ux + 3 * px, tipy - 7 * uy + 3 * py)
        canvas.line(tipx, tipy, tipx - 7 * ux - 3 * px, tipy - 7 * uy - 3 * py)
        if label:
            canvas.setFont("Helvetica", 6.5)
            canvas.drawCentredString((x1 + x2) / 2, (y1 + y2) / 2 + 5, label)

    def draw(self):
        c = self.canv
        self._box(c, 8, 201, 150, 115, "Student", [
            "student_id: str", "name: str", "points: int", "trust_score: int", "claims_log: list[Claim]",
        ])
        self._box(c, 185, 176, 156, 140, "Claim", [
            "action: str", "points: int", "status: str", "request_id: str", "review_level: str", "evidence_path: str", "evidence_hash: str",
        ])
        self._box(c, 367, 210, 142, 106, "PendingRequest", [
            "request_id: str", "student_id: str", "claim: Claim",
        ], GOLD)
        self._box(c, 47, 29, 192, 126, "ChallengeStore", [
            "students: dict[str, Student]", "pending_requests: list", "next_request_id: int", "register_student()", "submit_claim()", "review_claim()", "get_leaderboard()",
        ], DARK_GREEN)
        self._box(c, 297, 49, 174, 86, "Persistence", [
            "load_challenge_data()", "save_challenge_data()", "green_challenge_data.json",
        ], GREEN)
        self._arrow(c, 158, 257, 185, 257, "1   owns   *")
        self._arrow(c, 341, 262, 367, 262, "1 : 1")
        self._arrow(c, 143, 155, 88, 201, "manages *")
        self._arrow(c, 207, 155, 245, 176, "creates")
        self._arrow(c, 239, 90, 297, 90, "loads / saves")
        c.setFillColor(MUTED)
        c.setFont("Helvetica-Oblique", 7)
        c.drawString(10, 6, "UML relationships reflect the implemented data classes and ChallengeStore operations.")


class ArchitectureDiagram(Flowable):
    def __init__(self):
        super().__init__()
        self.width = 516
        self.height = 142

    def wrap(self, available_width, available_height):
        return self.width, self.height

    def draw(self):
        c = self.canv
        items = [
            (8, "CustomTkinter UI", "Login, forms, dashboards"),
            (138, "Application Controller", "UniversityGreenChallengeApp"),
            (287, "Business Rules", "ChallengeStore"),
            (416, "Local JSON Storage", "Persistence module"),
        ]
        for i, (x, title, subtitle) in enumerate(items):
            c.setFillColor(LIGHT_GREEN if i % 2 == 0 else PALE)
            c.setStrokeColor(MID_GREEN)
            c.roundRect(x, 40, 94, 63, 8, stroke=1, fill=1)
            c.setFillColor(DARK_GREEN)
            c.setFont("Helvetica-Bold", 8)
            for n, line in enumerate(title.split(" ", 1)):
                c.drawCentredString(x + 47, 84 - n * 10, line)
            c.setFillColor(MUTED)
            c.setFont("Helvetica", 6.5)
            c.drawCentredString(x + 47, 56, subtitle)
            if i < len(items) - 1:
                c.setStrokeColor(GREEN)
                c.setFillColor(GREEN)
                c.line(x + 95, 72, x + 123, 72)
                c.line(x + 123, 72, x + 117, 75)
                c.line(x + 123, 72, x + 117, 69)


def read_summary():
    with DATA.open(encoding="utf-8") as stream:
        data = json.load(stream)
    claims = [claim for student in data["students"] for claim in student["claims_log"]]
    approved = sum(claim["status"] in {"Admin-Approved", "Auto-Approved"} for claim in claims)
    rejected = sum(claim["status"] == "Rejected" for claim in claims)
    points = sum(student["points"] for student in data["students"])
    leaderboard = sorted(data["students"], key=lambda s: (-s["points"], -s["trust_score"], s["name"].casefold()))
    action_counts = {}
    for claim in claims:
        action_counts[claim["action"]] = action_counts.get(claim["action"], 0) + 1
    top_action = max(action_counts, key=action_counts.get) if action_counts else "No claims"
    return {
        "students": len(data["students"]), "claims": len(claims), "approved": approved,
        "rejected": rejected, "points": points, "leaderboard": leaderboard[:4],
        "top_action": top_action,
    }


def styles():
    base = getSampleStyleSheet()
    return {
        "cover_title": ParagraphStyle("CoverTitle", parent=base["Title"], fontName="Helvetica-Bold", fontSize=28, leading=33, textColor=DARK_GREEN, alignment=TA_CENTER, spaceAfter=10),
        "cover_sub": ParagraphStyle("CoverSub", parent=base["Normal"], fontName="Helvetica", fontSize=13, leading=19, textColor=MUTED, alignment=TA_CENTER),
        "section": ParagraphStyle("Section", parent=base["Heading1"], fontName="Helvetica-Bold", fontSize=17, leading=21, textColor=DARK_GREEN, spaceBefore=10, spaceAfter=8),
        "sub": ParagraphStyle("Sub", parent=base["Heading2"], fontName="Helvetica-Bold", fontSize=12, leading=15, textColor=GREEN, spaceBefore=9, spaceAfter=5),
        "body": ParagraphStyle("Body", parent=base["BodyText"], fontName="Helvetica", fontSize=9.5, leading=14, textColor=INK, alignment=TA_JUSTIFY, spaceAfter=7),
        "small": ParagraphStyle("Small", parent=base["Normal"], fontName="Helvetica", fontSize=8, leading=10.5, textColor=MUTED, spaceAfter=4),
        "bullet": ParagraphStyle("Bullet", parent=base["BodyText"], fontName="Helvetica", fontSize=9.3, leading=13, textColor=INK, leftIndent=16, firstLineIndent=-10, spaceAfter=4),
        "caption": ParagraphStyle("Caption", parent=base["Normal"], fontName="Helvetica-Oblique", fontSize=7.8, leading=10, textColor=MUTED, spaceBefore=3, spaceAfter=8),
        "code": ParagraphStyle("Code", parent=base["Code"], fontName="Courier", fontSize=7.2, leading=10, textColor=INK, backColor=PALE, borderColor=LINE, borderWidth=0.5, borderPadding=7, spaceBefore=3, spaceAfter=8),
    }


def p(text, style):
    return Paragraph(text, style)


def bullet(text, s):
    return Paragraph("- " + text, s["bullet"])


def heading(text, s):
    return [Paragraph(text, s["section"]), HRFlowable(width="100%", thickness=1, color=MID_GREEN, spaceAfter=8)]


def info_table(rows, col_widths, header=True, font_size=8.4):
    body_style = ParagraphStyle(
        "TableBody", fontName="Helvetica", fontSize=font_size, leading=font_size + 2,
        textColor=INK, alignment=TA_LEFT,
    )
    header_style = ParagraphStyle(
        "TableHeader", fontName="Helvetica-Bold", fontSize=font_size, leading=font_size + 2,
        textColor=colors.white, alignment=TA_LEFT,
    )
    rendered_rows = []
    for row_index, row in enumerate(rows):
        style = header_style if header and row_index == 0 else body_style
        rendered_rows.append([Paragraph(escape(str(cell)), style) for cell in row])
    table = Table(rendered_rows, colWidths=col_widths, repeatRows=1 if header else 0, hAlign="LEFT")
    commands = [
        ("GRID", (0, 0), (-1, -1), 0.4, LINE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), font_size),
        ("TEXTCOLOR", (0, 0), (-1, -1), INK),
    ]
    if header:
        commands += [
            ("BACKGROUND", (0, 0), (-1, 0), DARK_GREEN),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE]),
        ]
    table.setStyle(TableStyle(commands))
    return table


def callout(text, s):
    table = Table([[Paragraph(text, s["body"])]], colWidths=[516])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_GREEN),
        ("BOX", (0, 0), (-1, -1), 0.7, MID_GREEN),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return table


def page_decor(canvas, doc):
    canvas.saveState()
    width, height = letter
    if doc.page == 1:
        canvas.setFillColor(DARK_GREEN)
        canvas.rect(0, height - 18, width, 18, stroke=0, fill=1)
    else:
        canvas.setStrokeColor(MID_GREEN)
        canvas.setLineWidth(0.6)
        canvas.line(doc.leftMargin, height - 31, width - doc.rightMargin, height - 31)
        canvas.setFillColor(MUTED)
        canvas.setFont("Helvetica", 7.5)
        canvas.drawString(doc.leftMargin, height - 24, "University Green Challenge | Project Report")
        canvas.drawRightString(width - doc.rightMargin, 27, f"Page {doc.page}")
        canvas.setStrokeColor(MID_GREEN)
        canvas.line(doc.leftMargin, 36, width - doc.rightMargin, 36)
    canvas.restoreState()


def build():
    s = styles()
    summary = read_summary()
    doc = SimpleDocTemplate(
        str(OUT), pagesize=letter, leftMargin=0.65 * inch, rightMargin=0.65 * inch,
        topMargin=0.62 * inch, bottomMargin=0.6 * inch, title="University Green Challenge Project Report",
        author="University Green Challenge Project Team",
    )
    story = []

    # Cover
    story += [Spacer(1, 0.55 * inch)]
    if LOGO.exists():
        logo = Image(str(LOGO), width=1.35 * inch, height=1.35 * inch)
        logo.hAlign = "CENTER"
        story += [logo, Spacer(1, 0.18 * inch)]
    story += [
        p("UNIVERSITY GREEN CHALLENGE", s["cover_title"]),
        p("Project Report", s["cover_sub"]),
        Spacer(1, 0.26 * inch),
        HRFlowable(width="55%", thickness=2, color=GREEN, hAlign="CENTER"),
        Spacer(1, 0.22 * inch),
        p("A desktop sustainability engagement application that rewards verified eco-actions on campus.", s["cover_sub"]),
        Spacer(1, 0.9 * inch),
        p("Prepared for Project Assessment", s["cover_sub"]),
        Spacer(1, 0.12 * inch),
        p("August 2026", s["cover_sub"]),
        Spacer(1, 0.55 * inch),
        callout("<b>Scope:</b> This report documents the implemented Python application, its architecture, testing evidence, SDG alignment, constraints, and opportunities for future development.", s),
    ]
    story.append(PageBreak())

    # Executive summary / TOC
    story += heading("Executive Summary", s)
    story.append(p(
        "University Green Challenge is a local desktop application designed to make everyday sustainable choices visible, reviewable, and rewarding. Students register, submit photo-supported eco-action claims, monitor their progress, and view a leaderboard. Administrators review the queue, update statuses, approve or reject claims, and inspect analytics. The application uses CustomTkinter for the interface and a small Python domain layer for validation, scoring, persistence, and evidence reuse prevention.",
        s["body"],
    ))
    story.append(callout(
        "<b>Key result:</b> The implemented core rule checks passed 5 out of 5 isolated tests: registration, claim submission, duplicate-evidence rejection, approval scoring, and rejection trust-score handling.",
        s,
    ))
    story += [Spacer(1, 0.12 * inch), p("Report Structure", s["sub"])]
    toc_rows = [["Section", "Content"],
        ["2.1", "Introduction and SDG Background"], ["2.2", "Problem Statement"], ["2.3", "System Objectives"],
        ["2.4", "Application Design and UML Class Diagram"], ["2.5", "Implementation Details"],
        ["2.6", "Testing and Sample Outputs"], ["2.7", "Discussion and Limitations"], ["2.8", "Conclusion"],
    ]
    story.append(info_table(toc_rows, [75, 441]))
    story += [Spacer(1, 0.18 * inch), p("Evidence Base", s["sub"]), p(
        "The application-specific claims in this report are derived from the current project source code and saved demonstration data. SDG context is supported by the official United Nations Sustainable Development Goals pages listed in References.", s["body"]
    )]

    # Section 1
    story += heading("2.1. Introduction and SDG Background", s)
    story.append(p(
        "Universities are practical settings for sustainability action because students make repeated choices about transport, waste, energy, and consumption. However, informal activities are often difficult to record, verify, and recognize. University Green Challenge converts selected actions into a simple engagement cycle: action, evidence, review, points, feedback, and public ranking.", s["body"]
    ))
    story.append(p(
        "The project is directly aligned with SDG 12, Responsible Consumption and Production, by encouraging recycling, reusable bottles, and reduced waste. It also supports SDG 13, Climate Action, through lower-carbon mobility and energy-saving behaviours, and SDG 11, Sustainable Cities and Communities, through walking, cycling, and public transport. These connections are behavioural rather than measured emissions reductions; the application records participation and incentives, not verified carbon accounting. [1][2][3]", s["body"]
    ))
    sdg_rows = [["SDG", "Application link", "Examples implemented"],
        ["SDG 12", "Responsible use of materials and waste reduction.", "Recycle campus waste; use a reusable bottle."],
        ["SDG 13", "Encourage actions that can reduce operational emissions.", "Turn off unused devices; choose active mobility."],
        ["SDG 11", "Support sustainable and accessible transport choices.", "Walk/cycle to class; use public transport."],
    ]
    story.append(info_table(sdg_rows, [62, 195, 259], font_size=8))
    story.append(p("Table 1. SDG alignment of the implemented eco-actions. Sources: official UN SDG pages [1][2][3].", s["caption"]))

    # Problem
    story += heading("2.2. Problem Statement", s)
    story.append(p(
        "Campus sustainability initiatives can struggle to maintain student participation when there is no immediate feedback, transparent recognition, or consistent way to review evidence. Manual records are fragmented and a purely trust-based approach may allow duplicate or weak submissions. Administrators also need a manageable queue rather than informal messages or spreadsheets.", s["body"]
    ))
    story.append(p("The project addresses five practical gaps:", s["body"]))
    story += [
        bullet("Students need a quick way to record a completed eco-action and see its status.", s),
        bullet("Administrators need a controlled review process that can approve, reject, or request additional evidence.", s),
        bullet("The challenge needs a visible, stable leaderboard to reinforce participation.", s),
        bullet("Evidence should not be reused under a different filename.", s),
        bullet("The application state should persist between local sessions without requiring a database server.", s),
    ]

    # Objectives
    story += heading("2.3. System Objectives", s)
    objective_rows = [["Objective", "Implemented mechanism", "Success indicator"],
        ["Register participants", "Name and student ID validation; duplicate-ID prevention.", "New unique student can be stored."],
        ["Capture eco-actions", "Six selectable actions with predefined point values and image evidence.", "Claim enters pending review."],
        ["Review fairly", "Admin queue, statuses, notes, approval/rejection, trust-score changes.", "Every pending claim has an auditable final status."],
        ["Reward participation", "Points and deterministic leaderboard sorting.", "Approved claims update the ranking."],
        ["Protect evidence integrity", "SHA-256 fingerprint comparison of image bytes.", "Reused evidence is rejected."],
        ["Retain data locally", "JSON load/save after successful state changes.", "Records reappear after restart."],
    ]
    story.append(info_table(objective_rows, [115, 250, 151], font_size=7.6))
    story.append(p("Table 2. Objectives traced to concrete functions in the implementation.", s["caption"]))
    story.append(PageBreak())

    # Design
    story += heading("2.4. Application Design", s)
    story.append(p("The application follows a lightweight layered design. The interface controls screen changes and user input; the store applies rules; dataclasses define the domain model; and the persistence module serializes the current state to JSON. This separation keeps the most important rules testable without loading the graphical interface.", s["body"]))
    story.append(KeepTogether([ArchitectureDiagram(), p("Figure 1. Application architecture.", s["caption"])]))
    story += [p("UML Class Diagram", s["sub"]), KeepTogether([UMLDiagram(), p("Figure 2. UML class diagram for the implemented domain model.", s["caption"])])]
    story.append(p("Relationship summary: a <b>Student</b> owns a claim history; a <b>Claim</b> stores action, point value, status, evidence metadata, and review metadata; a <b>PendingRequest</b> references a claim awaiting a decision; and <b>ChallengeStore</b> coordinates registration, review, ranking, and persistence.", s["body"]))

    # Implementation
    story += heading("2.5. Implementation Details", s)
    story += [p("Technology Stack", s["sub"])]
    tech_rows = [["Layer", "Implementation", "Role"],
        ["Entry point", "university_green_challenge.py", "Launches the desktop application."],
        ["User interface", "CustomTkinter and tkinter widgets", "Login, registration, forms, tables, dashboards, dialogs."],
        ["Domain model", "dataclasses", "Student, Claim, and PendingRequest structures."],
        ["Business logic", "ChallengeStore", "Validation, scoring, trust changes, queue handling, leaderboard sorting."],
        ["Persistence", "JSON file", "Local state stored in green_challenge_data.json."],
        ["Evidence integrity", "hashlib.sha256", "Blocks re-use of an image by comparing file-content fingerprints."],
    ]
    story.append(info_table(tech_rows, [90, 165, 261], font_size=7.8))
    story.append(p("Table 3. Main implementation components.", s["caption"]))
    story += [p("Business Rules", s["sub"])]
    story += [
        bullet("The system normalizes student names and IDs, then rejects empty or duplicate IDs.", s),
        bullet("A submitted action must be one of six configured eco-actions. Their values are 5, 8, 10, 12, 15, or 25 points.", s),
        bullet("The evidence image is read in blocks and hashed with SHA-256. A matching historical hash raises an error before a new claim is saved.", s),
        bullet("Approval adds the claim points and increases trust by up to 5, capped at 100. Rejection reduces trust by 20, floored at 0.", s),
        bullet("Leaderboard order is stable: points descending, trust score descending, name ascending, then student ID ascending.", s),
    ]
    story += [p("Configured Eco-Actions", s["sub"])]
    action_rows = [["Eco-action", "Points"],
        ["Recycled campus waste", "10"], ["Walked or cycled to class", "15"], ["Used a reusable bottle", "5"],
        ["Turned off unused devices", "8"], ["Joined a campus clean-up", "25"], ["Used public transport to campus", "12"],
    ]
    story.append(info_table(action_rows, [370, 146], font_size=8.3))
    story.append(p("Table 4. Point configuration from constants.py.", s["caption"]))

    # Testing
    story += heading("2.6. Testing and Sample Outputs", s)
    story.append(p("Testing was performed on 24 August 2026 using an isolated temporary data file and unique evidence files. This avoids altering the saved demonstration data. The test covers business rules directly through ChallengeStore, which is appropriate because the store contains the validation and scoring logic used by the interface.", s["body"]))
    test_rows = [["Test case", "Expected result", "Observed result"],
        ["Register a unique student", "Student is stored with the supplied ID.", "PASS - T001 registered."],
        ["Submit a valid claim", "Claim is pending with configured points.", "PASS - reusable bottle claim stored with 5 points."],
        ["Reuse the same image", "Second claim is rejected before save.", "PASS - ValueError raised for duplicate evidence."],
        ["Approve a claim", "Points update; status becomes Admin-Approved.", "PASS - score updated to 5; trust remained 100."],
        ["Reject a claim", "Status becomes Rejected; trust decreases by 20.", "PASS - trust changed from 100 to 80."],
    ]
    story.append(info_table(test_rows, [132, 204, 180], font_size=7.5))
    story.append(p("Table 5. Core business-rule test results: 5/5 passed.", s["caption"]))
    story.append(p("Sample test output", s["sub"]))
    story.append(p(
        "Saved demo dataset: 7 students, 22 claims, 18 approved, 4 rejected\nCore rule tests: registration=PASS, claim submission=PASS, duplicate evidence rejected=PASS, approval updates score=PASS, rejection lowers trust=PASS\nResult: 5 / 5 passed",
        s["code"],
    ))
    story.append(p("Current Saved Demonstration Data", s["sub"]))
    sample_rows = [["Metric", "Value"],
        ["Registered students", str(summary["students"])], ["Stored claims", str(summary["claims"])],
        ["Approved claims", str(summary["approved"])], ["Rejected claims", str(summary["rejected"])],
        ["Points currently awarded", str(summary["points"])], ["Most frequent recorded action", summary["top_action"]],
    ]
    story.append(info_table(sample_rows, [245, 271], font_size=8.2))
    story.append(p("Table 6. Summary computed from the current green_challenge_data.json file.", s["caption"]))
    story.append(PageBreak())

    # Discussion
    story += heading("2.7. Discussion and Limitations", s)
    story.append(p("The main design strength is the direct connection between behaviour, review, and feedback. Students receive a clear outcome rather than an informal acknowledgement, while administrators retain control over point allocation. Separating ChallengeStore from the user interface also makes the core logic easier to test and extend.", s["body"]))
    limitation_rows = [["Area", "Current limitation", "Suggested next step"],
        ["Security", "The administrator password is a demo constant in source code.", "Use hashed credentials and role-based authentication."],
        ["Storage", "JSON is local and suitable only for small, single-machine use.", "Move to SQLite or a managed database for concurrency and backups."],
        ["Evidence", "Hashing prevents exact file reuse but does not judge whether a photo proves the action.", "Add structured review rubrics, timestamps, or supervised verification."],
        ["Fairness", "Extra-scrutiny selection is probabilistic and may feel inconsistent to users.", "Use explicit, explainable criteria with a review audit trail."],
        ["Integration", "No institutional sign-in, notification, or carbon-calculation integration.", "Connect campus SSO, email alerts, and an approved impact methodology."],
        ["Accessibility", "The report does not verify full keyboard or screen-reader coverage of the desktop UI.", "Conduct accessibility testing with target users and document findings."],
    ]
    story.append(info_table(limitation_rows, [80, 215, 221], font_size=7.4))
    story.append(p("Table 8. Practical limitations and future improvements.", s["caption"]))
    story.append(callout("<b>Important interpretation:</b> points are a participation incentive, not a quantified measure of environmental impact. Any future claims about carbon savings should use a transparent methodology and verified activity data.", s))

    # Conclusion
    story += heading("2.8. Conclusion", s)
    story.append(p("University Green Challenge demonstrates a focused, maintainable approach to campus sustainability engagement. It provides a complete local workflow from registration through evidence submission, administrative review, point allocation, trust adjustments, analytics, and ranking. The project supports sustainability learning through visible, repeatable actions that align with SDG 11, SDG 12, and SDG 13.", s["body"]))
    story.append(p("The tested rules confirm that the implemented core flow protects unique registration, captures claims, blocks duplicate evidence, and applies approval or rejection outcomes correctly. The strongest next development priorities are secure authentication, multi-user storage, more explainable review criteria, and institution-level integrations.", s["body"]))

    # References
    story += heading("References", s)
    references = [
        "[1] United Nations Department of Economic and Social Affairs. Goal 12: Responsible Consumption and Production. https://sdgs.un.org/goals/goal12",
        "[2] United Nations Department of Economic and Social Affairs. Goal 13: Climate Action. https://sdgs.un.org/goals/goal13",
        "[3] United Nations Department of Economic and Social Affairs. Goal 11: Sustainable Cities and Communities. https://sdgs.un.org/goals/goal11",
        "[4] University Green Challenge project source code: green_challenge/app.py, store.py, models.py, persistence.py, constants.py, and university_green_challenge.py.",
        "[5] University Green Challenge saved demonstration data: green_challenge_data.json, accessed 24 August 2026.",
    ]
    for ref in references:
        story.append(p(ref, s["small"]))

    doc.build(story, onFirstPage=page_decor, onLaterPages=page_decor)
    print(OUT)


if __name__ == "__main__":
    build()
