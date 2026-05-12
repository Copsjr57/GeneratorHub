from __future__ import annotations

import customtkinter as ctk

from utils.storage import AppStorage


class TopBar(ctk.CTkFrame):
    def __init__(
        self,
        master,
        storage: AppStorage,
        on_search,
        on_toggle_favorites,
    ) -> None:
        super().__init__(master, corner_radius=16)

        self.storage = storage
        self.on_search = on_search
        self.on_toggle_favorites = on_toggle_favorites

        self.grid_columnconfigure(1, weight=1)

        self.title = ctk.CTkLabel(
            self,
            text="GeneratorHub",
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        self.title.grid(row=0, column=0, padx=14, pady=12, sticky="w")

        self.search_var = ctk.StringVar(value="")
        self.search = ctk.CTkEntry(
            self,
            textvariable=self.search_var,
            placeholder_text="Search generators…",
            height=38,
        )
        self.search.grid(row=0, column=1, padx=12, pady=12, sticky="ew")
        self.search.bind("<KeyRelease>", lambda _e: self.on_search(self.search_var.get().strip()))

        self.fav_btn = ctk.CTkButton(
            self,
            text="★ Favorites",
            width=120,
            height=38,
            command=self.on_toggle_favorites,
        )
        self.fav_btn.grid(row=0, column=2, padx=12, pady=12, sticky="e")
