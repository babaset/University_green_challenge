"""Shared visual tokens for the CustomTkinter interface."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

import customtkinter as ctk


COLORS = {
    "window": "#D1E8D9",
    "surface": "#E9F7EF",
    "card": "#FFFFFF",
    "sidebar": "#0B4B32",
    "primary": "#18794E",
    "primary_hover": "#12613D",
    "text": "#0B4B32",
    "muted": "#6B7280",
    "field": "#F9FAFB",
    "border": "#E5E7EB",
    "mint": "#E8F6ED",
    "mint_dark": "#A7D4B8",
    "gold": "#B7791F",
    "pale_gold": "#FFF7E5",
    "red": "#B42318",
    "pale_red": "#FFF0EF",
    "sidebar_text": "#D5EEDF",
    "sidebar_muted": "#A7D4B8",
}

FONT_FAMILY = "Segoe UI"
MONO_FONT = "Cascadia Mono"


def configure_style(root: tk.Tk) -> dict[str, str]:
    """Set CustomTkinter to the light Figma-inspired visual language."""
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("green")
    root.configure(fg_color=COLORS["window"])

    # Treeview remains a Tk widget because it is the most practical way to
    # present sortable, scrollable admin tables. Its colours match CTk cards.
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass
    style.configure(
        "Green.Treeview",
        background=COLORS["card"],
        fieldbackground=COLORS["card"],
        foreground="#1F2937",
        borderwidth=0,
        rowheight=36,
        font=(FONT_FAMILY, 10),
    )
    style.map(
        "Green.Treeview",
        background=[("selected", COLORS["primary"])],
        foreground=[("selected", "#FFFFFF")],
    )
    style.configure(
        "Green.Treeview.Heading",
        background=COLORS["sidebar"],
        foreground="#FFFFFF",
        relief="flat",
        borderwidth=0,
        font=(FONT_FAMILY, 9, "bold"),
        padding=(10, 10),
    )
    style.map("Green.Treeview.Heading", background=[("active", COLORS["primary"])])

    # Kept for controller code which applies contextual table-row colours.
    return {
        **COLORS,
        "dark_green": COLORS["sidebar"],
        "green": COLORS["primary"],
        "pale_mint": COLORS["mint"],
    }
