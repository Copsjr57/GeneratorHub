from __future__ import annotations

import os
from typing import Callable

import customtkinter as ctk
import qrcode
from PIL import Image, ImageTk

from generators.base import GeneratorContext, GeneratorMeta, GeneratorPlugin
from utils.paths import exports_dir


class QRGeneratorFrame(ctk.CTkFrame):
    def __init__(self, master, ctx: GeneratorContext) -> None:
        super().__init__(master, fg_color="transparent")
        self.ctx = ctx

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.title = ctk.CTkLabel(self, text="QR Code Generator", font=ctk.CTkFont(size=20, weight="bold"))
        self.title.grid(row=0, column=0, sticky="w", padx=4, pady=(2, 12))

        self.controls = ctk.CTkFrame(self, corner_radius=16)
        self.controls.grid(row=1, column=0, sticky="ew", padx=4, pady=(0, 12))
        self._setup_controls()

        self.preview_frame = ctk.CTkFrame(self, corner_radius=16)
        self.preview_frame.grid(row=2, column=0, sticky="nsew", padx=4, pady=(0, 4))
        self.preview_frame.grid_columnconfigure(0, weight=1)
        self.preview_frame.grid_rowconfigure(1, weight=1)

        self.preview_label = ctk.CTkLabel(self.preview_frame, text="Preview", font=ctk.CTkFont(weight="bold"))
        self.preview_label.grid(row=0, column=0, sticky="w", padx=14, pady=(12, 4))

        self.image_label = ctk.CTkLabel(self.preview_frame, text="QR code will appear here")
        self.image_label.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 12))

        self.history: list[dict] = []

    def _setup_controls(self) -> None:
        self.controls.grid_columnconfigure(1, weight=1)

        self.type_var = ctk.StringVar(value="text")
        ctk.CTkLabel(self.controls, text="Type", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, sticky="w", padx=14, pady=(12, 4)
        )
        self.type_menu = ctk.CTkOptionMenu(
            self.controls,
            values=["Text", "URL", "Wi-Fi", "Contact"],
            variable=self.type_var,
            command=self._on_type_change,
        )
        self.type_menu.grid(row=0, column=1, sticky="ew", padx=14, pady=(12, 4))

        self.text_label = ctk.CTkLabel(self.controls, text="Content", font=ctk.CTkFont(weight="bold"))
        self.text_label.grid(row=1, column=0, sticky="w", padx=14, pady=(8, 4))
        self.text_entry = ctk.CTkTextbox(self.controls, height=80)
        self.text_entry.grid(row=1, column=1, sticky="ew", padx=14, pady=(8, 4))
        self.text_entry.insert("0.0", "https://example.com")
        self.text_entry.bind("<KeyRelease>", lambda _e: self._generate_qr())

        # Wi-Fi fields
        self.ssid_label = ctk.CTkLabel(self.controls, text="SSID", font=ctk.CTkFont(weight="bold"))
        self.ssid_entry = ctk.CTkEntry(self.controls)
        self.ssid_entry.insert(0, "MyNetwork")
        self.ssid_entry.bind("<KeyRelease>", lambda _e: self._generate_qr())

        self.password_label = ctk.CTkLabel(self.controls, text="Password", font=ctk.CTkFont(weight="bold"))
        self.password_entry = ctk.CTkEntry(self.controls, show="*")
        self.password_entry.insert(0, "secret123")
        self.password_entry.bind("<KeyRelease>", lambda _e: self._generate_qr())

        self.security_var = ctk.StringVar(value="WPA")
        self.security_label = ctk.CTkLabel(self.controls, text="Security", font=ctk.CTkFont(weight="bold"))
        self.security_menu = ctk.CTkOptionMenu(
            self.controls, values=["WPA", "WEP", "nopass"], variable=self.security_var, command=self._generate_qr
        )

        # Contact fields
        self.name_label = ctk.CTkLabel(self.controls, text="Name", font=ctk.CTkFont(weight="bold"))
        self.name_entry = ctk.CTkEntry(self.controls)
        self.name_entry.insert(0, "John Doe")
        self.name_entry.bind("<KeyRelease>", lambda _e: self._generate_qr())

        self.phone_label = ctk.CTkLabel(self.controls, text="Phone", font=ctk.CTkFont(weight="bold"))
        self.phone_entry = ctk.CTkEntry(self.controls)
        self.phone_entry.insert(0, "+1234567890")
        self.phone_entry.bind("<KeyRelease>", lambda _e: self._generate_qr())

        self.email_label = ctk.CTkLabel(self.controls, text="Email", font=ctk.CTkFont(weight="bold"))
        self.email_entry = ctk.CTkEntry(self.controls)
        self.email_entry.insert(0, "john@example.com")
        self.email_entry.bind("<KeyRelease>", lambda _e: self._generate_qr())

        btn_row = ctk.CTkFrame(self.controls, fg_color="transparent")
        btn_row.grid(row=10, column=0, columnspan=2, sticky="w", padx=14, pady=(8, 12))

        ctk.CTkButton(btn_row, text="Generate", command=self._generate_qr).pack(side="left")
        ctk.CTkButton(btn_row, text="Export PNG", command=self._export_png).pack(side="left", padx=(10, 0))
        ctk.CTkButton(btn_row, text="Export SVG", command=self._export_svg).pack(side="left", padx=(10, 0))

        # Defer QR generation until UI is fully set up
        self.after(100, self._on_type_change)

    def _on_type_change(self, _=None) -> None:
        # Hide all extra fields
        for w in [
            self.ssid_label,
            self.ssid_entry,
            self.password_label,
            self.password_entry,
            self.security_label,
            self.security_menu,
            self.name_label,
            self.name_entry,
            self.phone_label,
            self.phone_entry,
            self.email_label,
            self.email_entry,
        ]:
            w.grid_remove()

        typ = self.type_var.get().lower()
        if typ == "wi-fi":
            row = 2
            for w, col in [
                (self.ssid_label, 0),
                (self.ssid_entry, 1),
                (self.password_label, 0),
                (self.password_entry, 1),
                (self.security_label, 0),
                (self.security_menu, 1),
            ]:
                w.grid(row=row, column=col, sticky="ew", padx=14, pady=(8, 4))
                row += 1
        elif typ == "contact":
            row = 2
            for w, col in [
                (self.name_label, 0),
                (self.name_entry, 1),
                (self.phone_label, 0),
                (self.phone_entry, 1),
                (self.email_label, 0),
                (self.email_entry, 1),
            ]:
                w.grid(row=row, column=col, sticky="ew", padx=14, pady=(8, 4))
                row += 1

        self._generate_qr()

    def _get_content(self) -> str:
        typ = self.type_var.get().lower()
        if typ == "text":
            return self.text_entry.get("0.0", "end-1c")
        elif typ == "url":
            return self.text_entry.get("0.0", "end-1c")
        elif typ == "wi-fi":
            ssid = self.ssid_entry.get()
            pwd = self.password_entry.get()
            sec = self.security_var.get()
            return f"WIFI:T:{sec};S:{ssid};P:{pwd};;"
        elif typ == "contact":
            name = self.name_entry.get()
            phone = self.phone_entry.get()
            email = self.email_entry.get()
            return f"BEGIN:VCARD\nFN:{name}\nTEL:{phone}\nEMAIL:{email}\nEND:VCARD"
        return ""

    def _generate_qr(self) -> None:
        content = self._get_content()
        if not content:
            self.image_label.configure(image="", text="QR code will appear here")
            return

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(content)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white").convert("RGBA")
        img.thumbnail((300, 300), Image.Resampling.LANCZOS)

        photo = ImageTk.PhotoImage(img)
        self.image_label.configure(image=photo, text="")
        self.image_label.image = photo  # keep reference

    def _export_png(self) -> None:
        content = self._get_content()
        if not content:
            self.ctx.toast_host.show("Nothing to export", kind="error")
            return

        qr = qrcode.make(content)
        path = os.path.join(exports_dir(), "qr_code.png")
        qr.save(path)
        self.ctx.toast_host.show("Exported as qr_code.png", kind="success")
        self.ctx.storage.add_export_history({"generator": "qr", "file": "qr_code.png"})

    def _export_svg(self) -> None:
        import qrcode.image.svg

        content = self._get_content()
        if not content:
            self.ctx.toast_host.show("Nothing to export", kind="error")
            return

        qr = qrcode.QRCode(
            image_factory=qrcode.image.svg.SvgImage,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
        )
        qr.add_data(content)
        qr.make(fit=True)

        img = qr.make_image()
        path = os.path.join(exports_dir(), "qr_code.svg")
        img.save(path)
        self.ctx.toast_host.show("Exported as qr_code.svg", kind="success")
        self.ctx.storage.add_export_history({"generator": "qr", "file": "qr_code.svg"})


class QRGeneratorPlugin(GeneratorPlugin):
    meta = GeneratorMeta(
        id="qr",
        name="QR Code Generator",
        category="Utility",
        icon="📱",
        description="Generate QR codes from text, URLs, Wi-Fi, or contact cards.",
    )

    def __init__(self, storage) -> None:
        self.storage = storage

    def create_frame(self, master: ctk.CTkFrame, toast_host) -> ctk.CTkFrame:
        ctx = GeneratorContext(storage=self.storage, toast_host=toast_host)
        return QRGeneratorFrame(master, ctx)


def create_plugin(storage):
    return QRGeneratorPlugin(storage)
