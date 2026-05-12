from __future__ import annotations

import os
import random
from typing import Callable

import customtkinter as ctk

from generators.base import GeneratorContext, GeneratorMeta, GeneratorPlugin
from utils.paths import exports_dir


class UsernameGeneratorFrame(ctk.CTkFrame):
    def __init__(self, master, ctx: GeneratorContext) -> None:
        super().__init__(master, fg_color="transparent")
        self.ctx = ctx

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self.title = ctk.CTkLabel(self, text="Username Generator", font=ctk.CTkFont(size=20, weight="bold"))
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

        self.style_var = ctk.StringVar(value="gaming")
        ctk.CTkLabel(self.controls, text="Style", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, sticky="w", padx=14, pady=(12, 4)
        )
        self.style_menu = ctk.CTkOptionMenu(
            self.controls,
            values=["Gaming", "Random", "Stylish", "Professional"],
            variable=self.style_var,
        )
        self.style_menu.grid(row=0, column=1, sticky="ew", padx=14, pady=(12, 4))

        self.prefix_label = ctk.CTkLabel(self.controls, text="Prefix (optional)", font=ctk.CTkFont(weight="bold"))
        self.prefix_label.grid(row=1, column=0, sticky="w", padx=14, pady=(8, 4))
        self.prefix_entry = ctk.CTkEntry(self.controls)
        self.prefix_entry.grid(row=1, column=1, sticky="ew", padx=14, pady=(8, 4))

        self.suffix_label = ctk.CTkLabel(self.controls, text="Suffix (optional)", font=ctk.CTkFont(weight="bold"))
        self.suffix_label.grid(row=2, column=0, sticky="w", padx=14, pady=(4, 12))
        self.suffix_entry = ctk.CTkEntry(self.controls)
        self.suffix_entry.grid(row=2, column=1, sticky="ew", padx=14, pady=(4, 12))

        btn_row = ctk.CTkFrame(self.controls, fg_color="transparent")
        btn_row.grid(row=3, column=0, columnspan=2, sticky="w", padx=14, pady=(0, 12))

        ctk.CTkButton(btn_row, text="Generate", command=self._generate).pack(side="left")
        ctk.CTkButton(btn_row, text="Bulk Generate (20)", command=self._bulk_generate).pack(side="left", padx=(10, 0))

    def _setup_result(self) -> None:
        self.result_frame.grid_columnconfigure(0, weight=1)

        self.result_label = ctk.CTkLabel(self.result_frame, text="Username:", font=ctk.CTkFont(weight="bold"))
        self.result_label.grid(row=0, column=0, sticky="w", padx=14, pady=(12, 4))

        self.result_display = ctk.CTkEntry(self.result_frame, font=ctk.CTkFont(family="Consolas", size=14))
        self.result_display.grid(row=1, column=0, sticky="ew", padx=14, pady=(0, 12))

        btn_row = ctk.CTkFrame(self.result_frame, fg_color="transparent")
        btn_row.grid(row=2, column=0, sticky="w", padx=14, pady=(0, 12))

        ctk.CTkButton(btn_row, text="Copy", command=self._copy).pack(side="left")
        ctk.CTkButton(btn_row, text="Export List", command=self._export_list).pack(side="left", padx=(10, 0))

    def _generate(self) -> None:
        username = self._make_username()
        self.result_display.delete(0, "end")
        self.result_display.insert(0, username)
        self._add_to_history(username)

    def _bulk_generate(self) -> None:
        for _ in range(20):
            username = self._make_username()
            self._add_to_history(username)
        self.ctx.toast_host.show("Generated 20 usernames", kind="success")

    def _make_username(self) -> str:
        style = self.style_var.get().lower()
        prefix = self.prefix_entry.get().strip()
        suffix = self.suffix_entry.get().strip()

        base = ""
        if style == "gaming":
            base = random.choice(
                [
                    "Shadow", "Ninja", "Dragon", "Phoenix", "Storm", "Blade", "Frost", "Thunder",
                    "Viper", "Wolf", "Ghost", "Reaper", "Hunter", "Sniper", "Warrior", "Knight",
                ]
            )
            base += random.choice(
                ["X", "Z", "Pro", "Elite", "Master", "King", "Lord", "Legend", "Prime", "Max"]
            )
            base += str(random.randint(1, 9999))
        elif style == "random":
            adjs = ["Cool", "Fast", "Silent", "Brave", "Smart", "Quick", "Happy", "Lucky", "Bold", "Sharp"]
            nouns = ["Fox", "Eagle", "Tiger", "Bear", "Hawk", "Shark", "Lion", "Wolf", "Eagle", "Panther"]
            base = random.choice(adjs) + random.choice(nouns) + str(random.randint(1, 999))
        elif style == "stylish":
            stylish = ["xX", "Xx", "Im", "Mr", "Dr", "Lord", "Sir"]
            middle = random.choice(["Shadow", "Dark", "Night", "Soul", "Mystic", "Cyber", "Neo", "Void"])
            base = random.choice(stylish) + middle + random.choice(stylish[::-1])
        else:
            first = random.choice(["Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Jamie", "Avery"])
            last = random.choice(["Smith", "Johnson", "Brown", "Davis", "Wilson", "Moore", "Taylor", "Anderson"])
            base = (first + last).lower()

        username = prefix + base + suffix
        return username[:30]  # limit length

    def _add_to_history(self, username: str) -> None:
        self.history.insert(0, username)
        del self.history[200:]
        self._refresh_history()

    def _refresh_history(self) -> None:
        for w in self.history_frame.winfo_children():
            w.destroy()
        for i, name in enumerate(self.history[:30]):
            entry = ctk.CTkEntry(self.history_frame, font=ctk.CTkFont(family="Consolas", size=12))
            entry.insert(0, name)
            entry.grid(row=i, column=0, sticky="ew", padx=10, pady=2)
            entry.configure(state="readonly")

    def _copy(self) -> None:
        import pyperclip

        pyperclip.copy(self.result_display.get())
        self.ctx.toast_host.show("Copied to clipboard", kind="success")

    def _export_list(self) -> None:
        path = os.path.join(exports_dir(), "usernames.txt")
        with open(path, "w", encoding="utf-8") as f:
            for name in self.history:
                f.write(name + "\n")
        self.ctx.toast_host.show("List exported", kind="success")
        self.ctx.storage.add_export_history({"generator": "username", "file": "usernames.txt"})


class UsernameGeneratorPlugin(GeneratorPlugin):
    meta = GeneratorMeta(
        id="username",
        name="Username Generator",
        category="Gaming",
        icon="👤",
        description="Generate gaming, random, stylish, or professional usernames with prefixes/suffixes.",
    )

    def __init__(self, storage) -> None:
        self.storage = storage

    def create_frame(self, master: ctk.CTkFrame, toast_host) -> ctk.CTkFrame:
        ctx = GeneratorContext(storage=self.storage, toast_host=toast_host)
        return UsernameGeneratorFrame(master, ctx)


def create_plugin(storage):
    return UsernameGeneratorPlugin(storage)
