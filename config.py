import os

# --- PATHS ---
AI_NAME= ""   # Add your assistant's name here
BROWSER= '' #Add browser name here as key
BROWSER_PATH = r""  #Add your browser's .exe file's path here to open browser
DOWNLOADS_PATH = os.path.join(os.path.expanduser("~"), "Downloads") # New files will be created in downloads by default, can be changed later if want to.
SEARCH_URL= "https://www.google.com/search?q="   # By default

# --- SETTINGS ---
PTT_KEY = "ALT GR"      # (right alt) default Key to hold for talking (push-to-talk)
VOICE_RATE = 160           # Speed of speech
THEME_BG = "white"         # Background color
