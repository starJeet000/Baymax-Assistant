import tkinter as tk
import threading
from gui import Face
from logic import AssistantLogic

if __name__ == "__main__":
    # 1. Initialize Root
    root = tk.Tk()
    
    # 2. Initialize Logic
    logic = AssistantLogic()
    
    # 3. Initialize GUI (Pass logic to it)
    gui = Face(root, logic)
    
    # 4. Link GUI back to Logic
    logic.set_gui(gui)

    # 5. Start Background Thread
    t = threading.Thread(target=logic.run_lifecycle, daemon=True)
    t.start()

    # 6. Start Loop
    root.mainloop()
