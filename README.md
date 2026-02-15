# **Desktop Automation System**

A robust, modular voice-controlled automation suite designed for Windows environments. This system integrates speech recognition with low-level system controls, web automation, and file management to streamline daily desktop workflows.

## **📋 Overview**

This project serves as a central interface for controlling a Windows workstation hands-free. Unlike standard voice assistants, this tool focuses on **local execution and system automation**, allowing users to manipulate windows, organize files, launch applications, and query specific web tools using custom logic handles.

It features a lightweight Tkinter GUI for visual status feedback (Listening, Processing, Idle) without consuming significant system resources.

## **🚀 Key Capabilities**

### **🖥️ System & Power Control**

* **Window Management:** Minimize specific windows or clear the desktop via voice.  
* **Audio Control:** Adjust system volume or mute instantly.  
* **Power Functions:** Distinct voice commands to securely shutdown, restart, or hibernate the Windows PC, alongside options to simply shutdown/restart the Assistant script itself.  
* **Battery Monitoring:** Real-time feedback on battery health and percentage.

### **📂 Intelligent File Management**

* **Auto-Organizer:** One command (clean downloads) automatically sorts files in the Downloads directory into subfolders (Images, Documents, Installers, Audio, Video) based on file extensions.  
* **File Creation:** Generate folders and empty files instantly using voice commands.

### **🌐 Web & Application Integration**

* **Universal Launcher:** Uses pyautogui to interact with the Windows Start Menu, allowing the launching of *any* indexed application (e.g., "Open VS Code", "Launch Spotify").  
* **Browser Automation:** Configurable to work with specific browsers (Brave, Chrome, Edge, etc.).  
* **Direct Portal Access:** Hardcoded shortcuts for developer tools (GitHub, Claude, Gemini) and media (YouTube Music).

### **🛠️ Utilities**

* **Push-to-Talk Security:** Listens only when a specific key is held, preventing accidental triggers.  
* **Timer, Date & Time:** Built-in countdown timers and current time/date retrieval.

## **📂 Project Structure**

* **main.py**: The entry point. Initializes the GUI thread and the Logic thread concurrently.  
* **logic.py**: The core engine. Handles Speech-to-Text, Text-to-Speech, and command execution.  
* **gui.py**: Defines the Face class, a reactive Tkinter interface that visualizes the assistant's state.  
* **config.py**: Central configuration file for paths, API keys, and user preferences.

## **⚙️ Setup & Installation**

### **Prerequisites**

* Windows 10 or 11 (Required for pypiwin32 and system calls).  
* Python 3.8+.  
* A working microphone.

### **Installation Steps**

1. **Clone the repository:** git clone https://github.com/starJeet000/Desktop-Automation-System.git  
   cd desktop-automation-system  
2. **Install Dependencies:** pip install \-r requirements.txt  
   *Note: pypiwin32 is critical for audio driver access on Windows.* 3\. **Configure the Environment:** Open config.py and strictly update the following:  
   * **BROWSER\_PATH**: Point this to your actual browser executable (e.g., chrome.exe, brave.exe).  
   * **DOWNLOADS\_PATH**: Verify the path to your downloads folder.  
   * **PTT\_KEY**: Set your preferred Push-to-Talk key (Default: Right Alt).

## **▶️ Usage**

1. Run the main script:  
   python main.py  
2. The GUI dashboard will appear.  
3. **Hold** the configured Push-to-Talk key (e.g., Right Alt).  
4. **Speak** a command (see examples below).  
5. **Release** the key to execute.

## **🗣️ Command Syntax Examples**

| Context | Command Example | Function |
| :---- | :---- | :---- |
| **Launcher** | *"Open Notepad"* | Opens app via Start Menu |
| **Search** | *"Search for Python documentation"* | Opens query in default browser |
| **Files** | *"Clean downloads"* | Sorts files into subdirectories |
| **App Power** | *"Shutdown assistant"* | Safely closes the AI script |
| **PC Power** | *"Hibernate computer"* | Puts Windows into hibernation |
| **PC Power** | *"Shutdown computer"* | Shuts down the Windows PC |
| **Dev** | *"Search GitHub for react native"* | Searches GitHub repositories |
| **Media** | *"YouTube search lo-fi beats"* | Searches and opens YouTube |
| **Utils** | *"Set timer for 15 minutes"* | Starts a background timer |
| **Info** | *"What is the time"* | Speaks current time |

## **🧩 Extension**

To add new commands, navigate to the execute\_command method in logic.py. The architecture is designed to be easily extensible—simply add a new elif block with your desired keyword string and corresponding Python logic.
