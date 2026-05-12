from __future__ import annotations

import customtkinter as ctk

from utils.storage import AppStorage


class SettingsPage(ctk.CTkFrame):
    def __init__(self, master, storage: AppStorage, on_apply) -> None:
        super().__init__(master, fg_color="transparent")

        self.storage = storage
        self.on_apply = on_apply

        self.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(self, text="Settings", font=ctk.CTkFont(size=20, weight="bold"))
        title.grid(row=0, column=0, sticky="w", padx=4, pady=(2, 16))

        card = ctk.CTkFrame(self, corner_radius=18)
        card.grid(row=1, column=0, sticky="ew", padx=4)
        card.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(card, text="Theme", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, sticky="w", padx=14, pady=(14, 6))

        self.appearance = ctk.StringVar(value=self.storage.get_setting("appearance_mode", "Dark"))
        self.appearance_menu = ctk.CTkOptionMenu(card, values=["Dark", "Light", "System"], variable=self.appearance)
        self.appearance_menu.grid(row=0, column=1, sticky="ew", padx=14, pady=(14, 6))

        ctk.CTkLabel(card, text="Notifications", font=ctk.CTkFont(weight="bold")).grid(
            row=1, column=0, sticky="w", padx=14, pady=(6, 14)
        )
        self.notifications = ctk.BooleanVar(value=bool(self.storage.get_setting("notifications", True)))
        ctk.CTkSwitch(card, text="Enable toast notifications", variable=self.notifications).grid(
            row=1, column=1, sticky="w", padx=14, pady=(6, 14)
        )

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.grid(row=2, column=0, sticky="w", padx=4, pady=14)

        apply_btn = ctk.CTkButton(btn_row, text="Apply", height=38, command=self._apply)
        apply_btn.pack(side="left")

    def _apply(self) -> None:
        self.storage.set_setting("appearance_mode", self.appearance.get())
        self.storage.set_setting("notifications", bool(self.notifications.get()))
        self.on_apply()
