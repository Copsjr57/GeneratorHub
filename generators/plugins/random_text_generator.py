from __future__ import annotations

import os
import random
from typing import Callable

import customtkinter as ctk

from generators.base import GeneratorContext, GeneratorMeta, GeneratorPlugin
from utils.paths import exports_dir


class RandomTextGeneratorFrame(ctk.CTkFrame):
    def __init__(self, master, ctx: GeneratorContext) -> None:
        super().__init__(master, fg_color="transparent")
        self.ctx = ctx

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self.title = ctk.CTkLabel(self, text="Random Text Generator", font=ctk.CTkFont(size=20, weight="bold"))
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

        self.type_var = ctk.StringVar(value="bio")
        ctk.CTkLabel(self.controls, text="Type", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, sticky="w", padx=14, pady=(12, 4)
        )
        self.type_menu = ctk.CTkOptionMenu(
            self.controls,
            values=["Bio", "Description", "Project Idea", "Quote", "Gamer Tag"],
            variable=self.type_var,
        )
        self.type_menu.grid(row=0, column=1, sticky="ew", padx=14, pady=(12, 4))

        self.count_label = ctk.CTkLabel(self.controls, text="Count", font=ctk.CTkFont(weight="bold"))
        self.count_label.grid(row=1, column=0, sticky="w", padx=14, pady=(8, 4))
        self.count_var = ctk.IntVar(value=1)
        self.count_slider = ctk.CTkSlider(
            self.controls, from_=1, to=10, variable=self.count_var, number_of_steps=9
        )
        self.count_slider.grid(row=1, column=1, sticky="ew", padx=14, pady=(8, 4))
        self.count_label_value = ctk.CTkLabel(self.controls, text="1")
        self.count_label_value.grid(row=1, column=2, padx=(0, 14), pady=(8, 4))
        self.count_slider.configure(command=lambda v: self.count_label_value.configure(text=str(int(v))))

        btn_row = ctk.CTkFrame(self.controls, fg_color="transparent")
        btn_row.grid(row=2, column=0, columnspan=3, sticky="w", padx=14, pady=(8, 12))

        ctk.CTkButton(btn_row, text="Generate", command=self._generate).pack(side="left")
        ctk.CTkButton(btn_row, text="Export All", command=self._export_all).pack(side="left", padx=(10, 0))

    def _setup_result(self) -> None:
        self.result_frame.grid_columnconfigure(0, weight=1)

        self.result_label = ctk.CTkLabel(self.result_frame, text="Generated Text:", font=ctk.CTkFont(weight="bold"))
        self.result_label.grid(row=0, column=0, sticky="w", padx=14, pady=(12, 4))

        self.result_display = ctk.CTkTextbox(self.result_frame, height=120, wrap="word")
        self.result_display.grid(row=1, column=0, sticky="ew", padx=14, pady=(0, 12))

        btn_row = ctk.CTkFrame(self.result_frame, fg_color="transparent")
        btn_row.grid(row=2, column=0, sticky="w", padx=14, pady=(0, 12))

        ctk.CTkButton(btn_row, text="Copy", command=self._copy).pack(side="left")

    def _generate(self) -> None:
        typ = self.type_var.get().lower()
        count = self.count_var.get()

        texts = []
        for _ in range(count):
            if typ == "bio":
                texts.append(self._random_bio())
            elif typ == "description":
                texts.append(self._random_description())
            elif typ == "project idea":
                texts.append(self._random_project_idea())
            elif typ == "quote":
                texts.append(self._random_quote())
            elif typ == "gamer tag":
                texts.append(self._random_gamer_tag())

        combined = "\n\n".join(texts)
        self.result_display.delete("0.0", "end")
        self.result_display.insert("0.0", combined)

        for t in texts:
            self.history.insert(0, t)
        del self.history[200:]
        self._refresh_history()

    def _random_bio(self) -> str:
        templates = [
            "Passionate {adj} {profession} with {years} years of experience. Love {hobby} and {goal}.",
            "I'm a {profession} who enjoys {hobby} and believes in {belief}. Currently working on {project}.",
            "Coffee-addicted {profession}. When I'm not {activity}, you'll find me {hobby}.",
        ]
        return random.choice(templates).format(
            adj=random.choice(["creative", "dedicated", "innovative", "detail-oriented", "strategic"]),
            profession=random.choice(["developer", "designer", "writer", "analyst", "manager"]),
            years=random.randint(2, 15),
            hobby=random.choice(["hiking", "reading", "gaming", "cooking", "photography"]),
            goal=random.choice(["building great products", "learning new things", "making an impact", "solving problems"]),
            belief=random.choice(["continuous improvement", "work-life balance", "collaboration", "innovation"]),
            project=random.choice(["side projects", "open source", "automation tools", "data analysis"]),
            activity=random.choice(["coding", "designing", "writing", "planning"]),
        )

    def _random_description(self) -> str:
        templates = [
            "A {adj} tool for {purpose}. Built with {tech}. Features include {features}.",
            "This {product} helps {audience} achieve {benefit} by {method}.",
            "An {adj} platform that {action} and {result}.",
        ]
        return random.choice(templates).format(
            adj=random.choice(["modern", "powerful", "simple", "intuitive", "flexible"]),
            purpose=random.choice(["productivity", "automation", "creativity", "communication", "analysis"]),
            tech=random.choice(["Python", "JavaScript", "React", "Node.js", "FastAPI"]),
            features=random.choice(["real-time sync", "AI integration", "cloud storage", "team collaboration", "analytics"]),
            product=random.choice(["application", "service", "platform", "solution", "system"]),
            audience=random.choice(["developers", "businesses", "creatives", "students", "teams"]),
            benefit=random.choice(["efficiency", "growth", "innovation", "collaboration", "insights"]),
            method=random.choice(["automating workflows", "simplifying processes", "connecting people", "analyzing data"]),
            action=random.choice(["streamlines operations", "enhances productivity", "facilitates communication"]),
            result=random.choice(["drives success", "saves time", "improves quality", "reduces costs"]),
        )

    def _random_project_idea(self) -> str:
        templates = [
            "{platform} app that {verb} {object} for {audience}.",
            "A {adj} {product} that {benefit} using {technology}.",
            "{service} platform for {industry} with {feature}.",
        ]
        return random.choice(templates).format(
            platform=random.choice(["Web", "Mobile", "Desktop", "CLI", "Browser Extension"]),
            verb=random.choice(["automates", "simplifies", "enhances", "tracks", "connects"]),
            object=random.choice(["workflows", "tasks", "data", "communication", "learning"]),
            audience=random.choice(["remote teams", "freelancers", "students", "small businesses", "creatives"]),
            adj=random.choice(["AI-powered", "real-time", "collaborative", "secure", "scalable"]),
            product=random.choice(["dashboard", "marketplace", "analytics tool", "messaging app", "scheduler"]),
            benefit=random.choice(["predicts trends", "optimizes resources", "improves engagement", "streamlines processes"]),
            technology=random.choice(["machine learning", "blockchain", "IoT", "AR/VR", "voice recognition"]),
            service=random.choice(["SaaS", "PaaS", "API", "microservice", "serverless"]),
            industry=random.choice(["healthcare", "education", "finance", "retail", "entertainment"]),
            feature=random.choice(["real-time notifications", "AI recommendations", "multi-tenant support", "API integrations"]),
        )

    def _random_quote(self) -> str:
        templates = [
            "{adj} is the {noun} of {concept}.",
            "The {noun} of {concept} is {adj}.",
            "Without {concept}, {adj} is impossible.",
        ]
        return random.choice(templates).format(
            adj=random.choice(["Innovation", "Persistence", "Creativity", "Discipline", "Collaboration"]),
            noun=random.choice(["key", "foundation", "essence", "cornerstone", "heartbeat"]),
            concept=random.choice(["success", "progress", "excellence", "growth", "achievement"]),
        )

    def _random_gamer_tag(self) -> str:
        prefixes = ["xX", "Xx", "Im", "Mr", "Dr", "Lord", "Sir", "Pro", "Elite", "Shadow"]
        mids = ["Ninja", "Dragon", "Phoenix", "Storm", "Blade", "Frost", "Thunder", "Viper", "Wolf", "Ghost"]
        suffixes = ["Xx", "xX", "Z", "69", "420", "123", "777", "Prime", "Max", "Pro"]
        return f"{random.choice(prefixes)}{random.choice(mids)}{random.choice(suffixes)}"

    def _refresh_history(self) -> None:
        for w in self.history_frame.winfo_children():
            w.destroy()
        for i, text in enumerate(self.history[:20]):
            txt = ctk.CTkTextbox(self.history_frame, height=60, wrap="word")
            txt.insert("0.0", text)
            txt.grid(row=i, column=0, sticky="ew", padx=10, pady=2)
            txt.configure(state="disabled")

    def _copy(self) -> None:
        import pyperclip

        pyperclip.copy(self.result_display.get("0.0", "end-1c"))
        self.ctx.toast_host.show("Copied to clipboard", kind="success")

    def _export_all(self) -> None:
        path = os.path.join(exports_dir(), "random_texts.txt")
        with open(path, "w", encoding="utf-8") as f:
            for text in self.history:
                f.write(text + "\n---\n")
        self.ctx.toast_host.show("Exported all texts", kind="success")
        self.ctx.storage.add_export_history({"generator": "random_text", "file": "random_texts.txt"})


class RandomTextGeneratorPlugin(GeneratorPlugin):
    meta = GeneratorMeta(
        id="random_text",
        name="Random Text Generator",
        category="Creative",
        icon="📝",
        description="Generate random bios, descriptions, project ideas, quotes, and gamer tags.",
    )

    def __init__(self, storage) -> None:
        self.storage = storage

    def create_frame(self, master: ctk.CTkFrame, toast_host) -> ctk.CTkFrame:
        ctx = GeneratorContext(storage=self.storage, toast_host=toast_host)
        return RandomTextGeneratorFrame(master, ctx)


def create_plugin(storage):
    return RandomTextGeneratorPlugin(storage)
