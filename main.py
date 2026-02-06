import psutil
import webbrowser
import ctypes
import re 
import threading
import time
import speech_recognition as sr
import pyttsx3
import pyautogui
import pyperclip
import keyboard
import os
import sys 
import subprocess 
import shutil
import requests # NEW: For Weather
from datetime import datetime
import tkinter as tk 
from tkinter import filedialog 

# --- CONFIGURATION ---
BROWSER= ''     #Add browser name here as key
BRAVE_PATH = r""        #Add your browser's .exe file's path here to open browser
PTT_KEY = ""        #Add your push-to-talk key here

# --- GUI CLASS ---
class BaymaxFace:
    def __init__(self, root, logic_handler):
        self.root = root
        self.logic = logic_handler 
        self.root.title("Baymax - Platinum")
        self.root.geometry("600x500") 
        self.root.configure(bg="white")
        self.root.attributes("-topmost", False)     #Change to true for keeping baymax to the top of screen always over other applications.
        self.canvas = tk.Canvas(root, width=400, height=250, bg="white", highlightthickness=0)
        self.canvas.pack(pady=20)

        # FACE ELEMENTS
        self.left_eye = self.canvas.create_oval(100, 100, 130, 140, fill="black")
        self.right_eye = self.canvas.create_oval(270, 100, 300, 140, fill="black")
        self.bridge = self.canvas.create_line(115, 120, 285, 120, width=3, fill="black")

        self.status_label = tk.Label(root, text="System Online", bg="white", font=("Segoe UI", 10))
        self.status_label.pack(pady=(0, 10))

        # --- PROMPT BAR ---
        self.control_frame = tk.Frame(root, bg="white")
        self.control_frame.pack(side="bottom", fill="x", padx=20, pady=20)

        input_row = tk.Frame(self.control_frame, bg="white")
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


# --- LOGIC CLASS ---
class AssistantLogic:
    def __init__(self):
        self.gui = None 
        self.stop_speaking_flag = False
        self.setup_audio()
        self.register_browser()
        
        # PATH CONFIGURATION
        self.downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")

    def set_gui(self, gui):
        self.gui = gui

    def setup_audio(self):
        try:
            self.recognizer = sr.Recognizer()
            self.mic = sr.Microphone() 
            print(">> Audio System Online")
        except Exception as e:
            print(f"Mic Error: {e}")

    def register_browser(self):
        if os.path.exists(BRAVE_PATH):
            webbrowser.register(BRAVE, None, webbrowser.BackgroundBrowser(BRAVE_PATH))
            self.browser_key = BRAVE
        else:
            self.browser_key = None 

    def clean_command(self, text):
        text = text.lower()
        text = text.replace("baymax", "").replace("hey", "")
        clean = re.sub(r'\b(can|could|would|will) you\b', '', text)
        clean = re.sub(r'\b(please|kindly|just|be a dear and)\b', '', clean)
        return clean.strip()

    def speak(self, text):
        print(f"[Baymax]: {text}")
        self.stop_speaking_flag = False 

        def _speak_thread():
            if self.gui: 
                self.gui.is_speaking = True
                self.gui.root.after(0, lambda: self.gui.set_status("Executing...", "black"))

            try:
                local_engine = pyttsx3.init()
                local_engine.setProperty('rate', 160)
                voices = local_engine.getProperty('voices')
                if voices: local_engine.setProperty('voice', voices[0].id)
                
                chunks = re.split(r'(?<=[.?!])\s+|(?<=\n)', text)
                
                for chunk in chunks:
                    if self.stop_speaking_flag: break
                    if not chunk.strip(): continue
                    local_engine.say(chunk)
                    local_engine.runAndWait()
            except Exception as e:
                print(f"TTS Error: {e}")

            if self.gui:
                self.gui.is_speaking = False
                self.gui.root.after(0, lambda: self.gui.set_status("Idle", "black"))

        t = threading.Thread(target=_speak_thread)
        t.start()
        
        while t.is_alive():
            if self.gui: self.gui.root.update() 
            if keyboard.is_pressed(PTT_KEY): self.stop_speaking_flag = True
            time.sleep(0.05) 

    def listen(self):
        try:
            with self.mic as source:
                if self.gui: self.gui.set_status("Listening...", "green")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                self.recognizer.pause_threshold = 0.8 
                audio = self.recognizer.listen(source, timeout=5)
                if self.gui: self.gui.set_status("Processing...", "orange")
                text = self.recognizer.recognize_google(audio)
                print(f"[You]: {text}")
                return text.lower()
        except:
            if self.gui: self.gui.set_status("Idle", "black")
            return ""

    def handle_manual_input(self, text):
        if text:
            self.execute_command(text)

    # --- HELPER FUNCTIONS ---
    def start_timer(self, minutes):
        def timer_thread():
            self.speak(f"Timer set for {minutes} minutes.")
            time.sleep(minutes * 60)
            self.speak("Time is up. Your timer has finished.")
            # Optional: Add a beep sound here if you want
            # winsound.Beep(1000, 1000) 
        
        t = threading.Thread(target=timer_thread)
        t.start()

    def check_weather(self, city=""):
        try:
            # Uses wttr.in for simple text-based weather (No API Key needed)
            url = f"https://wttr.in/{city}?format=3" if city else "https://wttr.in?format=3"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                # Returns: "Paris: 15°C"
                weather_text = response.text.strip()
                # Clean up weird characters for TTS
                weather_text = weather_text.replace("+", "") 
                self.speak(f"Current weather: {weather_text}")
            else:
                self.speak("I could not connect to the weather service.")
        except:
            self.speak("Weather check failed. Opening Google.")
            webbrowser.open(f"https://www.google.com/search?q=weather+{city}")

    def organize_downloads(self):
        downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
        self.speak("Cleaning up Downloads folder.")
        extensions = {
            "Images": [".jpg", ".jpeg", ".JFIF",".png", ".gif", ".webp"],
            "Documents": [".pdf", ".docx", ".txt", ".xlsx", ".pptx"],
            "Installers": [".exe", ".msi", ".zip", ".7z",".rar"],
            "Audio": [".mp3", ".wav"],
            "Video": [".mp4", ".mkv"]
        }
        moved_count = 0
        try:
            for filename in os.listdir(downloads_path):
                file_path = os.path.join(downloads_path, filename)
                if os.path.isfile(file_path):
                    ext = os.path.splitext(filename)[1].lower()
                    for folder_name, ext_list in extensions.items():
                        if ext in ext_list:
                            target_folder = os.path.join(downloads_path, folder_name)
                            os.makedirs(target_folder, exist_ok=True)
                            try:
                                shutil.move(file_path, os.path.join(target_folder, filename))
                                moved_count += 1
                            except: pass
                            break
            self.speak(f"Finished. Organized {moved_count} files.")
        except: self.speak("Error organizing files.")

    def execute_command(self, raw_command):
        if not raw_command: return
        command = self.clean_command(raw_command)
        
        # --- 1. UNIVERSAL APP LAUNCHER ---
        if command.startswith("open ") or command.startswith("launch "):
            app_name = command.replace("open ", "").replace("launch ", "").strip()
            # Keywords to skip for custom logic
            special_keywords = ["youtube", "google", "code", "explorer", "project", "note", "folder", "file"]
            if app_name not in special_keywords:
                self.speak(f"Launching {app_name}")
                pyautogui.press('win')
                time.sleep(0.1)
                pyautogui.write(app_name)
                time.sleep(0.2)
                pyautogui.press('enter')
                return 

        # --- 2. NEW PLATINUM FEATURES ---
        
        # TIMER / POMODORO
        if "timer" in command or "remind me" in command:
            # Extract number: "Set timer for 10 minutes" -> 10
            try:
                minutes = int(re.search(r'\d+', command).group())
                self.start_timer(minutes)
            except:
                self.speak("I didn't hear a number for the timer.")

        # WEATHER
        elif "weather" in command:
            if "in" in command:
                city = command.split("in")[-1].strip()
                self.check_weather(city)
            else:
                self.check_weather() # Auto-detects location

        # DATE
        elif "date" in command or "day" in command:
            today = datetime.now().strftime("%A, %B %d, %Y")
            self.speak(f"Today is {today}.")

        # OPEN EXPLORER
        elif "open explorer" in command or "file manager" in command:
            self.speak("Opening Explorer.")
            os.system("explorer")

        # CREATE FOLDER (Desktop)
        elif "create folder" in command:
            folder_name = command.replace("create folder", "").strip()
            path = os.path.join(self.desktop_path, folder_name)
            try:
                os.makedirs(path)
                self.speak(f"Folder {folder_name} created on Desktop.")
                os.startfile(path)
            except: self.speak("Could not create folder.")

        # CREATE ANY FILE (Downloads)
        elif "create file" in command:
            # "Create file style.css"
            filename = command.replace("create file", "").strip()
            path = os.path.join(self.downloads_path, filename)
            try:
                with open(path, "w") as f: pass # Create empty file
                self.speak(f"File {filename} created on Downloads.")
            except: self.speak("Could not create file.")

        # --- 3. EXISTING FEATURES ---
        elif "volume up" in command:
            pyautogui.press("volumeup", presses=5)
            self.speak("Volume increased.")
        elif "volume down" in command:
            pyautogui.press("volumedown", presses=5)
            self.speak("Volume decreased.")
        elif "mute" in command:
            pyautogui.press("volumemute")
            self.speak("Audio muted.")
        elif "play" in command or "pause" in command:
            pyautogui.press("playpause")
        elif "minimize" in command:
            pyautogui.hotkey('win', 'd')
            self.speak("Desktop visible.")
        elif "switch window" in command:
            pyautogui.hotkey('alt', 'tab')

        elif "open github" in command:
            self.speak("Opening Github.")
            webbrowser.open_new_tab("https://github.com")

        elif "search github" in command:
            query = command.split("github")[-1].strip()
            self.speak(f"Searching GitHub for {query}")
            webbrowser.open_new_tab(f"https://github.com/search?q={query}")
        
        elif "youtube search" in command:
            query = command.split("youtube search")[-1].strip()
            self.speak(f"Searching YouTube for {query}")
            webbrowser.open_new_tab(f"https://www.youtube.com/results?search_query={query}")
        
        elif "open youtube" in command:
            self.speak("Opening YouTube.")
            webbrowser.open_new_tab("https://youtube.com")
        
        elif "search for" in command or "google" in command:
            query = command.replace("search for", "").replace("google", "").strip()
            self.speak(f"Searching for {query}")
            webbrowser.open_new_tab(f"https://www.google.com/search?q={query}")

        elif "open code" in command:
            self.speak("Opening VS Code.")
            os.system("code")

        elif "open gemini" in command:
            self.speak("Opening Gemini.")
            webbrowser.open_new_tab(f"https://gemini.google.com/app")
        
        elif "clean downloads" in command:
            self.organize_downloads()
        
        elif "create note" in command:
            note_content = command.replace("create note", "").strip()
            filename = f"Note_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            filepath = os.path.join(self.downloads_path, filename)
            try:
                with open(filepath, "w") as f: f.write(note_content)
                self.speak("Note saved to Downloads.")
                os.startfile(filepath)
            except: self.speak("Could not create note.")
        
        elif "battery status" in command:
            battery = psutil.sensors_battery()
            self.speak(f"Battery is at {battery.percent} percent.")
        
        elif "lock screen" in command:
            self.speak("Locking workstation.")
            ctypes.windll.user32.LockWorkStation()
        
        elif "shutdown" in command and "system" in command:
            self.speak("Shutting down system.")
            os._exit(0)

        elif "restart" in command and "system" in command:
            self.speak("Restarting systems.")
            subprocess.Popen([sys.executable] + sys.argv)
            os._exit(0)

    def run_lifecycle(self):
        self.speak("Baymax Online.")
        while True:
            try:
                if self.gui:
                    self.gui.set_status(f"Ready ({PTT_KEY})", "black")
                    self.gui.root.update()
                
                while not keyboard.is_pressed(PTT_KEY):
                    time.sleep(0.05)
                    if self.gui: self.gui.root.update()
                    
                command = self.listen()
                self.execute_command(command)
                
            except Exception as e:
                print(f"Loop Error: {e}")

# --- ENTRY POINT ---
if __name__ == "__main__":
    root = tk.Tk()
    logic = AssistantLogic()
    gui = BaymaxFace(root, logic)
    logic.set_gui(gui)

    t = threading.Thread(target=logic.run_lifecycle, daemon=True)
    t.start()

    root.mainloop()
