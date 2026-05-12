from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import customtkinter as ctk

from utils.storage import AppStorage


@dataclass(frozen=True)
class GeneratorMeta:
    id: str
    name: str
    category: str
    icon: str
    description: str


class GeneratorPlugin(Protocol):
    meta: GeneratorMeta

    def create_frame(self, master: ctk.CTkFrame, toast_host) -> ctk.CTkFrame: ...


class GeneratorContext:
    def __init__(self, storage: AppStorage, toast_host) -> None:
        self.storage = storage
        self.toast_host = toast_host
