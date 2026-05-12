from __future__ import annotations

import os
from datetime import datetime
from typing import Callable

import customtkinter as ctk
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph

from generators.base import GeneratorContext, GeneratorMeta, GeneratorPlugin
from utils.paths import exports_dir


class InvoiceGeneratorFrame(ctk.CTkFrame):
    def __init__(self, master, ctx: GeneratorContext) -> None:
        super().__init__(master, fg_color="transparent")
        self.ctx = ctx

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.title = ctk.CTkLabel(self, text="PDF Invoice Generator", font=ctk.CTkFont(size=20, weight="bold"))
        self.title.grid(row=0, column=0, sticky="w", padx=4, pady=(2, 12))

        self.form = ctk.CTkFrame(self, corner_radius=16)
        self.form.grid(row=1, column=0, sticky="ew", padx=4, pady=(0, 12))
        self._setup_form()

        self.items_frame = ctk.CTkScrollableFrame(self, corner_radius=16)
        self.items_frame.grid(row=2, column=0, sticky="nsew", padx=4, pady=(0, 4))
        self.items_frame.grid_columnconfigure(0, weight=1)

        self.items: list[dict] = []
        self._refresh_items()

    def _setup_form(self) -> None:
        self.form.grid_columnconfigure(1, weight=1)

        # Company info
        ctk.CTkLabel(self.form, text="Company Name", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, sticky="w", padx=14, pady=(12, 4)
        )
        self.company_name = ctk.CTkEntry(self.form)
        self.company_name.insert(0, "Acme Corp")
        self.company_name.grid(row=0, column=1, sticky="ew", padx=14, pady=(12, 4))

        ctk.CTkLabel(self.form, text="Company Address", font=ctk.CTkFont(weight="bold")).grid(
            row=1, column=0, sticky="w", padx=14, pady=(4, 4)
        )
        self.company_addr = ctk.CTkEntry(self.form)
        self.company_addr.insert(0, "123 Main St, City, State")
        self.company_addr.grid(row=1, column=1, sticky="ew", padx=14, pady=(4, 4))

        # Client info
        ctk.CTkLabel(self.form, text="Client Name", font=ctk.CTkFont(weight="bold")).grid(
            row=2, column=0, sticky="w", padx=14, pady=(4, 4)
        )
        self.client_name = ctk.CTkEntry(self.form)
        self.client_name.insert(0, "Client LLC")
        self.client_name.grid(row=2, column=1, sticky="ew", padx=14, pady=(4, 4))

        ctk.CTkLabel(self.form, text="Client Address", font=ctk.CTkFont(weight="bold")).grid(
            row=3, column=0, sticky="w", padx=14, pady=(4, 4)
        )
        self.client_addr = ctk.CTkEntry(self.form)
        self.client_addr.insert(0, "456 Oak St, Town, State")
        self.client_addr.grid(row=3, column=1, sticky="ew", padx=14, pady=(4, 4))

        # Invoice details
        ctk.CTkLabel(self.form, text="Invoice #", font=ctk.CTkFont(weight="bold")).grid(
            row=4, column=0, sticky="w", padx=14, pady=(4, 4)
        )
        self.invoice_number = ctk.CTkEntry(self.form)
        self.invoice_number.insert(0, "001")
        self.invoice_number.grid(row=4, column=1, sticky="ew", padx=14, pady=(4, 4))

        ctk.CTkLabel(self.form, text="Tax Rate (%)", font=ctk.CTkFont(weight="bold")).grid(
            row=5, column=0, sticky="w", padx=14, pady=(4, 12)
        )
        self.tax_rate = ctk.CTkEntry(self.form)
        self.tax_rate.insert(0, "10")
        self.tax_rate.grid(row=5, column=1, sticky="ew", padx=14, pady=(4, 12))

        btn_row = ctk.CTkFrame(self.form, fg_color="transparent")
        btn_row.grid(row=6, column=0, columnspan=2, sticky="w", padx=14, pady=(0, 12))

        ctk.CTkButton(btn_row, text="Add Item", command=self._add_item).pack(side="left")
        ctk.CTkButton(btn_row, text="Generate PDF", command=self._generate_pdf).pack(side="left", padx=(10, 0))

    def _add_item(self) -> None:
        self.items.append({"desc": "Service", "qty": 1, "price": 100.0})
        self._refresh_items()

    def _refresh_items(self) -> None:
        for w in self.items_frame.winfo_children():
            w.destroy()

        ctk.CTkLabel(self.items_frame, text="Items", font=ctk.CTkFont(size=16, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=14, pady=(12, 8)
        )

        for i, item in enumerate(self.items, start=1):
            row = ctk.CTkFrame(self.items_frame, fg_color="transparent")
            row.grid(row=i, column=0, sticky="ew", padx=14, pady=4)
            row.grid_columnconfigure(1, weight=1)

            desc = ctk.CTkEntry(row, width=200)
            desc.insert(0, item["desc"])
            desc.grid(row=0, column=0, padx=(0, 8))

            qty = ctk.CTkEntry(row, width=80)
            qty.insert(0, str(item["qty"]))
            qty.grid(row=0, column=1, padx=(0, 8))

            price = ctk.CTkEntry(row, width=100)
            price.insert(0, str(item["price"]))
            price.grid(row=0, column=2, padx=(0, 8))

            ctk.CTkButton(row, text="Remove", width=80, command=lambda idx=i-1: self._remove_item(idx)).grid(
                row=0, column=3
            )

    def _remove_item(self, idx: int) -> None:
        if 0 <= idx < len(self.items):
            del self.items[idx]
            self._refresh_items()

    def _generate_pdf(self) -> None:
        if not self.items:
            self.ctx.toast_host.show("Add at least one item", kind="error")
            return

        path = os.path.join(exports_dir(), f"invoice_{self.invoice_number.get()}.pdf")
        doc = SimpleDocTemplate(path, pagesize=letter)

        styles = getSampleStyleSheet()
        story = []

        story.append(Paragraph("INVOICE", styles["Title"]))
        story.append(Paragraph(f"Invoice #: {self.invoice_number.get()}", styles["Heading2"]))
        story.append(Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d')}", styles["Normal"]))
        story.append(Paragraph("", styles["Normal"]))

        story.append(Paragraph("From:", styles["Heading3"]))
        story.append(Paragraph(self.company_name.get(), styles["Normal"]))
        story.append(Paragraph(self.company_addr.get(), styles["Normal"]))
        story.append(Paragraph("", styles["Normal"]))

        story.append(Paragraph("To:", styles["Heading3"]))
        story.append(Paragraph(self.client_name.get(), styles["Normal"]))
        story.append(Paragraph(self.client_addr.get(), styles["Normal"]))
        story.append(Paragraph("", styles["Normal"]))

        data = [["Description", "Qty", "Unit Price", "Total"]]
        subtotal = 0.0
        for item in self.items:
            total = item["qty"] * item["price"]
            data.append([item["desc"], str(item["qty"]), f"${item['price']:.2f}", f"${total:.2f}"])
            subtotal += total

        tax = subtotal * float(self.tax_rate.get()) / 100
        grand_total = subtotal + tax

        data.append(["", "", "Subtotal", f"${subtotal:.2f}"])
        data.append(["", "", f"Tax ({self.tax_rate.get()}%)", f"${tax:.2f}"])
        data.append(["", "", "Grand Total", f"${grand_total:.2f}"])

        table = Table(data)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), "#cccccc"),
            ("TEXTCOLOR", (0, 0), (-1, 0), "#000000"),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 12),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("BACKGROUND", (0, 1), (-1, -1), "#f0f0f0"),
            ("GRID", (0, 0), (-1, -1), 1, "#000000")
        ]))
        story.append(table)

        doc.build(story)
        self.ctx.toast_host.show(f"Invoice saved to {os.path.basename(path)}", kind="success")
        self.ctx.storage.add_export_history({"generator": "invoice", "file": os.path.basename(path)})


class InvoiceGeneratorPlugin(GeneratorPlugin):
    meta = GeneratorMeta(
        id="invoice",
        name="PDF Invoice Generator",
        category="Documents",
        icon="🧾",
        description="Create professional PDF invoices with items, tax, and totals.",
    )

    def __init__(self, storage) -> None:
        self.storage = storage

    def create_frame(self, master: ctk.CTkFrame, toast_host) -> ctk.CTkFrame:
        ctx = GeneratorContext(storage=self.storage, toast_host=toast_host)
        return InvoiceGeneratorFrame(master, ctx)


def create_plugin(storage):
    return InvoiceGeneratorPlugin(storage)
