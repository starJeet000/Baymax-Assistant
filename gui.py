import tkinter as tk
import config

class Face:
    def __init__(self, root, logic_handler):
        self.root = root
        self.logic = logic_handler 
        self.root.title(f"{config.AI_NAME} Assistant")
        self.root.geometry("600x500") 
        self.root.configure(bg=config.THEME_BG)
        self.root.attributes("-topmost", False)  # Change it to true to keep it on the top alwyas

        # Face Canvas
        self.canvas = tk.Canvas(root, width=400, height=250, bg=config.THEME_BG, highlightthickness=0)
        self.canvas.pack(pady=20)

        # Drawing the Face
        self.left_eye = self.canvas.create_oval(100, 100, 130, 140, fill="black")
        self.right_eye = self.canvas.create_oval(270, 100, 300, 140, fill="black")
        self.bridge = self.canvas.create_line(115, 120, 285, 120, width=3, fill="black")

        self.status_label = tk.Label(root, text=f"{config.AI_NAME} Running", bg=config.THEME_BG, font=("Segoe UI", 10))
        self.status_label.pack(pady=(0, 10))

        # Prompt Bar
        self.control_frame = tk.Frame(root, bg=config.THEME_BG)
        self.control_frame.pack(side="bottom", fill="x", padx=20, pady=20)

        input_row = tk.Frame(self.control_frame, bg=config.THEME_BG)
        input_row.pack(side="top", fill="x", pady=5)

        self.prompt_entry = tk.Entry(input_row, font=("Segoe UI", 12), bg="#f9f9f9", bd=1, relief="solid")
        self.prompt_entry.pack(side="left", fill="x", expand=True, padx=5)
        self.prompt_entry.bind("<Return>", self.send_command) 

        self.send_btn = tk.Button(input_row, text="➤", font=("Segoe UI", 12),
        command=self.send_command, bg="#f0f0f0", bd=0)
        self.send_btn.pack(side="right", padx=(5, 0))

        self.is_speaking = False
        self.blink_loop()

    def send_command(self, event=None):
        text = self.prompt_entry.get()
        if not text: return
        self.prompt_entry.delete(0, tk.END)
        self.logic.handle_manual_input(text)

    def set_status(self, text, color="black"):
        # Safe thread update
        self.root.after(0, lambda: self._update_status(text, color))

    def _update_status(self, text, color):
        self.status_label.config(text=text, fg=color)
        self.canvas.itemconfig(self.left_eye, fill=color)
        self.canvas.itemconfig(self.right_eye, fill=color)
        self.canvas.itemconfig(self.bridge, fill=color)

    def blink_loop(self):
        if not self.is_speaking:
            self.canvas.coords(self.left_eye, 100, 118, 130, 122)
            self.canvas.coords(self.right_eye, 270, 118, 300, 122)
            self.root.update()
            self.root.after(150, self.open_eyes)
        else:
            self.root.after(1000, self.blink_loop)

    def open_eyes(self):
        self.canvas.coords(self.left_eye, 100, 100, 130, 140)
        self.canvas.coords(self.right_eye, 270, 100, 300, 140)
        self.root.after(3000, self.blink_loop)
