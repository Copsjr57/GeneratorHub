from __future__ import annotations

import os
import secrets
import string
from typing import Callable

import customtkinter as ctk

from generators.base import GeneratorContext, GeneratorMeta, GeneratorPlugin
from utils.paths import exports_dir


class PasswordGeneratorFrame(ctk.CTkFrame):
    def __init__(self, master, ctx: GeneratorContext) -> None:
        super().__init__(master, fg_color="transparent")
        self.ctx = ctx

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self.title = ctk.CTkLabel(self, text="Password Generator", font=ctk.CTkFont(size=20, weight="bold"))
        self.title.grid(row=0, column=0, sticky="w", padx=4, pady=(2, 12))

        self.controls = ctk.CTkFrame(self, corner_radius=16)
        self.controls.grid(row=1, column=0, sticky="ew", padx=4, pady=(0, 12))
        self._setup_controls()

        self.result_frame = ctk.CTkFrame(self, corner_radius=16)
        self.result_frame.grid(row=2, column=0, sticky="ew", padx=4, pady=(0, 12))
        self._setup_result()

        self.history_frame = ctk.CTkScrollableFrame(self, corner_radius=16)
        self.history_frame.grid(row=3, column=0, sticky="nsew", padx=4, pady=(0, 4))
        self.history_frame.grid_columnconfigure(0, weight=1)

        self.history: list[str] = []
        self._refresh_history()

    def _setup_controls(self) -> None:
        self.controls.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.controls, text="Length", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, sticky="w", padx=14, pady=(12, 4)
        )
        self.length_var = ctk.IntVar(value=16)
        self.length_slider = ctk.CTkSlider(
            self.controls, from_=8, to=64, variable=self.length_var, number_of_steps=56
        )
        self.length_slider.grid(row=0, column=1, sticky="ew", padx=14, pady=(12, 4))
        self.length_label = ctk.CTkLabel(self.controls, text="16")
        self.length_label.grid(row=0, column=2, padx=(0, 14), pady=(12, 4))
        self.length_slider.configure(command=lambda v: self.length_label.configure(text=str(int(v))))

        self.use_upper = ctk.BooleanVar(value=True)
        self.use_lower = ctk.BooleanVar(value=True)
        self.use_digits = ctk.BooleanVar(value=True)
        self.use_symbols = ctk.BooleanVar(value=True)

        for i, (var, text) in enumerate(
            [
                (self.use_upper, "Uppercase"),
                (self.use_lower, "Lowercase"),
                (self.use_digits, "Digits"),
                (self.use_symbols, "Symbols"),
            ]
        ):
            ctk.CTkSwitch(self.controls, text=text, variable=var).grid(
                row=1, column=i % 2, columnspan=2, sticky="w", padx=14, pady=(4, 12)
            )
            if i % 2 == 1:
                self.controls.grid_rowconfigure(i + 1, weight=1)

        btn_row = ctk.CTkFrame(self.controls, fg_color="transparent")
        btn_row.grid(row=2, column=0, columnspan=3, sticky="w", padx=14, pady=(0, 12))

        ctk.CTkButton(btn_row, text="Generate", command=self._generate).pack(side="left")
        ctk.CTkButton(btn_row, text="Bulk Generate (10)", command=self._bulk_generate).pack(side="left", padx=(10, 0))

    def _setup_result(self) -> None:
        self.result_frame.grid_columnconfigure(0, weight=1)

        self.result_label = ctk.CTkLabel(self.result_frame, text="Password:", font=ctk.CTkFont(weight="bold"))
        self.result_label.grid(row=0, column=0, sticky="w", padx=14, pady=(12, 4))

        self.result_display = ctk.CTkEntry(self.result_frame, font=ctk.CTkFont(family="Consolas", size=14))
        self.result_display.grid(row=1, column=0, sticky="ew", padx=14, pady=(0, 8))

        self.strength_label = ctk.CTkLabel(self.result_frame, text="Strength: –")
        self.strength_label.grid(row=2, column=0, sticky="w", padx=14, pady=(0, 12))

        btn_row = ctk.CTkFrame(self.result_frame, fg_color="transparent")
        btn_row.grid(row=3, column=0, sticky="w", padx=14, pady=(0, 12))

        ctk.CTkButton(btn_row, text="Copy", command=self._copy).pack(side="left")
        ctk.CTkButton(btn_row, text="Export History", command=self._export_history).pack(side="left", padx=(10, 0))

    def _generate(self) -> None:
        pwd = self._make_password()
        self.result_display.delete(0, "end")
        self.result_display.insert(0, pwd)
        self._update_strength(pwd)
        self._add_to_history(pwd)

    def _bulk_generate(self) -> None:
        for _ in range(10):
            pwd = self._make_password()
            self._add_to_history(pwd)
        self.ctx.toast_host.show("Generated 10 passwords", kind="success")

    def _make_password(self) -> str:
        length = self.length_var.get()
        charset = ""
        if self.use_upper.get():
            charset += string.ascii_uppercase
        if self.use_lower.get():
            charset += string.ascii_lowercase
        if self.use_digits.get():
            charset += string.digits
        if self.use_symbols.get():
            charset += "!@#$%^&*()_+-=[]{}|;:,.<>?"

        if not charset:
            charset = string.ascii_letters + string.digits

        return "".join(secrets.choice(charset) for _ in range(length))

    def _update_strength(self, pwd: str) -> None:
        score = 0
        if len(pwd) >= 12:
            score += 1
        if len(pwd) >= 20:
            score += 1
        if any(c.islower() for c in pwd):
            score += 1
        if any(c.isupper() for c in pwd):
            score += 1
        if any(c.isdigit() for c in pwd):
            score += 1
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in pwd):
            score += 1

        labels = ["Very Weak", "Weak", "Fair", "Good", "Strong", "Very Strong"]
        self.strength_label.configure(text=f"Strength: {labels[min(score, len(labels)-1)]}")

    def _add_to_history(self, pwd: str) -> None:
        self.history.insert(0, pwd)
        del self.history[100:]
        self._refresh_history()

    def _refresh_history(self) -> None:
        for w in self.history_frame.winfo_children():
            w.destroy()
        for i, pwd in enumerate(self.history[:20]):
            entry = ctk.CTkEntry(self.history_frame, font=ctk.CTkFont(family="Consolas", size=12))
            entry.insert(0, pwd)
            entry.grid(row=i, column=0, sticky="ew", padx=10, pady=2)
            entry.configure(state="readonly")

    def _copy(self) -> None:
        import pyperclip

        pyperclip.copy(self.result_display.get())
        self.ctx.toast_host.show("Copied to clipboard", kind="success")

    def _export_history(self) -> None:
        path = os.path.join(exports_dir(), "password_history.txt")
        with open(path, "w", encoding="utf-8") as f:
            for pwd in self.history:
                f.write(pwd + "\n")
        self.ctx.toast_host.show("History exported", kind="success")
        self.ctx.storage.add_export_history({"generator": "password", "file": "password_history.txt"})


class PasswordGeneratorPlugin(GeneratorPlugin):
    meta = GeneratorMeta(
        id="password",
        name="Password Generator",
        category="Security",
        icon="🔐",
        description="Generate secure passwords with options and strength meter.",
    )

    def __init__(self, storage) -> None:
        self.storage = storage

    def create_frame(self, master: ctk.CTkFrame, toast_host) -> ctk.CTkFrame:
        ctx = GeneratorContext(storage=self.storage, toast_host=toast_host)
        return PasswordGeneratorFrame(master, ctx)


def create_plugin(storage):
    return PasswordGeneratorPlugin(storage)
