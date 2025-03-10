import speech_recognition as sr

mic_index = 6  # 👈 Ensure this is the correct index for your Bluetooth mic

recognizer = sr.Recognizer()

try:
    with sr.Microphone(device_index=mic_index) as source:
        print(f"Testing microphone: {sr.Microphone.list_microphone_names()[mic_index]}")
        recognizer.adjust_for_ambient_noise(source, duration=2.5)
        print("Say something...")
        audio = recognizer.listen(source, timeout=10)
        print("Processing...")

        # Try recognizing speech
        text = recognizer.recognize_google(audio)
        print(f"You said: {text}")

except Exception as e:
    print(f"Error: {e}")
