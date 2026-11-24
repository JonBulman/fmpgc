"""
FMPGC Membership Communication & Administration System - GUI
Styled in accordance with the Flushing & Mylor Pilot Gig Club (FMPGC) Style Guide.

Place this file in: src/fmpgc_package/fmpgc_gui.py
Run with: python -m fmpgc_package.fmpgc_gui
"""

# Standard library
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import argparse
import os
import queue
import sys
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

# Third-party
import pandas as pd

# Local package imports
from fmpgc_package import (
    config_utils,
    fmpgc_classes,
    send_email,
    setup_environment,
)


# ----------------------------------------------------------------------
# FMPGC Club Colour Palette & Typography (from FMPGC_Style_Guide.md)
# ----------------------------------------------------------------------
COLOR_PRIMARY = "#810E49"       # Deep raspberry/burgundy — header, headings, primary buttons
COLOR_PRIMARY_DARK = "#650B39"  # Dark wine — hover states & strong accents
COLOR_ACCENT_GOLD = "#FFC857"   # Warm gold — accents on dark burgundy backgrounds only
COLOR_BG_PAGE = "#FAF7F8"       # Soft off-white — main window background
COLOR_SURFACE = "#FFFFFF"       # White — content cards, inputs & tables
COLOR_TEXT_MAIN = "#25202A"     # Charcoal — primary body text
COLOR_TEXT_MUTED = "#57505A"    # Muted charcoal — secondary/explanatory text
COLOR_BORDER = "#E8DFE4"        # Pale rose-grey — card borders, dividers & table rules
COLOR_ROW_ALT = "#F6F1F4"       # Subtle rose-tinted off-white for alternating table rows
COLOR_BTN_SECONDARY_HOVER = "#F2E9EE"

FONT_FAMILY = "Arial"
FONT_HEADER_TITLE = (FONT_FAMILY, 15, "bold")
FONT_HEADER_SUB = (FONT_FAMILY, 10)
FONT_SECTION = (FONT_FAMILY, 11, "bold")
FONT_BODY = (FONT_FAMILY, 10)
FONT_BODY_BOLD = (FONT_FAMILY, 10, "bold")
FONT_SMALL = (FONT_FAMILY, 9)
FONT_MONO = ("Consolas", 9)


class FMPGCGuiApp:
    def __init__(
        self,
        root: tk.Tk,
        data_folder: str = "data/",
        config_file: str = "data/fmpgc_settings.json",
        csv_file: str = "data/fmpgc_members.csv",
    ):
        self.root = root
        self.root.title("Flushing & Mylor Pilot Gig Club — Membership Administration")
        self.root.geometry("1040x700")
        self.root.minsize(820, 520)
        self.root.configure(bg=COLOR_BG_PAGE)

        # Runtime state
        self.config = None
        self.csv_data: pd.DataFrame | None = None
        self.templates: dict[str, str] = {}
        self.message_log = config_utils.SystemMonitor()

        # Config variables
        self.it_credentials = None
        self.it_token_file = None
        self.membership_credentials = None
        self.membership_token_file = None
        self.fmpgc_it_email = None
        self.fmpgc_membership_email = None
        self.bcc_emails = None

        # Threading & UI queue
        self.log_queue: queue.Queue = queue.Queue()
        self.stop_event = threading.Event()
        self.worker_thread: threading.Thread | None = None

        # Tk variables
        self.data_folder_var = tk.StringVar(value=data_folder)
        self.config_file_var = tk.StringVar(value=config_file)
        self.csv_file_var = tk.StringVar(value=csv_file)
        self.option_var = tk.StringVar(value=fmpgc_classes.OPTION_DEFINITIONS[0][0])
        self.bcc_mode_var = tk.BooleanVar(value=False)

        # Tailored template variables
        self.broadcast_template_var = tk.StringVar(value="membership_broadcast.html")
        self.custom_subject_var = tk.StringVar(value="")
        self.attachment_var = tk.StringVar(value="")
        self.status_var = tk.StringVar(value="Ready. Load configuration and members CSV to begin.")

        self._option_lookup = {label: (opt, subj, tmpl_key) for label, opt, subj, tmpl_key in fmpgc_classes.OPTION_DEFINITIONS}

        self._configure_styles()
        self._build_ui()
        self._poll_log_queue()

        # Attempt initial load on startup
        self.root.after(150, self._startup_init)

    # ------------------------------------------------------------------
    # FMPGC Theme & Widget Styling
    # ------------------------------------------------------------------
    def _configure_styles(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        # Base frames & labels
        style.configure("Page.TFrame", background=COLOR_BG_PAGE)
        style.configure("Card.TFrame", background=COLOR_SURFACE)
        style.configure(
            "CardBody.TLabel",
            background=COLOR_SURFACE,
            foreground=COLOR_TEXT_MAIN,
            font=FONT_BODY,
        )
        style.configure(
            "Muted.TLabel",
            background=COLOR_SURFACE,
            foreground=COLOR_TEXT_MUTED,
            font=FONT_SMALL,
        )

        # Primary Button: Burgundy background, White text, Dark Burgundy hover
        style.configure(
            "Primary.TButton",
            background=COLOR_PRIMARY,
            foreground=COLOR_SURFACE,
            bordercolor=COLOR_PRIMARY,
            lightcolor=COLOR_PRIMARY,
            darkcolor=COLOR_PRIMARY_DARK,
            font=FONT_BODY_BOLD,
            padding=(16, 7),
            relief="flat",
        )
        style.map(
            "Primary.TButton",
            background=[
                ("disabled", COLOR_BORDER),
                ("pressed", COLOR_PRIMARY_DARK),
                ("active", COLOR_PRIMARY_DARK),
            ],
            foreground=[
                ("disabled", COLOR_TEXT_MUTED),
                ("active", COLOR_SURFACE),
            ],
            bordercolor=[
                ("disabled", COLOR_BORDER),
                ("active", COLOR_PRIMARY_DARK),
            ],
        )

        # Secondary Button: White background, Burgundy text & border
        style.configure(
            "Secondary.TButton",
            background=COLOR_SURFACE,
            foreground=COLOR_PRIMARY,
            bordercolor=COLOR_PRIMARY,
            lightcolor=COLOR_SURFACE,
            darkcolor=COLOR_BORDER,
            font=FONT_BODY_BOLD,
            padding=(12, 5),
            relief="solid",
        )
        style.map(
            "Secondary.TButton",
            background=[
                ("disabled", COLOR_BG_PAGE),
                ("pressed", COLOR_BTN_SECONDARY_HOVER),
                ("active", COLOR_BTN_SECONDARY_HOVER),
            ],
            foreground=[
                ("disabled", COLOR_TEXT_MUTED),
                ("active", COLOR_PRIMARY_DARK),
            ],
            bordercolor=[
                ("disabled", COLOR_BORDER),
                ("active", COLOR_PRIMARY_DARK),
            ],
        )

        # Subtle Browse Button: Off-white surface with rose-grey border
        style.configure(
            "Browse.TButton",
            background=COLOR_BG_PAGE,
            foreground=COLOR_TEXT_MAIN,
            bordercolor=COLOR_BORDER,
            lightcolor=COLOR_BG_PAGE,
            darkcolor=COLOR_BORDER,
            font=FONT_SMALL,
            padding=(10, 4),
            relief="solid",
        )
        style.map(
            "Browse.TButton",
            background=[
                ("disabled", COLOR_BG_PAGE),
                ("active", COLOR_BTN_SECONDARY_HOVER),
            ],
            foreground=[
                ("disabled", COLOR_TEXT_MUTED),
                ("active", COLOR_PRIMARY),
            ],
            bordercolor=[
                ("disabled", COLOR_BORDER),
                ("active", COLOR_PRIMARY),
            ],
        )

        # Checkbutton
        style.configure(
            "Card.TCheckbutton",
            background=COLOR_SURFACE,
            foreground=COLOR_TEXT_MAIN,
            font=FONT_BODY,
        )
        style.map(
            "Card.TCheckbutton",
            background=[("active", COLOR_SURFACE)],
            foreground=[("disabled", COLOR_TEXT_MUTED)],
        )

        # Entry & Combobox
        style.configure(
            "FMPGC.TEntry",
            fieldbackground=COLOR_SURFACE,
            foreground=COLOR_TEXT_MAIN,
            bordercolor=COLOR_BORDER,
            lightcolor=COLOR_BORDER,
            darkcolor=COLOR_BORDER,
            insertcolor=COLOR_PRIMARY,
            padding=(6, 4),
            font=FONT_BODY,
        )
        style.map(
            "FMPGC.TEntry",
            fieldbackground=[("disabled", COLOR_BG_PAGE)],
            foreground=[("disabled", COLOR_TEXT_MUTED)],
            bordercolor=[("focus", COLOR_PRIMARY)],
        )

        style.configure(
            "FMPGC.TCombobox",
            fieldbackground=COLOR_SURFACE,
            background=COLOR_BG_PAGE,
            foreground=COLOR_TEXT_MAIN,
            arrowcolor=COLOR_PRIMARY,
            bordercolor=COLOR_BORDER,
            padding=(6, 4),
            font=FONT_BODY,
        )
        style.map(
            "FMPGC.TCombobox",
            fieldbackground=[
                ("readonly", COLOR_SURFACE),
                ("disabled", COLOR_BG_PAGE),
            ],
            foreground=[
                ("readonly", COLOR_TEXT_MAIN),
                ("disabled", COLOR_TEXT_MUTED),
            ],
            bordercolor=[("focus", COLOR_PRIMARY)],
        )

        # Treeview (Members Table)
        style.configure(
            "FMPGC.Treeview",
            background=COLOR_SURFACE,
            fieldbackground=COLOR_SURFACE,
            foreground=COLOR_TEXT_MAIN,
            bordercolor=COLOR_BORDER,
            rowheight=25,
            font=FONT_BODY,
        )
        style.configure(
            "FMPGC.Treeview.Heading",
            background=COLOR_PRIMARY,
            foreground=COLOR_SURFACE,
            bordercolor=COLOR_PRIMARY_DARK,
            relief="flat",
            font=FONT_BODY_BOLD,
            padding=(8, 5),
        )
        style.map(
            "FMPGC.Treeview.Heading",
            background=[("active", COLOR_PRIMARY_DARK)],
        )
        style.map(
            "FMPGC.Treeview",
            background=[("selected", COLOR_PRIMARY)],
            foreground=[("selected", COLOR_SURFACE)],
        )

        # Scrollbar
        style.configure(
            "FMPGC.Vertical.TScrollbar",
            background=COLOR_BORDER,
            troughcolor=COLOR_BG_PAGE,
            bordercolor=COLOR_BORDER,
            arrowcolor=COLOR_PRIMARY,
        )
        style.map(
            "FMPGC.Vertical.TScrollbar",
            background=[("active", COLOR_PRIMARY)],
        )

        # Progressbar
        style.configure(
            "FMPGC.Horizontal.TProgressbar",
            troughcolor=COLOR_BORDER,
            background=COLOR_PRIMARY,
            bordercolor=COLOR_BORDER,
            lightcolor=COLOR_PRIMARY,
            darkcolor=COLOR_PRIMARY_DARK,
        )

    def _create_card(self, parent, title: str, subtitle: str | None = None, expand: bool = False) -> tk.Frame:
        """Create a white card container with a pale rose-grey border and burgundy heading."""
        outer = tk.Frame(
            parent,
            bg=COLOR_SURFACE,
            highlightbackground=COLOR_BORDER,
            highlightthickness=1,
            padx=16,
            pady=10,
        )
        outer.pack(fill=tk.BOTH if expand else tk.X, expand=expand, pady=(0, 10))

        header_row = tk.Frame(outer, bg=COLOR_SURFACE)
        header_row.pack(fill=tk.X, pady=(0, 6))

        tk.Label(
            header_row,
            text=title,
            bg=COLOR_SURFACE,
            fg=COLOR_PRIMARY,
            font=FONT_SECTION,
            anchor=tk.W,
        ).pack(side=tk.LEFT)

        if subtitle:
            tk.Label(
                header_row,
                text=subtitle,
                bg=COLOR_SURFACE,
                fg=COLOR_TEXT_MUTED,
                font=FONT_SMALL,
                anchor=tk.E,
            ).pack(side=tk.RIGHT)

        # Subtle horizontal divider rule
        tk.Frame(outer, bg=COLOR_BORDER, height=1).pack(fill=tk.X, pady=(0, 8))

        body = tk.Frame(outer, bg=COLOR_SURFACE)
        body.pack(fill=tk.BOTH, expand=True)
        return body

    # ------------------------------------------------------------------
    # Page Scrolling Helpers
    # ------------------------------------------------------------------
    def _on_frame_configure(self, _event=None):
        """Update canvas scrollregion whenever inner content changes size."""
        self.page_canvas.configure(scrollregion=self.page_canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        """Keep the inner card container matched to the visible canvas width."""
        self.page_canvas.itemconfigure(self._canvas_window, width=event.width)

    def _is_descendant_of(self, widget, ancestor) -> bool:
        """Return True if widget is ancestor or contained inside ancestor."""
        current = widget
        while current is not None:
            if current == ancestor:
                return True
            current = getattr(current, "master", None)
        return False

    def _on_mousewheel(self, event):
        """Scroll the main page vertically unless the cursor is over an inner scrollable widget."""
        hovered = self.root.winfo_containing(event.x_root, event.y_root)
        if hovered is not None and (
            self._is_descendant_of(hovered, self.member_tree)
            or self._is_descendant_of(hovered, self.log_text)
        ):
            return

        # Only scroll when content exceeds the visible viewport height
        if self.page_canvas.yview() == (0.0, 1.0):
            return

        if getattr(event, "num", None) == 4:
            self.page_canvas.yview_scroll(-1, "units")
        elif getattr(event, "num", None) == 5:
            self.page_canvas.yview_scroll(1, "units")
        elif getattr(event, "delta", 0):
            if sys.platform == "darwin":
                self.page_canvas.yview_scroll(int(-1 * event.delta), "units")
            else:
                self.page_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # ------------------------------------------------------------------
    # Startup Initialisation
    # ------------------------------------------------------------------
    def _startup_init(self):
        todays_date = datetime.now(tz=ZoneInfo("Europe/London"))
        self.log(f"Application started: {todays_date:%Y-%m-%d %H:%M:%S %Z}")
        self.log(f"Working directory: [{os.getcwd()}]")
        setup_environment()
        self.load_all_data(silent_if_missing=True)

    # ------------------------------------------------------------------
    # UI Construction
    # ------------------------------------------------------------------
    def _build_ui(self):
        # 1. Fixed Branded Club Header Banner (Burgundy + Gold accent strip)
        banner = tk.Frame(self.root, bg=COLOR_PRIMARY, padx=20, pady=10)
        banner.pack(side=tk.TOP, fill=tk.X)

        title_col = tk.Frame(banner, bg=COLOR_PRIMARY)
        title_col.pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Label(
            title_col,
            text="Flushing & Mylor Pilot Gig Club",
            bg=COLOR_PRIMARY,
            fg=COLOR_SURFACE,
            font=FONT_HEADER_TITLE,
            anchor=tk.W,
        ).pack(anchor=tk.W)

        tk.Label(
            title_col,
            text="Membership Communication & Administration System",
            bg=COLOR_PRIMARY,
            fg=COLOR_ACCENT_GOLD,
            font=FONT_HEADER_SUB,
            anchor=tk.W,
        ).pack(anchor=tk.W, pady=(1, 0))

        # Gold accent rule beneath header
        tk.Frame(self.root, bg=COLOR_ACCENT_GOLD, height=3).pack(side=tk.TOP, fill=tk.X)

        # 2. Fixed Club Footer / Status Bar (packed before scroll area so it stays anchored)
        footer = tk.Frame(self.root, bg=COLOR_SURFACE, padx=20, pady=6)
        footer.pack(side=tk.BOTTOM, fill=tk.X)
        tk.Frame(self.root, bg=COLOR_BORDER, height=1).pack(side=tk.BOTTOM, fill=tk.X)

        tk.Label(
            footer,
            textvariable=self.status_var,
            bg=COLOR_SURFACE,
            fg=COLOR_TEXT_MAIN,
            font=FONT_SMALL,
            anchor=tk.W,
        ).pack(side=tk.LEFT)

        tk.Label(
            footer,
            text="Flushing & Mylor Pilot Gig Club",
            bg=COLOR_SURFACE,
            fg=COLOR_PRIMARY,
            font=("Arial", 9, "bold"),
            anchor=tk.E,
        ).pack(side=tk.RIGHT)

        # 3. Scrollable Main Viewport (Canvas + FMPGC Vertical Scrollbar)
        scroll_container = tk.Frame(self.root, bg=COLOR_BG_PAGE)
        scroll_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.page_canvas = tk.Canvas(
            scroll_container,
            bg=COLOR_BG_PAGE,
            highlightthickness=0,
            bd=0,
        )
        self.page_scrollbar = ttk.Scrollbar(
            scroll_container,
            orient=tk.VERTICAL,
            command=self.page_canvas.yview,
            style="FMPGC.Vertical.TScrollbar",
        )
        self.page_canvas.configure(yscrollcommand=self.page_scrollbar.set)

        self.page_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.page_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        main_frame = tk.Frame(self.page_canvas, bg=COLOR_BG_PAGE, padx=20, pady=14)
        self._canvas_window = self.page_canvas.create_window((0, 0), window=main_frame, anchor=tk.NW)

        main_frame.bind("<Configure>", self._on_frame_configure)
        self.page_canvas.bind("<Configure>", self._on_canvas_configure)

        # Cross-platform mousewheel bindings
        self.root.bind_all("<MouseWheel>", self._on_mousewheel)
        self.root.bind_all("<Button-4>", self._on_mousewheel)
        self.root.bind_all("<Button-5>", self._on_mousewheel)

        # --------------------------------------------------------------
        # Card 1: Configuration & Data Sources
        # --------------------------------------------------------------
        paths_body = self._create_card(
            main_frame,
            title="1. Configuration & data sources",
            subtitle="Select your settings JSON, templates folder and members CSV",
        )
        paths_body.columnconfigure(1, weight=1)

        ttk.Label(paths_body, text="Data folder:", style="CardBody.TLabel").grid(row=0, column=0, sticky=tk.W, padx=(0, 12), pady=3)
        ttk.Entry(paths_body, textvariable=self.data_folder_var, style="FMPGC.TEntry").grid(row=0, column=1, sticky=tk.EW, pady=3)
        ttk.Button(paths_body, text="Browse...", style="Browse.TButton", command=self._browse_data_folder).grid(row=0, column=2, padx=(8, 0), pady=3)

        ttk.Label(paths_body, text="Config JSON:", style="CardBody.TLabel").grid(row=1, column=0, sticky=tk.W, padx=(0, 12), pady=3)
        ttk.Entry(paths_body, textvariable=self.config_file_var, style="FMPGC.TEntry").grid(row=1, column=1, sticky=tk.EW, pady=3)
        ttk.Button(paths_body, text="Browse...", style="Browse.TButton", command=self._browse_config_file).grid(row=1, column=2, padx=(8, 0), pady=3)

        ttk.Label(paths_body, text="Members CSV:", style="CardBody.TLabel").grid(row=2, column=0, sticky=tk.W, padx=(0, 12), pady=3)
        ttk.Entry(paths_body, textvariable=self.csv_file_var, style="FMPGC.TEntry").grid(row=2, column=1, sticky=tk.EW, pady=3)
        ttk.Button(paths_body, text="Browse...", style="Browse.TButton", command=self._browse_csv_file).grid(row=2, column=2, padx=(8, 0), pady=3)

        load_bar = tk.Frame(paths_body, bg=COLOR_SURFACE)
        load_bar.grid(row=3, column=0, columnspan=3, sticky=tk.EW, pady=(6, 0))

        self.load_btn = ttk.Button(
            load_bar,
            text="Load / reload data",
            style="Secondary.TButton",
            command=self.load_all_data,
        )
        self.load_btn.pack(side=tk.LEFT)

        self.vars_label = ttk.Label(
            load_bar,
            text="Template variables: (not loaded)",
            style="Muted.TLabel",
        )
        self.vars_label.pack(side=tk.LEFT, padx=(14, 0))

        # --------------------------------------------------------------
        # Card 2: Loaded Members Preview Table
        # --------------------------------------------------------------
        table_body = self._create_card(
            main_frame,
            title="2. Loaded members preview",
            subtitle="Select a row and click 'Preview selected row' to inspect the rendered email",
        )

        tree_container = tk.Frame(table_body, bg=COLOR_SURFACE)
        tree_container.pack(fill=tk.BOTH, expand=True)

        self.member_tree = ttk.Treeview(
            tree_container,
            columns=("Row", "Name", "Email", "Membership Type"),
            show="headings",
            height=5,
            style="FMPGC.Treeview",
        )
        self.member_tree.heading("Row", text="#")
        self.member_tree.heading("Name", text="Name")
        self.member_tree.heading("Email", text="Email")
        self.member_tree.heading("Membership Type", text="Membership Type")

        self.member_tree.column("Row", width=55, anchor=tk.CENTER, stretch=False)
        self.member_tree.column("Name", width=220, anchor=tk.W)
        self.member_tree.column("Email", width=290, anchor=tk.W)
        self.member_tree.column("Membership Type", width=210, anchor=tk.W)

        self.member_tree.tag_configure("even", background=COLOR_SURFACE, foreground=COLOR_TEXT_MAIN)
        self.member_tree.tag_configure("odd", background=COLOR_ROW_ALT, foreground=COLOR_TEXT_MAIN)

        y_scroll = ttk.Scrollbar(
            tree_container,
            orient=tk.VERTICAL,
            command=self.member_tree.yview,
            style="FMPGC.Vertical.TScrollbar",
        )
        self.member_tree.configure(yscrollcommand=y_scroll.set)
        self.member_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # --------------------------------------------------------------
        # Card 3: Email Campaign Options & Actions
        # --------------------------------------------------------------
        action_body = self._create_card(
            main_frame,
            title="3. Email campaign options",
            subtitle="Choose the template action and verify recipient privacy settings",
        )
        action_body.columnconfigure(1, weight=1)

        ttk.Label(action_body, text="Email action:", style="CardBody.TLabel").grid(row=0, column=0, sticky=tk.W, padx=(0, 12), pady=3)
        self.option_combo = ttk.Combobox(
            action_body,
            textvariable=self.option_var,
            values=[item[0] for item in fmpgc_classes.OPTION_DEFINITIONS],
            state="readonly",
            style="FMPGC.TCombobox",
        )
        self.option_combo.grid(row=0, column=1, sticky=tk.EW, pady=3)
        self.option_combo.bind("<<ComboboxSelected>>", self._on_option_changed)

        self.bcc_checkbox = ttk.Checkbutton(
            action_body,
            text="Send email as BCC to recipient (hide sender and recipient addresses)",
            variable=self.bcc_mode_var,
            style="Card.TCheckbutton",
        )
        self.bcc_checkbox.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(3, 6))

        # Tailored template sub-panel (soft off-white box inside card)
        self.tailored_frame = tk.Frame(
            action_body,
            bg=COLOR_BG_PAGE,
            highlightbackground=COLOR_BORDER,
            highlightthickness=1,
            padx=12,
            pady=8,
        )
        self.tailored_frame.grid(row=2, column=0, columnspan=3, sticky=tk.EW, pady=(2, 8))
        self.tailored_frame.columnconfigure(1, weight=1)

        tk.Label(
            self.tailored_frame,
            text="Tailored / broadcast settings",
            bg=COLOR_BG_PAGE,
            fg=COLOR_PRIMARY,
            font=FONT_BODY_BOLD,
        ).grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 4))

        tk.Label(self.tailored_frame, text="Template file:", bg=COLOR_BG_PAGE, fg=COLOR_TEXT_MAIN, font=FONT_SMALL).grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=2)
        self.tmpl_entry = ttk.Entry(self.tailored_frame, textvariable=self.broadcast_template_var, style="FMPGC.TEntry")
        self.tmpl_entry.grid(row=1, column=1, sticky=tk.EW, pady=2)
        self.tmpl_browse_btn = ttk.Button(self.tailored_frame, text="Browse...", style="Browse.TButton", command=self._browse_template_file)
        self.tmpl_browse_btn.grid(row=1, column=2, padx=(8, 0), pady=2)

        tk.Label(self.tailored_frame, text="Subject:", bg=COLOR_BG_PAGE, fg=COLOR_TEXT_MAIN, font=FONT_SMALL).grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=2)
        self.subj_entry = ttk.Entry(self.tailored_frame, textvariable=self.custom_subject_var, style="FMPGC.TEntry")
        self.subj_entry.grid(row=2, column=1, columnspan=2, sticky=tk.EW, pady=2)

        tk.Label(self.tailored_frame, text="Attachment:", bg=COLOR_BG_PAGE, fg=COLOR_TEXT_MAIN, font=FONT_SMALL).grid(row=3, column=0, sticky=tk.W, padx=(0, 10), pady=2)
        self.attach_entry = ttk.Entry(self.tailored_frame, textvariable=self.attachment_var, style="FMPGC.TEntry")
        self.attach_entry.grid(row=3, column=1, sticky=tk.EW, pady=2)
        self.attach_browse_btn = ttk.Button(self.tailored_frame, text="Browse...", style="Browse.TButton", command=self._browse_attachment_file)
        self.attach_browse_btn.grid(row=3, column=2, padx=(8, 0), pady=2)

        # Action Controls Row (One primary action button + secondary buttons + progress bar)
        controls_frame = tk.Frame(action_body, bg=COLOR_SURFACE)
        controls_frame.grid(row=3, column=0, columnspan=3, sticky=tk.EW, pady=(2, 0))

        self.send_btn = ttk.Button(
            controls_frame,
            text="Send emails",
            style="Primary.TButton",
            command=self.start_sending,
        )
        self.send_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.preview_btn = ttk.Button(
            controls_frame,
            text="Preview selected row",
            style="Secondary.TButton",
            command=self.preview_email,
        )
        self.preview_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.stop_btn = ttk.Button(
            controls_frame,
            text="Stop batch",
            style="Secondary.TButton",
            command=self.stop_sending,
            state=tk.DISABLED,
        )
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 14))

        self.progress = ttk.Progressbar(
            controls_frame,
            mode="determinate",
            style="FMPGC.Horizontal.TProgressbar",
        )
        self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # --------------------------------------------------------------
        # Card 4: Activity Log
        # --------------------------------------------------------------
        log_body = self._create_card(
            main_frame,
            title="4. Activity log",
            subtitle="Live dispatch status and rate-limit updates",
        )

        self.log_text = scrolledtext.ScrolledText(
            log_body,
            height=6,
            state=tk.DISABLED,
            wrap=tk.WORD,
            font=FONT_MONO,
            bg=COLOR_BG_PAGE,
            fg=COLOR_TEXT_MAIN,
            relief=tk.FLAT,
            highlightbackground=COLOR_BORDER,
            highlightthickness=1,
            padx=8,
            pady=6,
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.tag_configure("timestamp", foreground=COLOR_TEXT_MUTED)
        self.log_text.tag_configure("error", foreground=COLOR_PRIMARY, font=("Consolas", 9, "bold"))

        self._on_option_changed()

    # ------------------------------------------------------------------
    # Browsers & UI State Helpers
    # ------------------------------------------------------------------
    def _browse_data_folder(self):
        path = filedialog.askdirectory(initialdir=self.data_folder_var.get() or os.getcwd(), title="Select Data Folder")
        if path:
            self.data_folder_var.set(path)

    def _browse_config_file(self):
        path = filedialog.askopenfilename(
            title="Select Config JSON",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if path:
            self.config_file_var.set(path)

    def _browse_csv_file(self):
        path = filedialog.askopenfilename(
            title="Select Members CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if path:
            self.csv_file_var.set(path)

    def _browse_template_file(self):
        path = filedialog.askopenfilename(
            initialdir=self.data_folder_var.get() or os.getcwd(),
            title="Select HTML Template",
            filetypes=[("HTML files", "*.html *.htm"), ("All files", "*.*")],
        )
        if path:
            self.broadcast_template_var.set(path)

    def _browse_attachment_file(self):
        path = filedialog.askopenfilename(title="Select Attachment", filetypes=[("All files", "*.*")])
        if path:
            self.attachment_var.set(path)

    def _on_option_changed(self, _event=None):
        selected_label = self.option_var.get()
        option, _default_subj, _tmpl_key = self._option_lookup[selected_label]
        state = tk.NORMAL if option == fmpgc_classes.Option.TAILORED_TEMPLATE else tk.DISABLED
        for widget in (
            self.tmpl_entry,
            self.tmpl_browse_btn,
            self.subj_entry,
            self.attach_entry,
            self.attach_browse_btn,
        ):
            widget.configure(state=state)

    def _set_running_state(self, running: bool):
        state = tk.DISABLED if running else tk.NORMAL
        self.load_btn.configure(state=state)
        self.send_btn.configure(state=state)
        self.preview_btn.configure(state=state)
        self.option_combo.configure(state="disabled" if running else "readonly")
        self.bcc_checkbox.configure(state=state)
        self.stop_btn.configure(state=tk.NORMAL if running else tk.DISABLED)
        if not running:
            self._on_option_changed()

    # ------------------------------------------------------------------
    # Logging (Thread-Safe)
    # ------------------------------------------------------------------
    def log(self, message: str, is_error: bool = False):
        timestamp = datetime.now(tz=ZoneInfo("Europe/London")).strftime("%H:%M:%S")
        self.log_queue.put((timestamp, message, is_error))

    def _poll_log_queue(self):
        while True:
            try:
                timestamp, msg, is_error = self.log_queue.get_nowait()
            except queue.Empty:
                break
            self.log_text.configure(state=tk.NORMAL)
            self.log_text.insert(tk.END, f"[{timestamp}] ", "timestamp")
            if is_error:
                self.log_text.insert(tk.END, msg + "\n", "error")
            else:
                self.log_text.insert(tk.END, msg + "\n")
            self.log_text.see(tk.END)
            self.log_text.configure(state=tk.DISABLED)
        self.root.after(100, self._poll_log_queue)

    # ------------------------------------------------------------------
    # Data Loading
    # ------------------------------------------------------------------
    def load_all_data(self, silent_if_missing: bool = False):
        config_path = self.config_file_var.get().strip()
        data_folder = self.data_folder_var.get().strip()
        csv_path = self.csv_file_var.get().strip()

        # 1. Load Config
        self.config = config_utils.load_config(config_path)
        if self.config is None:
            msg = f"Failed to load configuration file: [{config_path}]"
            self.log(msg, is_error=True)
            self.status_var.set(msg)
            if not silent_if_missing:
                messagebox.showerror("Configuration error", msg)
            return

        self.it_credentials = config_utils.get_variable("GOOGLE_FMPGC_IT_CREDENTIALS", self.config)
        self.it_token_file = config_utils.get_variable("GOOGLE_FMPGC_IT_TOKEN", self.config)
        self.membership_credentials = config_utils.get_variable("GOOGLE_FMPGC_MEMBERSHIP_CREDENTIALS", self.config)
        self.membership_token_file = config_utils.get_variable("GOOGLE_FMPGC_MEMBERSHIP_TOKEN", self.config)
        self.fmpgc_it_email = config_utils.get_variable("FMPGC_IT_EMAIL", self.config)
        self.fmpgc_membership_email = config_utils.get_variable("FMPGC_MEMBERSHIP_EMAIL", self.config)
        self.bcc_emails = config_utils.get_variable("FMPGC_BCC_EMAILS", self.config)
        self.log(f"Loaded config [{config_path}] | BCC emails: [{self.bcc_emails}]")

        # 2. Load CSV
        try:
            df = pd.read_csv(csv_path, encoding="cp1252")
        except OSError as e:
            msg = f"Error reading CSV file [{csv_path}]: {e}"
            self.log(msg, is_error=True)
            self.status_var.set(msg)
            if not silent_if_missing:
                messagebox.showerror("CSV error", msg)
            return

        df = df.dropna(how="all")
        required_columns = {"Name", "Email", "Invite Link"}
        missing_columns = required_columns - set(df.columns)
        if missing_columns:
            msg = f"CSV is missing required columns: {', '.join(sorted(missing_columns))}"
            self.log(msg, is_error=True)
            self.status_var.set(msg)
            messagebox.showerror("CSV validation error", msg)
            return

        self.csv_data = df

        # Populate Treeview with alternating FMPGC row shading
        for item in self.member_tree.get_children():
            self.member_tree.delete(item)

        has_membership_type = "Membership Type" in df.columns
        for row_num, (idx, row) in enumerate(df.iterrows()):
            m_type = "" if not has_membership_type or pd.isna(row["Membership Type"]) else str(row["Membership Type"])
            row_tag = "odd" if row_num % 2 else "even"
            self.member_tree.insert(
                "",
                tk.END,
                iid=str(idx),
                values=(idx, row["Name"], row["Email"], m_type),
                tags=(row_tag,),
            )

        col_names = df.columns.tolist()
        self.vars_label.configure(
            text=f"Loaded {len(df)} members  •  Variables: {', '.join(f'{{{{{c}}}}}' for c in col_names)}"
        )
        self.log(f"Loaded {len(df)} rows from [{csv_path}]. Available variables: {col_names}")

        # 3. Load HTML Templates
        loaded_templates = config_utils.load_templates(data_folder)
        #try:
        #    for key, filename in fmpgc_classes.TEMPLATE_FILE.items():
        #        html_path = Path(data_folder) / filename
        #        loaded_templates[key] = html_path.read_text(encoding="utf-8")
        #except OSError as e:
        #    msg = f"Error reading template file: {e}"
        #    self.log(msg, is_error=True)
        #    self.status_var.set(msg)
        #    if not silent_if_missing:
        #        messagebox.showerror("Template error", msg)
        #    return

        self.templates = loaded_templates
        self.log(f"Loaded {len(self.templates)} standard HTML templates from [{data_folder}].")
        self.status_var.set(f"Ready — {len(df)} members loaded.")

    # ------------------------------------------------------------------
    # Preview Email
    # ------------------------------------------------------------------
    def _resolve_template_and_subject(self):
        selected_label = self.option_var.get()
        option, default_subject, tmpl_key = self._option_lookup[selected_label]

        if option == fmpgc_classes.Option.TAILORED_TEMPLATE:
            subject = self.custom_subject_var.get().strip()
            if not subject:
                raise ValueError("Please enter a subject for the tailored template.")
            tmpl_input = self.broadcast_template_var.get().strip() or "membership_broadcast.html"
            tmpl_path = Path(tmpl_input)
            if not tmpl_path.is_absolute():
                tmpl_path = Path(self.data_folder_var.get().strip()) / tmpl_path
            template_html = tmpl_path.read_text(encoding="utf-8")
            attachment = self.attachment_var.get().strip()
            return option, subject, template_html, attachment

        return option, default_subject, self.templates[tmpl_key], ""

    def preview_email(self):
        df = self.csv_data
        if df is None or df.empty:
            messagebox.showwarning("No data loaded", "Please load a valid members CSV first.")
            return

        selection = self.member_tree.selection()
        if selection:
            row_pos = self.member_tree.index(selection[0])
            row: pd.Series = df.iloc[row_pos]
        else:
            row = df.iloc[0]

        try:
            option, subject, template_html, attachment = self._resolve_template_and_subject()
        except Exception as e:
            messagebox.showerror("Preview error", str(e))
            return

        rendered_html = config_utils.template_edit_html(row, template_html)

        win = tk.Toplevel(self.root)
        win.title(f"FMPGC Email Preview — {row['Name']}")
        win.geometry("760x540")
        win.configure(bg=COLOR_BG_PAGE)

        # Burgundy header strip in preview window
        top_bar = tk.Frame(win, bg=COLOR_PRIMARY, padx=16, pady=10)
        top_bar.pack(fill=tk.X)
        tk.Label(
            top_bar,
            text=f"Email preview: {option.name}",
            bg=COLOR_PRIMARY,
            fg=COLOR_SURFACE,
            font=FONT_SECTION,
        ).pack(anchor=tk.W)
        tk.Frame(win, bg=COLOR_ACCENT_GOLD, height=2).pack(fill=tk.X)

        meta_card = tk.Frame(
            win,
            bg=COLOR_SURFACE,
            highlightbackground=COLOR_BORDER,
            highlightthickness=1,
            padx=14,
            pady=10,
        )
        meta_card.pack(fill=tk.X, padx=16, pady=(12, 8))

        tk.Label(
            meta_card,
            text=f"To: {row['Name']} <{row['Email']}>",
            bg=COLOR_SURFACE,
            fg=COLOR_TEXT_MAIN,
            font=FONT_BODY_BOLD,
        ).pack(anchor=tk.W)
        tk.Label(
            meta_card,
            text=f"Subject: {subject}",
            bg=COLOR_SURFACE,
            fg=COLOR_PRIMARY,
            font=FONT_BODY,
        ).pack(anchor=tk.W, pady=(2, 0))
        if attachment:
            tk.Label(
                meta_card,
                text=f"Attachment: {attachment}",
                bg=COLOR_SURFACE,
                fg=COLOR_TEXT_MUTED,
                font=FONT_SMALL,
            ).pack(anchor=tk.W, pady=(2, 0))

        body_box = scrolledtext.ScrolledText(
            win,
            wrap=tk.WORD,
            font=FONT_MONO,
            bg=COLOR_SURFACE,
            fg=COLOR_TEXT_MAIN,
            relief=tk.FLAT,
            highlightbackground=COLOR_BORDER,
            highlightthickness=1,
            padx=10,
            pady=8,
        )
        body_box.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 16))
        body_box.insert(tk.END, rendered_html)
        body_box.configure(state=tk.DISABLED)

    # ------------------------------------------------------------------
    # Sending Workflow (Background Thread)
    # ------------------------------------------------------------------
    def start_sending(self):
        df = self.csv_data
        if self.config is None or df is None or df.empty:
            messagebox.showwarning("Not ready", "Please load configuration, templates and CSV data first.")
            return

        try:
            option, subject, template_html, attachment = self._resolve_template_and_subject()
        except Exception as e:
            messagebox.showerror("Configuration error", str(e))
            return

        total = len(df)
        bcc_mode = self.bcc_mode_var.get()
        confirm = messagebox.askyesno(
            "Confirm email send",
            f"Action: {option.name}\n"
            f"Recipients: {total} members\n"
            f"Subject: {subject}\n"
            f"Send as BCC: {'Yes' if bcc_mode else 'No'}\n\n"
            f"Would you like to proceed with sending?",
        )
        if not confirm:
            return

        self.stop_event.clear()
        self.progress.configure(maximum=total, value=0)
        self._set_running_state(True)
        self.status_var.set(f"Sending {option.name} emails (0/{total})...")

        self.worker_thread = threading.Thread(
            target=self._send_worker,
            args=(df.copy(), option, subject, template_html, attachment, bcc_mode),
            daemon=True,
        )
        self.worker_thread.start()

    def stop_sending(self):
        self.stop_event.set()
        self.log("Stop requested — finishing current email before halting...")
        self.status_var.set("Stopping...")

    def _send_worker(
        self,
        df: pd.DataFrame,
        option,
        subject: str,
        template_html: str,
        attachment: str,
        email_bcc: bool,
    ):
        cc = None
        if option in fmpgc_classes.IT_OPTIONS:
            credentials = self.it_credentials
            token_file = self.it_token_file
            from_email = self.fmpgc_it_email
            if option in fmpgc_classes.CC_MEMBERSHIP_OPTIONS:
                cc = self.fmpgc_membership_email
        else:
            credentials = self.membership_credentials
            token_file = self.membership_token_file
            from_email = self.fmpgc_membership_email

        total = len(df)
        count = 0

        self.log(f"Starting batch: {option.name} | From: {from_email} | Count: {total}")

        for _index, row in df.iterrows():
            if self.stop_event.is_set():
                self.log(f"Batch stopped by user after {count}/{total} emails.")
                break

            name = row["Name"]
            email_address = row["Email"]
            raw_type = row["Membership Type"] if "Membership Type" in row.index else ""
            membership_type = "" if pd.isna(raw_type) else str(raw_type)

            if email_bcc:
                if option in (
                    fmpgc_classes.Option.ADD_NEW_MEMBER,
                    fmpgc_classes.Option.ADD_NEW_MEMBER_EASYTEAM,
                ):
                    bcc = f"{email_address},{self.bcc_emails}"
                else:
                    bcc = email_address
                recipient_to = None
            else:
                if membership_type not in ("Concessionary (FXU)", "") and option in (
                    fmpgc_classes.Option.ADD_NEW_MEMBER,
                    fmpgc_classes.Option.ADD_NEW_MEMBER_EASYTEAM,
                ):
                    bcc = self.bcc_emails
                else:
                    bcc = None
                recipient_to = email_address

            count += 1
            if count % 60 == 0:
                self.log("Rate-limit pause: sleeping 60 seconds to avoid Gmail API limits...")
                for _ in range(60):
                    if self.stop_event.is_set():
                        break
                    time.sleep(1)
                if self.stop_event.is_set():
                    self.log(f"Batch stopped by user during rate-limit pause ({count - 1}/{total}).")
                    break

            email_body = config_utils.template_edit_html(row, template_html)

            try:
                email_result = send_email(
                    credentials,
                    token_file,
                    recipient_to,
                    subject,
                    email_body,
                    cc,
                    bcc,
                    attachment,
                )
            except Exception as e:
                email_result = f"ERROR: {e}"
                self.log(f"Failed sending to {name} ({email_address}): {e}", is_error=True)
            else:
                self.log(f"[{count}/{total}] Sent to {name} ({email_address}) -> {email_result}")

            fromcc = f"from:{from_email}"
            if cc:
                fromcc += f" cc:{cc}"
            if bcc:
                fromcc += f" bcc:{bcc}"

            self.message_log.messagelog(
                str(recipient_to),
                fromcc,
                action=option.name,
                result=email_result,
            )

            self.root.after(0, self._update_progress, count, total, option.name)

        self.log(f"Processed {count} emails for option: {option.name}\n")
        self.root.after(0, self._finish_sending, count, total, option.name)

    def _update_progress(self, count: int, total: int, option_name: str):
        self.progress.configure(value=count)
        self.status_var.set(f"Sending {option_name} emails ({count}/{total})...")

    def _finish_sending(self, count: int, total: int, option_name: str):
        self._set_running_state(False)
        status = f"Completed {count}/{total} emails for {option_name}."
        self.status_var.set(status)
        messagebox.showinfo("Batch finished", status)


def main():
    parser = argparse.ArgumentParser(description="FMPGC Membership Communication & Administration System (GUI)")
    parser.add_argument("--data-folder", "-d", type=str, default="data/", help="Data folder location")
    parser.add_argument("--config-file", "-c", type=str, default="data/fmpgc_settings.json", help="Location of the config file")
    parser.add_argument("--csv-file", "-csv", type=str, default="data/fmpgc_members.csv", help="Location of the CSV file")
    args = parser.parse_args()

    root = tk.Tk()
    FMPGCGuiApp(
        root,
        data_folder=args.data_folder,
        config_file=args.config_file,
        csv_file=args.csv_file,
    )
    root.mainloop()


if __name__ == "__main__":
    main()
