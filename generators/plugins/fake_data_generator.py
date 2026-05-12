from __future__ import annotations

import os
import random
from typing import Callable

import customtkinter as ctk

from generators.base import GeneratorContext, GeneratorMeta, GeneratorPlugin
from utils.paths import exports_dir


class FakeDataGeneratorFrame(ctk.CTkFrame):
    def __init__(self, master, ctx: GeneratorContext) -> None:
        super().__init__(master, fg_color="transparent")
        self.ctx = ctx

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self.title = ctk.CTkLabel(self, text="Fake Data Generator", font=ctk.CTkFont(size=20, weight="bold"))
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

        self.history: list[dict] = []
        self._refresh_history()

    def _setup_controls(self) -> None:
        self.controls.grid_columnconfigure(1, weight=1)

        self.type_var = ctk.StringVar(value="name")
        ctk.CTkLabel(self.controls, text="Data Type", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, sticky="w", padx=14, pady=(12, 4)
        )
        self.type_menu = ctk.CTkOptionMenu(
            self.controls,
            values=["Name", "Email", "Phone", "Address", "Full Profile"],
            variable=self.type_var,
        )
        self.type_menu.grid(row=0, column=1, sticky="ew", padx=14, pady=(12, 4))

        self.count_label = ctk.CTkLabel(self.controls, text="Count", font=ctk.CTkFont(weight="bold"))
        self.count_label.grid(row=1, column=0, sticky="w", padx=14, pady=(8, 4))
        self.count_var = ctk.IntVar(value=5)
        self.count_slider = ctk.CTkSlider(
            self.controls, from_=1, to=50, variable=self.count_var, number_of_steps=49
        )
        self.count_slider.grid(row=1, column=1, sticky="ew", padx=14, pady=(8, 4))
        self.count_label_value = ctk.CTkLabel(self.controls, text="5")
        self.count_label_value.grid(row=1, column=2, padx=(0, 14), pady=(8, 4))
        self.count_slider.configure(command=lambda v: self.count_label_value.configure(text=str(int(v))))

        btn_row = ctk.CTkFrame(self.controls, fg_color="transparent")
        btn_row.grid(row=2, column=0, columnspan=3, sticky="w", padx=14, pady=(8, 12))

        ctk.CTkButton(btn_row, text="Generate", command=self._generate).pack(side="left")
        ctk.CTkButton(btn_row, text="Export All", command=self._export_all).pack(side="left", padx=(10, 0))

    def _setup_result(self) -> None:
        self.result_frame.grid_columnconfigure(0, weight=1)

        self.result_label = ctk.CTkLabel(self.result_frame, text="Generated Data:", font=ctk.CTkFont(weight="bold"))
        self.result_label.grid(row=0, column=0, sticky="w", padx=14, pady=(12, 4))

        self.result_display = ctk.CTkTextbox(self.result_frame, height=160, font=ctk.CTkFont(family="Consolas", size=12))
        self.result_display.grid(row=1, column=0, sticky="ew", padx=14, pady=(0, 12))

        btn_row = ctk.CTkFrame(self.result_frame, fg_color="transparent")
        btn_row.grid(row=2, column=0, sticky="w", padx=14, pady=(0, 12))

        ctk.CTkButton(btn_row, text="Copy All", command=self._copy_all).pack(side="left")

    def _generate(self) -> None:
        typ = self.type_var.get().lower()
        count = self.count_var.get()

        items = []
        for _ in range(count):
            if typ == "name":
                items.append({"type": "name", "value": self._fake_name()})
            elif typ == "email":
                items.append({"type": "email", "value": self._fake_email()})
            elif typ == "phone":
                items.append({"type": "phone", "value": self._fake_phone()})
            elif typ == "address":
                items.append({"type": "address", "value": self._fake_address()})
            elif typ == "full profile":
                items.append({"type": "profile", "value": self._fake_profile()})

        combined = "\n---\n".join(item["value"] for item in items)
        self.result_display.delete("0.0", "end")
        self.result_display.insert("0.0", combined)

        self.history.extend(items)
        del self.history[200:]
        self._refresh_history()

    def _fake_name(self) -> str:
        first = random.choice([
            "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", "William", "Elizabeth",
            "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen"
        ])
        last = random.choice([
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
            "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"
        ])
        return f"{first} {last}"

    def _fake_email(self) -> str:
        name = self._fake_name().lower().replace(" ", ".")
        domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "example.com", "mail.com"]
        return f"{name}@{random.choice(domains)}"

    def _fake_phone(self) -> str:
        patterns = [
            "({area}) {exchange}-{line}",
            "{area}-{exchange}-{line}",
            "+1-{area}-{exchange}-{line}",
        ]
        area = f"{random.randint(200, 999)}"
        exchange = f"{random.randint(200, 999)}"
        line = f"{random.randint(1000, 9999)}"
        return random.choice(patterns).format(area=area, exchange=exchange, line=line)

    def _fake_address(self) -> str:
        number = random.randint(100, 9999)
        street = random.choice([
            "Main St", "Oak Ave", "Elm St", "Park Ave", "Pine St", "Maple Ave", "Cedar St", "Washington St",
            "Lincoln Ave", "Jefferson St", "Madison Ave", "Adams St", "Jackson St", "Franklin Ave", "Washington Ave"
        ])
        city = random.choice([
            "Springfield", "Franklin", "Georgetown", "Clinton", "Greenville", "Madison", "Salem", "Fairview",
            "Washington", "Lincoln", "Jackson", "Chester", "Milton", "Newport", "Riverside"
        ])
        state = random.choice(["CA", "TX", "FL", "NY", "PA", "IL", "OH", "GA", "NC", "MI"])
        zipcode = f"{random.randint(10000, 99999)}"
        return f"{number} {street}, {city}, {state} {zipcode}"

    def _fake_profile(self) -> str:
        name = self._fake_name()
        email = self._fake_email()
        phone = self._fake_phone()
        address = self._fake_address()
        company = random.choice([
            "Tech Solutions Inc.", "Global Systems Ltd.", "Digital Innovations Corp.", "Advanced Technologies",
            "Creative Solutions", "Future Systems", "Innovation Labs", "Tech Enterprises"
        ])
        job = random.choice([
            "Software Engineer", "Product Manager", "Data Analyst", "UX Designer", "Marketing Manager",
            "Sales Representative", "Project Coordinator", "Business Analyst", "Consultant", "Developer"
        ])
        return f"""Name: {name}
Email: {email}
Phone: {phone}
Address: {address}
Company: {company}
Job Title: {job}"""

    def _refresh_history(self) -> None:
        for w in self.history_frame.winfo_children():
            w.destroy()
        for i, item in enumerate(self.history[:20]):
            txt = ctk.CTkTextbox(self.history_frame, height=80, wrap="word")
            txt.insert("0.0", item["value"])
            txt.grid(row=i, column=0, sticky="ew", padx=10, pady=2)
            txt.configure(state="disabled")

    def _copy_all(self) -> None:
        import pyperclip

        pyperclip.copy(self.result_display.get("0.0", "end-1c"))
        self.ctx.toast_host.show("Copied to clipboard", kind="success")

    def _export_all(self) -> None:
        path = os.path.join(exports_dir(), "fake_data.txt")
        with open(path, "w", encoding="utf-8") as f:
            for item in self.history:
                f.write(f"--- {item['type'].upper()} ---\n")
                f.write(item["value"] + "\n\n")
        self.ctx.toast_host.show("Data exported", kind="success")
        self.ctx.storage.add_export_history({"generator": "fake_data", "file": "fake_data.txt"})


class FakeDataGeneratorPlugin(GeneratorPlugin):
    meta = GeneratorMeta(
        id="fake_data",
        name="Fake Data Generator",
        category="Utility",
        icon="🎭",
        description="Generate fake names, emails, phones, addresses, or full profiles.",
    )

    def __init__(self, storage) -> None:
        self.storage = storage

    def create_frame(self, master: ctk.CTkFrame, toast_host) -> ctk.CTkFrame:
        ctx = GeneratorContext(storage=self.storage, toast_host=toast_host)
        return FakeDataGeneratorFrame(master, ctx)


def create_plugin(storage):
    return FakeDataGeneratorPlugin(storage)
