import os
import threading
from typing import Dict, List, Optional

import customtkinter as ctk

from generators.registry import GeneratorRegistry
from ui.sidebar import Sidebar
from ui.topbar import TopBar
from ui.transitions import FrameSwitcher
from ui.toast import ToastHost
from ui.pages.home_page import HomePage
from ui.pages.settings_page import SettingsPage
from utils.paths import ensure_app_dirs
from utils.storage import AppStorage


class GeneratorHubApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()

        ensure_app_dirs()
        self.storage = AppStorage()

        ctk.set_appearance_mode(self.storage.get_setting("appearance_mode", "Dark"))
        ctk.set_default_color_theme("dark-blue")

        self.title("GeneratorHub")
        self.geometry("1200x760")
        self.minsize(980, 640)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.toast_host = ToastHost(self)

        self.registry = GeneratorRegistry(self.storage)
        self.registry.discover()

        self.sidebar = Sidebar(
            master=self,
            registry=self.registry,
            storage=self.storage,
            on_navigate=self._navigate,
        )
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsw")

        self.topbar = TopBar(
            master=self,
            storage=self.storage,
            on_search=self._on_search,
            on_toggle_favorites=self.sidebar.toggle_favorites_filter,
        )
        self.topbar.grid(row=0, column=1, sticky="new", padx=(12, 12), pady=(12, 0))

        self.switcher = FrameSwitcher(master=self)
        self.switcher.grid(row=1, column=1, sticky="nsew", padx=12, pady=12)

        self.pages: Dict[str, ctk.CTkFrame] = {}
        self._ensure_core_pages()

        self._navigate("home")

    def _ensure_core_pages(self) -> None:
        self.pages["home"] = HomePage(
            master=self.switcher.container,
            registry=self.registry,
            storage=self.storage,
            on_open_generator=self._open_generator,
        )
        self.pages["settings"] = SettingsPage(
            master=self.switcher.container,
            storage=self.storage,
            on_apply=self._apply_settings,
        )

        for gen in self.registry.list_generators():
            self.pages[gen.meta.id] = gen.create_frame(self.switcher.container, self.toast_host)

    def _apply_settings(self) -> None:
        mode = self.storage.get_setting("appearance_mode", "Dark")
        ctk.set_appearance_mode(mode)
        self.toast_host.show("Settings applied")

    def _on_search(self, query: str) -> None:
        self.sidebar.set_search_query(query)
        home = self.pages.get("home")
        if isinstance(home, HomePage):
            home.set_search_query(query)

    def _open_generator(self, generator_id: str) -> None:
        if generator_id not in self.pages:
            self.toast_host.show("Generator not available", kind="error")
            return

        self.storage.add_recent(generator_id)
        self.sidebar.refresh_badges()
        self._navigate(generator_id)

    def _navigate(self, page_id: str) -> None:
        if page_id == "settings":
            self.sidebar.select_settings()
        elif page_id == "home":
            self.sidebar.select_home()
        else:
            self.sidebar.select_generator(page_id)

        frame = self.pages.get(page_id)
        if frame is None:
            self.toast_host.show("Page not found", kind="error")
            return

        self.switcher.show(frame)
