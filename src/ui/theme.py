import tkinter as tk
from tkinter import ttk

class Theme:
    # Colors
    PRIMARY = "#1a73e8"      # Google Blue
    PRIMARY_DARK = "#1557b0"
    SECONDARY = "#2c3e50"    # Dark Slate
    BG_MAIN = "#f0f2f5"      # Light Grey
    BG_WHITE = "#ffffff"
    TEXT_MAIN = "#202124"
    TEXT_LIGHT = "#5f6368"
    SUCCESS = "#2ecc71"
    ERROR = "#ea4335"        # Google Red
    
    # Fonts
    FONT_HEADER = ("Segoe UI", 20, "bold")
    FONT_SUBHEADER = ("Segoe UI", 14, "bold")
    FONT_BODY = ("Segoe UI", 11)
    FONT_SMALL = ("Segoe UI", 9)

    @staticmethod
    def apply_theme(root):
        style = ttk.Style(root)
        style.theme_use("clam") # Base for custom

        # General
        root.configure(bg=Theme.BG_MAIN)
        
        # Frames
        style.configure("TFrame", background=Theme.BG_MAIN)
        style.configure("White.TFrame", background=Theme.BG_WHITE)
        
        # Labels
        style.configure("TLabel", background=Theme.BG_MAIN, foreground=Theme.TEXT_MAIN, font=Theme.FONT_BODY)
        style.configure("Header.TLabel", font=Theme.FONT_HEADER, background=Theme.BG_MAIN)
        style.configure("White.TLabel", background=Theme.BG_WHITE)
        
        # Buttons
        style.configure("TButton", 
                        font=("Segoe UI", 10, "bold"), 
                        background=Theme.PRIMARY, 
                        foreground="white", 
                        borderwidth=0, 
                        focuscolor="none")
        style.map("TButton", background=[("active", Theme.PRIMARY_DARK)])
        
        style.configure("Accent.TButton", background=Theme.SUCCESS)
        style.map("Accent.TButton", background=[("active", "#27ae60")])
        
        style.configure("Danger.TButton", background=Theme.ERROR)
        style.map("Danger.TButton", background=[("active", "#c0392b")])

        # Treeview
        style.configure("Treeview", 
                        background=Theme.BG_WHITE,
                        fieldbackground=Theme.BG_WHITE,
                        foreground=Theme.TEXT_MAIN,
                        rowheight=30,
                        font=Theme.FONT_BODY,
                        borderwidth=0)
        style.configure("Treeview.Heading", 
                        font=("Segoe UI", 10, "bold"), 
                        background=Theme.BG_MAIN, 
                        foreground=Theme.TEXT_MAIN)
        style.map("Treeview", background=[("selected", Theme.PRIMARY)], foreground=[("selected", "white")])
        
        # Entry
        style.configure("TEntry", fieldbackground=Theme.BG_WHITE, padding=5)

    @staticmethod
    def create_card_frame(parent, padding=20):
        """Helper to create a unified Card style frame"""
        frame = tk.Frame(parent, bg=Theme.BG_WHITE, padx=padding, pady=padding, relief=tk.RIDGE, bd=1)
        return frame
