"""Small CustomTkinter feedback dialogs."""

from __future__ import annotations

import customtkinter as ctk

from .styles import COLORS, FONT_FAMILY


def show_feedback(root, kind: str, title: str, message: str) -> None:
    """Show a compact, colour-coded modal that matches the new interface."""
    palette = {
        "success": ("✓", COLORS["mint"], "#145A37", "Great progress!"),
        "error": ("!", COLORS["pale_red"], COLORS["red"], "Please check this"),
        "info": ("i", COLORS["pale_gold"], "#7A5100", "Update"),
    }
    icon, background, accent, fallback_title = palette.get(kind, palette["info"])
    dialog = ctk.CTkToplevel(root)
    dialog.title(title or fallback_title)
    dialog.configure(fg_color=COLORS["card"])
    dialog.resizable(False, False)
    dialog.transient(root)

    card = ctk.CTkFrame(dialog, fg_color=COLORS["card"], corner_radius=0)
    card.pack(fill="both", expand=True, padx=20, pady=20)
    banner = ctk.CTkFrame(card, fg_color=background, corner_radius=9)
    banner.pack(fill="x")
    ctk.CTkLabel(
        banner,
        text=f"{icon}  {title or fallback_title}",
        text_color=accent,
        font=(FONT_FAMILY, 13, "bold"),
        anchor="w",
    ).pack(fill="x", padx=13, pady=10)
    ctk.CTkLabel(
        card,
        text=message,
        text_color="#374151",
        font=(FONT_FAMILY, 12),
        justify="left",
        wraplength=390,
        anchor="w",
    ).pack(anchor="w", fill="x", pady=(15, 17))
    ctk.CTkButton(
        card,
        text="Got it",
        width=90,
        height=34,
        corner_radius=8,
        fg_color=COLORS["primary"],
        hover_color=COLORS["primary_hover"],
        font=(FONT_FAMILY, 11, "bold"),
        command=dialog.destroy,
    ).pack(anchor="e")

    dialog.update_idletasks()
    x_position = root.winfo_rootx() + max(0, (root.winfo_width() - dialog.winfo_width()) // 2)
    y_position = root.winfo_rooty() + max(0, (root.winfo_height() - dialog.winfo_height()) // 2)
    dialog.geometry(f"+{x_position}+{y_position}")
    dialog.grab_set()
    dialog.focus_force()
