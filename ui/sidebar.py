from __future__ import annotations

from typing import Dict, Optional

import customtkinter as ctk

from generators.registry import GeneratorRegistry
from utils.storage import AppStorage


class Sidebar(ctk.CTkFrame):
    def __init__(
        self,
        master,
        registry: GeneratorRegistry,
        storage: AppStorage,
        on_navigate,
    ) -> None:
        super().__init__(master, width=280, corner_radius=0)

        self.registry = registry
        self.storage = storage
        self.on_navigate = on_navigate

        self._search_query = ""
        self._favorites_only = False

        self.grid_rowconfigure(4, weight=1)

        self.logo = ctk.CTkLabel(self, text="GH", font=ctk.CTkFont(size=28, weight="bold"))
        self.logo.grid(row=0, column=0, padx=18, pady=(18, 8), sticky="w")

        self.nav_home = ctk.CTkButton(self, text="⌂ Home", height=40, command=lambda: self.on_navigate("home"))
        self.nav_home.grid(row=1, column=0, padx=14, pady=(8, 6), sticky="ew")

        self.nav_settings = ctk.CTkButton(
            self, text="⚙ Settings", height=40, fg_color="transparent", command=lambda: self.on_navigate("settings")
        )
        self.nav_settings.grid(row=2, column=0, padx=14, pady=(0, 10), sticky="ew")

        self.section = ctk.CTkLabel(
            self,
            text="Generators",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.section.grid(row=3, column=0, padx=16, pady=(8, 6), sticky="w")

        self.scroll = ctk.CTkScrollableFrame(self, corner_radius=0)
        self.scroll.grid(row=4, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.scroll.grid_columnconfigure(0, weight=1)

        self._gen_buttons: Dict[str, ctk.CTkButton] = {}
        self._build_generators()

    def _build_generators(self) -> None:
        for w in self.scroll.winfo_children():
            w.destroy()
        self._gen_buttons.clear()

        row = 0
        for gen in self.registry.list_generators():
            btn = ctk.CTkButton(
                self.scroll,
                text=f"{gen.meta.icon}  {gen.meta.name}",
                height=38,
                anchor="w",
                fg_color="transparent",
                command=lambda gid=gen.meta.id: self.on_navigate(gid),
            )
            btn.grid(row=row, column=0, sticky="ew", padx=6, pady=4)
            self._gen_buttons[gen.meta.id] = btn
            row += 1

        self._apply_filters()

    def refresh_badges(self) -> None:
        # reserved for future badges (recent counts etc.)
        pass

    def set_search_query(self, query: str) -> None:
        self._search_query = query.lower().strip()
        self._apply_filters()

    def toggle_favorites_filter(self) -> None:
        self._favorites_only = not self._favorites_only
        self._apply_filters()

    def _apply_filters(self) -> None:
        q = self._search_query
        fav = set(self.storage.list_favorites())

        for gen in self.registry.list_generators():
            btn = self._gen_buttons.get(gen.meta.id)
            if btn is None:
                continue

            visible = True
            if self._favorites_only and gen.meta.id not in fav:
                visible = False
            if q and q not in gen.meta.name.lower() and q not in gen.meta.category.lower():
                visible = False

            if visible:
                btn.grid()
            else:
                btn.grid_remove()

    def select_home(self) -> None:
        self._set_active(self.nav_home)

    def select_settings(self) -> None:
        self._set_active(self.nav_settings)

    def select_generator(self, generator_id: str) -> None:
        btn = self._gen_buttons.get(generator_id)
        if btn is not None:
            self._set_active(btn)

    def _set_active(self, active: ctk.CTkButton) -> None:
        # Reset
        for b in [self.nav_home, self.nav_settings, *self._gen_buttons.values()]:
            try:
                b.configure(fg_color="transparent")
            except Exception:
                pass
        try:
            active.configure(fg_color="#1f2937")
        except Exception:
            pass
