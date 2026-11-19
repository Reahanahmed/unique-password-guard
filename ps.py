import os
import re
import tkinter as tk
from collections import Counter
from datetime import datetime


class PasswordStrengthApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Password Strength & Uniqueness Analyzer")
        self.root.geometry("980x660")
        self.root.minsize(520, 560)
        self.root.resizable(True, True)

        # Refined, High-Visibility Elegant Palette
        self.outer_bg = "#F1F5F9"       # Crisp cool slate backdrop
        self.card_bg = "#FFFFFF"        # Pure white elevated surface
        self.banner_bg = "#1E1B4B"      # Deep royal indigo header
        self.banner_sub = "#C7D2FE"     # Soft periwinkle subtitle
        self.primary_btn = "#4F46E5"    # Vibrant indigo ("Analyze & Save")
        self.primary_hover = "#4338CA"
        self.new_btn = "#0D9488"        # Rich teal ("Enter New Password")
        self.new_hover = "#0F766E"
        self.text_dark = "#0F172A"      # Deep midnight ink
        self.text_muted = "#64748B"     # Slate secondary text
        self.border_color = "#CBD5E1"   # Clean border
        self.divider_color = "#E2E8F0"

        # Semantic Status Colors
        self.pass_fg = "#059669"        # Emerald green
        self.pass_bg = "#ECFDF5"        # Soft mint pill
        self.fail_fg = "#DC2626"        # Crisp crimson
        self.fail_bg = "#FEF2F2"        # Soft rose pill
        self.pending_fg = "#475569"     # Neutral slate
        self.pending_bg = "#F8FAFC"     # Soft ice pill

        self.root.configure(bg=self.outer_bg)

        # Track whether we are currently displaying results ("analyze" vs "reset")
        self.is_result_state = False
        self.is_wide_layout = None

        # Ensure storage folder exists in the same directory
        self.save_dir = r"C:\Users\acer\Documents\project\saved_passwords"
        os.makedirs(self.save_dir, exist_ok=True)

        self.build_ui()

    def build_ui(self):
        # Main fluid outer container that resizes freely with the window
        self.outer_frame = tk.Frame(
            self.root, bg=self.outer_bg, padx=24, pady=20
        )
        self.outer_frame.pack(fill="both", expand=True)

        # Elevated Main Card
        self.card = tk.Frame(
            self.outer_frame,
            bg=self.card_bg,
            highlightbackground=self.border_color,
            highlightthickness=1,
        )
        self.card.pack(fill="both", expand=True)

        # --- HEADER BANNER ---
        banner = tk.Frame(self.card, bg=self.banner_bg, padx=28, pady=18)
        banner.pack(fill="x")

        tk.Label(
            banner,
            text=" UNIQUE PASSCODE GUARD",
            font=("Helvetica", 9, "bold"),
            bg=self.banner_bg,
            fg="#818CF8",
            anchor="w",
        ).pack(fill="x", pady=(0, 2))

        tk.Label(
            banner,
            text="Anti-Reuse Credential Complexity Evaluator",
            font=("Georgia", 19, "bold"),
            bg=self.banner_bg,
            fg="#FFFFFF",
            anchor="w",
        ).pack(fill="x", pady=(0, 4))

        tk.Label(
            banner,
            text="Enforces unique non-repeating characters, 8+ length, and zero password reuse.",
            font=("Helvetica", 10),
            bg=self.banner_bg,
            fg=self.banner_sub,
            anchor="w",
        ).pack(fill="x")

        # --- MAIN WORKSPACE ---
        self.body = tk.Frame(self.card, bg=self.card_bg, padx=28, pady=20)
        self.body.pack(fill="both", expand=True)

        # Top Input Bar Section
        input_section = tk.Frame(self.body, bg=self.card_bg)
        input_section.pack(fill="x", pady=(0, 16))

        self.input_title_lbl = tk.Label(
            input_section,
            text="ENTER PASSWORD TO EVALUATE",
            font=("Helvetica", 9, "bold"),
            bg=self.card_bg,
            fg=self.text_muted,
            anchor="w",
        )
        self.input_title_lbl.pack(fill="x", pady=(0, 6))

        # Input + Action Button Row (stretches cleanly when resized)
        entry_row = tk.Frame(input_section, bg=self.card_bg)
        entry_row.pack(fill="x", pady=(0, 6))

        self.password_var = tk.StringVar()
        self.entry = tk.Entry(
            entry_row,
            textvariable=self.password_var,
            font=("Consolas", 13),
            bg="#F8FAFC",
            fg=self.text_dark,
            disabledbackground="#F1F5F9",
            disabledforeground="#94A3B8",
            insertbackground=self.primary_btn,
            relief="solid",
            bd=1,
            highlightthickness=1,
            highlightbackground=self.border_color,
            highlightcolor=self.primary_btn,
        )
        self.entry.pack(side="left", fill="x", expand=True, ipady=9, padx=(0, 12))
        self.entry.bind("<Return>", lambda e: self.handle_action_button())
        self.entry.focus_set()

        self.action_btn = tk.Button(
            entry_row,
            text="Analyze & Save Password",
            command=self.handle_action_button,
            font=("Helvetica", 11, "bold"),
            bg=self.primary_btn,
            fg="#FFFFFF",
            activebackground=self.primary_hover,
            activeforeground="#FFFFFF",
            relief="flat",
            cursor="hand2",
            padx=22,
            pady=10,
        )
        self.action_btn.pack(side="right")

        # Show/Hide Toggle
        self.show_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            input_section,
            text="Show Password Characters",
            variable=self.show_var,
            command=self.toggle_password,
            font=("Helvetica", 9),
            bg=self.card_bg,
            fg=self.text_muted,
            activebackground=self.card_bg,
            activeforeground=self.text_dark,
            selectcolor=self.card_bg,
            anchor="w",
        ).pack(fill="x")

        # Divider
        tk.Frame(self.body, height=1, bg=self.divider_color).pack(
            fill="x", pady=(0, 16)
        )

        # --- RESPONSIVE RESULTS AREA (Side-by-Side on Wide Windows, Stacked on Narrow) ---
        self.results_container = tk.Frame(self.body, bg=self.card_bg)
        self.results_container.pack(fill="both", expand=True)

        # Left/Top Pane: Validation Checks
        self.left_pane = tk.Frame(self.results_container, bg=self.card_bg)

        tk.Label(
            self.left_pane,
            text="VALIDATION CHECKS",
            font=("Helvetica", 9, "bold"),
            bg=self.card_bg,
            fg=self.primary_btn,
            anchor="w",
        ).pack(fill="x", pady=(0, 8))

        self.validation_labels = {}
        self.criteria = [
            ("unique_pwd", "UNIQUE PASSWORD (NO PREVIOUS MATCH)"),
            ("min_length", "MINIMUM 8 CHARACTERS"),
            ("uppercase", "UPPERCASE LETTERS"),
            ("lowercase", "LOWERCASE LETTERS"),
            ("special", "SPECIAL CHARACTERS"),
            ("numerals", "NUMERALS (0-9)"),
            ("rep_chars", "REPEATED CHARACTERS"),
            ("rep_nums", "REPEATED NUMERALS"),
            ("rep_special", "REPEATED SPECIAL CHARS"),
        ]

        for key, title in self.criteria:
            lbl = tk.Label(
                self.left_pane,
                text=f"  •  {title}: Pending",
                font=("Helvetica", 9, "bold"),
                bg=self.pending_bg,
                fg=self.pending_fg,
                anchor="w",
                padx=10,
                pady=5,
            )
            lbl.pack(fill="x", pady=2)
            self.validation_labels[key] = lbl

        # Right/Bottom Pane: Strength Assessment
        self.right_pane = tk.Frame(
            self.results_container,
            bg="#F8FAFC",
            highlightbackground=self.divider_color,
            highlightthickness=1,
            padx=20,
            pady=18,
        )

        tk.Label(
            self.right_pane,
            text="STRENGTH ASSESSMENT",
            font=("Helvetica", 9, "bold"),
            bg="#F8FAFC",
            fg=self.primary_btn,
            anchor="w",
        ).pack(fill="x", pady=(0, 10))

        self.tested_info_label = tk.Label(
            self.right_pane,
            text="Evaluated Password: None yet",
            font=("Consolas", 10),
            bg="#F8FAFC",
            fg=self.text_muted,
            anchor="w",
        )
        self.tested_info_label.pack(fill="x", pady=(0, 10))

        self.rating_label = tk.Label(
            self.right_pane,
            text="Strength Level: —",
            font=("Georgia", 17, "bold"),
            bg="#F8FAFC",
            fg=self.text_dark,
            anchor="w",
        )
        self.rating_label.pack(fill="x", pady=(0, 6))

        self.score_label = tk.Label(
            self.right_pane,
            text="Numerical Score: 0 / 100",
            font=("Helvetica", 13, "bold"),
            bg="#F8FAFC",
            fg=self.text_muted,
            anchor="w",
        )
        self.score_label.pack(fill="x", pady=(0, 10))

        # Visual Score Progress Bar
        self.bar_bg = tk.Frame(self.right_pane, bg="#E2E8F0", height=10)
        self.bar_bg.pack(fill="x", pady=(0, 16))
        self.bar_fill = tk.Frame(self.bar_bg, bg=self.primary_btn, height=10)
        self.bar_fill.place(x=0, y=0, relheight=1.0, relwidth=0.0)

        # Suggestion Card inside Assessment Pane
        self.suggestion_label = tk.Label(
            self.right_pane,
            text="Suggestion: Enter a password above and click 'Analyze & Save Password' to view full security feedback.",
            font=("Helvetica", 10),
            bg="#FFFFFF",
            fg=self.text_dark,
            wraplength=340,
            justify="left",
            anchor="nw",
            padx=12,
            pady=12,
            highlightbackground=self.divider_color,
            highlightthickness=1,
        )
        self.suggestion_label.pack(fill="both", expand=True, pady=(0, 10))

        # File Save Confirmation
        self.status_label = tk.Label(
            self.right_pane,
            text="",
            font=("Helvetica", 9, "italic"),
            bg="#F8FAFC",
            fg=self.pass_fg,
            anchor="w",
        )
        self.status_label.pack(fill="x", pady=(4, 0))

        # Bind dynamic resize listener so user can resize/expand window freely
        self.root.bind("<Configure>", self.on_window_resize)
        self.apply_responsive_layout(980)

    def on_window_resize(self, event):
        if event.widget == self.root:
            self.apply_responsive_layout(event.width)

    def apply_responsive_layout(self, width):
        use_wide = width >= 780
        if use_wide != self.is_wide_layout:
            self.is_wide_layout = use_wide
            self.left_pane.pack_forget()
            self.right_pane.pack_forget()

            if use_wide:
                self.left_pane.pack(
                    side="left", fill="both", expand=True, padx=(0, 16)
                )
                self.right_pane.pack(
                    side="right", fill="both", expand=True, padx=(8, 0)
                )
            else:
                self.left_pane.pack(fill="x", pady=(0, 14))
                self.right_pane.pack(fill="both", expand=True)

        # Dynamically adjust suggestion text wrapping to fit current window width
        if use_wide:
            wrap_w = max(240, int((width - 160) * 0.46))
        else:
            wrap_w = max(280, width - 140)
        self.suggestion_label.config(wraplength=wrap_w)

    def toggle_password(self):
        if self.show_var.get():
            self.entry.config(show="")
        else:
            self.entry.config(show="*")

    def handle_action_button(self):
        if self.is_result_state:
            self.reset_for_new_password()
        else:
            self.analyze_and_save()

    def reset_for_new_password(self):
        """Resets the UI so the user can enter a fresh password."""
        self.is_result_state = False
        self.entry.config(state="normal")
        self.password_var.set("")
        self.entry.focus_set()

        self.input_title_lbl.config(
            text="ENTER PASSWORD TO EVALUATE", fg=self.text_muted
        )
        self.action_btn.config(
            text="Analyze & Save Password",
            bg=self.primary_btn,
            activebackground=self.primary_hover,
        )

        # Reset validation pills to Pending
        for key, title in self.criteria:
            self.validation_labels[key].config(
                text=f"  •  {title}: Pending",
                bg=self.pending_bg,
                fg=self.pending_fg,
                font=("Helvetica", 9, "bold"),
            )

        # Reset assessment panel
        self.tested_info_label.config(text="Evaluated Password: None yet")
        self.rating_label.config(text="Strength Level: —", fg=self.text_dark)
        self.score_label.config(
            text="Numerical Score: 0 / 100", fg=self.text_muted
        )
        self.bar_fill.place(x=0, y=0, relheight=1.0, relwidth=0.0)
        self.suggestion_label.config(
            text="Suggestion: Enter a password above and click 'Analyze & Save Password' to view full security feedback."
        )
        self.status_label.config(text="")

    def is_password_already_saved(self, pwd):
        """Checks all previously saved password files in saved_passwords/."""
        if not os.path.exists(self.save_dir):
            return False, None

        for filename in os.listdir(self.save_dir):
            if filename.endswith(".txt"):
                filepath = os.path.join(self.save_dir, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        for line in f:
                            if line.startswith("Password Entered"):
                                saved_pwd = line.split(":", 1)[1].rstrip("\r\n")
                                if saved_pwd.startswith(" "):
                                    saved_pwd = saved_pwd[1:]
                                if saved_pwd == pwd:
                                    return True, filename
                except OSError:
                    continue
        return False, None

    def analyze_and_save(self):
        pwd = self.password_var.get()
        if not pwd:
            self.suggestion_label.config(
                text="Suggestion: Please type a password in the input box first."
            )
            self.entry.focus_set()
            return

        # 0. Check if exact password has already been used/saved
        already_exists, existing_file = self.is_password_already_saved(pwd)

        # 1. Perform Core Presence Validations
        length = len(pwd)
        has_min_len = length >= 8
        has_upper = bool(re.search(r"[A-Z]", pwd))
        has_lower = bool(re.search(r"[a-z]", pwd))
        has_special = bool(re.search(r"[^A-Za-z0-9]", pwd))
        has_numeral = bool(re.search(r"[0-9]", pwd))

        # 2. Check Global Repetition Anywhere in the Password
        counts = Counter(pwd)

        letter_counts = Counter(ch.lower() for ch in pwd if ch.isalpha())
        repeated_letters = sorted([ch for ch, c in letter_counts.items() if c > 1])
        rep_chars = len(repeated_letters) > 0

        repeated_nums = sorted([ch for ch, c in counts.items() if ch.isdigit() and c > 1])
        rep_nums = len(repeated_nums) > 0

        repeated_specials = sorted(
            [ch for ch, c in counts.items() if not ch.isalnum() and c > 1]
        )
        rep_special = len(repeated_specials) > 0

        # Update Vertical Validation Pill Rows
        self.update_check(
            "unique_pwd",
            "UNIQUE PASSWORD",
            not already_exists,
            "Passed (New Password)",
            f"Duplicate ({existing_file})",
        )
        self.update_check(
            "min_length",
            "MINIMUM 8 CHARACTERS",
            has_min_len,
            f"Passed ({length} chars)",
            f"Failed ({length}/8 chars)",
        )
        self.update_check(
            "uppercase", "UPPERCASE LETTERS", has_upper, "Present", "Missing"
        )
        self.update_check(
            "lowercase", "LOWERCASE LETTERS", has_lower, "Present", "Missing"
        )
        self.update_check(
            "special", "SPECIAL CHARACTERS", has_special, "Present", "Missing"
        )
        self.update_check(
            "numerals", "NUMERALS (0-9)", has_numeral, "Present", "Missing"
        )
        self.update_check(
            "rep_chars",
            "REPEATED CHARACTERS",
            not rep_chars,
            "None (Good)",
            f"Detected ({', '.join(repeated_letters)}) (-15 pts)",
        )
        self.update_check(
            "rep_nums",
            "REPEATED NUMERALS",
            not rep_nums,
            "None (Good)",
            f"Detected ({', '.join(repeated_nums)}) (-15 pts)",
        )
        self.update_check(
            "rep_special",
            "REPEATED SPECIAL CHARS",
            not rep_special,
            "None (Good)",
            f"Detected ({', '.join(repeated_specials)}) (-15 pts)",
        )

        # 3. Calculate Numerical Score out of 100
        score = 0
        suggestions = []

        if length >= 14:
            score += 40
        elif length >= 10:
            score += 30
        elif length >= 8:
            score += 20
        else:
            score += 5
            suggestions.append(
                "Password must be at least 8 characters long to be rated Strong."
            )

        if has_upper:
            score += 15
        else:
            suggestions.append("Add uppercase letters (A-Z).")

        if has_lower:
            score += 15
        else:
            suggestions.append("Add lowercase letters (a-z).")

        if has_special:
            score += 15
        else:
            suggestions.append("Include special symbols (!@#$%^&*).")

        if has_numeral:
            score += 15
        else:
            suggestions.append("Add numbers (0-9).")

        if rep_chars:
            score -= 15
            suggestions.append(
                f"Do not repeat letters anywhere (repeated: {', '.join(repeated_letters)})."
            )

        if rep_nums:
            score -= 15
            suggestions.append(
                f"Do not repeat numerals anywhere (repeated: {', '.join(repeated_nums)})."
            )

        if rep_special:
            score -= 15
            suggestions.append(
                f"Do not repeat special characters anywhere (repeated: {', '.join(repeated_specials)})."
            )

        score = max(0, min(100, score))

        # Hard cap: cannot be Strong or Very Strong if under 8 characters
        if not has_min_len and score >= 70:
            score = 65

        # Display masked or visible summary of evaluated password
        display_pwd = pwd if self.show_var.get() else "•" * len(pwd)
        self.tested_info_label.config(
            text=f"Evaluated Password: {display_pwd} ({length} chars)"
        )

        if already_exists:
            score = 0
            rating = "Not Secure (Reused)"
            tier_color = self.fail_fg
            suggestions.insert(
                0,
                "This exact password was already saved previously. Click 'Enter New Password' to try another.",
            )
            self.rating_label.config(
                text=f"Strength Level: {rating}", fg=tier_color
            )
            self.score_label.config(
                text=f"Numerical Score: {score} / 100", fg=tier_color
            )
            self.bar_fill.config(bg=tier_color)
            self.bar_fill.place(x=0, y=0, relheight=1.0, relwidth=0.0)
            self.suggestion_label.config(
                text="Suggestions: " + " ".join(suggestions)
            )
            self.status_label.config(
                text=f"✘ Not saved: Duplicate found in saved_passwords/{existing_file}",
                fg=self.fail_fg,
            )
        else:
            # 4. Determine Strength Tier
            if score < 25:
                rating = "Not Secure"
                tier_color = "#DC2626"  # Crimson
            elif score < 50:
                rating = "Weak"
                tier_color = "#EA580C"  # Warm terracotta
            elif score < 70 or not has_min_len:
                rating = "Average"
                tier_color = "#D97706"  # Amber gold
            elif score < 90:
                rating = "Strong"
                tier_color = "#0284C7"  # Cerulean blue
            else:
                rating = "Very Strong"
                tier_color = "#059669"  # Emerald green

            self.rating_label.config(
                text=f"Strength Level: {rating}", fg=tier_color
            )
            self.score_label.config(
                text=f"Numerical Score: {score} / 100", fg=tier_color
            )
            self.bar_fill.config(bg=tier_color)
            self.bar_fill.place(
                x=0, y=0, relheight=1.0, relwidth=score / 100.0
            )

            if suggestions:
                self.suggestion_label.config(
                    text="Suggestions: " + " ".join(suggestions)
                )
            else:
                self.suggestion_label.config(
                    text="Suggestions: Excellent! Every character is unique and all security criteria are met."
                )

            # 5. Save each new unique password in a separate text file
            self.save_to_file(
                pwd,
                rating,
                score,
                has_min_len,
                has_upper,
                has_lower,
                has_special,
                has_numeral,
                rep_chars,
                rep_nums,
                rep_special,
            )

        # 6. Clear Input Box & Switch Button to "Enter New Password"
        self.password_var.set("")
        self.entry.config(state="disabled")
        self.input_title_lbl.config(
            text="ANALYSIS COMPLETE — CLICK 'ENTER NEW PASSWORD' TO TEST ANOTHER",
            fg=self.new_btn,
        )
        self.action_btn.config(
            text="Enter New Password",
            bg=self.new_btn,
            activebackground=self.new_hover,
        )
        self.is_result_state = True
        self.action_btn.focus_set()

    def update_check(self, key, label_text, passed, pass_msg, fail_msg):
        status = pass_msg if passed else fail_msg
        symbol = "✔" if passed else "✘"
        fg = self.pass_fg if passed else self.fail_fg
        bg = self.pass_bg if passed else self.fail_bg
        self.validation_labels[key].config(
            text=f"  {symbol}  {label_text}: {status}",
            fg=fg,
            bg=bg,
            font=("Helvetica", 9, "bold"),
        )

    def save_to_file(
        self,
        pwd,
        rating,
        score,
        min_len,
        upper,
        lower,
        special,
        numeral,
        rep_chars,
        rep_nums,
        rep_special,
    ):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"password_{timestamp}.txt"
        filepath = os.path.join(self.save_dir, filename)

        report = (
            f"Password Analysis Report\n"
            f"========================\n"
            f"Timestamp              : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Password Entered       : {pwd}\n"
            f"Strength Rating        : {rating}\n"
            f"Numerical Score        : {score} / 100\n\n"
            f"Validation Breakdown:\n"
            f"- UNIQUE PASSWORD      : Yes\n"
            f"- MIN 8 CHARACTERS     : {'Yes' if min_len else 'No'} ({len(pwd)} chars)\n"
            f"- UPPERCASE            : {'Yes' if upper else 'No'}\n"
            f"- LOWERCASE            : {'Yes' if lower else 'No'}\n"
            f"- SPECIAL CHARACTERS   : {'Yes' if special else 'No'}\n"
            f"- NUMERALS             : {'Yes' if numeral else 'No'}\n"
            f"- REPEATED CHARS       : {'Yes' if rep_chars else 'No'}\n"
            f"- REPEATED NUMERALS    : {'Yes' if rep_nums else 'No'}\n"
            f"- REPEATED SPECIAL     : {'Yes' if rep_special else 'No'}\n"
        )

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(report)

        self.status_label.config(
            text=f"✔ Saved report to: saved_passwords/{filename}",
            fg=self.pass_fg,
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordStrengthApp(root)
    root.mainloop()