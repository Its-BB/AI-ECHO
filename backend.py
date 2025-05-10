import json
from datetime import datetime
import threading
import time
import speech_recognition as sr
import os
import pyttsx3
from llama_cpp import Llama
import winsound
import webbrowser
import subprocess
import shutil
import psutil
import platform
import pyautogui
import sys
import glob
from pathlib import Path

# Global variables
model = None
tts_engine = None
tts_lock = threading.Lock()
wake_word = "echo"
is_listening = True
speech_lock = threading.Lock()

def setup_voice():
    """Initialize the TTS engine with optimal settings"""
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    preferred_voices = ["Zira", "Hazel", "Susan"]
    
    selected_voice = None
    for preferred in preferred_voices:
        for voice in voices:
            if preferred.lower() in voice.name.lower():
                selected_voice = voice
                break
        if selected_voice:
            break
    
    if selected_voice:
        engine.setProperty('voice', selected_voice.id)
    
    engine.setProperty('rate', 170)
    engine.setProperty('volume', 0.9)
    return engine

def initialize_model():
    global model
    MODEL_PATH = "models/phi-2.Q5_0.gguf"
    
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")
    
    print("Loading LLM model...")
    model = Llama(
        model_path=MODEL_PATH,
        n_ctx=2048,  # Increased context
        n_batch=512,  # Increased batch
        n_threads=8,  # Increased threads
        n_gpu_layers=0
    )
    print("Model loaded successfully!")

def generate_response(user_message):
    """Generate response without conversation history"""
    prompt = f"""<|system|>You are Echo, a friendly AI with full system access. Execute any command, open any file/folder/app, and perform any system task. Be concise and conversational. Current date: {datetime.now().strftime("%Y-%m-%d")}.<|user|>{user_message}<|assistant|>"""
    
    try:
        response = model.create_completion(
            prompt=prompt,
            max_tokens=500, 
            temperature=0.7,
            top_p=0.95,
            stop=["<|user|>", "<|system|>"],
            stream=False
        )
        return response["choices"][0]["text"].strip()
    except Exception as e:
        print(f"Error generating response: {e}")
        return "Sorry, I'm having trouble processing that. Try again?"

def speak_text(text):
    """Thread-safe text-to-speech"""
    global tts_engine
    with tts_lock:
        if tts_engine is None:
            tts_engine = setup_voice()
    
    try:
        with tts_lock:
            print(f"Speaking: '{text}'")
            tts_engine.say(text)
            tts_engine.runAndWait()
    except Exception as e:
        print(f"TTS error: {e}")
        with tts_lock:
            tts_engine = setup_voice()
            tts_engine.say(text)
            tts_engine.runAndWait()
    time.sleep(0.5)

def find_and_open(path_or_name):
    """Dynamically find and open files, folders, or applications"""
    path_or_name = path_or_name.strip()
    
    if os.path.exists(path_or_name):
        if os.path.isfile(path_or_name):
            os.startfile(path_or_name)
            return True, f"Opened file: {path_or_name}"
        elif os.path.isdir(path_or_name):
            os.startfile(path_or_name)
            return True, f"Opened folder: {path_or_name}"

    search_locations = [
        Path.home() / "Desktop",
        Path.home() / "Documents",
        Path.home() / "Downloads",
        "C:\\Program Files",
        "C:\\Program Files (x86)",
        Path.home()
    ]

    # Try to find file/folder/app
    for location in search_locations:
        try:
            # Search for files/folders
            for item in glob.glob(f"{location}/**/{path_or_name}*", recursive=True):
                if os.path.exists(item):
                    os.startfile(item)
                    return True, f"Opened: {item}"
            
            # Try with common extensions for apps
            for ext in [".exe", ".lnk"]:
                for item in glob.glob(f"{location}/**/{path_or_name}{ext}", recursive=True):
                    if os.path.isfile(item):
                        os.startfile(item)
                        return True, f"Opened application: {item}"
        except Exception as e:
            continue

    return False, f"Couldn't find {path_or_name}. Please provide more details."

def open_website(url):
    """Open a website"""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    try:
        webbrowser.open(url)
        return True, f"Opening {url}"
    except Exception as e:
        return False, f"Couldn't open {url}"

def search_web(query):
    """Search the web"""
    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    try:
        webbrowser.open(search_url)
        return True, f"Searching for {query}"
    except Exception as e:
        return False, "Couldn't perform search"

def get_system_info():
    """Get system information"""
    info = {
        "System": platform.system(),
        "Version": platform.version(),
        "Machine": platform.machine(),
        "Processor": platform.processor(),
        "RAM": f"{round(psutil.virtual_memory().total / (1024**3), 2)} GB",
        "CPU Usage": f"{psutil.cpu_percent()}%",
        "Memory Usage": f"{psutil.virtual_memory().percent}%"
    }
    return "\n".join(f"{k}: {v}" for k, v in info.items())

def take_screenshot():
    """Take a screenshot"""
    desktop = Path.home() / "Desktop"
    screenshot_path = desktop / f"echo_screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    try:
        screenshot = pyautogui.screenshot()
        screenshot.save(screenshot_path)
        return True, f"Screenshot saved to {screenshot_path}"
    except Exception as e:
        return False, "Couldn't take screenshot"

def list_files(directory=None):
    """List files in directory"""
    directory = directory or os.getcwd()
    try:
        files = os.listdir(directory)
        if not files:
            return f"No files in {directory}"
        return "\n".join(f"{i}. {file}" for i, file in enumerate(files[:20], 1))
    except Exception as e:
        return f"Couldn't list files in {directory}: {str(e)}"

def control_volume(action):
    """Control system volume"""
    try:
        action = action.lower()
        if action in ["mute", "unmute"]:
            pyautogui.press("volumemute")
            return True, "Toggled mute"
        elif action in ["up", "increase"]:
            pyautogui.press("volumeup", presses=5)
            return True, "Volume increased"
        elif action in ["down", "decrease"]:
            pyautogui.press("volumedown", presses=5)
            return True, "Volume decreased"
        return False, "Invalid volume command"
    except Exception as e:
        return False, "Couldn't control volume"

def shutdown_or_restart(action):
    """Shutdown or restart computer"""
    try:
        action = action.lower()
        if action == "shutdown":
            subprocess.Popen("shutdown /s /t 60", shell=True)
            return True, "Shutting down in 1 minute"
        elif action == "restart":
            subprocess.Popen("shutdown /r /t 60", shell=True)
            return True, "Restarting in 1 minute"
        elif action == "cancel":
            subprocess.Popen("shutdown /a", shell=True)
            return True, "Canceled shutdown/restart"
        return False, "Invalid shutdown command"
    except Exception as e:
        return False, "Couldn't control shutdown/restart"

def create_file(filename, content=""):
    """Create a new file"""
    try:
        with open(filename, 'w') as f:
            f.write(content)
        return True, f"Created file: {filename}"
    except Exception as e:
        return False, f"Couldn't create file {filename}: {str(e)}"

def send_keystroke(keys):
    """Send keyboard shortcuts"""
    try:
        pyautogui.hotkey(*keys.split('+'))
        return True, f"Sent keystroke: {keys}"
    except Exception as e:
        return False, "Couldn't send keystroke"

def process_command(command):
    """Process user command with full system access"""
    print(f"Processing: {command}")
    if len(command.strip()) < 2:
        return
    
    command_lower = command.lower()
    response_text = None
    action_taken = False

    # Dynamic file/folder/app opening
    if "open" in command_lower:
        parts = command_lower.split("open ")
        if len(parts) > 1:
            target = parts[1].strip()
            success, message = find_and_open(target)
            response_text = message
            action_taken = success

    # Website commands
    elif any(x in command_lower for x in ["website", "site", ".com", ".org"]):
        url = command_lower.split("open ")[1] if "open " in command_lower else command_lower
        success, message = open_website(url.strip())
        response_text = message
        action_taken = success

    # Search commands
    elif any(x in command_lower for x in ["search", "look up", "google"]):
        query = command_lower.split("search for ")[1] if "search for " in command_lower else \
                command_lower.split("search ")[1] if "search " in command_lower else \
                command_lower.split("google ")[1] if "google " in command_lower else command_lower
        success, message = search_web(query.strip())
        response_text = message
        action_taken = success

    # System commands
    elif "system info" in command_lower:
        response_text = get_system_info()
        action_taken = True
    elif "screenshot" in command_lower:
        success, message = take_screenshot()
        response_text = message
        action_taken = success
    elif "list files" in command_lower:
        response_text = list_files()
        action_taken = True
    elif "volume" in command_lower:
        action = "up" if any(x in command_lower for x in ["up", "increase"]) else \
                 "down" if any(x in command_lower for x in ["down", "decrease"]) else \
                 "mute" if "mute" in command_lower else "unmute"
        success, message = control_volume(action)
        response_text = message
        action_taken = success
    elif any(x in command_lower for x in ["shutdown", "restart", "reboot"]):
        action = "shutdown" if "shutdown" in command_lower else \
                 "restart" if any(x in command_lower for x in ["restart", "reboot"]) else "cancel"
        success, message = shutdown_or_restart(action)
        response_text = message
        action_taken = success
    elif any(x in command_lower for x in ["create file", "make file"]):
        filename = command_lower.split("file ")[1].strip() + (".txt" if not "." in command_lower else "")
        success, message = create_file(filename)
        response_text = message
        action_taken = success
    elif any(x in command_lower for x in ["press", "keystroke"]):
        keys = command_lower.split("press ")[1].strip() if "press " in command_lower else command_lower
        success, message = send_keystroke(keys)
        response_text = message
        action_taken = success

    # Fallback to LLM
    if not action_taken:
        response_text = generate_response(command)

    print(f"Echo: {response_text}")
    speak_text(response_text)
    time.sleep(1.0)

def play_beep():
    """Play a short beep"""
    try:
        winsound.Beep(1000, 180)
    except:
        pass

def get_command():
    """Improved command capture with longer phrase time"""
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 150
    recognizer.dynamic_energy_threshold = True
    recognizer.pause_threshold = 1.5  # Increased pause detection
    recognizer.non_speaking_duration = 0.7  # Allow longer non-speaking periods
    
    try:
        with sr.Microphone() as source:
            print("Listening for command...")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=15)
            try:
                command = recognizer.recognize_google(audio)
                print(f"Heard command: {command}")
                return command
            except sr.UnknownValueError:
                print("Could not understand command")
                return None
            except sr.RequestError as e:
                print(f"API error: {e}")
                return None
    except Exception as e:
        print(f"Error getting command: {e}")
        return None

def listen_continuously():
    """Main listening loop"""
    print(f"Echo is listening... Say '{wake_word}' to activate")
    
    while is_listening:
        if not wait_for_wake_word():
            time.sleep(0.1)
            continue
            
        print("\n" + "*" * 50)
        print("WAKE WORD DETECTED")
        print("*" * 50)
        play_beep()
        
        command = get_command()
        if command:
            process_command(command)
        
        print("\nReturning to wake word listening...")
        time.sleep(1.0)

def wait_for_wake_word():
    """Wait for wake word"""
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 150
    
    try:
        with sr.Microphone() as source:
            print("\nListening for wake word...")
            audio = recognizer.listen(source, timeout=None, phrase_time_limit=3)
            try:
                text = recognizer.recognize_google(audio).lower()
                print(f"Heard: {text}")
                return wake_word in text or any(alt in text for alt in ["echo", "eco", "ecko"])
            except sr.UnknownValueError:
                pass
            except sr.RequestError as e:
                print(f"API error: {e}")
    except Exception as e:
        print(f"Error in wake word detection: {e}")
        time.sleep(0.5)
    
    return False

def main():
    """Main entry point"""
    print("Starting Enhanced Echo AI Assistant...")
    initialize_model()
    print("\n" + "=" * 50)
    print(f"ECHO IS NOW ACTIVE - SAY '{wake_word}'")
    print("=" * 50 + "\n")
    
    speak_text("Hello, I'm Echo. I have full system access. How can I help?")
    
    try:
        listen_continuously()
    except KeyboardInterrupt:
        print("\nShutting down Echo...")
    except Exception as e:
        print(f"Fatal error: {e}")
    
    print("Echo has been stopped.")

if __name__ == "__main__":
    main()