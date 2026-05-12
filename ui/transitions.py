import customtkinter as ctk


class FrameSwitcher(ctk.CTkFrame):
    """Simple, smooth-ish transition container.

    We keep transitions lightweight (alpha-like fade isn't available per-frame),
    so we animate a short slide-in by updating padding.
    """

    def __init__(self, master) -> None:
        super().__init__(master, corner_radius=16)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.grid(row=0, column=0, sticky="nsew")

        self._current: ctk.CTkFrame | None = None

    def show(self, frame: ctk.CTkFrame) -> None:
        if self._current is frame:
            return

        if self._current is not None:
            self._current.grid_forget()

        self._current = frame
        frame.grid(row=0, column=0, sticky="nsew")

        # small slide animation
        self._animate_in(frame, start=18)

    def _animate_in(self, frame: ctk.CTkFrame, start: int) -> None:
        step = 3

        def tick(p: int) -> None:
            frame.grid_configure(padx=(p, 0))
            if p <= 0:
                frame.grid_configure(padx=0)
                return
            self.after(12, lambda: tick(p - step))

        tick(start)
