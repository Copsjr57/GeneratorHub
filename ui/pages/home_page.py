from __future__ import annotations

from typing import Dict, List

import customtkinter as ctk

from generators.registry import GeneratorRegistry
from utils.storage import AppStorage


class HomePage(ctk.CTkFrame):
    def __init__(
        self,
        master,
        registry: GeneratorRegistry,
        storage: AppStorage,
        on_open_generator,
    ) -> None:
        super().__init__(master, fg_color="transparent")

        self.registry = registry
        self.storage = storage
        self.on_open_generator = on_open_generator

        self._query = ""

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.header = ctk.CTkLabel(
            self,
            text="All-in-one generator toolbox",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        self.header.grid(row=0, column=0, sticky="w", padx=4, pady=(2, 10))

        self.sub = ctk.CTkLabel(
            self,
            text="Developer, Security, Documents, Creative, Utility, Gaming",
            text_color="#9ca3af",
        )
        self.sub.grid(row=1, column=0, sticky="w", padx=4, pady=(0, 14))

        self.grid_frame = ctk.CTkScrollableFrame(self, corner_radius=16)
        self.grid_frame.grid(row=2, column=0, sticky="nsew")

        self._cards: Dict[str, ctk.CTkFrame] = {}
        self._build_cards()

    def set_search_query(self, query: str) -> None:
        self._query = query.lower().strip()
        self._apply_filter()

    def _build_cards(self) -> None:
        for w in self.grid_frame.winfo_children():
            w.destroy()
        self._cards.clear()

        gens = self.registry.list_generators()
        cols = 2
        for c in range(cols):
            self.grid_frame.grid_columnconfigure(c, weight=1)

        for i, gen in enumerate(gens):
            r = i // cols
            c = i % cols

            card = ctk.CTkFrame(self.grid_frame, corner_radius=18)
            card.grid(row=r, column=c, sticky="ew", padx=10, pady=10)
            card.grid_columnconfigure(0, weight=1)

            title = ctk.CTkLabel(
                card,
                text=f"{gen.meta.icon}  {gen.meta.name}",
                font=ctk.CTkFont(size=16, weight="bold"),
            )
            title.grid(row=0, column=0, sticky="w", padx=14, pady=(12, 4))

            desc = ctk.CTkLabel(card, text=gen.meta.description, text_color="#9ca3af", wraplength=420, justify="left")
            desc.grid(row=1, column=0, sticky="w", padx=14, pady=(0, 10))

            meta = ctk.CTkLabel(card, text=f"Category: {gen.meta.category}", text_color="#6b7280")
            meta.grid(row=2, column=0, sticky="w", padx=14, pady=(0, 10))

            btn_row = ctk.CTkFrame(card, fg_color="transparent")
            btn_row.grid(row=3, column=0, sticky="ew", padx=14, pady=(0, 12))

            open_btn = ctk.CTkButton(btn_row, text="Open", height=36, command=lambda gid=gen.meta.id: self.on_open_generator(gid))
            open_btn.pack(side="left")

            fav_btn = ctk.CTkButton(
                btn_row,
                text="☆ Favorite",
                height=36,
                fg_color="transparent",
                command=lambda gid=gen.meta.id: self._toggle_favorite(gid),
            )
            fav_btn.pack(side="left", padx=(10, 0))

            self._cards[gen.meta.id] = card

        self._apply_filter()

    def _toggle_favorite(self, generator_id: str) -> None:
        self.storage.toggle_favorite(generator_id)
        self._apply_filter()

    def _apply_filter(self) -> None:
        q = self._query
        fav = set(self.storage.list_favorites())

        for gen in self.registry.list_generators():
            card = self._cards.get(gen.meta.id)
            if card is None:
                continue

            visible = True
            if q and q not in gen.meta.name.lower() and q not in gen.meta.category.lower():
                visible = False

            if visible:
                card.grid()
            else:
                card.grid_remove()
