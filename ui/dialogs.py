import tkinter as tk

from .colors import (
    BLUE,
    CYAN,
    WHITE,
    BLACK,
)

class Dialogs:

    def __init__(self, root):
        self.root = root

    def create_jb_button(self, parent, text, bg_color, command):
        SHADOW = 6
        WIDTH = 120
        HEIGHT = 34

        canvas = tk.Canvas(
            parent,
            width=WIDTH + SHADOW,
            height=HEIGHT + SHADOW,
            bg=CYAN,
            highlightthickness=0,
            borderwidth=0
        )

        # Тінь
        canvas.create_rectangle(
            SHADOW,
            SHADOW,
            SHADOW + WIDTH,
            SHADOW + HEIGHT,
            fill=BLACK,
            outline=BLACK
        )

        # Кнопка
        button_rect = canvas.create_rectangle(
            0,
            0,
            WIDTH,
            HEIGHT,
            fill=bg_color,
            outline=BLACK,
            width=1
        )

        # Текст
        canvas.create_text(
            WIDTH // 2,
            HEIGHT // 2,
            text=text,
            fill=BLACK,
            font=("Menlo", 11, "bold")
        )

        # Click
        canvas.bind(
            "<Button-1>",
            lambda event: command()
        )

        # Hover
        canvas.bind(
            "<Enter>",
            lambda event: canvas.itemconfig(
                button_rect,
                fill="#eeeeee"
            )
        )

        canvas.bind(
            "<Leave>",
            lambda event: canvas.itemconfig(
                button_rect,
                fill=bg_color
            )
        )

        return canvas