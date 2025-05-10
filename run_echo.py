# run_echo.py
import os
import sys
import platform
import subprocess

def check_dependencies():
    """Check if all required dependencies are installed"""
    try:
        import llama_cpp
        import pyttsx3
        import speech_recognition
        return True
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Please run: pip install llama-cpp-python pyttsx3 SpeechRecognition")
        return False

def check_model():
    """Check if the model file exists, download if not"""
    model_path = "models/phi-2.Q5_0.gguf"
    if not os.path.exists(model_path):
        print("Model not found. Downloading now...")
        try:
            from model_downloader import download_model
            download_model()
            return True
        except Exception as e:
            print(f"Error downloading model: {e}")
            print("Please run model_downloader.py separately.")
            return False
    return True

def ensure_directories():
    """Make sure necessary directories exist"""
    os.makedirs("models", exist_ok=True)

def main():
    """Main entry point for running Echo"""
    print("=" * 50)
    print("STARTING ECHO VOICE ASSISTANT")
    print("=" * 50)
    
    ensure_directories()
    
    if not check_dependencies():
        print("Missing required dependencies.")
        return
    
    # Verify model is downloaded
    if not check_model():
        print("Model file is required to run Echo.")
        return
    
    try:
        print("Starting Echo...")
        from backend import main as run_backend
        run_backend()
    except Exception as e:
        print(f"Error running Echo: {e}")
        print("Try running 'python backend.py' directly.")

if __name__ == "__main__":
    main()