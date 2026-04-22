import json
import re
import sys
import threading
import subprocess
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

PROJECT_DIR  = Path(__file__).parent.parent
REQUESTS_DIR = PROJECT_DIR / "requests"
REQUESTS_DIR.mkdir(exist_ok=True)

BG_HEADER = "#0f1117"
BG_MAIN   = "#13151f"
BG_CARD   = "#1a1d2e"
BG_DEEP   = "#0d0f18"
ACCENT    = "#4f8ef7"


class ClientScreen(ctk.CTkFrame):
    def __init__(self, parent, client_name, on_back):
        super().__init__(parent, fg_color=BG_MAIN, corner_radius=0)
        self.client_name = client_name
        self.on_back     = on_back
        self._images     = []          # attached image paths for current request
        self._sheet_tasks = []         # list of (BooleanVar, row_list) tuples
        self._build()

    # ══════════════════════════════════════════════════════════════════════════
    # UI BUILD
    # ══════════════════════════════════════════════════════════════════════════

    def _build(self):
        self._build_header()
        self._build_tabs()
        self.tab_var.set("manual")
        self._switch_tab()

    def _build_header(self):
        hdr = ctk.CTkFrame(self, height=64, corner_radius=0, fg_color=BG_HEADER)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        ctk.CTkButton(
            hdr, text="← Volver", width=90, height=34,
            fg_color="transparent", hover_color="#1c1f30",
            font=ctk.CTkFont(size=13),
            command=self.on_back,
        ).pack(side="left", padx=12, pady=15)

        ctk.CTkLabel(
            hdr, text=self.client_name.upper(),
            font=ctk.CTkFont(size=19, weight="bold"), text_color="white",
        ).pack(side="left", padx=6)

    def _build_tabs(self):
        # Tab selector
        tab_bar = ctk.CTkFrame(self, height=48, corner_radius=0, fg_color=BG_DEEP)
        tab_bar.pack(fill="x")
        tab_bar.pack_propagate(False)

        self.tab_var = ctk.StringVar(value="manual")
        for label, val in [("✏️  Pedido manual", "manual"), ("📊  Google Sheet", "sheet")]:
            ctk.CTkRadioButton(
                tab_bar, text=label, variable=self.tab_var, value=val,
                command=self._switch_tab,
                font=ctk.CTkFont(size=13),
                fg_color=ACCENT,
            ).pack(side="left", padx=24, pady=12)

        # Containers
        self.manual_frame = self._make_manual_tab()
        self.sheet_frame  = self._make_sheet_tab()

    def _switch_tab(self):
        self.manual_frame.pack_forget()
        self.sheet_frame.pack_forget()
        if self.tab_var.get() == "manual":
            self.manual_frame.pack(fill="both", expand=True)
        else:
            self.sheet_frame.pack(fill="both", expand=True)

    # ── Manual tab ────────────────────────────────────────────────────────────

    def _make_manual_tab(self):
        frame = ctk.CTkFrame(self, fg_color=BG_MAIN, corner_radius=0)

        # Two-column layout
        left = ctk.CTkFrame(frame, fg_color=BG_MAIN)
        left.pack(side="left", fill="both", expand=True, padx=(24, 12), pady=24)

        right = ctk.CTkFrame(frame, fg_color=BG_MAIN)
        right.pack(side="right", fill="both", expand=True, padx=(12, 24), pady=24)

        # ── LEFT: new request ─────────────────────────────────────────────
        ctk.CTkLabel(
            left, text="Nuevo pedido de diseño", anchor="w",
            font=ctk.CTkFont(size=15, weight="bold"),
        ).pack(anchor="w", pady=(0, 8))

        self.req_text = ctk.CTkTextbox(left, height=200, corner_radius=8,
                                        font=ctk.CTkFont(size=13), fg_color=BG_CARD,
                                        border_width=1, border_color="#252840")
        self.req_text.pack(fill="x")
        self.req_text.insert("1.0", "Describí el pedido...")
        self.req_text.bind("<FocusIn>", self._clear_placeholder)

        # Image attach
        attach_row = ctk.CTkFrame(left, fg_color="transparent")
        attach_row.pack(fill="x", pady=(12, 4))
        ctk.CTkLabel(attach_row, text="Imágenes de referencia:",
                     font=ctk.CTkFont(size=12), text_color="#9ca3af").pack(side="left")
        ctk.CTkButton(
            attach_row, text="📎 Adjuntar", width=100, height=30,
            fg_color="#252840", hover_color="#333660",
            font=ctk.CTkFont(size=12),
            command=self._attach_images,
        ).pack(side="right")

        self.img_scroll = ctk.CTkScrollableFrame(
            left, height=76, fg_color=BG_DEEP, corner_radius=6,
        )
        self.img_scroll.pack(fill="x", pady=(0, 14))

        ctk.CTkButton(
            left, text="🚀  Ejecutar en Photoshop", height=44,
            fg_color="#16a34a", hover_color="#15803d",
            font=ctk.CTkFont(size=15, weight="bold"), corner_radius=8,
            command=self._execute_manual,
        ).pack(fill="x")

        # Status label
        self.manual_status = ctk.CTkLabel(left, text="", font=ctk.CTkFont(size=12),
                                           text_color="#9ca3af")
        self.manual_status.pack(anchor="w", pady=(8, 0))

        # ── RIGHT: history ────────────────────────────────────────────────
        ctk.CTkLabel(
            right, text="Historial de pedidos", anchor="w",
            font=ctk.CTkFont(size=15, weight="bold"),
        ).pack(anchor="w", pady=(0, 8))

        self.history_scroll = ctk.CTkScrollableFrame(right, fg_color=BG_MAIN, corner_radius=0)
        self.history_scroll.pack(fill="both", expand=True)
        self._refresh_history()

        return frame

    # ── Sheet tab ─────────────────────────────────────────────────────────────

    def _make_sheet_tab(self):
        frame = ctk.CTkFrame(self, fg_color=BG_MAIN, corner_radius=0)

        # URL input area
        url_box = ctk.CTkFrame(frame, fg_color=BG_CARD, corner_radius=10,
                                border_width=1, border_color="#252840")
        url_box.pack(fill="x", padx=24, pady=(24, 0))

        ctk.CTkLabel(
            url_box, text="Google Sheet con pedidos de diseño",
            font=ctk.CTkFont(size=14, weight="bold"), anchor="w",
        ).pack(anchor="w", padx=16, pady=(14, 6))

        url_row = ctk.CTkFrame(url_box, fg_color="transparent")
        url_row.pack(fill="x", padx=16, pady=(0, 6))

        self.sheet_url = ctk.CTkEntry(
            url_row,
            placeholder_text="https://docs.google.com/spreadsheets/d/...",
            height=38, font=ctk.CTkFont(size=12), fg_color=BG_DEEP,
        )
        self.sheet_url.pack(side="left", fill="x", expand=True, padx=(0, 10))

        ctk.CTkButton(
            url_row, text="🔍 Analizar", width=110, height=38,
            fg_color=ACCENT, hover_color="#3a7aee",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._analyze_sheet,
        ).pack(side="right")

        # Save URL row
        save_row = ctk.CTkFrame(url_box, fg_color="transparent")
        save_row.pack(fill="x", padx=16, pady=(0, 14))

        self.sheet_status = ctk.CTkLabel(save_row, text="", font=ctk.CTkFont(size=12),
                                          text_color="#9ca3af")
        self.sheet_status.pack(side="left")

        ctk.CTkButton(
            save_row, text="💾 Guardar link", width=120, height=28,
            fg_color="transparent", border_width=1, border_color="#333660",
            font=ctk.CTkFont(size=12),
            command=self._save_sheet_url,
        ).pack(side="right")

        # Load saved URL
        saved = self._load_sheet_url()
        if saved:
            self.sheet_url.insert(0, saved)

        # Tasks area
        ctk.CTkLabel(
            frame, text="Tareas encontradas:", anchor="w",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).pack(anchor="w", padx=24, pady=(16, 4))

        self.tasks_scroll = ctk.CTkScrollableFrame(
            frame, fg_color=BG_DEEP, corner_radius=8,
        )
        self.tasks_scroll.pack(fill="both", expand=True, padx=24, pady=(0, 12))

        ctk.CTkButton(
            frame, text="🚀  Ejecutar tareas seleccionadas", height=44,
            fg_color="#16a34a", hover_color="#15803d",
            font=ctk.CTkFont(size=15, weight="bold"), corner_radius=8,
            command=self._execute_sheet_tasks,
        ).pack(fill="x", padx=24, pady=(0, 24))

        return frame

    # ══════════════════════════════════════════════════════════════════════════
    # ACTIONS
    # ══════════════════════════════════════════════════════════════════════════

    def _clear_placeholder(self, event=None):
        if self.req_text.get("1.0", "end").strip() == "Describí el pedido...":
            self.req_text.delete("1.0", "end")

    # ── Image attach ──────────────────────────────────────────────────────────

    def _attach_images(self):
        paths = filedialog.askopenfilenames(
            title="Seleccionar imágenes de referencia",
            filetypes=[
                ("Imágenes", "*.jpg *.jpeg *.png *.psd *.webp *.gif"),
                ("Todos los archivos", "*.*"),
            ],
        )
        for p in paths:
            if p not in self._images:
                self._images.append(p)
                self._add_img_chip(p)

    def _add_img_chip(self, path):
        chip = ctk.CTkFrame(self.img_scroll, fg_color="#1e223a", corner_radius=5, height=28)
        chip.pack(fill="x", pady=2, padx=2)
        chip.pack_propagate(False)
        ctk.CTkLabel(
            chip, text="🖼  " + Path(path).name, anchor="w",
            font=ctk.CTkFont(size=11), text_color="#d1d5db",
        ).pack(side="left", padx=8, fill="x", expand=True)
        ctk.CTkButton(
            chip, text="✕", width=26, height=22,
            fg_color="transparent", hover_color="#3b1c1c", text_color="#9ca3af",
            command=lambda: self._remove_img(path, chip),
        ).pack(side="right", padx=4)

    def _remove_img(self, path, chip):
        self._images = [p for p in self._images if p != path]
        chip.destroy()

    # ── Manual execution ──────────────────────────────────────────────────────

    def _execute_manual(self):
        text = self.req_text.get("1.0", "end").strip()
        if not text or text == "Describí el pedido...":
            messagebox.showwarning("Pedido vacío", "Escribí el pedido antes de ejecutar.")
            return

        req = {
            "id":        datetime.now().strftime("%Y%m%d_%H%M%S"),
            "timestamp": datetime.now().isoformat(),
            "text":      text,
            "images":    list(self._images),
            "status":    "executing",
        }
        self._save_req(req)
        self._refresh_history()
        self.manual_status.configure(text="⚙️  Ejecutando en Photoshop...", text_color="#60a5fa")

        # Reset form
        self.req_text.delete("1.0", "end")
        self.req_text.insert("1.0", "Describí el pedido...")
        self._images.clear()
        for w in self.img_scroll.winfo_children():
            w.destroy()

        threading.Thread(target=self._run_agent, args=(req,), daemon=True).start()

    def _run_agent(self, req):
        try:
            cmd = [
                sys.executable, str(PROJECT_DIR / "main.py"),
                req["text"],
                "--load-client", self.client_name,
                "--quiet",
            ]
            for img in req.get("images", []):
                cmd += ["--reference-psd", img]

            result = subprocess.run(
                cmd, capture_output=True, text=True,
                timeout=600, cwd=str(PROJECT_DIR),
            )
            status = "done" if result.returncode == 0 else "error"
            output = (result.stdout or result.stderr or "")[-600:]
        except subprocess.TimeoutExpired:
            status, output = "error", "Timeout (10 min)"
        except Exception as e:
            status, output = "error", str(e)

        self._update_req(req["id"], status, output)
        self.after(0, self._refresh_history)
        self.after(0, lambda: self.manual_status.configure(
            text=f"{'✓ Listo' if status == 'done' else '✗ Error'}: {output[:80]}",
            text_color="#4ade80" if status == "done" else "#f87171",
        ))

    # ── Sheet analysis ────────────────────────────────────────────────────────

    def _analyze_sheet(self):
        url = self.sheet_url.get().strip()
        if not url:
            messagebox.showwarning("URL vacía", "Pegá el link del Google Sheet.")
            return
        sheet_id = _extract_sheet_id(url)
        if not sheet_id:
            messagebox.showerror("URL inválida", "No se pudo extraer el ID del Sheet.\n"
                                  "Revisá que sea un link de Google Sheets.")
            return
        self.sheet_status.configure(text="⏳ Leyendo sheet...", text_color="#fbbf24")
        threading.Thread(target=self._fetch_sheet, args=(sheet_id,), daemon=True).start()

    def _fetch_sheet(self, sheet_id):
        try:
            sys.path.insert(0, str(PROJECT_DIR / "tools"))
            from drive_reader import read_sheet_rows
            rows = read_sheet_rows(sheet_id)
            self.after(0, lambda: self._display_tasks(rows))
        except Exception as e:
            msg = str(e)
            self.after(0, lambda: self.sheet_status.configure(
                text=f"Error: {msg[:80]}", text_color="#f87171",
            ))

    def _display_tasks(self, rows):
        for w in self.tasks_scroll.winfo_children():
            w.destroy()
        self._sheet_tasks.clear()

        if not rows:
            self.sheet_status.configure(text="El sheet está vacío.", text_color="#9ca3af")
            return

        data_rows = rows[1:] if len(rows) > 1 else rows
        headers   = rows[0] if len(rows) > 1 else []

        self.sheet_status.configure(
            text=f"✓  {len(data_rows)} fila(s) encontradas",
            text_color="#4ade80",
        )

        # Column headers
        if headers:
            h = ctk.CTkFrame(self.tasks_scroll, fg_color="#1a1d2e", corner_radius=4, height=30)
            h.pack(fill="x", padx=4, pady=(4, 2))
            h.pack_propagate(False)
            ctk.CTkLabel(
                h, text="   " + "   |   ".join(str(x) for x in headers),
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="#93c5fd", anchor="w",
            ).pack(side="left", padx=10, fill="x")

        # Data rows with checkboxes
        for row in data_rows:
            var = ctk.BooleanVar(value=True)
            self._sheet_tasks.append((var, row))

            r = ctk.CTkFrame(self.tasks_scroll, fg_color=BG_CARD, corner_radius=6, height=38)
            r.pack(fill="x", padx=4, pady=3)
            r.pack_propagate(False)

            ctk.CTkCheckBox(r, text="", variable=var, width=30,
                            fg_color=ACCENT).pack(side="left", padx=8)
            cell_text = "   |   ".join(str(c) for c in row if c)
            ctk.CTkLabel(
                r, text=cell_text, anchor="w",
                font=ctk.CTkFont(size=12), text_color="#e5e7eb",
            ).pack(side="left", fill="x", expand=True, padx=(0, 10))

    def _execute_sheet_tasks(self):
        selected = [(v, r) for v, r in self._sheet_tasks if v.get()]
        if not selected:
            messagebox.showwarning("Sin selección", "Seleccioná al menos una tarea.")
            return

        count = len(selected)
        for var, row in selected:
            task_text = " — ".join(str(c) for c in row if c)
            req = {
                "id":        datetime.now().strftime("%Y%m%d_%H%M%S"),
                "timestamp": datetime.now().isoformat(),
                "text":      f"[Sheet] {task_text}",
                "images":    [],
                "status":    "executing",
                "source":    "sheet",
            }
            self._save_req(req)
            threading.Thread(target=self._run_agent, args=(req,), daemon=True).start()

        self.tab_var.set("manual")
        self._switch_tab()
        self._refresh_history()
        self.manual_status.configure(
            text=f"⚙️  {count} tarea(s) enviadas a Photoshop...",
            text_color="#60a5fa",
        )

    # ── Sheet URL persistence ─────────────────────────────────────────────────

    def _client_path(self):
        return PROJECT_DIR / "clients" / f"{self.client_name}.json"

    def _load_sheet_url(self):
        p = self._client_path()
        if p.exists():
            try:
                return json.loads(p.read_text(encoding="utf-8")).get("sheet_url", "")
            except Exception:
                pass
        return ""

    def _save_sheet_url(self):
        url = self.sheet_url.get().strip()
        p   = self._client_path()
        try:
            data = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {"client_name": self.client_name}
            data["sheet_url"] = url
            p.write_text(json.dumps(data, ensure_ascii=False, indent=2))
            self.sheet_status.configure(text="✓ Link guardado", text_color="#4ade80")
        except Exception as e:
            messagebox.showerror("Error al guardar", str(e))

    # ── Request store ─────────────────────────────────────────────────────────

    def _req_path(self):
        return REQUESTS_DIR / f"{self.client_name}.json"

    def _load_reqs(self):
        p = self._req_path()
        if p.exists():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                pass
        return []

    def _save_req(self, req):
        reqs = self._load_reqs()
        reqs.insert(0, req)
        self._req_path().write_text(json.dumps(reqs, ensure_ascii=False, indent=2))

    def _update_req(self, req_id, status, output=""):
        reqs = self._load_reqs()
        for r in reqs:
            if r["id"] == req_id:
                r["status"] = status
                r["result"] = output
                break
        self._req_path().write_text(json.dumps(reqs, ensure_ascii=False, indent=2))

    def _refresh_history(self):
        for w in self.history_scroll.winfo_children():
            w.destroy()
        reqs = self._load_reqs()
        if not reqs:
            ctk.CTkLabel(
                self.history_scroll, text="Sin pedidos todavía.",
                font=ctk.CTkFont(size=13), text_color="#6b7280",
            ).pack(pady=30)
            return
        for req in reqs[:30]:
            _HistoryCard(self.history_scroll, req).pack(fill="x", pady=5, padx=2)


# ══════════════════════════════════════════════════════════════════════════════
# History card widget
# ══════════════════════════════════════════════════════════════════════════════

_STATUS_COLORS = {
    "executing": "#60a5fa",
    "done":      "#4ade80",
    "error":     "#f87171",
    "pending":   "#fbbf24",
}
_STATUS_ICONS = {
    "executing": "⚙️",
    "done":      "✓",
    "error":     "✗",
    "pending":   "⏳",
}


class _HistoryCard(ctk.CTkFrame):
    def __init__(self, parent, req):
        super().__init__(
            parent, corner_radius=8, fg_color=BG_CARD,
            border_width=1, border_color="#252840",
        )
        status = req.get("status", "pending")
        color  = _STATUS_COLORS.get(status, "#9ca3af")
        icon   = _STATUS_ICONS.get(status, "·")

        # Top row: timestamp + status badge
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=14, pady=(10, 4))

        ts = req.get("timestamp", "")[:16].replace("T", "  ")
        src = "  [Sheet]" if req.get("source") == "sheet" else ""
        ctk.CTkLabel(
            top, text=f"{ts}{src}", anchor="w",
            font=ctk.CTkFont(size=11), text_color="#6b7280",
        ).pack(side="left")

        ctk.CTkLabel(
            top, text=f"{icon}  {status.upper()}",
            font=ctk.CTkFont(size=10, weight="bold"), text_color=color,
        ).pack(side="right")

        # Request text preview
        preview = (req.get("text") or "")[:160]
        if len(req.get("text", "")) > 160:
            preview += "…"
        ctk.CTkLabel(
            self, text=preview, anchor="w", justify="left",
            wraplength=360, font=ctk.CTkFont(size=12), text_color="#d1d5db",
        ).pack(anchor="w", padx=14, pady=(0, 4))

        # Images indicator
        if req.get("images"):
            ctk.CTkLabel(
                self, text=f"📎  {len(req['images'])} imagen(es) adjunta(s)",
                anchor="w", font=ctk.CTkFont(size=11), text_color="#93c5fd",
            ).pack(anchor="w", padx=14)

        # Result snippet (if done/error)
        if req.get("result") and status in ("done", "error"):
            snippet = req["result"][:100] + ("…" if len(req["result"]) > 100 else "")
            ctk.CTkLabel(
                self, text=snippet, anchor="w", justify="left",
                wraplength=360, font=ctk.CTkFont(size=11),
                text_color="#4ade80" if status == "done" else "#f87171",
            ).pack(anchor="w", padx=14, pady=(2, 0))

        ctk.CTkFrame(self, height=1, fg_color="transparent").pack(pady=4)


# ══════════════════════════════════════════════════════════════════════════════
# Helpers
# ══════════════════════════════════════════════════════════════════════════════

def _extract_sheet_id(url: str):
    m = re.search(r"/spreadsheets/d/([a-zA-Z0-9_-]+)", url)
    return m.group(1) if m else None
