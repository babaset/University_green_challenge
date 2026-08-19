"""CustomTkinter screens for the University Green Challenge app.

The layout follows the supplied Figma prototype: a wide emerald sign-in panel,
compact dashboard navigation, calm mint workspace, and soft elevated cards.
Business rules remain in :mod:`green_challenge.store` and controller actions in
:mod:`green_challenge.app`.
"""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import ttk

import customtkinter as ctk
from PIL import Image

from .constants import ECO_ACTIONS
from .styles import COLORS, FONT_FAMILY


LOGO_PATH = Path(__file__).resolve().parent / "assets" / "green_challenge_logo.png"


class ScreenRouter(ctk.CTkFrame):
    """A small frame router with the subset of Notebook behaviour the app uses."""

    def __init__(self, master, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self._pages: dict[int, dict[str, object]] = {}
        self._selected = None
        self._tab_changed_callback = None

    def add(self, page, text: str) -> None:
        self._pages[id(page)] = {"page": page, "text": text, "state": "normal"}
        page.place(relx=0, rely=0, relwidth=1, relheight=1)
        page.place_forget()

    def tab(self, page, state: str | None = None):
        record = self._pages[id(page)]
        if state is None:
            return record
        record["state"] = state
        if state == "hidden" and page is self._selected:
            page.place_forget()

    def select(self, page=None):
        if page is None:
            return str(self._selected) if self._selected is not None else ""
        record = self._pages[id(page)]
        if record["state"] == "hidden":
            return self.select()
        if self._selected is not None:
            self._selected.place_forget()
        self._selected = page
        page.place(relx=0, rely=0, relwidth=1, relheight=1)
        if self._tab_changed_callback is not None:
            self._tab_changed_callback(None)
        return str(page)

    def bind(self, sequence=None, func=None, add=None):  # noqa: A003 - Tk API name.
        if sequence == "<<NotebookTabChanged>>":
            self._tab_changed_callback = func
            return "router-tab-changed"
        return super().bind(sequence, func, add)


def build_interface(app) -> None:
    """Create the CustomTkinter shell, screens, and reusable navigation."""
    shell = ctk.CTkFrame(app.root, fg_color=COLORS["surface"], corner_radius=0)
    shell.pack(fill="both", expand=True)

    sidebar = ctk.CTkFrame(shell, width=440, fg_color=COLORS["sidebar"], corner_radius=0)
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)
    app.sidebar = sidebar

    workspace = ctk.CTkFrame(shell, fg_color=COLORS["surface"], corner_radius=0)
    workspace.pack(side="left", fill="both", expand=True)
    app.workspace = workspace
    app.notebook = ScreenRouter(workspace, fg_color=COLORS["surface"], corner_radius=0)
    app.notebook.pack(fill="both", expand=True)

    app.login_tab = ctk.CTkFrame(app.notebook, fg_color=COLORS["surface"], corner_radius=0)
    app.registration_tab = ctk.CTkFrame(app.notebook, fg_color=COLORS["surface"], corner_radius=0)
    app.claim_tab = ctk.CTkFrame(app.notebook, fg_color=COLORS["surface"], corner_radius=0)
    app.admin_tab = ctk.CTkFrame(app.notebook, fg_color=COLORS["surface"], corner_radius=0)
    app.analytics_tab = ctk.CTkFrame(app.notebook, fg_color=COLORS["surface"], corner_radius=0)
    app.leaderboard_tab = ctk.CTkFrame(app.notebook, fg_color=COLORS["surface"], corner_radius=0)
    app.history_tab = ctk.CTkFrame(app.notebook, fg_color=COLORS["surface"], corner_radius=0)
    for tab, title in (
        (app.login_tab, "Sign In"),
        (app.registration_tab, "Student Registration"),
        (app.claim_tab, "Student Dashboard"),
        (app.admin_tab, "Admin Panel"),
        (app.analytics_tab, "Challenge Analytics"),
        (app.leaderboard_tab, "Leaderboard"),
        (app.history_tab, "Claim History"),
    ):
        app.notebook.add(tab, title)

    build_sidebar(app)
    build_login_tab(app)
    build_registration_tab(app)
    build_claim_tab(app)
    build_admin_tab(app)
    build_analytics_tab(app)
    build_leaderboard_tab(app)
    build_history_tab(app)

    app.feature_tabs = (app.registration_tab, app.claim_tab, app.admin_tab, app.analytics_tab, app.leaderboard_tab, app.history_tab)
    app.notebook.bind("<<NotebookTabChanged>>", app.update_navigation_active)


def build_sidebar(app) -> None:
    """Build both the generous login hero and compact dashboard navigation."""
    sidebar = app.sidebar
    brand_row = ctk.CTkFrame(sidebar, fg_color="transparent")
    brand_row.pack(anchor="w", fill="x", padx=18, pady=(20, 18))
    create_leaf_mark(brand_row, 34, COLORS["sidebar"]).pack(side="left", padx=(0, 9))
    brand_text = ctk.CTkFrame(brand_row, fg_color="transparent")
    brand_text.pack(side="left")
    app.sidebar_brand = ctk.CTkLabel(
        brand_text, text="University", text_color="#FFFFFF", font=(FONT_FAMILY, 12, "bold"), anchor="w"
    )
    app.sidebar_brand.pack(anchor="w")
    app.sidebar_subtitle = ctk.CTkLabel(
        brand_text, text="Green Challenge", text_color=COLORS["sidebar_muted"], font=(FONT_FAMILY, 10), anchor="w"
    )
    app.sidebar_subtitle.pack(anchor="w")

    app.session_status_var = tk.StringVar(value="Not signed in")
    app.sidebar_status_label = ctk.CTkLabel(
        sidebar,
        textvariable=app.session_status_var,
        text_color=COLORS["sidebar_muted"],
        font=(FONT_FAMILY, 10),
        justify="left",
        anchor="w",
        wraplength=155,
    )
    app.sidebar_status_label.pack(anchor="w", fill="x", padx=18, pady=(0, 14))

    app.navigation_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
    app.navigation_frame.pack(fill="both", expand=True, padx=10)
    build_navigation(app)

    app.sidebar_separator = ctk.CTkFrame(sidebar, height=1, fg_color="#1B6348", corner_radius=0)
    app.sidebar_separator.pack(fill="x", padx=18, pady=(8, 12))
    app.logout_button = ctk.CTkButton(
        sidebar,
        text="↪  Log Out",
        height=36,
        corner_radius=7,
        fg_color="transparent",
        hover_color="#145D40",
        text_color=COLORS["sidebar_text"],
        font=(FONT_FAMILY, 11, "bold"),
        anchor="w",
        command=app.show_login_screen,
        state="disabled",
    )
    app.logout_button.pack(fill="x", padx=10, pady=(0, 16))
    build_login_hero(app)


def build_navigation(app) -> None:
    """Build role-aware sidebar links."""
    app.navigation_items = []
    for icon, label, tab in (
        ("⌂", "My Dashboard", app.claim_tab),
        ("♜", "Leaderboard", app.leaderboard_tab),
        ("◴", "Claim History", app.history_tab),
        ("＋", "Register Student", app.registration_tab),
        ("⌕", "Review Claims", app.admin_tab),
        ("▥", "Analytics", app.analytics_tab),
    ):
        button = ctk.CTkButton(
            app.navigation_frame,
            text=f"{icon}  {label}",
            height=38,
            corner_radius=7,
            fg_color="transparent",
            hover_color="#145D40",
            text_color=COLORS["sidebar_text"],
            font=(FONT_FAMILY, 11, "bold"),
            anchor="w",
            command=lambda target=tab: app.notebook.select(target),
        )
        app.navigation_items.append((tab, button))


def style_navigation_button(button, active: bool) -> None:
    """Apply the Figma active-link treatment to one CTk navigation button."""
    button.configure(
        fg_color=COLORS["primary"] if active else "transparent",
        hover_color=COLORS["primary_hover"] if active else "#145D40",
        text_color="#FFFFFF" if active else COLORS["sidebar_text"],
    )


def build_login_tab(app) -> None:
    """Build the 340-pixel Figma login form inside the mint workspace."""
    login_shell = ctk.CTkFrame(app.login_tab, fg_color=COLORS["surface"], corner_radius=0)
    login_shell.pack(fill="both", expand=True)
    login_panel = ctk.CTkFrame(login_shell, width=340, height=360, fg_color="transparent", corner_radius=0)
    login_panel.place(relx=0.5, rely=0.5, anchor="center")
    login_panel.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(
        login_panel, text="Welcome back", text_color=COLORS["text"], font=(FONT_FAMILY, 22, "bold"), anchor="w"
    ).grid(row=0, column=0, sticky="ew")
    ctk.CTkLabel(
        login_panel,
        text="Sign in to your account to continue",
        text_color="#4B5563",
        font=(FONT_FAMILY, 13),
        anchor="w",
    ).grid(row=1, column=0, sticky="ew", pady=(3, 26))

    toggle = ctk.CTkFrame(login_panel, fg_color="transparent", corner_radius=0)
    toggle.grid(row=2, column=0, sticky="ew", pady=(0, 24))
    toggle.grid_columnconfigure((0, 1), weight=1)
    app.student_role_button = ctk.CTkButton(
        toggle,
        text="🎓  Student",
        height=34,
        corner_radius=7,
        font=(FONT_FAMILY, 13, "bold"),
        command=lambda: show_login_role(app, "student"),
    )
    app.student_role_button.grid(row=0, column=0, sticky="ew")
    app.admin_role_button = ctk.CTkButton(
        toggle,
        text="🔐  Admin",
        height=34,
        corner_radius=7,
        font=(FONT_FAMILY, 13, "bold"),
        command=lambda: show_login_role(app, "admin"),
    )
    app.admin_role_button.grid(row=0, column=1, sticky="ew")

    app.login_form_area = ctk.CTkFrame(login_panel, fg_color="transparent", corner_radius=0)
    app.login_form_area.grid(row=3, column=0, sticky="ew")
    app.login_form_area.grid_columnconfigure(0, weight=1)
    app.student_login_form = ctk.CTkFrame(app.login_form_area, fg_color="transparent", corner_radius=0)
    app.student_login_form.grid_columnconfigure(0, weight=1)
    ctk.CTkLabel(app.student_login_form, text="Student ID", text_color="#374151", font=(FONT_FAMILY, 12, "bold"), anchor="w").grid(
        row=0, column=0, sticky="ew", pady=(0, 7)
    )
    app.student_login_id_entry = ctk.CTkEntry(
        app.student_login_form,
        height=39,
        corner_radius=8,
        fg_color=COLORS["field"],
        border_color=COLORS["border"],
        text_color="#1F2937",
        placeholder_text="e.g. STU-2034",
        placeholder_text_color="#9CA3AF",
        font=(FONT_FAMILY, 13),
    )
    app.student_login_id_entry.grid(row=1, column=0, sticky="ew")
    app.student_login_id_entry.bind("<Return>", lambda _event: app.login_student())
    ctk.CTkButton(
        app.student_login_form,
        text="Sign In →",
        height=43,
        corner_radius=8,
        fg_color=COLORS["primary"],
        hover_color=COLORS["primary_hover"],
        font=(FONT_FAMILY, 14, "bold"),
        command=app.login_student,
    ).grid(row=2, column=0, sticky="ew", pady=(18, 0))

    app.admin_login_form = ctk.CTkFrame(app.login_form_area, fg_color="transparent", corner_radius=0)
    app.admin_login_form.grid_columnconfigure(0, weight=1)
    ctk.CTkLabel(app.admin_login_form, text="Admin password", text_color="#374151", font=(FONT_FAMILY, 12, "bold"), anchor="w").grid(
        row=0, column=0, sticky="ew", pady=(0, 7)
    )
    app.admin_password_entry = ctk.CTkEntry(
        app.admin_login_form,
        height=39,
        corner_radius=8,
        fg_color=COLORS["field"],
        border_color=COLORS["border"],
        text_color="#1F2937",
        placeholder_text="Enter administrator password",
        placeholder_text_color="#9CA3AF",
        show="•",
        font=(FONT_FAMILY, 13),
    )
    app.admin_password_entry.grid(row=1, column=0, sticky="ew")
    app.admin_password_entry.bind("<Return>", lambda _event: app.login_admin())
    ctk.CTkButton(
        app.admin_login_form,
        text="Admin Login →",
        height=43,
        corner_radius=8,
        fg_color=COLORS["primary"],
        hover_color=COLORS["primary_hover"],
        font=(FONT_FAMILY, 14, "bold"),
        command=app.login_admin,
    ).grid(row=2, column=0, sticky="ew", pady=(18, 0))

    demo = ctk.CTkFrame(login_panel, fg_color=COLORS["mint"], border_width=1, border_color="#CBE7D4", corner_radius=8)
    demo.grid(row=4, column=0, sticky="ew", pady=(20, 0))
    app.login_demo_var = tk.StringVar(value="Demo: Enter your registered Student ID to continue.")
    ctk.CTkLabel(
        demo,
        textvariable=app.login_demo_var,
        text_color=COLORS["primary"],
        font=(FONT_FAMILY, 11),
        justify="left",
        anchor="w",
        wraplength=310,
    ).pack(fill="x", padx=14, pady=10)
    show_login_role(app, "student")


def build_login_hero(app) -> None:
    """Build the tall decorative Figma panel shown on the sign-in screen."""
    app.login_hero = ctk.CTkFrame(app.sidebar, fg_color=COLORS["sidebar"], corner_radius=0)
    decoration = tk.Canvas(
        app.login_hero,
        background=COLORS["sidebar"],
        highlightthickness=0,
        bd=0,
        width=440,
        height=680,
    )
    decoration.place(x=0, y=0, relwidth=1, relheight=1)
    decoration.create_oval(-160, -100, 140, 200, outline="#1A704E", width=2)
    decoration.create_oval(275, 4, 430, 159, outline="#1A704E", width=2)
    decoration.create_oval(154, 620, 440, 900, outline="#1A704E", width=2)
    content = ctk.CTkFrame(app.login_hero, fg_color="transparent", corner_radius=0)
    content.pack(fill="both", expand=True, padx=48)
    create_leaf_mark(content, 116, COLORS["sidebar"]).pack(pady=(125, 38))
    ctk.CTkLabel(
        content,
        text="University\nGreen Challenge",
        text_color="#FFFFFF",
        font=(FONT_FAMILY, 24, "bold"),
        justify="center",
    ).pack()
    ctk.CTkLabel(
        content,
        text="Track your eco-friendly actions, earn points, and compete with fellow students to build a greener campus.",
        text_color=COLORS["sidebar_muted"],
        font=(FONT_FAMILY, 13),
        justify="center",
        wraplength=270,
    ).pack(pady=(16, 34))
    actions = ctk.CTkFrame(content, fg_color="transparent", corner_radius=0)
    actions.pack()
    for icon, label in (("♻", "Recycled\ncampus waste"), ("♧", "Walked or\ncycled to class"), ("▯", "Used a reusable\nbottle")):
        item = ctk.CTkFrame(actions, width=84, fg_color="transparent", corner_radius=0)
        item.pack(side="left", padx=6)
        ctk.CTkLabel(
            item,
            text=icon,
            width=38,
            height=38,
            corner_radius=7,
            fg_color="#176243",
            text_color=COLORS["mint_dark"],
            font=(FONT_FAMILY, 18, "bold"),
        ).pack()
        ctk.CTkLabel(
            item,
            text=label,
            text_color=COLORS["sidebar_muted"],
            font=(FONT_FAMILY, 10),
            justify="center",
        ).pack(pady=(6, 0))


def create_leaf_mark(parent, size: int, background: str) -> ctk.CTkLabel:
    """Return the supplied University Green Challenge logo at the requested size."""
    with Image.open(LOGO_PATH) as source:
        logo = source.convert("RGBA")
    height = round(size * logo.height / logo.width)
    image = ctk.CTkImage(light_image=logo, dark_image=logo, size=(size, height))
    label = ctk.CTkLabel(parent, text="", image=image, width=size, height=height, fg_color="transparent")
    # CTkImage must stay referenced for the image to remain visible in Tk.
    label.logo_image = image
    return label


def show_login_role(app, role: str) -> None:
    """Switch sign-in fields and active role treatment."""
    app.student_login_form.grid_forget()
    app.admin_login_form.grid_forget()
    is_student = role == "student"
    active_form = app.student_login_form if is_student else app.admin_login_form
    active_form.grid(row=0, column=0, sticky="ew")
    active = {"fg_color": COLORS["card"], "hover_color": "#F3F4F6", "text_color": COLORS["text"]}
    inactive = {"fg_color": "transparent", "hover_color": "#E0F0E6", "text_color": "#9CA3AF"}
    app.student_role_button.configure(**(active if is_student else inactive))
    app.admin_role_button.configure(**(inactive if is_student else active))
    app.login_demo_var.set(
        "Demo: Enter your registered Student ID to continue."
        if is_student
        else "Demo password: admin123. Use this role to register students and review claims."
    )


def set_login_sidebar(app) -> None:
    """Expand the left side to the 440-pixel Figma sign-in hero."""
    app.sidebar.configure(width=440)
    app.sidebar_status_label.pack_forget()
    app.navigation_frame.pack_forget()
    app.sidebar_separator.pack_forget()
    app.logout_button.pack_forget()
    app.login_hero.pack(fill="both", expand=True)


def set_dashboard_sidebar(app) -> None:
    """Return to the compact navigation sidebar used by dashboard screens."""
    app.sidebar.configure(width=192)
    app.login_hero.pack_forget()
    app.sidebar_status_label.pack(anchor="w", fill="x", padx=18, pady=(0, 14))
    app.navigation_frame.pack(fill="both", expand=True, padx=10)
    app.sidebar_separator.pack(fill="x", padx=18, pady=(8, 12))
    app.logout_button.pack(fill="x", padx=10, pady=(0, 16))


def build_registration_tab(app) -> None:
    page = page_container(app.registration_tab)
    add_page_heading(page, "Register Student", "Add a student to the University Green Challenge.")
    card = card_frame(page)
    card.pack(anchor="nw", fill="x", pady=(18, 0))
    card.grid_columnconfigure(1, weight=1)
    form_label(card, "Student name").grid(row=0, column=0, sticky="w", padx=(20, 16), pady=(20, 8))
    app.name_entry = input_field(card, placeholder="e.g. Priya Sharma")
    app.name_entry.grid(row=0, column=1, sticky="ew", padx=(0, 20), pady=(20, 8))
    form_label(card, "Student ID").grid(row=1, column=0, sticky="w", padx=(20, 16), pady=8)
    app.id_entry = input_field(card, placeholder="e.g. STU-2034")
    app.id_entry.grid(row=1, column=1, sticky="ew", padx=(0, 20), pady=8)
    app.register_button = primary_button(card, "＋  Register Student", app.register_student, width=190)
    app.register_button.grid(row=2, column=1, sticky="w", padx=(0, 20), pady=(12, 20))
    ctk.CTkLabel(
        page,
        text="Every new student begins with 0 points and a trust score of 100.",
        text_color=COLORS["muted"],
        font=(FONT_FAMILY, 11),
    ).pack(anchor="w", pady=(13, 0))


def build_claim_tab(app) -> None:
    page = page_container(app.claim_tab)
    header = ctk.CTkFrame(page, fg_color="transparent", corner_radius=0)
    header.pack(fill="x")
    heading = ctk.CTkFrame(header, fg_color="transparent", corner_radius=0)
    heading.pack(side="left")
    ctk.CTkLabel(heading, text="Student Dashboard", text_color=COLORS["text"], font=(FONT_FAMILY, 18, "bold"), anchor="w").pack(anchor="w")
    ctk.CTkLabel(heading, text="Track and submit your eco-actions", text_color=COLORS["muted"], font=(FONT_FAMILY, 11), anchor="w").pack(anchor="w", pady=(1, 0))

    app.student_points_var = tk.StringVar(value="—")
    app.student_trust_var = tk.StringVar(value="—")
    app.student_rank_var = tk.StringVar(value="—")
    metrics = ctk.CTkFrame(header, fg_color="transparent", corner_radius=0)
    metrics.pack(side="right")
    add_metric_card(metrics, 0, "⚡  Total Points", app.student_points_var)
    add_metric_card(metrics, 1, "♢  Trust Score", app.student_trust_var)
    add_metric_card(metrics, 2, "♛  Rank", app.student_rank_var)

    tabs = ctk.CTkFrame(page, fg_color="transparent", corner_radius=0)
    tabs.pack(anchor="w", pady=(22, 14))
    primary_button(tabs, "▣  Submit Claim", lambda: None, width=128, height=33).pack(side="left")
    ctk.CTkButton(
        tabs,
        text="◷  Claim History",
        width=126,
        height=33,
        corner_radius=7,
        fg_color="transparent",
        hover_color="#DFF1E5",
        text_color="#4B5563",
        font=(FONT_FAMILY, 11, "bold"),
        command=lambda: app.notebook.select(app.history_tab),
    ).pack(side="left", padx=(8, 0))

    content = ctk.CTkFrame(page, fg_color="transparent", corner_radius=0)
    content.pack(fill="both", expand=True)
    form = card_frame(content)
    form.pack(side="left", fill="both", expand=True, padx=(0, 18))
    form.grid_columnconfigure(0, weight=1)
    ctk.CTkLabel(form, text="Submit Eco-Action Claim", text_color=COLORS["text"], font=(FONT_FAMILY, 15, "bold"), anchor="w").grid(
        row=0, column=0, sticky="ew", padx=20, pady=(19, 16)
    )

    # The student selector remains in the controller, but is intentionally
    # hidden: the prototype derives the student from the signed-in session.
    app.claim_student_var = tk.StringVar()
    app.claim_student_combo = ctk.CTkComboBox(form, values=[], variable=app.claim_student_var)
    form_label(form, "Eco-Action").grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 6))
    app.action_var = tk.StringVar(value="Select an eco-action…")
    app.action_display_to_name = {app.action_display_name(action): action for action in ECO_ACTIONS}
    app.action_combo = ctk.CTkComboBox(
        form,
        values=["Select an eco-action…", *app.action_display_to_name],
        variable=app.action_var,
        height=37,
        corner_radius=8,
        fg_color=COLORS["field"],
        border_color=COLORS["border"],
        button_color="#DCEFE3",
        button_hover_color="#C5E2D0",
        dropdown_fg_color=COLORS["card"],
        dropdown_hover_color=COLORS["mint"],
        text_color="#374151",
        font=(FONT_FAMILY, 12),
    )
    app.action_combo.grid(row=2, column=0, sticky="ew", padx=20)

    form_label(form, "Photo Evidence").grid(row=3, column=0, sticky="ew", padx=20, pady=(14, 6))
    app.proof_path_var = tk.StringVar()
    app.proof_upload_button = ctk.CTkButton(
        form,
        text="⇧\nDrag & drop or click to upload",
        height=82,
        corner_radius=8,
        fg_color=COLORS["field"],
        hover_color="#F0F7F2",
        border_width=1,
        border_color="#DCE4DF",
        text_color="#9CA3AF",
        font=(FONT_FAMILY, 11),
        command=app.choose_proof_photo,
    )
    app.proof_upload_button.grid(row=4, column=0, sticky="ew", padx=20)
    app.proof_file_label = ctk.CTkLabel(form, textvariable=app.proof_path_var, text_color=COLORS["muted"], font=(FONT_FAMILY, 10), anchor="w")
    app.proof_file_label.grid(row=5, column=0, sticky="ew", padx=20, pady=(4, 0))

    form_label(form, "Description").grid(row=6, column=0, sticky="ew", padx=20, pady=(12, 6))
    app.proof_description_entry = ctk.CTkTextbox(
        form,
        height=62,
        corner_radius=8,
        fg_color=COLORS["field"],
        border_width=1,
        border_color=COLORS["border"],
        text_color="#374151",
        font=(FONT_FAMILY, 12),
        wrap="word",
    )
    app.proof_description_entry.grid(row=7, column=0, sticky="ew", padx=20)
    app.proof_description_entry.insert("0.0", "")
    app.submit_button = primary_button(form, "Submit Claim →", app.submit_claim, height=39)
    app.submit_button.grid(row=8, column=0, sticky="ew", padx=20, pady=(16, 20))

    side = card_frame(content, width=206)
    side.pack(side="right", fill="y")
    side.pack_propagate(False)
    ctk.CTkLabel(side, text="♧  Points Guide", text_color=COLORS["text"], font=(FONT_FAMILY, 13, "bold"), anchor="w").pack(
        fill="x", padx=17, pady=(17, 10)
    )
    for action, points in ECO_ACTIONS.items():
        line = ctk.CTkFrame(side, fg_color="transparent", corner_radius=0)
        line.pack(fill="x", padx=17, pady=5)
        ctk.CTkLabel(
            line,
            text=app.action_display_name(action),
            text_color="#4B5563",
            font=(FONT_FAMILY, 10),
            justify="left",
            anchor="w",
            wraplength=128,
        ).pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(line, text=f"+{points}", text_color=COLORS["gold"], font=(FONT_FAMILY, 10, "bold")).pack(side="right")
    current = ctk.CTkFrame(side, fg_color=COLORS["mint"], corner_radius=8)
    current.pack(fill="x", padx=17, pady=(14, 17))
    ctk.CTkLabel(current, text="Your current points", text_color=COLORS["muted"], font=(FONT_FAMILY, 9)).pack(pady=(9, 0))
    ctk.CTkLabel(current, textvariable=app.student_points_var, text_color=COLORS["primary"], font=(FONT_FAMILY, 19, "bold")).pack(pady=(0, 8))


def build_admin_tab(app) -> None:
    page = page_container(app.admin_tab)
    header = ctk.CTkFrame(page, fg_color="transparent", corner_radius=0)
    header.pack(fill="x")
    heading = ctk.CTkFrame(header, fg_color="transparent", corner_radius=0)
    heading.pack(side="left")
    ctk.CTkLabel(heading, text="Admin Panel", text_color=COLORS["text"], font=(FONT_FAMILY, 19, "bold"), anchor="w").pack(anchor="w")
    ctk.CTkLabel(heading, text="Manage students and review eco-action claims.", text_color=COLORS["muted"], font=(FONT_FAMILY, 11), anchor="w").pack(anchor="w", pady=(2, 0))
    app.pending_count_var = tk.StringVar(value="0")
    app.student_count_var = tk.StringVar(value="0")
    metrics = ctk.CTkFrame(header, fg_color="transparent", corner_radius=0)
    metrics.pack(side="right")
    add_metric_card(metrics, 0, "Pending Claims", app.pending_count_var)
    add_metric_card(metrics, 1, "Total Students", app.student_count_var)

    filters = ctk.CTkFrame(page, fg_color="transparent", corner_radius=0)
    filters.pack(fill="x", pady=(18, 0))
    filters.grid_columnconfigure(0, weight=1)
    form_label(filters, "Search").grid(row=0, column=0, sticky="w")
    form_label(filters, "Status").grid(row=0, column=1, sticky="w", padx=(10, 0))
    form_label(filters, "Eco-action").grid(row=0, column=2, sticky="w", padx=(10, 0))
    app.pending_search_var = tk.StringVar()
    app.pending_search_entry = ctk.CTkEntry(
        filters,
        textvariable=app.pending_search_var,
        height=34,
        corner_radius=8,
        fg_color=COLORS["field"],
        border_color=COLORS["border"],
        placeholder_text="Name, ID, action, or status",
        font=(FONT_FAMILY, 11),
    )
    app.pending_search_entry.grid(row=1, column=0, sticky="ew", pady=(5, 0))
    app.pending_search_var.trace_add("write", lambda *_args: app.refresh_pending_queue())
    app.pending_status_filter = tk.StringVar(value="All statuses")
    app.pending_status_combo = ctk.CTkComboBox(
        filters,
        values=["All statuses", "Pending Review", "Under Review", "Needs More Evidence"],
        variable=app.pending_status_filter,
        width=155,
        height=34,
        corner_radius=8,
        fg_color=COLORS["field"],
        border_color=COLORS["border"],
        button_color="#DCEFE3",
        button_hover_color="#C5E2D0",
        dropdown_fg_color=COLORS["card"],
        command=lambda _choice: app.refresh_pending_queue(),
        font=(FONT_FAMILY, 11),
    )
    app.pending_status_combo.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=(5, 0))
    app.pending_action_filter = tk.StringVar(value="All actions")
    app.pending_action_combo = ctk.CTkComboBox(
        filters,
        values=["All actions", *ECO_ACTIONS],
        variable=app.pending_action_filter,
        width=190,
        height=34,
        corner_radius=8,
        fg_color=COLORS["field"],
        border_color=COLORS["border"],
        button_color="#DCEFE3",
        button_hover_color="#C5E2D0",
        dropdown_fg_color=COLORS["card"],
        command=lambda _choice: app.refresh_pending_queue(),
        font=(FONT_FAMILY, 11),
    )
    app.pending_action_combo.grid(row=1, column=2, sticky="ew", padx=(10, 0), pady=(5, 0))
    secondary_button(filters, "Clear", app.clear_pending_filters, width=80).grid(row=1, column=3, padx=(10, 0), pady=(5, 0))

    ctk.CTkLabel(page, text="Pending Claims", text_color=COLORS["text"], font=(FONT_FAMILY, 15, "bold"), anchor="w").pack(anchor="w", pady=(22, 9))
    table_card = card_frame(page)
    table_card.pack(fill="both", expand=True)
    tree_frame = ctk.CTkFrame(table_card, fg_color="transparent", corner_radius=0)
    tree_frame.pack(fill="both", expand=True, padx=12, pady=12)
    columns = ("student", "student_id", "action", "status", "evidence", "points", "trust")
    app.pending_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse", style="Green.Treeview")
    headings = {"student": "Student", "student_id": "Student ID", "action": "Claimed eco-action", "status": "Review status", "evidence": "Photo proof", "points": "Points", "trust": "Current trust"}
    app.pending_headings = headings
    widths = {"student": 125, "student_id": 90, "action": 160, "status": 135, "evidence": 110, "points": 65, "trust": 165}
    for column in columns:
        app.pending_tree.heading(column, text=headings[column], command=lambda current=column: app.sort_pending_queue(current))
        app.pending_tree.column(column, width=widths[column], minwidth=60, anchor="center" if column in ("points", "trust") else "w")
    app.pending_tree.pack(side="left", fill="both", expand=True)
    add_scrollbars(tree_frame, app.pending_tree)
    app.pending_tree.bind("<<TreeviewSelect>>", app.show_selected_evidence)
    app.pending_tree.tag_configure("status_pending", background=COLORS["pale_gold"], foreground="#6E4A00")
    app.pending_tree.tag_configure("status_in_review", background="#EAF2FF", foreground="#1D4E89")
    app.pending_tree.tag_configure("status_needs_evidence", background=COLORS["pale_red"], foreground=COLORS["red"])
    app.pending_empty_label = ctk.CTkLabel(table_card, text="♧ No pending requests — every submitted claim has been reviewed.", text_color=COLORS["muted"], font=(FONT_FAMILY, 11))

    evidence = card_frame(page)
    evidence.pack(fill="x", pady=(12, 0))
    app.evidence_details_var = tk.StringVar(value="Select a pending request to view its proof details.")
    ctk.CTkLabel(evidence, textvariable=app.evidence_details_var, text_color="#4B5563", font=(FONT_FAMILY, 10), justify="left", anchor="w", wraplength=660).pack(side="left", fill="x", expand=True, padx=15, pady=11)
    app.open_proof_button = secondary_button(evidence, "View Evidence", app.open_selected_proof, width=132)
    app.open_proof_button.pack(side="right", padx=14, pady=11)
    app.open_proof_button.configure(state="disabled")

    note_card = card_frame(page)
    note_card.pack(fill="x", pady=(12, 0))
    form_label(note_card, "Admin note / reason (saved with the next review action)").pack(anchor="w", padx=15, pady=(12, 6))
    app.admin_note_entry = ctk.CTkTextbox(
        note_card,
        height=54,
        corner_radius=8,
        fg_color=COLORS["field"],
        border_width=1,
        border_color=COLORS["border"],
        text_color="#374151",
        font=(FONT_FAMILY, 11),
        wrap="word",
    )
    app.admin_note_entry.pack(fill="x", padx=15, pady=(0, 13))

    actions = ctk.CTkFrame(page, fg_color="transparent", corner_radius=0)
    actions.pack(fill="x", pady=(12, 0))
    app.approve_button = primary_button(actions, "✓  Approve Selected", lambda: app.review_request("approve"), width=175)
    app.approve_button.pack(side="left")
    app.reject_button = ctk.CTkButton(actions, text="✕  Reject Selected", width=160, height=36, corner_radius=8, fg_color="#B7791F", hover_color="#915C0F", font=(FONT_FAMILY, 11, "bold"), command=lambda: app.review_request("reject"))
    app.reject_button.pack(side="left", padx=(10, 0))
    secondary_button(actions, "Mark Under Review", lambda: app.update_request_status("Under Review"), width=155).pack(side="left", padx=(10, 0))
    secondary_button(actions, "Request Evidence", lambda: app.update_request_status("Needs More Evidence"), width=155).pack(side="left", padx=(10, 0))
    app.delete_claim_button = ctk.CTkButton(
        actions,
        text="Delete",
        width=82,
        height=36,
        corner_radius=8,
        fg_color=COLORS["red"],
        hover_color="#8E1D14",
        font=(FONT_FAMILY, 11, "bold"),
        command=app.delete_selected_request,
    )
    app.delete_claim_button.pack(side="right")

    # Keep the review controls visible even when the queue has many rows.
    note_card.pack_forget()
    note_card.pack(fill="x", pady=(0, 12), before=table_card)
    actions.pack_forget()
    actions.pack(fill="x", pady=(0, 12), before=table_card)


def build_analytics_tab(app) -> None:
    """Build a read-only dashboard for challenge-wide claim statistics."""
    page = page_container(app.analytics_tab)
    add_page_heading(page, "Challenge Analytics", "A live overview of claim outcomes and participation.")

    app.analytics_total_claims_var = tk.StringVar(value="0")
    app.analytics_approved_var = tk.StringVar(value="0")
    app.analytics_pending_var = tk.StringVar(value="0")
    app.analytics_points_var = tk.StringVar(value="0")
    metrics = ctk.CTkFrame(page, fg_color="transparent", corner_radius=0)
    metrics.pack(anchor="w", pady=(18, 0))
    add_metric_card(metrics, 0, "Total Claims", app.analytics_total_claims_var)
    add_metric_card(metrics, 1, "Approved", app.analytics_approved_var)
    add_metric_card(metrics, 2, "In Progress", app.analytics_pending_var)
    add_metric_card(metrics, 3, "Points Awarded", app.analytics_points_var)

    app.analytics_summary_var = tk.StringVar(value="Approval rate: 0%   •   Rejected: 0   •   Most common action: No claims yet")
    ctk.CTkLabel(
        page,
        textvariable=app.analytics_summary_var,
        text_color=COLORS["muted"],
        font=(FONT_FAMILY, 11),
        anchor="w",
        justify="left",
        wraplength=740,
    ).pack(anchor="w", fill="x", pady=(20, 10))

    chart_card = card_frame(page)
    chart_card.pack(fill="both", expand=True)
    ctk.CTkLabel(chart_card, text="Claim outcomes", text_color=COLORS["text"], font=(FONT_FAMILY, 14, "bold"), anchor="w").pack(
        anchor="w", padx=16, pady=(15, 4)
    )
    app.analytics_chart = tk.Canvas(
        chart_card,
        height=245,
        background=COLORS["card"],
        highlightthickness=0,
        bd=0,
    )
    app.analytics_chart.pack(fill="both", expand=True, padx=15, pady=(0, 15))
    app.analytics_chart.bind("<Configure>", lambda _event: app.draw_analytics_chart())


def build_leaderboard_tab(app) -> None:
    page = page_container(app.leaderboard_tab)
    add_page_heading(page, "Leaderboard", "Green champions ranked by points and trust score.")
    table_card = card_frame(page)
    table_card.pack(fill="both", expand=True, pady=(18, 0))
    tree_frame = ctk.CTkFrame(table_card, fg_color="transparent", corner_radius=0)
    tree_frame.pack(fill="both", expand=True, padx=12, pady=12)
    columns = ("rank", "name", "student_id", "points", "trust")
    app.leaderboard_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", style="Green.Treeview")
    headings = {"rank": "Rank", "name": "Student", "student_id": "Student ID", "points": "Points earned", "trust": "Trust progress"}
    widths = {"rank": 90, "name": 220, "student_id": 125, "points": 125, "trust": 250}
    for column in columns:
        app.leaderboard_tree.heading(column, text=headings[column])
        app.leaderboard_tree.column(column, width=widths[column], minwidth=70, anchor="center" if column != "name" else "w")
    app.leaderboard_tree.pack(side="left", fill="both", expand=True)
    add_scrollbars(tree_frame, app.leaderboard_tree)
    app.leaderboard_tree.tag_configure("trust_high", background=COLORS["mint"])
    app.leaderboard_tree.tag_configure("trust_medium", background=COLORS["pale_gold"])
    app.leaderboard_tree.tag_configure("trust_low", background=COLORS["pale_red"])
    app.leaderboard_empty_label = ctk.CTkLabel(table_card, text="🌱 No leaderboard entries yet. Register the first green champion to begin.", text_color=COLORS["muted"], font=(FONT_FAMILY, 11))


def build_history_tab(app) -> None:
    page = page_container(app.history_tab)
    add_page_heading(page, "Claim History", "Review each student's sustainability journey.")
    chooser = ctk.CTkFrame(page, fg_color="transparent", corner_radius=0)
    chooser.pack(fill="x", pady=(14, 8))
    form_label(chooser, "Student").pack(side="left")
    app.history_student_var = tk.StringVar()
    app.history_student_combo = ctk.CTkComboBox(
        chooser,
        values=[],
        variable=app.history_student_var,
        width=280,
        height=36,
        corner_radius=8,
        fg_color=COLORS["field"],
        border_color=COLORS["border"],
        button_color="#DCEFE3",
        button_hover_color="#C5E2D0",
        dropdown_fg_color=COLORS["card"],
        command=lambda _choice: app.get_student_history(),
    )
    app.history_student_combo.pack(side="left", padx=(10, 0))
    secondary_button(chooser, "View History", app.get_student_history, width=120).pack(side="left", padx=(10, 0))
    app.delete_approved_claim_button = ctk.CTkButton(
        chooser,
        text="Delete Approved Action",
        width=170,
        height=36,
        corner_radius=8,
        fg_color=COLORS["red"],
        hover_color="#8E1D14",
        font=(FONT_FAMILY, 11, "bold"),
        command=app.delete_selected_approved_claim,
        state="disabled",
    )
    app.delete_approved_claim_button.pack(side="right")
    app.history_summary = ctk.CTkLabel(page, text="🌱 Select a student to view their sustainability journey.", text_color=COLORS["muted"], font=(FONT_FAMILY, 11), anchor="w")
    app.history_summary.pack(anchor="w", pady=(6, 8))
    table_card = card_frame(page)
    table_card.pack(fill="both", expand=True)
    tree_frame = ctk.CTkFrame(table_card, fg_color="transparent", corner_radius=0)
    tree_frame.pack(fill="both", expand=True, padx=12, pady=12)
    columns = ("number", "action", "points", "status", "submitted", "reviewed", "note", "evidence")
    app.history_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse", style="Green.Treeview")
    headings = {"number": "#", "action": "Eco-action", "points": "Points", "status": "Status", "submitted": "Submitted", "reviewed": "Reviewed", "note": "Admin note", "evidence": "Photo proof"}
    widths = {"number": 55, "action": 220, "points": 85, "status": 155, "submitted": 135, "reviewed": 135, "note": 240, "evidence": 180}
    for column in columns:
        app.history_tree.heading(column, text=headings[column])
        app.history_tree.column(column, width=widths[column], minwidth=65, anchor="center" if column != "action" else "w")
    app.history_tree.pack(side="left", fill="both", expand=True)
    add_scrollbars(tree_frame, app.history_tree)
    app.history_tree.tag_configure("status_pending", background=COLORS["pale_gold"], foreground="#6E4A00")
    app.history_tree.tag_configure("status_in_review", background="#EAF2FF", foreground="#1D4E89")
    app.history_tree.tag_configure("status_needs_evidence", background=COLORS["pale_red"], foreground=COLORS["red"])
    app.history_tree.tag_configure("status_approved", background=COLORS["mint"], foreground="#145A37")
    app.history_tree.tag_configure("status_rejected", background=COLORS["pale_red"], foreground="#962019")


def page_container(parent):
    page = ctk.CTkFrame(parent, fg_color=COLORS["surface"], corner_radius=0)
    page.pack(fill="both", expand=True, padx=20, pady=18)
    return page


def add_page_heading(parent, title: str, subtitle: str) -> None:
    ctk.CTkLabel(parent, text=title, text_color=COLORS["text"], font=(FONT_FAMILY, 20, "bold"), anchor="w").pack(anchor="w")
    ctk.CTkLabel(parent, text=subtitle, text_color=COLORS["muted"], font=(FONT_FAMILY, 11), anchor="w").pack(anchor="w", pady=(2, 0))


def form_label(parent, text: str):
    return ctk.CTkLabel(parent, text=text, text_color="#374151", font=(FONT_FAMILY, 12, "bold"), anchor="w")


def card_frame(parent, width: int | None = None):
    kwargs = {"fg_color": COLORS["card"], "corner_radius": 12, "border_width": 1, "border_color": "#EDF1EE"}
    if width is not None:
        kwargs["width"] = width
    return ctk.CTkFrame(parent, **kwargs)


def input_field(parent, placeholder: str = ""):
    return ctk.CTkEntry(
        parent,
        height=38,
        corner_radius=8,
        fg_color=COLORS["field"],
        border_color=COLORS["border"],
        text_color="#1F2937",
        placeholder_text=placeholder,
        placeholder_text_color="#9CA3AF",
        font=(FONT_FAMILY, 12),
    )


def primary_button(parent, text: str, command, width: int | None = None, height: int = 36):
    kwargs = {"text": text, "height": height, "corner_radius": 8, "fg_color": COLORS["primary"], "hover_color": COLORS["primary_hover"], "font": (FONT_FAMILY, 11, "bold"), "command": command}
    if width is not None:
        kwargs["width"] = width
    return ctk.CTkButton(parent, **kwargs)


def secondary_button(parent, text: str, command, width: int | None = None):
    kwargs = {"text": text, "height": 36, "corner_radius": 8, "fg_color": "transparent", "hover_color": "#DFF1E5", "border_width": 1, "border_color": "#CBE7D4", "text_color": COLORS["primary"], "font": (FONT_FAMILY, 11, "bold"), "command": command}
    if width is not None:
        kwargs["width"] = width
    return ctk.CTkButton(parent, **kwargs)


def add_metric_card(parent, column: int, label: str, value_variable: tk.StringVar) -> None:
    card = ctk.CTkFrame(parent, width=100, height=60, fg_color=COLORS["mint"], corner_radius=9)
    card.grid(row=0, column=column, padx=(0 if column == 0 else 8, 0))
    card.grid_propagate(False)
    ctk.CTkLabel(card, text=label, text_color=COLORS["muted"], font=(FONT_FAMILY, 9), anchor="w").pack(anchor="w", padx=11, pady=(8, 0))
    ctk.CTkLabel(card, textvariable=value_variable, text_color=COLORS["text"], font=(FONT_FAMILY, 17, "bold"), anchor="w").pack(anchor="w", padx=11, pady=(0, 6))


def add_scrollbars(parent, tree: ttk.Treeview) -> None:
    vertical = ctk.CTkScrollbar(parent, orientation="vertical", command=tree.yview, width=11, button_color=COLORS["primary"], button_hover_color=COLORS["primary_hover"])
    horizontal = ctk.CTkScrollbar(parent, orientation="horizontal", command=tree.xview, height=11, button_color=COLORS["primary"], button_hover_color=COLORS["primary_hover"])
    tree.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
    vertical.pack(side="right", fill="y", padx=(6, 0))
    horizontal.pack(side="bottom", fill="x", pady=(6, 0))
