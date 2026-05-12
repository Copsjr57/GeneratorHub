from __future__ import annotations

import os
from typing import Callable

import customtkinter as ctk
from markdown import markdown

from generators.base import GeneratorContext, GeneratorMeta, GeneratorPlugin
from utils.paths import exports_dir


class ReadmeGeneratorFrame(ctk.CTkFrame):
    def __init__(self, master, ctx: GeneratorContext) -> None:
        super().__init__(master, fg_color="transparent")
        self.ctx = ctx

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.title = ctk.CTkLabel(self, text="README Generator", font=ctk.CTkFont(size=20, weight="bold"))
        self.title.grid(row=0, column=0, sticky="w", padx=4, pady=(2, 12))

        self.form = ctk.CTkFrame(self, corner_radius=16)
        self.form.grid(row=1, column=0, sticky="ew", padx=4, pady=(0, 12))
        self.form.grid_columnconfigure(1, weight=1)

        self._fields = {}
        self._setup_form()

        self.preview = ctk.CTkTextbox(self, wrap="word", font=ctk.CTkFont(family="Consolas", size=12))
        self.preview.grid(row=2, column=0, sticky="nsew", padx=4, pady=(0, 4))

        self._refresh_preview()

    def _setup_form(self) -> None:
        fields = [
            ("Project Name", "name", "My Awesome Project"),
            ("Description", "description", "A short description of the project."),
            ("Features", "features", "- Feature 1\n- Feature 2\n- Feature 3"),
            ("Installation", "installation", "```bash\npip install myproject\n```"),
            ("Usage", "usage", "```python\nimport myproject\nmyproject.run()\n```"),
            ("Technologies", "technologies", "- Python 3.11+\n- FastAPI\n- PostgreSQL"),
            ("License", "license", "MIT"),
        ]

        for i, (label, key, default) in enumerate(fields):
            ctk.CTkLabel(self.form, text=label, font=ctk.CTkFont(weight="bold")).grid(
                row=i, column=0, sticky="w", padx=14, pady=(8, 4)
            )
            entry = ctk.CTkTextbox(self.form, height=60)
            entry.insert("0.0", default)
            entry.grid(row=i, column=1, sticky="ew", padx=14, pady=(8, 4))
            entry.bind("<KeyRelease>", lambda _e, k=key: self._refresh_preview())
            self._fields[key] = entry

        btn_row = ctk.CTkFrame(self.form, fg_color="transparent")
        btn_row.grid(row=len(fields), column=0, columnspan=2, sticky="w", padx=14, pady=(8, 12))

        ctk.CTkButton(btn_row, text="Export README.md", command=self._export).pack(side="left")
        ctk.CTkButton(btn_row, text="Copy to Clipboard", command=self._copy).pack(side="left", padx=(10, 0))

    def _refresh_preview(self) -> None:
        md = self._build_markdown()
        self.preview.delete("0.0", "end")
        self.preview.insert("0.0", md)

    def _build_markdown(self) -> str:
        data = {k: v.get("0.0", "end-1c") for k, v in self._fields.items()}
        return f"""# {data['name']}

{data['description']}

## Features

{data['features']}

## Installation

{data['installation']}

## Usage

{data['usage']}

## Technologies

{data['technologies']}

## License

{data['license']}
"""

    def _export(self) -> None:
        md = self._build_markdown()
        name = self._fields["name"].get("0.0", "end-1c").strip() or "README"
        safe_name = "".join(c for c in name if c.isalnum() or c in (" ", "-", "_")).rstrip()
        filename = f"{safe_name}.md"
        path = os.path.join(exports_dir(), filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(md)
        self.ctx.toast_host.show(f"Exported to {filename}", kind="success")
        self.ctx.storage.add_export_history({"generator": "readme", "file": filename})

    def _copy(self) -> None:
        import pyperclip

        pyperclip.copy(self._build_markdown())
        self.ctx.toast_host.show("Copied to clipboard", kind="success")


class ReadmeGeneratorPlugin(GeneratorPlugin):
    meta = GeneratorMeta(
        id="readme",
        name="README Generator",
        category="Developer Tools",
        icon="📄",
        description="Generate professional GitHub README files with sections and export.",
    )

    def __init__(self, storage) -> None:
        self.storage = storage

    def create_frame(self, master: ctk.CTkFrame, toast_host) -> ctk.CTkFrame:
        ctx = GeneratorContext(storage=self.storage, toast_host=toast_host)
        return ReadmeGeneratorFrame(master, ctx)


def create_plugin(storage):
    return ReadmeGeneratorPlugin(storage)
