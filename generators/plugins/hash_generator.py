from __future__ import annotations

import hashlib
import os
import secrets
from typing import Callable

import bcrypt
import customtkinter as ctk
import pyperclip

from generators.base import GeneratorContext, GeneratorMeta, GeneratorPlugin
from utils.paths import exports_dir


class HashGeneratorFrame(ctk.CTkFrame):
    def __init__(self, master, ctx: GeneratorContext) -> None:
        super().__init__(master, fg_color="transparent")
        self.ctx = ctx

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)

        self.title = ctk.CTkLabel(self, text="Hash Generator", font=ctk.CTkFont(size=20, weight="bold"))
        self.title.grid(row=0, column=0, sticky="w", padx=4, pady=(2, 12))

        self.mode_frame = ctk.CTkFrame(self, corner_radius=16)
        self.mode_frame.grid(row=1, column=0, sticky="ew", padx=4, pady=(0, 12))
        self._setup_mode_selection()

        self.controls = ctk.CTkFrame(self, corner_radius=16)
        self.controls.grid(row=2, column=0, sticky="ew", padx=4, pady=(0, 12))
        self._setup_controls()

        self.result_frame = ctk.CTkFrame(self, corner_radius=16)
        self.result_frame.grid(row=3, column=0, sticky="ew", padx=4, pady=(0, 12))
        self._setup_result()

        self.history_frame = ctk.CTkScrollableFrame(self, corner_radius=16)
        self.history_frame.grid(row=4, column=0, sticky="nsew", padx=4, pady=(0, 4))
        self.history_frame.grid_columnconfigure(0, weight=1)

        self.history: list[dict] = []
        self._refresh_history()

    def _setup_mode_selection(self) -> None:
        self.mode_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(self.mode_frame, text="Mode", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, sticky="w", padx=14, pady=(12, 4)
        )
        
        self.mode_var = ctk.StringVar(value="text")
        modes = ["Text Hash", "Password Hash", "File Integrity"]
        self.mode_menu = ctk.CTkOptionMenu(
            self.mode_frame, variable=self.mode_var, values=modes, command=self._on_mode_change
        )
        self.mode_menu.grid(row=0, column=1, sticky="e", padx=14, pady=(12, 4))

    def _setup_controls(self) -> None:
        self.controls.grid_columnconfigure(1, weight=1)
        
        # Input field
        ctk.CTkLabel(self.controls, text="Input", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, sticky="w", padx=14, pady=(12, 4)
        )
        self.input_var = ctk.StringVar()
        self.input_entry = ctk.CTkEntry(self.controls, textvariable=self.input_var, placeholder_text="Enter text or select file...")
        self.input_entry.grid(row=0, column=1, sticky="ew", padx=14, pady=(12, 4))
        
        # File selection button (for file integrity mode)
        self.file_button = ctk.CTkButton(self.controls, text="Select File", command=self._select_file)
        self.file_button.grid(row=0, column=2, sticky="e", padx=(0, 14), pady=(12, 4))
        self.file_button.grid_remove()
        
        # Hash algorithm selection
        ctk.CTkLabel(self.controls, text="Algorithm", font=ctk.CTkFont(weight="bold")).grid(
            row=1, column=0, sticky="w", padx=14, pady=(4, 4)
        )
        self.algo_var = ctk.StringVar(value="sha256")
        self.algo_menu = ctk.CTkOptionMenu(
            self.controls, variable=self.algo_var, values=["md5", "sha1", "sha256", "bcrypt"]
        )
        self.algo_menu.grid(row=1, column=1, sticky="ew", padx=14, pady=(4, 4))
        
        # Salt options (for password hash mode)
        self.salt_frame = ctk.CTkFrame(self.controls, fg_color="transparent")
        self.salt_frame.grid(row=2, column=0, columnspan=3, sticky="ew", padx=14, pady=(4, 12))
        self.salt_frame.grid_columnconfigure(1, weight=1)
        self.salt_frame.grid_remove()
        
        ctk.CTkLabel(self.salt_frame, text="Salt", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, sticky="w", padx=0, pady=4
        )
        self.salt_var = ctk.StringVar()
        self.salt_entry = ctk.CTkEntry(self.salt_frame, textvariable=self.salt_var, placeholder_text="Auto-generated if empty")
        self.salt_entry.grid(row=0, column=1, sticky="ew", padx=(8, 0), pady=4)
        
        self.generate_salt_button = ctk.CTkButton(self.salt_frame, text="Generate Salt", command=self._generate_salt, width=120)
        self.generate_salt_button.grid(row=0, column=2, sticky="e", padx=(8, 0), pady=4)
        
        # Generate button
        self.generate_button = ctk.CTkButton(self.controls, text="Generate Hash", command=self._generate_hash, height=40)
        self.generate_button.grid(row=3, column=0, columnspan=3, sticky="ew", padx=14, pady=(4, 12))

    def _setup_result(self) -> None:
        self.result_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(self.result_frame, text="Result", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, sticky="w", padx=14, pady=(12, 4)
        )
        
        self.result_text = ctk.CTkTextbox(self.result_frame, height=80)
        self.result_text.grid(row=1, column=0, sticky="ew", padx=14, pady=(0, 8))
        self.result_text.configure(state="disabled")
        
        # Action buttons
        self.button_frame = ctk.CTkFrame(self.result_frame, fg_color="transparent")
        self.button_frame.grid(row=2, column=0, sticky="ew", padx=14, pady=(0, 12))
        
        self.copy_button = ctk.CTkButton(self.button_frame, text="Copy", command=self._copy_result, width=100)
        self.copy_button.grid(row=0, column=0, sticky="w", padx=0)
        
        self.export_button = ctk.CTkButton(self.button_frame, text="Export", command=self._export_result, width=100)
        self.export_button.grid(row=0, column=1, sticky="e", padx=0)
        self.button_frame.grid_columnconfigure(0, weight=1)
        self.button_frame.grid_columnconfigure(1, weight=1)

    def _on_mode_change(self, value: str) -> None:
        mode = self.mode_var.get()
        
        if mode == "Text Hash":
            self.input_entry.configure(placeholder_text="Enter text to hash...")
            self.file_button.grid_remove()
            self.salt_frame.grid_remove()
            self.algo_menu.configure(values=["md5", "sha1", "sha256"])
            self.algo_var.set("sha256")
        elif mode == "Password Hash":
            self.input_entry.configure(placeholder_text="Enter password to hash...")
            self.file_button.grid_remove()
            self.salt_frame.grid()
            self.algo_menu.configure(values=["sha256", "bcrypt"])
            self.algo_var.set("sha256")
        elif mode == "File Integrity":
            self.input_entry.configure(placeholder_text="Select file to check integrity...")
            self.file_button.grid()
            self.salt_frame.grid_remove()
            self.algo_menu.configure(values=["md5", "sha1", "sha256"])
            self.algo_var.set("sha256")

    def _select_file(self) -> None:
        from tkinter import filedialog
        
        file_path = filedialog.askopenfilename(
            title="Select File",
            filetypes=[("All Files", "*.*")]
        )
        
        if file_path:
            self.input_var.set(file_path)

    def _generate_salt(self) -> None:
        salt = secrets.token_hex(16)
        self.salt_var.set(salt)
        self.ctx.toast_host.show("Salt generated successfully!")

    def _generate_hash(self) -> None:
        mode = self.mode_var.get()
        algorithm = self.algo_var.get()
        input_text = self.input_var.get()
        
        if not input_text:
            self.ctx.toast_host.show("Please enter input text or select a file")
            return
        
        try:
            if mode == "Text Hash":
                result = self._hash_text(input_text, algorithm)
            elif mode == "Password Hash":
                result = self._hash_password(input_text, algorithm)
            elif mode == "File Integrity":
                result = self._hash_file(input_text, algorithm)
            else:
                result = "Invalid mode"
            
            self.result_text.configure(state="normal")
            self.result_text.delete("1.0", "end")
            self.result_text.insert("1.0", result)
            self.result_text.configure(state="disabled")
            
            # Add to history
            self._add_to_history(mode, algorithm, input_text, result)
            
            self.ctx.toast_host.show("Hash generated successfully!")
            
        except Exception as e:
            self.ctx.toast_host.show(f"Error: {str(e)}")

    def _hash_text(self, text: str, algorithm: str) -> str:
        if algorithm == "md5":
            return hashlib.md5(text.encode()).hexdigest()
        elif algorithm == "sha1":
            return hashlib.sha1(text.encode()).hexdigest()
        elif algorithm == "sha256":
            return hashlib.sha256(text.encode()).hexdigest()
        return "Invalid algorithm"

    def _hash_password(self, password: str, algorithm: str) -> str:
        salt = self.salt_var.get()
        
        if algorithm == "sha256":
            if salt:
                salted = password + salt
                return hashlib.sha256(salted.encode()).hexdigest()
            else:
                return hashlib.sha256(password.encode()).hexdigest()
        elif algorithm == "bcrypt":
            if salt:
                salt_bytes = salt.encode()
                hashed = bcrypt.hashpw(password.encode(), salt_bytes)
                return hashed.decode()
            else:
                salt = bcrypt.gensalt()
                hashed = bcrypt.hashpw(password.encode(), salt)
                return f"{hashed.decode()}\n(Salt: {salt.decode()})"
        return "Invalid algorithm"

    def _hash_file(self, file_path: str, algorithm: str) -> str:
        if not os.path.exists(file_path):
            raise FileNotFoundError("File not found")
        
        hash_func = None
        if algorithm == "md5":
            hash_func = hashlib.md5()
        elif algorithm == "sha1":
            hash_func = hashlib.sha1()
        elif algorithm == "sha256":
            hash_func = hashlib.sha256()
        else:
            return "Invalid algorithm"
        
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_func.update(chunk)
        
        return f"File: {os.path.basename(file_path)}\nAlgorithm: {algorithm.upper()}\nHash: {hash_func.hexdigest()}"

    def _copy_result(self) -> None:
        result = self.result_text.get("1.0", "end").strip()
        if result:
            pyperclip.copy(result)
            self.ctx.toast_host.show("Copied to clipboard!")

    def _export_result(self) -> None:
        result = self.result_text.get("1.0", "end").strip()
        if not result:
            return
        
        from tkinter import filedialog
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            initialdir=str(exports_dir())
        )
        
        if file_path:
            with open(file_path, "w") as f:
                f.write(result)
            self.ctx.toast_host.show(f"Exported to {file_path}")

    def _add_to_history(self, mode: str, algorithm: str, input_text: str, result: str) -> None:
        entry = {
            "mode": mode,
            "algorithm": algorithm,
            "input": input_text[:50] + "..." if len(input_text) > 50 else input_text,
            "result": result[:100] + "..." if len(result) > 100 else result,
            "timestamp": ctk.CTkLabel(self.history_frame, text=self._get_timestamp())
        }
        self.history.insert(0, entry)
        if len(self.history) > 20:
            self.history.pop()
        self._refresh_history()

    def _get_timestamp(self) -> str:
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")

    def _refresh_history(self) -> None:
        for widget in self.history_frame.winfo_children():
            widget.destroy()
        
        for entry in self.history:
            frame = ctk.CTkFrame(self.history_frame, corner_radius=8)
            frame.grid(row=self.history.index(entry), column=0, sticky="ew", padx=4, pady=2)
            frame.grid_columnconfigure(0, weight=1)
            
            info_text = f"{entry['mode']} | {entry['algorithm'].upper()} | {entry['input']}"
            info_label = ctk.CTkLabel(frame, text=info_text, font=ctk.CTkFont(size=11))
            info_label.grid(row=0, column=0, sticky="w", padx=8, pady=(6, 2))
            
            result_label = ctk.CTkLabel(frame, text=entry['result'], font=ctk.CTkFont(size=10), text_color="gray")
            result_label.grid(row=1, column=0, sticky="w", padx=8, pady=(0, 6))
            
            entry["timestamp"].grid(row=0, column=1, sticky="e", padx=8, pady=(6, 2))


class HashGeneratorPlugin:
    meta = GeneratorMeta(
        id="hash_generator",
        name="Hash Generator",
        category="Security",
        icon="🔐",
        description="Generate MD5, SHA-1, SHA-256, bcrypt hashes with salt generation and file integrity checking"
    )

    def create_frame(self, master: ctk.CTkFrame, toast_host) -> ctk.CTkFrame:
        from utils.storage import AppStorage
        ctx = GeneratorContext(AppStorage(), toast_host)
        return HashGeneratorFrame(master, ctx)


PLUGIN = HashGeneratorPlugin()
