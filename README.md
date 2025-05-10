# Echo Voice Assistant

![Status](https://img.shields.io/badge/status-completed-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## 🎤 Overview

Echo is a powerful offline voice assistant with complete system access, built as a personal project to explore the capabilities of local language models and voice recognition technology. Echo uses the Phi-2 model (quantized) to provide intelligent responses while maintaining privacy by processing everything locally on your machine.

> **Note:** This project is complete and no longer actively maintained. It was developed as a personal experiment and learning exercise.

## ✨ Features

- **Voice Activation**: Responds to the wake word "echo"
- **System Control**: Full access to open applications, files, and perform system tasks
- **Web Integration**: Can search the web and open websites
- **File Management**: Create files and navigate directories
- **System Information**: Get details about your computer's specifications
- **Screenshot Capture**: Take and save screenshots to your desktop
- **Volume Control**: Adjust system volume through voice commands
- **Shutdown/Restart**: Control system power state
- **Keyboard Shortcuts**: Send keystrokes to the active application
- **Offline Processing**: All language processing happens locally using the Phi-2 model

## 🛠️ Technical Architecture

Echo consists of several key components:

- **Language Model**: Uses llama-cpp to run the Phi-2 quantized model
- **Voice Recognition**: Employs SpeechRecognition with Google's API
- **Text-to-Speech**: Utilizes pyttsx3 for voice responses
- **System Interaction**: Built with various Python libraries for system control

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Windows OS (some features are Windows-specific)
- At least 4GB of RAM
- Microphone and speakers

### Installation

1. Clone this repository:
   ```
   git clone https://github.com/Its-BB/AI-ECHO.git
   ```

2. Install required packages:
   ```
   pip install llama-cpp-python pyttsx3 SpeechRecognition pyautogui psutil
   ```

3. Create the required directories structure:
   ```
   mkdir -p models
   ```

4. Download the Phi-2 quantized model

### Running Echo

Simply run:
```
python run_echo.py
```

The assistant will start listening for the wake word "echo". Once activated, you can speak your command.

## 🎯 Usage Examples

- "Echo, open Chrome"
- "Echo, search for Python tutorials"
- "Echo, take a screenshot"
- "Echo, system info"
- "Echo, open documents folder"
- "Echo, volume up"
- "Echo, create file notes.txt"
- "Echo, press Ctrl+C"
- "Echo, shutdown in 1 minute"

## 🔮 How It Works

1. The system continuously listens for the wake word "echo"
2. When detected, it plays a beep to indicate activation
3. Voice input is captured and converted to text
4. The command is parsed and executed if it matches known system functions
5. If not recognized as a system command, the query is passed to the LLM for response
6. The response is converted to speech and played back

## 📝 Code Structure

- **backend.py** - Core functionality and system integration
- **run_echo.py** - Entry point and dependency checker

## ⚠️ Limitations

- Heavy system commands may cause delays
- Some functionality is Windows-specific
- Speech recognition requires internet connectivity
- Not designed for enterprise or production use
- Limited to the capabilities of the Phi-2 model

## 🙏 Acknowledgements

This project would not be possible without:
- The Phi-2 model from Microsoft
- The llama-cpp library
- Various Python packages for system interaction

## 📄 License

This project is available under the MIT License.

---

**Note:** This was a personal project created for learning purposes, and is no longer being actively maintained or updated.