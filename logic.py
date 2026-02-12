import os
import sys
import subprocess
import webbrowser
import psutil
import ctypes
import re
import threading
import time
import shutil
from datetime import datetime
import speech_recognition as sr
import pyttsx3
import pyautogui
import keyboard
import config  # Importing settings

class AssistantLogic:
    def __init__(self):
        self.gui = None 
        self.stop_speaking_flag = False
        self.setup_audio()
        self.register_browser()

    def set_gui(self, gui):
        self.gui = gui

    def setup_audio(self):
        try:
            self.recognizer = sr.Recognizer()
            self.mic = sr.Microphone() 
            # Dynamic Thresold: helps adjust room noise automatically 
            self.recognizer.dynamic_energy_threshold = True 
            self.recognizer.energy_threshold = 300
            print(">> Audio System Online")
        except Exception as e:
            print(f"Mic Error: {e}")

    def register_browser(self):
        if os.path.exists(config.BROWSER_PATH):
            webbrowser.register(config.BROWSER, None, webbrowser.BackgroundBrowser(config.BROWSER_PATH))
            self.browser_key = config.BROWSER
        else:
            self.browser_key = None

    # --- HELPER: Open URL with Specific Browser ---
    def open_url(self, url):
        if self.browser_key:
            try:
                webbrowser.get(self.browser_key).open(url)
            except:
                webbrowser.open(url)
        else:
            webbrowser.open(url)

    def clean_command(self, text):
        text = text.lower()
        # Ensure AI_NAME is treated as a string
        ai_name = str(config.AI_NAME).lower()

        # Remove AI name (only is it's part of a sentence)
        text = text.replace(f"{config.AI_NAME.lower()}", "").replace("hey", "")
        
        # Remove polite filler words to make matching easier
        # Regex substitution ensures we are only removing specific string patterns
        clean = re.sub(r'\b(can|could|would|will) you\b', '', text)
        clean = re.sub(r'\b(please|kindly|just|be a dear and)\b', '', clean)
        return clean.strip()

    def speak(self, text):
        print(f"{config.AI_NAME}: {text}")
        self.stop_speaking_flag = False 

        def _speak_thread():
            if self.gui: 
                self.gui.is_speaking = True
                self.gui.set_status("Executing...", "black")

            try:
                local_engine = pyttsx3.init()
                local_engine.setProperty('rate', config.VOICE_RATE)
                voices = local_engine.getProperty('voices')
                if voices: local_engine.setProperty('voice', voices[0].id)
                
                # chunks = re.split(r'(?<=[.?!])\s+|(?<=\n)', text)
                
                # for chunk in chunks:
                #     if self.stop_speaking_flag: break
                #     if not chunk.strip(): continue
                #     local_engine.say(chunk)
                #     local_engine.runAndWait()

                #Simplified speaking logic to prevent cutting off half-sentence
                if self.stop_speaking_flag: return
                local_engine.say(text)
                local_engine.runAndWait()

            except Exception as e:
                print(f"TTS Error: {e}")

            if self.gui:
                self.gui.is_speaking = False
                self.gui.set_status("Idle", "black")

        t = threading.Thread(target=_speak_thread)
        t.start()
        
        while t.is_alive():
            if self.gui: self.gui.root.update() 
            if keyboard.is_pressed(config.PTT_KEY): self.stop_speaking_flag = True
            time.sleep(0.05) 

    def listen(self):
        try:
            with self.mic as source:
                if self.gui: self.gui.set_status("Listening...", "green")

                # Increased Adjust Time: Gives mic 1 second to mute background noise
                self.recognizer.adjust_for_ambient_noise(source, duration=1.0)
                self.recognizer.pause_threshold = 1.0   # Wait 1 sec silence before ending
                
                # Listen
                audio = self.recognizer.listen(source, timeout=8)
                
                if self.gui: self.gui.set_status("Processing...", "orange")
                text = self.recognizer.recognize_google(audio)
                print(f"[You]: {text}")
                return text.lower()

        except sr.WaitTimeoutError:
            return ""   # Didn't hear anything
        except sr.UnknownValueError:
            return ""   # Heard noise but no words
        except Exception as e:
            if self.gui: self.gui.set_status("Idle", "black")
            print(f"Listen Error: {e}")
            return ""

    def handle_manual_input(self, text):
        if text: self.execute_command(text)

    # --- FEATURES ---

    def start_timer(self, minutes):
        def timer_thread():
            self.speak(f"Timer set for {minutes} minutes.")
            time.sleep(minutes * 60)
            self.speak("Time is up.")
        t = threading.Thread(target=timer_thread)
        t.start()

    def organize_downloads(self):
        self.speak("Cleaning up Downloads folder.")
        extensions = {
            "Images": [".jpg", ".jpeg", ".jfif", ".png", ".gif", ".webp"],
            "Documents": [".pdf", ".docx", ".txt", ".xlsx"],
            "Installers": [".exe", ".msi", ".7z", ".zip", ".rar"],
            "Audio": [".mp3", ".wav"],
            "Video": [".mp4", ".mkv"]
        }
        moved_count = 0
        try:
            for filename in os.listdir(config.DOWNLOADS_PATH):
                file_path = os.path.join(config.DOWNLOADS_PATH, filename)
                if os.path.isfile(file_path):
                    ext = os.path.splitext(filename)[1].lower()
                    for folder_name, ext_list in extensions.items():
                        if ext in ext_list:
                            target_folder = os.path.join(config.DOWNLOADS_PATH, folder_name)
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

        # Ensure command is a string
        raw_command = str(raw_command)

        # WAKE WORD LOGIC
        ai_name = str(config.AI_NAME).lower()
        if raw_command.strip() == ai_name:
            self.speak("I am listening")
            return
        
        command = self.clean_command(raw_command)
        
        # --- UNIVERSAL LAUNCHER ---
        if command.startswith("open ") or command.startswith("launch "):
            app_name = command.replace("open ", "").replace("launch ", "").strip()
            ignored_apps = ["youtube", "music", "gemini", "claude", "github", "code", "explorer", "folder", "file", "timer"]
            if app_name not in ignored_apps:
                self.speak(f"Launching {app_name}")
                pyautogui.press('win')
                time.sleep(0.1)
                pyautogui.write(app_name)
                time.sleep(0.2)
                pyautogui.press('enter')
                return 

        # --- TIMER & UTILS ---
        if "set timer for" in command or "remind me in" in command:
            # Extract number: "Set timer for 10 minutes" -> 10
            try:
                minutes = int(re.search(r'\d+', command).group())
                self.start_timer(minutes)
            except: 
                self.speak("I didn't hear a number.")

        elif "date" in command:
            self.speak(f"Today is {datetime.now().strftime('%A, %B %d')}.")

        elif "time" in command:
            self.speak(f"The time is {datetime.now().strftime('%I:%M %p')}.")

        elif "open explorer" in command:
            self.speak("Opening Explorer.")
            os.system("explorer")

        elif "open code" in command: 
            self.speak("Opening VS Code")
            os.system("code")
        
        elif "clean downloads" in command: 
            self.organize_downloads()

        elif "create folder" in command:
            folder_name = command.replace("create folder", "").strip()
            path = os.path.join(config.DOWNLOADS_PATH, folder_name)
            try:
                os.makedirs(path)
                self.speak(f"Folder {folder_name} created.")
                os.startfile(path)
            except: 
                self.speak("Failed to create folder.")

        elif "create file" in command:
            # "Create file ideas.txt"
            filename = command.replace("create file", "").strip()
            path = os.path.join(config.DOWNLOADS_PATH, filename)
            try:
                with open(path, "w") as f: pass
                self.speak(f"File {filename} created.")
            except: self.speak("Failed to create file.")

        # --- WEB ---
        elif "open gemini" in command:
            self.speak("Opening Gemini.")
            self.open_url(f"https://gemini.google.com/app")

        elif "open claude" in command:
            self.speak("Opening Claude.")
            self.open_url(f"https://claude.ai/new")

        elif "open github" in command:
            self.speak("Opening Github.")
            self.open_url("https://github.com")
        
        elif "search github" in command:
            query = command.split("search github")[-1].strip()
            self.speak(f"Searching GitHub for {query}")
            self.open_url(f"https://github.com/search?q={query}")
        
        elif "open youtube" in command:
            self.speak("Opening YouTube")
            self.open_url("https://youtube.com")

        elif "youtube search" in command:
            query = command.split("youtube search")[-1].strip()
            self.speak(f"Searching YouTube for {query}")
            self.open_url(f"https://www.youtube.com/results?search_query={query}")
        
        elif "open music" in command:
            self.speak("Opening Youtube Music.")
            self.open_url("https://music.youtube.com")

        elif "music search" in command:
            query = command.split("music search")[-1].strip()
            self.speak(f"Searching music for {query}")
            self.open_url(f"https://music.youtube.com/search?q={query}")

        elif "search for" in command or "run a search on" in command:
            query = command.replace("search for", "").replace("run a search on", "").strip()
            self.speak(f"Search initiated for {query}")
            self.open_url(f"{config.SEARCH_URL}{query}")
        
        # --- WINDOW & VOLUME SYSTEM ---
        elif "volume up" in command: 
            pyautogui.press("volumeup", presses=5)
        elif "volume down" in command: 
            pyautogui.press("volumedown", presses=5)
        elif "play" in command or "pause" in command:
            pyautogui.press("playpause")
        elif "mute" in command: 
            pyautogui.press("volumemute")
            self.speak("Volume Muted")
        
        elif "minimize" in command: 
            pyautogui.hotkey('win', 'd')
        elif "minimize all" in command:
            pyautogui.hotkey('win', 'm')
        elif "switch window" in command: 
            pyautogui.hotkey('alt', 'tab')

        elif "battery status" in command:
            battery = psutil.sensors_battery()
            self.speak(f"Battery is at {battery.percent} percent.")
        
        elif "lock screen" in command:
            self.speak("Locking Workstation") 
            ctypes.windll.user32.LockWorkStation()

        # --- PC POWER CONTROL (Turns off/restarts Windows) ---
        elif "shutdown computer" in command or "shutdown pc" in command:
            self.speak("Shutting down your computer.")
            os.system("shutdown /s /t 5")
            os._exit(0)

        elif "restart computer" in command or "restart pc" in command:
            self.speak("Restarting your computer.")
            os.system("shutdown /r /t 5")
            os._exit(0)
            
        elif "hibernate computer" in command or "hibernate pc" in command:
            self.speak("Hibernating your computer.")
            os.system("shutdown /h")
            os._exit(0)

        # --- APP POWER CONTROL (Turns off/restarts the Assistant script) ---
        elif "shutdown system" in command or "assistant shutdown" in command:
            self.speak("Assistant Shutting down. See you later.")
            if self.gui: self.gui.root.quit()
            os._exit(0)

        elif "restart system" in command or "assistant restart" in command:
            self.speak("Assistant Restarting.")
            subprocess.Popen([sys.executable] + sys.argv)
            os._exit(0)

        # --- MISC ---
        elif "who are you" in command:
            self.speak(f"I am {config.AI_NAME}, your personal desktop assistant.")

    def run_lifecycle(self):
        self.speak(f"{config.AI_NAME} Online.")
        while True:
            try:
                if self.gui:
                    self.gui.set_status(f"Ready ({config.PTT_KEY})", "black")
                    self.gui.root.update()
                
                # Check for key press every 0.05 seconds to avoid freezing
                while not keyboard.is_pressed(config.PTT_KEY):
                    time.sleep(0.05)
                    if self.gui: self.gui.root.update()
                    
                command = self.listen()
                self.execute_command(command)
                
            except Exception as e:
                print(f"Loop Error: {e}")

