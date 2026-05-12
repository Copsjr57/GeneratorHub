from __future__ import annotations

import os
import random
from typing import Callable

import customtkinter as ctk
from PIL import Image, ImageDraw

from generators.base import GeneratorContext, GeneratorMeta, GeneratorPlugin
from utils.paths import exports_dir


class ColorPaletteGeneratorFrame(ctk.CTkFrame):
    def __init__(self, master, ctx: GeneratorContext) -> None:
        super().__init__(master, fg_color="transparent")
        self.ctx = ctx

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.title = ctk.CTkLabel(self, text="Color Palette Generator", font=ctk.CTkFont(size=20, weight="bold"))
        self.title.grid(row=0, column=0, sticky="w", padx=4, pady=(2, 12))

        self.controls = ctk.CTkFrame(self, corner_radius=16)
        self.controls.grid(row=1, column=0, sticky="ew", padx=4, pady=(0, 12))
        self._setup_controls()

        self.palette_frame = ctk.CTkScrollableFrame(self, corner_radius=16)
        self.palette_frame.grid(row=2, column=0, sticky="nsew", padx=4, pady=(0, 4))
        self.palette_frame.grid_columnconfigure(0, weight=1)

        self.current_palette: list[str] = []
        self.history: list[list[str]] = []
        self._generate_palette()

    def _setup_controls(self) -> None:
        self.controls.grid_columnconfigure(1, weight=1)

        self.scheme_var = ctk.StringVar(value="complementary")
        ctk.CTkLabel(self.controls, text="Scheme", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, sticky="w", padx=14, pady=(12, 4)
        )
        self.scheme_menu = ctk.CTkOptionMenu(
            self.controls,
            values=["Complementary", "Triadic", "Analogous", "Monochromatic", "Random"],
            variable=self.scheme_var,
        )
        self.scheme_menu.grid(row=0, column=1, sticky="ew", padx=14, pady=(12, 4))

        self.count_label = ctk.CTkLabel(self.controls, text="Colors", font=ctk.CTkFont(weight="bold"))
        self.count_label.grid(row=1, column=0, sticky="w", padx=14, pady=(8, 4))
        self.count_var = ctk.IntVar(value=5)
        self.count_slider = ctk.CTkSlider(
            self.controls, from_=3, to=12, variable=self.count_var, number_of_steps=9
        )
        self.count_slider.grid(row=1, column=1, sticky="ew", padx=14, pady=(8, 4))
        self.count_label_value = ctk.CTkLabel(self.controls, text="5")
        self.count_label_value.grid(row=1, column=2, padx=(0, 14), pady=(8, 4))
        self.count_slider.configure(command=lambda v: self.count_label_value.configure(text=str(int(v))))

        btn_row = ctk.CTkFrame(self.controls, fg_color="transparent")
        btn_row.grid(row=2, column=0, columnspan=3, sticky="w", padx=14, pady=(8, 12))

        ctk.CTkButton(btn_row, text="Generate", command=self._generate_palette).pack(side="left")
        ctk.CTkButton(btn_row, text="Export Palette", command=self._export_palette).pack(side="left", padx=(10, 0))
        ctk.CTkButton(btn_row, text="Export History", command=self._export_history).pack(side="left", padx=(10, 0))

    def _generate_palette(self) -> None:
        scheme = self.scheme_var.get().lower()
        count = self.count_var.get()

        if scheme == "random":
            self.current_palette = [self._random_hex() for _ in range(count)]
        elif scheme == "monochromatic":
            base = self._random_hex()
            self.current_palette = self._monochromatic_palette(base, count)
        elif scheme == "complementary":
            base = self._random_hex()
            self.current_palette = self._complementary_palette(base, count)
        elif scheme == "triadic":
            base = self._random_hex()
            self.current_palette = self._triadic_palette(base, count)
        elif scheme == "analogous":
            base = self._random_hex()
            self.current_palette = self._analogous_palette(base, count)
        else:
            self.current_palette = [self._random_hex() for _ in range(count)]

        self.history.append(self.current_palette.copy())
        del self.history[50:]
        self._refresh_palette()

    def _random_hex(self) -> str:
        return f"#{random.randint(0, 0xFFFFFF):06X}"

    def _hex_to_rgb(self, hex_color: str) -> tuple[int, int, int]:
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def _rgb_to_hex(self, rgb: tuple[int, int, int]) -> str:
        return f"#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}"

    def _monochromatic_palette(self, base: str, count: int) -> list[str]:
        base_rgb = self._hex_to_rgb(base)
        palette = []
        for i in range(count):
            factor = 0.2 + (0.8 * i / (count - 1)) if count > 1 else 0.5
            rgb = tuple(min(255, max(0, int(c * factor))) for c in base_rgb)
            palette.append(self._rgb_to_hex(rgb))
        return palette

    def _complementary_palette(self, base: str, count: int) -> list[str]:
        base_rgb = self._hex_to_rgb(base)
        comp_rgb = tuple(min(255, max(0, 255 - c)) for c in base_rgb)
        comp_hex = self._rgb_to_hex(comp_rgb)
        
        palette = []
        for i in range(count):
            if i < count // 2:
                factor = 0.3 + (0.7 * i / max(1, count // 2 - 1))
                rgb = tuple(min(255, max(0, int(c * factor))) for c in base_rgb)
                palette.append(self._rgb_to_hex(rgb))
            else:
                factor = 0.3 + (0.7 * (i - count // 2) / max(1, count // 2 - 1))
                rgb = tuple(min(255, max(0, int(c * factor))) for c in comp_rgb)
                palette.append(self._rgb_to_hex(rgb))
        return palette[:count]

    def _triadic_palette(self, base: str, count: int) -> list[str]:
        base_rgb = self._hex_to_rgb(base)
        h, s, v = self._rgb_to_hsv(base_rgb)
        
        palette = []
        for i in range(count):
            hue = (h + (i * 120 / count)) % 360
            rgb = self._hsv_to_rgb(hue, s, v)
            palette.append(self._rgb_to_hex(rgb))
        return palette

    def _analogous_palette(self, base: str, count: int) -> list[str]:
        base_rgb = self._hex_to_rgb(base)
        h, s, v = self._rgb_to_hsv(base_rgb)
        
        palette = []
        for i in range(count):
            hue = (h - 30 + (i * 60 / (count - 1))) % 360 if count > 1 else h
            rgb = self._hsv_to_rgb(hue, s, v)
            palette.append(self._rgb_to_hex(rgb))
        return palette

    def _rgb_to_hsv(self, rgb: tuple[int, int, int]) -> tuple[float, float, float]:
        r, g, b = [c / 255.0 for c in rgb]
        mx, mn = max(r, g, b), min(r, g, b)
        df = mx - mn
        if mx == mn:
            h = 0
        elif mx == r:
            h = (60 * ((g - b) / df) + 360) % 360
        elif mx == g:
            h = (60 * ((b - r) / df) + 120) % 360
        else:
            h = (60 * ((r - g) / df) + 240) % 360
        s = 0 if mx == 0 else df / mx
        v = mx
        return h, s, v

    def _hsv_to_rgb(self, h: float, s: float, v: float) -> tuple[int, int, int]:
        c = v * s
        x = c * (1 - abs((h / 60) % 2 - 1))
        m = v - c
        if 0 <= h < 60:
            r, g, b = c, x, 0
        elif 60 <= h < 120:
            r, g, b = x, c, 0
        elif 120 <= h < 180:
            r, g, b = 0, c, x
        elif 180 <= h < 240:
            r, g, b = 0, x, c
        elif 240 <= h < 300:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x
        return tuple(int((c + m) * 255) for c in (r, g, b))

    def _refresh_palette(self) -> None:
        for w in self.palette_frame.winfo_children():
            w.destroy()

        ctk.CTkLabel(self.palette_frame, text="Current Palette", font=ctk.CTkFont(size=16, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=14, pady=(12, 8)
        )

        for i, color in enumerate(self.current_palette):
            row = ctk.CTkFrame(self.palette_frame, fg_color="transparent")
            row.grid(row=i + 1, column=0, sticky="ew", padx=14, pady=4)
            row.grid_columnconfigure(1, weight=1)

            # Color swatch - ensure color is valid hex format
            clean_color = color if color.startswith('#') else f"#{color}"
            swatch = ctk.CTkFrame(row, width=60, height=40, corner_radius=8)
            swatch.grid(row=0, column=0, padx=(0, 12))
            swatch.configure(fg_color=clean_color)

            # Color info
            info_frame = ctk.CTkFrame(row, fg_color="transparent")
            info_frame.grid(row=0, column=1, sticky="ew")
            info_frame.grid_columnconfigure(0, weight=1)

            hex_label = ctk.CTkLabel(info_frame, text=color, font=ctk.CTkFont(family="Consolas", size=12))
            hex_label.grid(row=0, column=0, sticky="w")

            rgb = self._hex_to_rgb(color)
            rgb_label = ctk.CTkLabel(info_frame, text=f"RGB: {rgb}", font=ctk.CTkFont(family="Consolas", size=10))
            rgb_label.grid(row=1, column=0, sticky="w")

            # Copy button
            ctk.CTkButton(row, text="Copy", width=60, command=lambda c=color: self._copy_color(c)).grid(
                row=0, column=2, padx=(8, 0)
            )

    def _copy_color(self, color: str) -> None:
        import pyperclip
        pyperclip.copy(color)
        self.ctx.toast_host.show(f"Copied {color}", kind="success")

    def _export_palette(self) -> None:
        path = os.path.join(exports_dir(), "palette.png")
        self._create_palette_image(path)
        self.ctx.toast_host.show("Palette exported as PNG", kind="success")
        self.ctx.storage.add_export_history({"generator": "color_palette", "file": "palette.png"})

    def _create_palette_image(self, path: str) -> None:
        width = 800
        height = 200
        img = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(img)

        color_width = width // len(self.current_palette)
        for i, color in enumerate(self.current_palette):
            x0 = i * color_width
            x1 = (i + 1) * color_width
            draw.rectangle([x0, 0, x1, height], fill=color)

        img.save(path)

    def _export_history(self) -> None:
        path = os.path.join(exports_dir(), "palette_history.txt")
        with open(path, "w", encoding="utf-8") as f:
            for i, palette in enumerate(self.history, 1):
                f.write(f"Palette {i}:\n")
                for color in palette:
                    rgb = self._hex_to_rgb(color)
                    f.write(f"  {color} (RGB: {rgb})\n")
                f.write("\n")
        self.ctx.toast_host.show("History exported", kind="success")
        self.ctx.storage.add_export_history({"generator": "color_palette", "file": "palette_history.txt"})


class ColorPaletteGeneratorPlugin(GeneratorPlugin):
    meta = GeneratorMeta(
        id="color_palette",
        name="Color Palette Generator",
        category="Creative",
        icon="🎨",
        description="Generate color palettes with various schemes and export capabilities.",
    )

    def __init__(self, storage) -> None:
        self.storage = storage

    def create_frame(self, master: ctk.CTkFrame, toast_host) -> ctk.CTkFrame:
        ctx = GeneratorContext(storage=self.storage, toast_host=toast_host)
        return ColorPaletteGeneratorFrame(master, ctx)


def create_plugin(storage):
    return ColorPaletteGeneratorPlugin(storage)
