from __future__ import annotations

import os
import random
from typing import Callable

import customtkinter as ctk

from generators.base import GeneratorContext, GeneratorMeta, GeneratorPlugin
from utils.paths import exports_dir


class FilenameGeneratorFrame(ctk.CTkFrame):
    def __init__(self, master, ctx: GeneratorContext) -> None:
        super().__init__(master, fg_color="transparent")
        self.ctx = ctx

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self.title = ctk.CTkLabel(self, text="File Name Generator", font=ctk.CTkFont(size=20, weight="bold"))
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

        self.mode_var = ctk.StringVar(value="numbered")
        ctk.CTkLabel(self.controls, text="Mode", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, sticky="w", padx=14, pady=(12, 4)
        )
        self.mode_menu = ctk.CTkOptionMenu(
            self.controls,
            values=["Numbered", "Random", "Timestamp", "UUID"],
            variable=self.mode_var,
        )
        self.mode_menu.grid(row=0, column=1, sticky="ew", padx=14, pady=(12, 4))

        self.prefix_label = ctk.CTkLabel(self.controls, text="Prefix", font=ctk.CTkFont(weight="bold"))
        self.prefix_label.grid(row=1, column=0, sticky="w", padx=14, pady=(8, 4))
        self.prefix_entry = ctk.CTkEntry(self.controls)
        self.prefix_entry.insert(0, "file")
        self.prefix_entry.grid(row=1, column=1, sticky="ew", padx=14, pady=(8, 4))

        self.suffix_label = ctk.CTkLabel(self.controls, text="Suffix", font=ctk.CTkFont(weight="bold"))
        self.suffix_label.grid(row=2, column=0, sticky="w", padx=14, pady=(4, 4))
        self.suffix_entry = ctk.CTkEntry(self.controls)
        self.suffix_entry.insert(0, ".txt")
        self.suffix_entry.grid(row=2, column=1, sticky="ew", padx=14, pady=(4, 4))

        self.count_label = ctk.CTkLabel(self.controls, text="Count", font=ctk.CTkFont(weight="bold"))
        self.count_label.grid(row=3, column=0, sticky="w", padx=14, pady=(4, 12))
        self.count_var = ctk.IntVar(value=5)
        self.count_slider = ctk.CTkSlider(
            self.controls, from_=1, to=50, variable=self.count_var, number_of_steps=49
        )
        self.count_slider.grid(row=3, column=1, sticky="ew", padx=14, pady=(4, 12))
        self.count_label_value = ctk.CTkLabel(self.controls, text="5")
        self.count_label_value.grid(row=3, column=2, padx=(0, 14), pady=(4, 12))
        self.count_slider.configure(command=lambda v: self.count_label_value.configure(text=str(int(v))))

        btn_row = ctk.CTkFrame(self.controls, fg_color="transparent")
        btn_row.grid(row=4, column=0, columnspan=3, sticky="w", padx=14, pady=(0, 12))

        ctk.CTkButton(btn_row, text="Generate", command=self._generate).pack(side="left")
        ctk.CTkButton(btn_row, text="Export List", command=self._export_list).pack(side="left", padx=(10, 0))

    def _setup_result(self) -> None:
        self.result_frame.grid_columnconfigure(0, weight=1)

        self.result_label = ctk.CTkLabel(self.result_frame, text="Generated Names:", font=ctk.CTkFont(weight="bold"))
        self.result_label.grid(row=0, column=0, sticky="w", padx=14, pady=(12, 4))

        self.result_display = ctk.CTkTextbox(self.result_frame, height=120, font=ctk.CTkFont(family="Consolas", size=12))
        self.result_display.grid(row=1, column=0, sticky="ew", padx=14, pady=(0, 12))

        btn_row = ctk.CTkFrame(self.result_frame, fg_color="transparent")
        btn_row.grid(row=2, column=0, sticky="w", padx=14, pady=(0, 12))

        ctk.CTkButton(btn_row, text="Copy All", command=self._copy_all).pack(side="left")

    def _generate(self) -> None:
        mode = self.mode_var.get().lower()
        prefix = self.prefix_entry.get().strip()
        suffix = self.suffix_entry.get().strip()
        count = self.count_var.get()

        names = []
        for i in range(1, count + 1):
            if mode == "numbered":
                name = f"{prefix}_{i:03d}{suffix}"
            elif mode == "random":
                name = f"{prefix}_{self._random_string(8)}{suffix}"
            elif mode == "timestamp":
                import time
                ts = int(time.time())
                name = f"{prefix}_{ts}{suffix}"
            elif mode == "uuid":
                import uuid
                name = f"{prefix}_{uuid.uuid4().hex[:8]}{suffix}"
            else:
                name = f"{prefix}_{i}{suffix}"
            names.append(name)

        combined = "\n".join(names)
        self.result_display.delete("0.0", "end")
        self.result_display.insert("0.0", combined)

        self.history.extend(names)
        del self.history[500:]
        self._refresh_history()

    def _random_string(self, length: int) -> str:
        import string
        return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))

    def _refresh_history(self) -> None:
        for w in self.history_frame.winfo_children():
            w.destroy()
        for i, name in enumerate(self.history[:40]):
            entry = ctk.CTkEntry(self.history_frame, font=ctk.CTkFont(family="Consolas", size=12))
            entry.insert(0, name)
            entry.grid(row=i, column=0, sticky="ew", padx=10, pady=2)
            entry.configure(state="readonly")

    def _copy_all(self) -> None:
        import pyperclip

        pyperclip.copy(self.result_display.get("0.0", "end-1c"))
        self.ctx.toast_host.show("Copied to clipboard", kind="success")

    def _export_list(self) -> None:
        path = os.path.join(exports_dir(), "filenames.txt")
        with open(path, "w", encoding="utf-8") as f:
            for name in self.history:
                f.write(name + "\n")
        self.ctx.toast_host.show("List exported", kind="success")
        self.ctx.storage.add_export_history({"generator": "filename", "file": "filenames.txt"})


class FilenameGeneratorPlugin(GeneratorPlugin):
    meta = GeneratorMeta(
        id="filename",
        name="File Name Generator",
        category="Utility",
        icon="📂",
        description="Generate batch filenames with numbering, random, timestamp, or UUID patterns.",
    )

    def __init__(self, storage) -> None:
        self.storage = storage

    def create_frame(self, master: ctk.CTkFrame, toast_host) -> ctk.CTkFrame:
        ctx = GeneratorContext(storage=self.storage, toast_host=toast_host)
        return FilenameGeneratorFrame(master, ctx)


def create_plugin(storage):
    return FilenameGeneratorPlugin(storage)
