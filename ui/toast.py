import time
from typing import Literal

import customtkinter as ctk


ToastKind = Literal["info", "success", "error"]


class ToastHost:
    def __init__(self, master: ctk.CTk) -> None:
        self.master = master
        self._toast: ctk.CTkFrame | None = None

    def show(self, message: str, kind: ToastKind = "info", duration_ms: int = 2600) -> None:
        if self._toast is not None:
            try:
                self._toast.destroy()
            except Exception:
                pass
            self._toast = None

        color = {
            "info": "#1f2937",
            "success": "#064e3b",
            "error": "#7f1d1d",
        }.get(kind, "#1f2937")

        toast = ctk.CTkFrame(self.master, corner_radius=14, fg_color=color)
        toast.place(relx=1.0, rely=1.0, x=-18, y=-18, anchor="se")

        label = ctk.CTkLabel(toast, text=message, font=ctk.CTkFont(size=13, weight="bold"))
        label.pack(padx=14, pady=10)

        self._toast = toast
        self.master.after(duration_ms, self._destroy_current)

    def _destroy_current(self) -> None:
        if self._toast is None:
            return
        try:
            self._toast.destroy()
        except Exception:
            pass
        self._toast = None
