import os
import shutil
import subprocess
import sys
import tkinter as tk
from pathlib import Path
from datetime import datetime
from tkinter import messagebox

from ui.dialogs import Dialogs
from ui.colors import *

# ============================================================
# COLORS (Classic Midnight Commander & JetBrains Retro Palette)
# ============================================================

BLUE = "#0000aa"
DARK_BLUE = "#000080"
CYAN = "#00aaaa"
LIGHT_CYAN = "#00ffff"
WHITE = "#ffffff"
BLACK = "#000000"
YELLOW = "#ffff00"


# ============================================================
# MAIN APPLICATION
# ============================================================

class MiniCommander:

    def __init__(self, root):
        self.root = root

        self.dialogs = Dialogs(self.root)

        self.root.title("Mini Commander")
        self.root.geometry("1250x760")
        self.root.minsize(900, 550)
        self.root.configure(bg=BLUE)

        self.left_path = Path.home()
        self.right_path = Path.home() / "Downloads"

        if not self.right_path.exists():
            self.right_path = Path.home()

        self.active_panel = "left"
        self.active_popup = None

        self.left_items = []
        self.right_items = []

        self.build_interface()
        self.refresh_all()

        self.root.bind("<F3>", lambda e: self.view_file())
        self.root.bind("<F4>", lambda e: self.edit_file())
        self.root.bind("<F5>", lambda e: self.copy_file())
        self.root.bind("<F6>", lambda e: self.move_file())
        self.root.bind("<F7>", lambda e: self.make_directory())
        self.root.bind("<F8>", lambda e: self.delete_file())
        self.root.bind("<F10>", lambda e: self.root.destroy())

        self.root.bind("<Tab>", self.switch_panel)
        self.root.bind("<Alt-Left>", lambda e: self.go_parent())
        self.root.bind("<BackSpace>", lambda e: self.go_parent())

    # ========================================================
    # INTERFACE
    # ========================================================

    def build_interface(self):

        # ----------------------------------------------------
        # TOP MENU
        # ----------------------------------------------------

        self.menu_bar = tk.Frame(
            self.root,
            bg=CYAN,
            height=24
        )
        self.menu_bar.pack(fill="x")

        self.btn_left = self.create_menu_button("Left", self.left_menu)
        self.btn_file = self.create_menu_button("File", self.file_menu)
        self.btn_command = self.create_menu_button("Command", self.command_menu)
        self.btn_options = self.create_menu_button("Options", self.options_menu)

        spacer = tk.Label(
            self.menu_bar,
            text="",
            bg=CYAN
        )
        spacer.pack(side="left", fill="x", expand=True)

        self.btn_right = self.create_menu_button("Right", self.right_menu)

        # ----------------------------------------------------
        # PANELS
        # ----------------------------------------------------

        panels = tk.Frame(
            self.root,
            bg=BLUE
        )
        panels.pack(
            fill="both",
            expand=True,
            padx=0,
            pady=0
        )

        self.left_frame = self.create_panel(
            panels,
            "left"
        )

        separator = tk.Frame(
            panels,
            width=1,
            bg=CYAN
        )

        self.right_frame = self.create_panel(
            panels,
            "right"
        )

        self.left_frame.pack(
            side="left",
            fill="both",
            expand=True
        )

        separator.pack(
            side="left",
            fill="y"
        )

        self.right_frame.pack(
            side="right",
            fill="both",
            expand=True
        )

        # ----------------------------------------------------
        # DISK INFORMATION
        # ----------------------------------------------------

        self.disk_info = tk.Label(
            self.root,
            text="",
            bg=BLUE,
            fg=WHITE,
            anchor="w",
            font=("Menlo", 10)
        )

        self.disk_info.pack(
            fill="x",
            padx=4
        )

        # ----------------------------------------------------
        # STATUS BAR
        # ----------------------------------------------------

        self.status = tk.Label(
            self.root,
            text="",
            bg=BLUE,
            fg=WHITE,
            anchor="w",
            font=("Menlo", 10)
        )

        self.status.pack(
            fill="x",
            padx=4
        )

        # ----------------------------------------------------
        # FUNCTION KEYS (F1-F10)
        # ----------------------------------------------------

        self.function_bar = tk.Frame(
            self.root,
            bg=BLACK,
            height=24
        )

        self.function_bar.pack(
            fill="x",
            side="bottom"
        )

        functions = [
            ("1", "Help", self.show_help),
            ("2", "Menu", self.file_menu_from_btn),
            ("3", "View", self.view_file),
            ("4", "Edit", self.edit_file),
            ("5", "Copy", self.copy_file),
            ("6", "RenMov", self.move_file),
            ("7", "Mkdir", self.make_directory),
            ("8", "Delete", self.delete_file),
            ("9", "PullDn", self.file_menu_from_btn),
            ("10", "Quit", self.root.destroy),
        ]

        for num, text, command in functions:
            f = tk.Frame(self.function_bar, bg=CYAN)
            f.pack(side="left", fill="both", expand=True, padx=1)

            btn = tk.Button(
                f,
                text=f"{num}{text}",
                command=command,
                bg=CYAN,
                fg=BLACK,
                activebackground=WHITE,
                activeforeground=BLACK,
                relief="flat",
                borderwidth=0,
                font=("Menlo", 10, "bold"),
                anchor="w",
                padx=2,
                pady=1
            )
            btn.pack(fill="both", expand=True)

    # ========================================================
    # PANEL
    # ========================================================

    def create_panel(self, parent, side):

        frame = tk.Frame(
            parent,
            bg=BLUE
        )

        path_label = tk.Label(
            frame,
            text="",
            bg=BLUE,
            fg=WHITE,
            anchor="w",
            font=("Menlo", 11, "bold")
        )

        path_label.pack(
            fill="x",
            padx=4,
            pady=(2, 0)
        )

        header = tk.Label(
            frame,
            text="     Name                         Size       Modify time",
            bg=BLUE,
            fg=YELLOW,
            anchor="w",
            font=("Menlo", 10, "bold")
        )

        header.pack(
            fill="x",
            padx=2
        )

        listbox = tk.Listbox(
            frame,
            bg=BLUE,
            fg=WHITE,
            selectbackground=CYAN,
            selectforeground=BLACK,
            activestyle="none",
            font=("Menlo", 11),
            borderwidth=0,
            relief="flat",
            highlightthickness=0,
            selectmode=tk.SINGLE
        )

        listbox.pack(
            fill="both",
            expand=True,
            padx=2,
            pady=(0, 2)
        )

        listbox.bind(
            "<Double-Button-1>",
            lambda e, s=side: self.double_click(s)
        )

        listbox.bind(
            "<Button-1>",
            lambda e, s=side: self.activate_panel(s)
        )

        listbox.bind(
            "<Return>",
            lambda e, s=side: self.enter_selected(s)
        )

        if side == "left":
            self.left_path_label = path_label
            self.left_list = listbox
        else:
            self.right_path_label = path_label
            self.right_list = listbox

        return frame

    # ========================================================
    # MENU BUTTONS
    # ========================================================

    def create_menu_button(self, text, command):

        button = tk.Button(
            self.menu_bar,
            text=text,
            command=command,
            bg=CYAN,
            fg=BLACK,
            activebackground=YELLOW,
            activeforeground=BLACK,
            relief="flat",
            borderwidth=0,
            font=("Menlo", 10, "bold"),
            padx=12,
            pady=0
        )

        button.pack(
            side="left",
            fill="y"
        )
        return button

    # ========================================================
    # TRUE NCURSES-STYLE DIALOG BOX (MC Style with Shadow)
    # ========================================================

    def show_ncurses_dialog(self, title, items):
        if self.active_popup:
            try:
                self.active_popup.destroy()
            except:
                pass
            self.active_popup = None

        popup = tk.Toplevel(self.root)
        popup.overrideredirect(True)
        popup.configure(bg=BLACK)

        shadow_frame = tk.Frame(popup, bg=BLACK)
        shadow_frame.pack(fill="both", expand=True, padx=(0, 6), pady=(0, 6))

        outer_frame = tk.Frame(shadow_frame, bg=WHITE, bd=2, relief="solid")
        outer_frame.pack(fill="both", expand=True)

        inner_frame = tk.Frame(outer_frame, bg=BLUE)
        inner_frame.pack(fill="both", expand=True, padx=1, pady=1)

        title_label = tk.Label(
            inner_frame,
            text=f" {title} ",
            bg=BLUE,
            fg=WHITE,
            font=("Menlo", 11, "bold")
        )
        title_label.pack(anchor="w", padx=10, pady=(6, 4))

        listbox = tk.Listbox(
            inner_frame,
            bg=BLUE,
            fg=WHITE,
            selectbackground=WHITE,
            selectforeground=BLACK,
            activestyle="none",
            font=("Menlo", 11),
            borderwidth=0,
            relief="flat",
            highlightthickness=0,
            selectmode=tk.SINGLE
        )
        listbox.pack(fill="both", expand=True, padx=10, pady=(0, 8))

        for text_label, shortcut, cmd in items:
            if text_label == "---":
                listbox.insert(tk.END, " -------------------------------- ")
            else:
                formatted = f" {text_label:<25} {shortcut}"
                listbox.insert(tk.END, formatted)

        def execute_selection(event=None):
            sel = listbox.curselection()
            if sel:
                idx = sel[0]
                text_label, _, cmd = items[idx]
                if text_label != "---" and cmd:
                    popup.destroy()
                    self.active_popup = None
                    cmd()

        listbox.bind("<Return>", execute_selection)
        listbox.bind("<Double-Button-1>", execute_selection)

        popup.geometry("500x380+400+150")
        self.active_popup = popup
        listbox.focus_set()

        def close_on_click(event):
            try:
                if not popup.winfo_exists():
                    return
                px, py = popup.winfo_rootx(), popup.winfo_rooty()
                pw, ph = popup.winfo_width(), popup.winfo_height()
                if not (px <= event.x_root <= px + pw and py <= event.y_root <= py + ph):
                    popup.destroy()
                    self.active_popup = None
                    self.root.unbind("<Button-1>", self._click_bind_id)
            except:
                pass

        self._click_bind_id = self.root.bind("<Button-1>", close_on_click, add=True)

    # ========================================================
    # JETBRAINS-STYLE MODAL DIALOGS (Exact Match to Reference 2)
    # ========================================================

    def show_jetbrains_dialog(self, title, message, is_input=False, default_val=""):
        dialog = tk.Toplevel(self.root)
        dialog.overrideredirect(True)
        dialog.configure(bg=BLACK)
        dialog.grab_set()

        # Повноцінний розмір вікна (не маленьке)
        dialog.geometry("620x320")

        # Зовнішня чорна тінь вікна
        window_shadow = tk.Frame(dialog, bg=BLACK)
        window_shadow.pack(fill="both", expand=True, padx=(0, 10), pady=(0, 10))

        # Подвійна рамка JetBrains як на другому скріншоті:
        # Зовнішня товста біла рамка
        outer_frame = tk.Frame(window_shadow, bg=WHITE, bd=3, relief="solid")
        outer_frame.pack(fill="both", expand=True)

        # Тонкий шар між рамками (бірюзовий колір панелі)
        gap_frame = tk.Frame(outer_frame, bg=CYAN)
        gap_frame.pack(fill="both", expand=True, padx=2, pady=2)

        # Внутрішня біла рамка
        inner_frame = tk.Frame(gap_frame, bg=WHITE, bd=2, relief="solid")
        inner_frame.pack(fill="both", expand=True, padx=2, pady=2)

        # Всередині — бірюзове поле з контентом
        content_bg = tk.Frame(inner_frame, bg=CYAN)
        content_bg.pack(fill="both", expand=True, padx=35, pady=30)

        # Заголовок у чорній плашці по центру на верхній рамці (як на скріншоті Cookie Settings)
        title_frame = tk.Frame(content_bg, bg=BLACK, bd=1, relief="solid")
        title_lbl = tk.Label(
            title_frame,
            text=f" {title} ",
            bg=BLACK,
            fg=WHITE,
            font=("Menlo", 11, "bold")
        )
        title_lbl.pack(padx=6, pady=3)
        title_frame.place(relx=0.5, rely=0.0, anchor="n", y=-38)

        # Текст повідомлення (великий та зручний)
        msg_lbl = tk.Label(
            content_bg,
            text=message,
            bg=CYAN,
            fg=BLACK,
            font=("Menlo", 13, "bold"),
            anchor="w",
            justify="left"
        )
        msg_lbl.pack(anchor="w", fill="x", pady=(20, 20))

        result = [None]
        entry = None
        if is_input:
            entry_frame = tk.Frame(content_bg, bg=WHITE, bd=2, relief="solid")
            entry_frame.pack(fill="x", pady=(0, 20))
            entry = tk.Entry(
                entry_frame,
                bg=WHITE,
                fg=BLACK,
                font=("Menlo", 13),
                borderwidth=0,
                highlightthickness=0
            )
            entry.pack(fill="x", padx=8, pady=8)
            entry.insert(0, default_val)
            entry.select_range(0, tk.END)

        # Контейнер для кнопок знизу
        btn_frame = tk.Frame(content_bg, bg=CYAN)
        btn_frame.pack(anchor="center", pady=(15, 0))

        def on_ok(event=None):
            if is_input:
                result[0] = entry.get()
            else:
                result[0] = True
            dialog.destroy()

        def on_cancel(event=None):
            result[0] = None
            dialog.destroy()

        # # Створення оригінальних кнопок з чіткою чорною тіттю праворуч і знизу
        # def create_jb_button(parent, text, bg_color, command):
        #
        #     SHADOW = 6
        #     WIDTH = 120
        #     HEIGHT = 34
        #
        #     TOTAL_WIDTH = WIDTH + SHADOW
        #     TOTAL_HEIGHT = HEIGHT + SHADOW
        #
        #     # --------------------------------------------------------
        #     # CANVAS — повністю контролюємо кожен піксель
        #     # --------------------------------------------------------
        #
        #     canvas = tk.Canvas(
        #         parent,
        #         width=TOTAL_WIDTH,
        #         height=TOTAL_HEIGHT,
        #         bg=CYAN,
        #         highlightthickness=0,
        #         borderwidth=0,
        #         relief="flat"
        #     )
        #
        #     # --------------------------------------------------------
        #     # ЧОРНА ТІНЬ
        #     # --------------------------------------------------------
        #     #
        #     # Тінь зміщена на 6 px вправо + вниз
        #     #
        #     canvas.create_rectangle(
        #         SHADOW,
        #         SHADOW,
        #         SHADOW + WIDTH,
        #         SHADOW + HEIGHT,
        #         fill=BLACK,
        #         outline=BLACK
        #     )
        #
        #     # --------------------------------------------------------
        #     # ОСНОВНА БІЛА КНОПКА
        #     # --------------------------------------------------------
        #
        #     button_rect = canvas.create_rectangle(
        #         0,
        #         0,
        #         WIDTH,
        #         HEIGHT,
        #         fill=bg_color,
        #         outline=BLACK,
        #         width=1
        #     )
        #
        #     # --------------------------------------------------------
        #     # ТЕКСТ
        #     # --------------------------------------------------------
        #
        #     button_text = canvas.create_text(
        #         WIDTH // 2,
        #         HEIGHT // 2,
        #         text=text,
        #         fill=BLACK,
        #         font=("Menlo", 11, "bold")
        #     )
        #
        #     # --------------------------------------------------------
        #     # CLICK
        #     # --------------------------------------------------------
        #
        #     def click(event=None):
        #         command()
        #
        #     canvas.bind("<Button-1>", click)
        #
        #     # --------------------------------------------------------
        #     # HOVER
        #     # --------------------------------------------------------
        #
        #     def enter(event=None):
        #         canvas.itemconfig(
        #             button_rect,
        #             fill="#eeeeee"
        #         )
        #
        #     def leave(event=None):
        #         canvas.itemconfig(
        #             button_rect,
        #             fill=bg_color
        #         )
        #
        #     canvas.bind("<Enter>", enter)
        #     canvas.bind("<Leave>", leave)
        #
        #     return canvas

        ok_wrapper = self.dialogs.create_jb_button(
            btn_frame,
            " Create " if is_input else " Yes ",
            YELLOW,
            on_ok
        )

        ok_wrapper.pack(
            side="left",
            padx=(3, 28),
            pady=(3, 0)
        )

        cancel_wrapper = self.dialogs.create_jb_button(
            btn_frame,
            " Cancel ",
            WHITE,
            on_cancel
        )

        cancel_wrapper.pack(
            side="left",
            padx=(0, 3),
            pady=(3, 0)
        )

        if is_input and entry:
            entry.bind("<Return>", on_ok)
            entry.focus_set()

        dialog.bind("<Escape>", on_cancel)

        # Центрування вікна на екрані
        dialog.update_idletasks()
        w = dialog.winfo_width()
        h = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() - w) // 2
        y = (dialog.winfo_screenheight() - h) // 2
        dialog.geometry(f"+{x}+{y}")

        self.root.wait_window(dialog)
        return result[0]

    # ========================================================
    # MENUS DEFINITIONS
    # ========================================================

    def left_menu(self):
        items = [
            ("Left panel", "", lambda: self.activate_panel("left")),
            ("---", "", None),
            ("Home", "", lambda: self.set_path("left", Path.home())),
            ("Desktop", "", lambda: self.set_path("left", Path.home() / "Desktop")),
            ("Downloads", "", lambda: self.set_path("left", Path.home() / "Downloads")),
        ]
        self.show_ncurses_dialog("Left Panel Options", items)

    def right_menu(self):
        items = [
            ("Right panel", "", lambda: self.activate_panel("right")),
            ("---", "", None),
            ("Home", "", lambda: self.set_path("right", Path.home())),
            ("Downloads", "", lambda: self.set_path("right", Path.home() / "Downloads")),
        ]
        self.show_ncurses_dialog("Right Panel Options", items)

    def file_menu(self):
        items = [
            ("View file...", "F3", self.view_file),
            ("Edit", "F4", self.edit_file),
            ("Copy", "F5", self.copy_file),
            ("Rename / Move", "F6", self.move_file),
            ("Mkdir", "F7", self.make_directory),
            ("Delete", "F8", self.delete_file),
            ("---", "", None),
            ("Exit", "F10", self.root.destroy),
        ]
        self.show_ncurses_dialog("File Operations", items)

    def file_menu_from_btn(self):
        self.file_menu()

    def command_menu(self):
        items = [
            ("Copy", "F5", self.copy_file),
            ("Move", "F6", self.move_file),
            ("Make directory", "F7", self.make_directory),
            ("Delete", "F8", self.delete_file),
        ]
        self.show_ncurses_dialog("Command Operations", items)

    def options_menu(self):
        items = [
            ("Refresh", "", self.refresh_all),
            ("Home directories", "", self.reset_paths),
        ]
        self.show_ncurses_dialog("Options", items)

    # ========================================================
    # REFRESH & NAVIGATION
    # ========================================================

    def refresh_all(self):
        self.refresh_panel("left")
        self.refresh_panel("right")
        self.update_disk()
        self.update_status()

    def refresh_panel(self, side):
        if side == "left":
            path = self.left_path
            listbox = self.left_list
            label = self.left_path_label
        else:
            path = self.right_path
            listbox = self.right_list
            label = self.right_path_label

        label.config(text=str(path))
        listbox.delete(0, tk.END)
        items = []

        try:
            entries = list(path.iterdir())
            entries.sort(key=lambda p: (not p.is_dir(), p.name.lower()))

            for item in entries:
                items.append(item)
                if item.is_dir():
                    name = f"[DIR] {item.name}"
                    size = "<DIR>"
                else:
                    name = f"      {item.name}"
                    try:
                        size = self.format_size(item.stat().st_size)
                    except OSError:
                        size = "?"

                try:
                    mtime = datetime.fromtimestamp(item.stat().st_mtime).strftime("%b %d %H:%M")
                except OSError:
                    mtime = "?"

                text = f"{name:<42}{size:>10}   {mtime}"
                listbox.insert(tk.END, text)
        except PermissionError:
            listbox.insert(tk.END, "      Permission denied")
        except OSError as error:
            listbox.insert(tk.END, f"      ERROR: {error}")

        if side == "left":
            self.left_items = items
        else:
            self.right_items = items

    def activate_panel(self, side):
        self.active_panel = side
        self.update_status()

    def switch_panel(self, event=None):
        if self.active_panel == "left":
            self.active_panel = "right"
            self.right_list.focus_set()
        else:
            self.active_panel = "left"
            self.left_list.focus_set()
        self.update_status()
        return "break"

    def get_active(self):
        if self.active_panel == "left":
            return (self.left_path, self.left_list, self.left_items)
        return (self.right_path, self.right_list, self.right_items)

    def get_other(self):
        if self.active_panel == "left":
            return (self.right_path, self.right_list, self.right_items)
        return (self.left_path, self.left_list, self.left_items)

    def enter_selected(self, side):
        listbox = self.left_list if side == "left" else self.right_list
        items = self.left_items if side == "left" else self.right_items
        selection = listbox.curselection()
        if not selection:
            return
        index = selection[0]
        if index >= len(items):
            return
        item = items[index]
        if item.is_dir():
            if side == "left":
                self.left_path = item
            else:
                self.right_path = item
            self.refresh_panel(side)
            self.update_disk()

    def double_click(self, side):
        self.activate_panel(side)
        self.enter_selected(side)

    def go_parent(self):
        if self.active_panel == "left":
            if self.left_path.parent != self.left_path:
                self.left_path = self.left_path.parent
                self.refresh_panel("left")
        else:
            if self.right_path.parent != self.right_path:
                self.right_path = self.right_path.parent
                self.refresh_panel("right")
        self.update_disk()

    # ========================================================
    # FILE OPERATIONS
    # ========================================================

    def get_selected_file(self):
        path, listbox, items = self.get_active()
        selection = listbox.curselection()
        if not selection:
            return None
        index = selection[0]
        if index >= len(items):
            return None
        return items[index]

    def copy_file(self):
        source = self.get_selected_file()
        if source is None:
            return
        destination_path, _, _ = self.get_other()
        target = destination_path / source.name
        try:
            if source.is_dir():
                if target.exists():
                    messagebox.showerror("Copy", "Destination directory already exists.")
                    return
                shutil.copytree(source, target)
            else:
                shutil.copy2(source, target)
            self.refresh_all()
            self.status.config(text=f"Copied: {source.name}")
        except Exception as error:
            messagebox.showerror("Copy error", str(error))

    def move_file(self):
        source = self.get_selected_file()
        if source is None:
            return
        destination_path, _, _ = self.get_other()
        target = destination_path / source.name
        try:
            shutil.move(str(source), str(target))
            self.refresh_all()
            self.status.config(text=f"Moved: {source.name}")
        except Exception as error:
            messagebox.showerror("Move error", str(error))

    def delete_file(self):
        source = self.get_selected_file()
        if source is None:
            return

        confirmed = self.show_jetbrains_dialog(
            "Delete Confirmation",
            f"Are you sure you want to delete:\n{source.name}?"
        )
        if not confirmed:
            return

        try:
            if source.is_dir():
                shutil.rmtree(source)
            else:
                source.unlink()
            self.refresh_all()
            self.status.config(text=f"Deleted: {source.name}")
        except Exception as error:
            messagebox.showerror("Delete error", str(error))

    def make_directory(self):
        path, _, _ = self.get_active()

        name = self.show_jetbrains_dialog(
            "Create Directory",
            "Enter directory name:",
            is_input=True
        )
        if not name:
            return
        try:
            (path / name).mkdir()
            self.refresh_all()
        except Exception as error:
            messagebox.showerror("Mkdir error", str(error))

    def view_file(self):
        file = self.get_selected_file()
        if file is None:
            return
        if file.is_dir():
            self.enter_selected(self.active_panel)
            return
        try:
            if file.stat().st_size > 10 * 1024 * 1024:
                messagebox.showwarning("View", "File is larger than 10 MB.")
                return
            content = file.read_text(encoding="utf-8", errors="replace")
        except Exception as error:
            messagebox.showerror("View error", str(error))
            return
        self.open_text_window(file.name, content, readonly=True)

    def edit_file(self):
        file = self.get_selected_file()
        if file is None or file.is_dir():
            return
        try:
            subprocess.Popen(["open", str(file)] if sys.platform == "darwin" else ["xdg-open", str(file)])
        except Exception as error:
            messagebox.showerror("Edit", str(error))

    def open_text_window(self, title, content, readonly=False):
        window = tk.Toplevel(self.root)
        window.title(title)
        window.geometry("900x650")
        window.configure(bg=BLUE)

        text = tk.Text(
            window,
            bg=BLUE,
            fg=WHITE,
            insertbackground=WHITE,
            selectbackground=CYAN,
            selectforeground=BLACK,
            font=("Menlo", 12),
            wrap="none"
        )
        text.pack(fill="both", expand=True)
        text.insert("1.0", content)
        if readonly:
            text.config(state="disabled")

    def update_disk(self):
        try:
            usage = shutil.disk_usage(Path.home())
            total, free = usage.total, usage.free
            used = total - free
            percent = used / total * 100
            text = f"Disk: {self.format_size(used)} / {self.format_size(total)} ({percent:.0f}%)"
            self.disk_info.config(text=text)
        except Exception:
            self.disk_info.config(text="")

    def update_status(self):
        path, listbox, items = self.get_active()
        selection = listbox.curselection()
        if selection and selection[0] < len(items):
            item = items[selection[0]]
            info = "UP--DIR" if item.is_dir() else self.format_size(item.stat().st_size) if hasattr(item,
                                                                                                    'stat') else "?"
            text = f"{item.name}     {info}"
        else:
            text = str(path)
        self.status.config(text=text)

    @staticmethod
    def format_size(size):
        units = ["B", "K", "M", "G", "T"]
        value = float(size)
        for unit in units:
            if value < 1024:
                return f"{value:.0f}{unit}"
            value /= 1024
        return f"{value:.1f}P"

    def show_help(self):
        messagebox.showinfo(
            "Mini Commander",
            "Keyboard shortcuts:\n\n"
            "Tab       Switch panel\n"
            "Enter     Open directory\n"
            "Backspace Parent directory\n\n"
            "F3        View\n"
            "F4        Open/Edit\n"
            "F5        Copy\n"
            "F6        Move\n"
            "F7        Mkdir\n"
            "F8        Delete\n"
            "F10       Quit"
        )

    def set_path(self, side, path):
        path = Path(path).expanduser()
        if not path.exists() or not path.is_dir():
            messagebox.showerror("Path", f"Directory does not exist:\n{path}")
            return
        if side == "left":
            self.left_path = path
            self.refresh_panel("left")
        else:
            self.right_path = path
            self.refresh_panel("right")
        self.update_disk()

    def reset_paths(self):
        self.left_path = Path.home()
        self.right_path = Path.home() / "Downloads"
        if not self.right_path.exists():
            self.right_path = Path.home()
        self.refresh_all()


# ============================================================
# START
# ============================================================

if __name__ == "__main__":
    root = tk.Tk()
    app = MiniCommander(root)
    root.mainloop()