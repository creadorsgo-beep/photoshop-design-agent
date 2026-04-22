import json
import customtkinter as ctk
from pathlib import Path

CLIENTS_DIR = Path(__file__).parent.parent / "clients"

BG_HEADER = "#0f1117"
BG_MAIN   = "#13151f"
BG_CARD   = "#1a1d2e"
ACCENT    = "#4f8ef7"


class MainScreen(ctk.CTkFrame):
    def __init__(self, parent, on_select):
        super().__init__(parent, fg_color=BG_MAIN, corner_radius=0)
        self.on_select = on_select
        self._build()

    def _build(self):
        # ── Header ──────────────────────────────────────────────────────────
        header = ctk.CTkFrame(self, height=64, corner_radius=0, fg_color=BG_HEADER)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header, text="⬡  Design Agent",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=ACCENT,
        ).pack(side="left", padx=24)

        ctk.CTkButton(
            header, text="+ Nuevo cliente", width=150, height=36,
            fg_color=ACCENT, hover_color="#3a7aee",
            font=ctk.CTkFont(size=13, weight="bold"),
            corner_radius=8,
            command=self._new_client,
        ).pack(side="right", padx=24, pady=14)

        # ── Subtitle ─────────────────────────────────────────────────────────
        sub = ctk.CTkFrame(self, height=44, corner_radius=0, fg_color="#0d0f18")
        sub.pack(fill="x")
        sub.pack_propagate(False)
        ctk.CTkLabel(
            sub, text="Seleccioná un cliente para gestionar sus pedidos",
            font=ctk.CTkFont(size=12), text_color="#6b7280",
        ).pack(side="left", padx=24, pady=0)

        # ── Client grid ──────────────────────────────────────────────────────
        self.scroll = ctk.CTkScrollableFrame(self, fg_color=BG_MAIN, corner_radius=0)
        self.scroll.pack(fill="both", expand=True, padx=0, pady=0)

        self._load_clients()

    def _load_clients(self):
        for w in self.scroll.winfo_children():
            w.destroy()

        paths = sorted(CLIENTS_DIR.glob("*.json"))
        if not paths:
            ctk.CTkLabel(
                self.scroll,
                text="No hay clientes todavía.\nUsá el botón «+ Nuevo cliente» para empezar.",
                font=ctk.CTkFont(size=14), text_color="#6b7280",
            ).pack(pady=60)
            return

        COLS = 3
        for c in range(COLS):
            self.scroll.columnconfigure(c, weight=1)

        for i, path in enumerate(paths):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                data = {}

            name  = data.get("client_name") or path.stem
            color = _primary_color(data)

            card = _ClientCard(
                self.scroll, name=name, color=color,
                on_click=lambda n=name: self.on_select(n),
            )
            card.grid(row=i // COLS, column=i % COLS, padx=16, pady=16, sticky="nsew")

    def _new_client(self):
        dialog = ctk.CTkInputDialog(text="Nombre del cliente:", title="Nuevo cliente")
        name = dialog.get_input()
        if name and name.strip():
            path = CLIENTS_DIR / f"{name.strip()}.json"
            if not path.exists():
                path.write_text(
                    json.dumps({"client_name": name.strip(), "style_guide": {}},
                               ensure_ascii=False, indent=2)
                )
            self._load_clients()


def _primary_color(data):
    try:
        return data["style_guide"]["colors"]["primary"]
    except (KeyError, TypeError):
        return "#4f8ef7"


class _ClientCard(ctk.CTkFrame):
    def __init__(self, parent, name, color, on_click):
        super().__init__(
            parent, cursor="hand2", height=110, corner_radius=12,
            fg_color=BG_CARD, border_width=1, border_color="#252840",
        )
        self.pack_propagate(False)

        # Color accent strip on the left
        accent = ctk.CTkFrame(self, width=5, corner_radius=0, fg_color=color)
        accent.pack(side="left", fill="y")

        # Content
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(side="left", fill="both", expand=True, padx=18, pady=14)

        ctk.CTkLabel(
            content, text=name.upper(), anchor="w",
            font=ctk.CTkFont(size=16, weight="bold"), text_color="white",
        ).pack(anchor="w")

        ctk.CTkLabel(
            content, text="Pedidos · Sheet · Historial  →", anchor="w",
            font=ctk.CTkFont(size=11), text_color="#6b7280",
        ).pack(anchor="w", pady=(3, 0))

        # Color dot
        dot = ctk.CTkFrame(self, width=14, height=14, corner_radius=7, fg_color=color)
        dot.pack(side="right", padx=18)

        # Click bindings throughout the whole card
        self._bind_click(on_click)

    def _bind_click(self, cmd):
        for w in [self] + list(self._iter_children(self)):
            try:
                w.bind("<Button-1>", lambda e: cmd())
            except Exception:
                pass

    def _iter_children(self, widget):
        for child in widget.winfo_children():
            yield child
            yield from self._iter_children(child)
