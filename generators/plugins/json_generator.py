from __future__ import annotations

import json
import os
from typing import Callable

import customtkinter as ctk

from generators.base import GeneratorContext, GeneratorMeta, GeneratorPlugin
from utils.paths import exports_dir


class JSONGeneratorFrame(ctk.CTkFrame):
    def __init__(self, master, ctx: GeneratorContext) -> None:
        super().__init__(master, fg_color="transparent")
        self.ctx = ctx

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.title = ctk.CTkLabel(self, text="JSON Generator", font=ctk.CTkFont(size=20, weight="bold"))
        self.title.grid(row=0, column=0, sticky="w", padx=4, pady=(2, 12))

        self.controls = ctk.CTkFrame(self, corner_radius=16)
        self.controls.grid(row=1, column=0, sticky="ew", padx=4, pady=(0, 12))
        self._setup_controls()

        self.editor_frame = ctk.CTkFrame(self, corner_radius=16)
        self.editor_frame.grid(row=2, column=0, sticky="nsew", padx=4, pady=(0, 4))
        self.editor_frame.grid_columnconfigure(0, weight=1)
        self.editor_frame.grid_rowconfigure(1, weight=1)

        self.editor_label = ctk.CTkLabel(self.editor_frame, text="JSON Output:", font=ctk.CTkFont(weight="bold"))
        self.editor_label.grid(row=0, column=0, sticky="w", padx=14, pady=(12, 4))

        self.editor = ctk.CTkTextbox(self.editor_frame, font=ctk.CTkFont(family="Consolas", size=12))
        self.editor.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 12))

        self._generate_sample()

    def _setup_controls(self) -> None:
        self.controls.grid_columnconfigure(1, weight=1)

        self.template_var = ctk.StringVar(value="user_profile")
        ctk.CTkLabel(self.controls, text="Template", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, sticky="w", padx=14, pady=(12, 4)
        )
        self.template_menu = ctk.CTkOptionMenu(
            self.controls,
            values=["User Profile", "API Response", "Config File", "Product Catalog", "Empty Object"],
            variable=self.template_var,
            command=self._on_template_change,
        )
        self.template_menu.grid(row=0, column=1, sticky="ew", padx=14, pady=(12, 4))

        self.format_var = ctk.BooleanVar(value=True)
        ctk.CTkSwitch(self.controls, text="Pretty Format", variable=self.format_var).grid(
            row=1, column=0, columnspan=2, sticky="w", padx=14, pady=(4, 12)
        )

        btn_row = ctk.CTkFrame(self.controls, fg_color="transparent")
        btn_row.grid(row=2, column=0, columnspan=2, sticky="w", padx=14, pady=(0, 12))

        ctk.CTkButton(btn_row, text="Generate", command=self._generate_sample).pack(side="left")
        ctk.CTkButton(btn_row, text="Validate", command=self._validate).pack(side="left", padx=(10, 0))
        ctk.CTkButton(btn_row, text="Export JSON", command=self._export).pack(side="left", padx=(10, 0))
        ctk.CTkButton(btn_row, text="Copy", command=self._copy).pack(side="left", padx=(10, 0))

    def _on_template_change(self, _=None) -> None:
        self._generate_sample()

    def _generate_sample(self) -> None:
        template = self.template_var.get().lower().replace(" ", "_")
        data = None

        if template == "user_profile":
            data = {
                "id": 12345,
                "username": "john_doe",
                "email": "john@example.com",
                "profile": {
                    "firstName": "John",
                    "lastName": "Doe",
                    "age": 30,
                    "city": "New York",
                    "country": "USA"
                },
                "preferences": {
                    "theme": "dark",
                    "notifications": True,
                    "language": "en"
                },
                "createdAt": "2024-01-15T10:30:00Z",
                "isActive": True
            }
        elif template == "api_response":
            data = {
                "status": "success",
                "code": 200,
                "message": "Data retrieved successfully",
                "data": {
                    "users": [
                        {"id": 1, "name": "Alice", "role": "admin"},
                        {"id": 2, "name": "Bob", "role": "user"},
                        {"id": 3, "name": "Charlie", "role": "moderator"}
                    ],
                    "pagination": {
                        "page": 1,
                        "limit": 10,
                        "total": 3,
                        "hasNext": False
                    }
                },
                "timestamp": "2024-01-15T10:30:00Z"
            }
        elif template == "config_file":
            data = {
                "application": {
                    "name": "MyApp",
                    "version": "1.0.0",
                    "environment": "production"
                },
                "database": {
                    "host": "localhost",
                    "port": 5432,
                    "name": "myapp_db",
                    "username": "admin",
                    "password": "secret123"
                },
                "features": {
                    "enableLogging": True,
                    "enableCache": True,
                    "maxConnections": 100,
                    "timeout": 30
                },
                "endpoints": {
                    "api": "https://api.example.com",
                    "auth": "https://auth.example.com",
                    "cdn": "https://cdn.example.com"
                }
            }
        elif template == "product_catalog":
            data = {
                "catalog": {
                    "id": "cat_001",
                    "name": "Electronics",
                    "description": "Latest electronic devices",
                    "products": [
                        {
                            "id": "prod_001",
                            "name": "Smartphone X",
                            "price": 699.99,
                            "currency": "USD",
                            "category": "Mobile",
                            "specs": {
                                "screen": "6.5 inches",
                                "storage": "128GB",
                                "camera": "48MP",
                                "battery": "4000mAh"
                            },
                            "availability": True
                        },
                        {
                            "id": "prod_002",
                            "name": "Laptop Pro",
                            "price": 1299.99,
                            "currency": "USD",
                            "category": "Computer",
                            "specs": {
                                "cpu": "Intel i7",
                                "ram": "16GB",
                                "storage": "512GB SSD",
                                "display": "15.6 inches"
                            },
                            "availability": True
                        }
                    ]
                }
            }
        else:
            data = {}

        if self.format_var.get():
            json_str = json.dumps(data, indent=2, ensure_ascii=False)
        else:
            json_str = json.dumps(data, separators=(',', ':'), ensure_ascii=False)

        self.editor.delete("0.0", "end")
        self.editor.insert("0.0", json_str)

    def _validate(self) -> None:
        content = self.editor.get("0.0", "end-1c").strip()
        if not content:
            self.ctx.toast_host.show("Empty JSON", kind="error")
            return

        try:
            json.loads(content)
            self.ctx.toast_host.show("Valid JSON", kind="success")
        except json.JSONDecodeError as e:
            self.ctx.toast_host.show(f"Invalid JSON: {e}", kind="error")

    def _export(self) -> None:
        content = self.editor.get("0.0", "end-1c").strip()
        if not content:
            self.ctx.toast_host.show("Empty JSON", kind="error")
            return

        try:
            json.loads(content)  # Validate before export
            path = os.path.join(exports_dir(), "output.json")
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            self.ctx.toast_host.show("Exported to output.json", kind="success")
            self.ctx.storage.add_export_history({"generator": "json", "file": "output.json"})
        except json.JSONDecodeError as e:
            self.ctx.toast_host.show(f"Cannot export invalid JSON: {e}", kind="error")

    def _copy(self) -> None:
        import pyperclip

        content = self.editor.get("0.0", "end-1c").strip()
        if not content:
            self.ctx.toast_host.show("Empty JSON", kind="error")
            return

        try:
            json.loads(content)  # Validate before copy
            pyperclip.copy(content)
            self.ctx.toast_host.show("Copied to clipboard", kind="success")
        except json.JSONDecodeError as e:
            self.ctx.toast_host.show(f"Cannot copy invalid JSON: {e}", kind="error")


class JSONGeneratorPlugin(GeneratorPlugin):
    meta = GeneratorMeta(
        id="json",
        name="JSON Generator",
        category="Developer Tools",
        icon="{}",
        description="Generate JSON templates with pretty formatting and validation.",
    )

    def __init__(self, storage) -> None:
        self.storage = storage

    def create_frame(self, master: ctk.CTkFrame, toast_host) -> ctk.CTkFrame:
        ctx = GeneratorContext(storage=self.storage, toast_host=toast_host)
        return JSONGeneratorFrame(master, ctx)


def create_plugin(storage):
    return JSONGeneratorPlugin(storage)
