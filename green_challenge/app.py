"""Application controller: connects the CustomTkinter views to the challenge rules."""

from __future__ import annotations

import os
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk

from .constants import ACTION_ICONS, ADMIN_PASSWORD, IMAGE_FILE_TYPES, VALID_IMAGE_EXTENSIONS
from .dialogs import show_feedback
from .store import ChallengeStore
from .styles import configure_style
from .views import build_interface, set_dashboard_sidebar, set_login_sidebar, show_login_role, style_navigation_button


class UniversityGreenChallengeApp:
    """Coordinate sign-in, user actions, and the on-screen application views."""

    def __init__(self, root: ctk.CTk):
        self.root = root
        self.root.title("University Green Challenge Leaderboard")
        self.root.geometry("1050x680")
        self.root.minsize(850, 550)

        self.store = ChallengeStore()
        self.current_role: str | None = None
        self.logged_in_student_id: str | None = None
        self.processing_request_ids: set[str] = set()
        self.student_display_to_id: dict[str, str] = {}
        self.action_display_to_name: dict[str, str] = {}
        self.pending_sort_column = "request_id"
        self.pending_sort_reverse = False

        self.theme_colors = configure_style(root)
        build_interface(self)
        self.refresh_all_views()
        self.show_login_screen()

    # ------------------------------------------------------------------
    # Small display helpers
    # ------------------------------------------------------------------
    @staticmethod
    def action_display_name(action: str) -> str:
        """Add a familiar icon without changing the stored action name."""
        return f"{ACTION_ICONS.get(action, '🌿')}  {action}"

    @staticmethod
    def status_details(status: str) -> tuple[str, str]:
        """Return an accessible status label and the matching table row tag."""
        if status in ("Admin-Approved", "Auto-Approved"):
            return "✓ Approved", "status_approved"
        if status == "Rejected":
            return "✕ Rejected", "status_rejected"
        if status == "Under Review":
            return "◌ Under review", "status_in_review"
        if status == "Needs More Evidence":
            return "! Needs more evidence", "status_needs_evidence"
        return "⌛ Pending review", "status_pending"

    @staticmethod
    def trust_details(trust_score: int) -> tuple[str, str]:
        """Create a readable trust progress bar and its row style tag."""
        filled_blocks = max(0, min(10, round(trust_score / 10)))
        progress_bar = "■" * filled_blocks + "□" * (10 - filled_blocks)
        if trust_score >= 80:
            return f"🟢 High  {progress_bar}  {trust_score}/100", "trust_high"
        if trust_score >= 50:
            return f"🟡 Medium  {progress_bar}  {trust_score}/100", "trust_medium"
        return f"🔴 Needs review  {progress_bar}  {trust_score}/100", "trust_low"

    def display_name_for_student(self, student_id: str) -> str:
        """Return the value shown in student-selection lists."""
        student = self.store.students.get(student_id)
        if student is None:
            return ""
        return f"{student.name} ({student.student_id})"

    def feedback(self, kind: str, title: str, message: str) -> None:
        """Open a standard feedback dialog."""
        show_feedback(self.root, kind, title, message)

    def update_navigation(self, allowed_tabs) -> None:
        """Show sidebar links only for pages available to the signed-in role."""
        for tab, button in self.navigation_items:
            button.pack_forget()
            if tab in allowed_tabs:
                button.pack(fill="x", pady=2)
        self.update_navigation_active()

    def update_navigation_active(self, _event=None) -> None:
        """Highlight the sidebar link for the notebook page currently shown."""
        selected_tab = self.notebook.select()
        for tab, button in self.navigation_items:
            style_navigation_button(button, str(tab) == selected_tab)

    # ------------------------------------------------------------------
    # Sign-in and permissions
    # ------------------------------------------------------------------
    def show_login_screen(self) -> None:
        """End the current session and expose only the role-selection screen."""
        self.current_role = None
        self.logged_in_student_id = None
        self.session_status_var.set("Not signed in")
        self.logout_button.configure(state="disabled")
        self.claim_student_combo.configure(state="readonly")
        self.history_student_combo.configure(state="readonly")
        self.claim_student_var.set("")
        self.history_student_var.set("")
        self.delete_approved_claim_button.configure(state="disabled")
        set_login_sidebar(self)
        show_login_role(self, "student")

        for tab in self.feature_tabs:
            self.notebook.tab(tab, state="hidden")
        self.notebook.tab(self.login_tab, state="normal")
        self.notebook.select(self.login_tab)
        self.update_navigation(())
        self.student_login_id_entry.delete(0, tk.END)
        self.admin_password_entry.delete(0, tk.END)
        self.student_login_id_entry.focus_set()
        self.get_student_history()

    def login_student(self) -> None:
        """Sign in a registered student using their student ID."""
        student_id = self.student_login_id_entry.get().strip().upper()
        if not student_id:
            self.feedback("error", "Login error", "Please enter your student ID.")
            self.student_login_id_entry.focus_set()
            return
        if student_id not in self.store.students:
            self.feedback("error", "Login error", "That student ID is not registered. Please ask an administrator to register you first.")
            self.student_login_id_entry.focus_set()
            return
        self.current_role = "student"
        self.logged_in_student_id = student_id
        self.open_role_dashboard()

    def login_admin(self) -> None:
        """Sign in the administrator for this classroom demonstration app."""
        if self.admin_password_entry.get() != ADMIN_PASSWORD:
            self.feedback("error", "Login error", "The administrator password is incorrect.")
            self.admin_password_entry.focus_set()
            return
        self.current_role = "admin"
        self.logged_in_student_id = None
        self.open_role_dashboard()

    def open_role_dashboard(self) -> None:
        """Show only the tabs that the signed-in role can use."""
        self.refresh_all_views()
        set_dashboard_sidebar(self)
        for tab in self.feature_tabs:
            self.notebook.tab(tab, state="hidden")

        if self.current_role == "student":
            student = self.store.students[self.logged_in_student_id]
            self.session_status_var.set(f"Signed in as student: {student.name} ({student.student_id})")
            allowed_tabs = (self.claim_tab, self.leaderboard_tab, self.history_tab)
            start_tab = self.claim_tab
        else:
            self.session_status_var.set("Signed in as administrator")
            allowed_tabs = (self.registration_tab, self.admin_tab, self.analytics_tab, self.leaderboard_tab, self.history_tab)
            start_tab = self.registration_tab

        for tab in allowed_tabs:
            self.notebook.tab(tab, state="normal")
        self.notebook.tab(self.login_tab, state="hidden")
        self.logout_button.configure(state="normal")
        self.delete_approved_claim_button.configure(state="normal" if self.current_role == "admin" else "disabled")
        self.update_navigation(allowed_tabs)
        self.notebook.select(start_tab)

    # ------------------------------------------------------------------
    # Student registration and claim submission
    # ------------------------------------------------------------------
    def register_student(self) -> None:
        """Validate and register a student. Administrators only."""
        if self.current_role != "admin":
            self.feedback("error", "Access denied", "Only an administrator can register students.")
            return

        self.register_button.configure(state="disabled")
        try:
            try:
                student = self.store.register_student(self.name_entry.get(), self.id_entry.get())
            except ValueError as error:
                self.feedback("error", "Registration error", str(error))
                if not self.name_entry.get().strip():
                    self.name_entry.focus_set()
                else:
                    self.id_entry.focus_set()
                return

            self.name_entry.delete(0, tk.END)
            self.id_entry.delete(0, tk.END)
            self.refresh_all_views()
            self.feedback("success", "Student registered", f"{student.name} has been registered with 100 trust points.")
        finally:
            self.register_button.configure(state="normal")

    def choose_proof_photo(self) -> None:
        """Let a student choose an image to attach to a claim."""
        if self.current_role != "student":
            self.feedback("error", "Access denied", "Please sign in as a student to attach proof.")
            return
        selected_path = filedialog.askopenfilename(title="Choose photo evidence", filetypes=IMAGE_FILE_TYPES)
        if selected_path:
            self.proof_path_var.set(selected_path)

    def submit_claim(self) -> None:
        """Validate evidence, then submit the signed-in student's claim."""
        if self.current_role != "student" or self.logged_in_student_id not in self.store.students:
            self.feedback("error", "Access denied", "Please sign in as a registered student to submit a claim.")
            return

        display_name = self.claim_student_var.get()
        action = self.action_display_to_name.get(self.action_var.get(), self.action_var.get())
        proof_path = self.proof_path_var.get().strip()
        description = " ".join(self.proof_description_entry.get("1.0", "end-1c").split())
        student_id = self.student_display_to_id.get(display_name)

        if student_id != self.logged_in_student_id:
            self.feedback("error", "Claim error", "You can submit claims only for your own student account.")
            return
        if not proof_path:
            self.feedback("error", "Claim error", "Please attach a photo as proof for this claim.")
            return
        if not description:
            self.feedback("error", "Claim error", "Please add a brief description of the photo evidence.")
            self.proof_description_entry.focus_set()
            return
        if not os.path.isfile(proof_path):
            self.feedback("error", "Claim error", "The selected photo can no longer be found. Please choose it again.")
            self.proof_path_var.set("")
            return
        if not proof_path.lower().endswith(VALID_IMAGE_EXTENSIONS):
            self.feedback("error", "Claim error", "Please select an image file (PNG, JPG, JPEG, GIF, or BMP).")
            self.proof_path_var.set("")
            return

        self.submit_button.configure(state="disabled")
        try:
            try:
                self.store.submit_claim(student_id, action, proof_path, description)
            except ValueError as error:
                self.feedback("error", "Claim error", str(error))
                return

            self.action_var.set("")
            self.proof_path_var.set("")
            self.proof_description_entry.delete("1.0", "end")
            self.refresh_all_views()
            self.feedback("info", "Claim pending review", "The claim is pending admin verification. Points will be awarded only after approval.")
        finally:
            self.submit_button.configure(state="normal")

    # ------------------------------------------------------------------
    # Administrator review and evidence
    # ------------------------------------------------------------------
    def review_request(self, decision: str) -> None:
        """Approve or reject the selected pending request."""
        if self.current_role != "admin":
            self.feedback("error", "Access denied", "Only an administrator can review claims.")
            return
        selection = self.pending_tree.selection()
        if not selection:
            self.feedback("error", "Review error", "Please select a pending request first.")
            return

        request_id = selection[0]
        if request_id in self.processing_request_ids:
            return
        self.processing_request_ids.add(request_id)
        self.approve_button.configure(state="disabled")
        self.reject_button.configure(state="disabled")
        try:
            try:
                student, claim = self.store.review_claim(request_id, decision, self.admin_note())
            except (ValueError, LookupError) as error:
                self.refresh_all_views()
                self.feedback("error", "Review error", str(error))
                return

            self.admin_note_entry.delete("1.0", "end")
            self.refresh_all_views()
            if decision == "approve":
                message = f"Approved {student.name}'s claim. {claim.points} points were awarded and trust is now {student.trust_score}."
                self.feedback("success", "Claim approved", message)
            else:
                message = f"Rejected {student.name}'s claim. No points were awarded and trust is now {student.trust_score}."
                self.feedback("info", "Claim rejected", message)
        finally:
            self.processing_request_ids.discard(request_id)
            self.approve_button.configure(state="normal")
            self.reject_button.configure(state="normal")

    def admin_note(self) -> str:
        """Return a trimmed optional comment entered by the administrator."""
        return " ".join(self.admin_note_entry.get("1.0", "end-1c").split())

    def update_request_status(self, status: str) -> None:
        """Record an in-progress review status without changing scores."""
        if self.current_role != "admin":
            self.feedback("error", "Access denied", "Only an administrator can update review status.")
            return
        selection = self.pending_tree.selection()
        if not selection:
            self.feedback("error", "Review error", "Please select a pending request first.")
            return

        try:
            claim = self.store.update_pending_status(selection[0], status, self.admin_note())
        except ValueError as error:
            self.refresh_all_views()
            self.feedback("error", "Review error", str(error))
            return

        self.admin_note_entry.delete("1.0", "end")
        self.refresh_all_views()
        self.feedback("info", "Review updated", f"Request #{claim.request_id} is now marked as {claim.status}.")

    def delete_selected_request(self) -> None:
        """Let an administrator permanently delete a selected pending claim."""
        if self.current_role != "admin":
            self.feedback("error", "Access denied", "Only an administrator can delete claims.")
            return
        selection = self.pending_tree.selection()
        if not selection:
            self.feedback("error", "Delete error", "Please select a pending request first.")
            return
        if not messagebox.askyesno(
            "Delete claim",
            "Delete this pending claim permanently? This action cannot be undone.",
            parent=self.root,
        ):
            return

        try:
            claim = self.store.delete_pending_claim(selection[0])
        except (ValueError, LookupError) as error:
            self.refresh_all_views()
            self.feedback("error", "Delete error", str(error))
            return

        self.admin_note_entry.delete("1.0", "end")
        self.refresh_all_views()
        self.feedback("success", "Claim deleted", f"Request #{claim.request_id} was removed from the student's history.")

    def show_selected_evidence(self, _event=None) -> None:
        """Show path, description, and review priority for the selected proof."""
        selection = self.pending_tree.selection()
        request = self.store.get_pending_request(selection[0]) if selection else None
        if request is None:
            self.evidence_details_var.set("Select a pending request to view its proof details.")
            self.open_proof_button.configure(state="disabled")
            return

        claim = request.claim
        note = claim.admin_note or "No admin note yet."
        submitted = claim.created_at or "Not recorded for older claims."
        self.evidence_details_var.set(
            f"Status: {claim.status}  |  Review: {claim.review_level}\n"
            f"Submitted: {submitted}\nPhoto: {claim.evidence_path}\n"
            f"Description: {claim.evidence_description or 'No description provided.'}\nAdmin note: {note}"
        )
        self.open_proof_button.configure(state="normal" if os.path.isfile(claim.evidence_path) else "disabled")

    def open_selected_proof(self) -> None:
        """Open the selected photo in the computer's default image viewer."""
        if self.current_role != "admin":
            self.feedback("error", "Access denied", "Only an administrator can open submitted proof.")
            return
        selection = self.pending_tree.selection()
        request = self.store.get_pending_request(selection[0]) if selection else None
        if request is None:
            self.feedback("error", "Evidence error", "Please select a pending request first.")
            return
        if not os.path.isfile(request.claim.evidence_path):
            self.show_selected_evidence()
            self.feedback("error", "Evidence error", "The proof photo is no longer available at the saved location.")
            return
        try:
            os.startfile(request.claim.evidence_path)
        except OSError:
            self.feedback("error", "Evidence error", "The photo could not be opened with the default image viewer.")

    # ------------------------------------------------------------------
    # Tables and data refresh
    # ------------------------------------------------------------------
    def get_student_history(self):
        """Render the selected student's complete claim history."""
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)

        if self.current_role == "student" and self.logged_in_student_id in self.store.students:
            student_id = self.logged_in_student_id
            self.history_student_var.set(self.display_name_for_student(student_id))
        else:
            student_id = self.student_display_to_id.get(self.history_student_var.get())

        student = self.store.students.get(student_id)
        if student is None:
            self.history_current_student_id = None
            self.history_summary.configure(text="🌱 Select a registered student to view their sustainability journey.")
            return []
        self.history_current_student_id = student_id
        if not student.claims_log:
            self.history_summary.configure(text=f"🌱 {student.name}: No claims recorded yet — make your first green impact!")
            return []

        self.history_summary.configure(text=f"{student.name}: {len(student.claims_log)} claim(s) recorded.")
        for number, claim in enumerate(student.claims_log, start=1):
            status_label, status_tag = self.status_details(claim.status)
            evidence_name = os.path.basename(claim.evidence_path) or "No photo attached"
            created_at = claim.created_at or "—"
            reviewed_at = claim.reviewed_at or "—"
            note = claim.admin_note or "—"
            self.history_tree.insert(
                "",
                "end",
                iid=claim.request_id,
                values=(number, self.action_display_name(claim.action), claim.points, status_label, created_at, reviewed_at, note, evidence_name),
                tags=(status_tag,),
            )
        return student.claims_log

    def delete_selected_approved_claim(self) -> None:
        """Let an administrator delete an approved historical claim and its points."""
        if self.current_role != "admin":
            self.feedback("error", "Access denied", "Only an administrator can delete approved claims.")
            return
        selection = self.history_tree.selection()
        student_id = getattr(self, "history_current_student_id", None)
        if not selection or student_id is None:
            self.feedback("error", "Delete error", "Select an approved claim in Claim History first.")
            return

        request_id = selection[0]
        student = self.store.students.get(student_id)
        claim = next((item for item in student.claims_log if item.request_id == request_id), None) if student else None
        if claim is None or claim.status not in {"Admin-Approved", "Auto-Approved"}:
            self.feedback("error", "Delete error", "Only approved claims can be deleted from Claim History.")
            return
        if not messagebox.askyesno(
            "Delete approved claim",
            f"Delete this approved claim and remove {claim.points} points from {student.name}? This cannot be undone.",
            parent=self.root,
        ):
            return

        try:
            deleted_claim = self.store.delete_approved_claim(student_id, request_id)
        except ValueError as error:
            self.refresh_all_views()
            self.feedback("error", "Delete error", str(error))
            return

        self.refresh_all_views()
        self.feedback(
            "success",
            "Approved claim deleted",
            f"Request #{deleted_claim.request_id} was deleted and {deleted_claim.points} points were removed from {student.name}.",
        )

    def refresh_student_selectors(self) -> None:
        """Update dropdowns after a student record or session changes."""
        current_claim_selection = self.claim_student_var.get()
        current_history_selection = self.history_student_var.get()
        self.student_display_to_id = {
            f"{student.name} ({student.student_id})": student.student_id for student in self.store.get_leaderboard()
        }
        choices = list(self.student_display_to_id)
        if self.current_role == "student" and self.logged_in_student_id in self.store.students:
            own_name = self.display_name_for_student(self.logged_in_student_id)
            self.claim_student_combo.configure(values=[own_name])
            self.history_student_combo.configure(values=[own_name])
            self.claim_student_var.set(own_name)
            self.history_student_var.set(own_name)
            self.claim_student_combo.configure(state="disabled")
            self.history_student_combo.configure(state="disabled")
        else:
            self.claim_student_combo.configure(values=choices)
            self.history_student_combo.configure(values=choices)
            self.claim_student_var.set(current_claim_selection if current_claim_selection in self.student_display_to_id else "")
            self.history_student_var.set(current_history_selection if current_history_selection in self.student_display_to_id else "")
            self.claim_student_combo.configure(state="readonly")
            self.history_student_combo.configure(state="readonly")

    def clear_pending_filters(self) -> None:
        """Return the administrative queue to its unfiltered view."""
        self.pending_search_var.set("")
        self.pending_status_filter.set("All statuses")
        self.pending_action_filter.set("All actions")
        self.refresh_pending_queue()

    def sort_pending_queue(self, column: str) -> None:
        """Sort the visible review queue when an administrator clicks a heading."""
        if column == self.pending_sort_column:
            self.pending_sort_reverse = not self.pending_sort_reverse
        else:
            self.pending_sort_column = column
            self.pending_sort_reverse = False
        self.refresh_pending_queue()

    def _pending_sort_value(self, request):
        """Return a type-safe ordering value for one review queue column."""
        student = self.store.students.get(request.student_id)
        claim = request.claim
        values = {
            "student": student.name.casefold() if student else "",
            "student_id": request.student_id.casefold(),
            "action": claim.action.casefold(),
            "status": claim.status.casefold(),
            "evidence": os.path.basename(claim.evidence_path).casefold(),
            "points": claim.points,
            "trust": student.trust_score if student else 0,
            "request_id": int(request.request_id) if request.request_id.isdigit() else request.request_id,
        }
        return values.get(self.pending_sort_column, values["request_id"])

    def _visible_pending_requests(self):
        """Filter then order requests using the administrator's queue controls."""
        search = self.pending_search_var.get().strip().casefold()
        status_filter = self.pending_status_filter.get()
        action_filter = self.pending_action_filter.get()
        visible_requests = []
        for request in self.store.pending_requests:
            student = self.store.students.get(request.student_id)
            if student is None:
                continue
            claim = request.claim
            searchable = " ".join((student.name, student.student_id, claim.action, claim.status)).casefold()
            if search and search not in searchable:
                continue
            if status_filter != "All statuses" and claim.status != status_filter:
                continue
            if action_filter != "All actions" and claim.action != action_filter:
                continue
            visible_requests.append(request)
        return sorted(visible_requests, key=self._pending_sort_value, reverse=self.pending_sort_reverse)

    def _update_pending_sort_headings(self) -> None:
        """Show the active queue sort column and direction in the table heading."""
        arrow = " ▼" if self.pending_sort_reverse else " ▲"
        for column, heading in self.pending_headings.items():
            label = f"{heading}{arrow}" if column == self.pending_sort_column else heading
            self.pending_tree.heading(column, text=label)

    def refresh_pending_queue(self) -> None:
        """Render the filtered and sorted claims awaiting administrator review."""
        for item in self.pending_tree.get_children():
            self.pending_tree.delete(item)
        visible_requests = self._visible_pending_requests()
        for request in visible_requests:
            student = self.store.students.get(request.student_id)
            if student is None:
                continue
            claim = request.claim
            status_label, status_tag = self.status_details(claim.status)
            if claim.review_level == "Extra scrutiny" and claim.status == "Pending Review":
                status_label = "⌛ Pending — extra scrutiny"
            trust_label, _ = self.trust_details(student.trust_score)
            self.pending_tree.insert("", "end", iid=request.request_id, values=(student.name, student.student_id, self.action_display_name(claim.action), status_label, os.path.basename(claim.evidence_path) or "No photo attached", claim.points, trust_label), tags=(status_tag,))

        self._update_pending_sort_headings()
        if visible_requests:
            self.pending_empty_label.pack_forget()
        else:
            self.pending_empty_label.configure(
                text="No requests match the current filters." if self.store.pending_requests else "♧ No pending requests — every submitted claim has been reviewed."
            )
            self.pending_empty_label.pack(anchor="w", pady=(10, 0))
        self.show_selected_evidence()

    def refresh_leaderboard(self) -> None:
        """Render the sorted ranking table."""
        for item in self.leaderboard_tree.get_children():
            self.leaderboard_tree.delete(item)
        leaderboard = self.store.get_leaderboard()
        medals = ("🥇", "🥈", "🥉")
        for position, student in enumerate(leaderboard, start=1):
            rank = f"{medals[position - 1]} {position}" if position <= 3 else str(position)
            trust_label, trust_tag = self.trust_details(student.trust_score)
            self.leaderboard_tree.insert("", "end", values=(rank, student.name, student.student_id, f"⭐ {student.points} pts", trust_label), tags=(trust_tag,))

        if leaderboard:
            self.leaderboard_empty_label.pack_forget()
        else:
            self.leaderboard_empty_label.pack(anchor="w", pady=(10, 0))

    def refresh_dashboard_metrics(self) -> None:
        """Update the visual statistic cards without changing stored data."""
        self.pending_count_var.set(str(len(self.store.pending_requests)))
        self.student_count_var.set(str(len(self.store.students)))

        student = self.store.students.get(self.logged_in_student_id)
        if self.current_role != "student" or student is None:
            self.student_points_var.set("—")
            self.student_trust_var.set("—")
            self.student_rank_var.set("—")
            return

        leaderboard = self.store.get_leaderboard()
        rank = next(
            (position for position, entry in enumerate(leaderboard, start=1) if entry.student_id == student.student_id),
            None,
        )
        self.student_points_var.set(str(student.points))
        self.student_trust_var.set(f"{student.trust_score}%")
        self.student_rank_var.set(f"#{rank}" if rank is not None else "—")

    def refresh_analytics(self) -> None:
        """Calculate read-only challenge statistics for the administrator dashboard."""
        claims = [claim for student in self.store.students.values() for claim in student.claims_log]
        total_claims = len(claims)
        approved = sum(claim.status in {"Admin-Approved", "Auto-Approved"} for claim in claims)
        rejected = sum(claim.status == "Rejected" for claim in claims)
        in_progress = sum(claim.status in {"Pending Review", "Under Review", "Needs More Evidence"} for claim in claims)
        approval_rate = round((approved / total_claims) * 100) if total_claims else 0
        points_awarded = sum(student.points for student in self.store.students.values())

        self.analytics_total_claims_var.set(str(total_claims))
        self.analytics_approved_var.set(str(approved))
        self.analytics_pending_var.set(str(in_progress))
        self.analytics_points_var.set(str(points_awarded))

        action_counts: dict[str, int] = {}
        for claim in claims:
            action_counts[claim.action] = action_counts.get(claim.action, 0) + 1
        top_action = max(action_counts, key=action_counts.get) if action_counts else "No claims yet"
        self.analytics_summary_var.set(
            f"Approval rate: {approval_rate}%   •   Rejected: {rejected}   •   Most common action: {top_action}"
        )
        self._analytics_status_counts = {
            "Pending": in_progress,
            "Approved": approved,
            "Rejected": rejected,
        }
        self.root.after_idle(self.draw_analytics_chart)

    def draw_analytics_chart(self) -> None:
        """Draw a compact status-count bar chart using the existing Tk canvas."""
        chart = self.analytics_chart
        chart.delete("all")
        width = max(chart.winfo_width(), chart.winfo_reqwidth())
        height = max(chart.winfo_height(), chart.winfo_reqheight())
        left, right, top, bottom = 45, 20, 25, 36
        chart.create_line(left, top, left, height - bottom, fill="#CBE7D4")
        chart.create_line(left, height - bottom, width - right, height - bottom, fill="#CBE7D4")

        status_counts = getattr(self, "_analytics_status_counts", {"Pending": 0, "Approved": 0, "Rejected": 0})
        data = list(status_counts.items())
        maximum = max(1, *(count for _, count in data))
        available_width = width - left - right
        slot_width = available_width / len(data)
        bar_width = min(90, slot_width * 0.52)
        colors = {"Pending": "#B7791F", "Approved": "#18794E", "Rejected": "#B42318"}
        for index, (label, count) in enumerate(data):
            center = left + slot_width * (index + 0.5)
            bar_height = (height - top - bottom) * count / maximum
            x0, x1 = center - bar_width / 2, center + bar_width / 2
            y0 = height - bottom - bar_height
            chart.create_rectangle(x0, y0, x1, height - bottom, fill=colors[label], outline="")
            chart.create_text(center, y0 - 10, text=str(count), fill="#0B4B32", font=("Segoe UI", 10, "bold"))
            chart.create_text(center, height - 17, text=label, fill="#6B7280", font=("Segoe UI", 9))

    def refresh_all_views(self) -> None:
        """Refresh every data-dependent control after a model change."""
        self.refresh_student_selectors()
        self.refresh_pending_queue()
        self.refresh_leaderboard()
        self.get_student_history()
        self.refresh_dashboard_metrics()
        self.refresh_analytics()


def main() -> None:
    """Start the desktop application."""
    root = ctk.CTk()
    UniversityGreenChallengeApp(root)
    root.mainloop()
