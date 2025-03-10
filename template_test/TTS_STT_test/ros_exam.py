# tts_stt_test/ros_exam.py

import speech_recognition as sr
import pyttsx3
import ollama

# Define the sections with symptoms
review_of_systems = {
    "General": ["Fever", "Chills", "Fatigue", "Unintentional weight loss or gain"],
    "Musculoskeletal": ["Neck pain or stiffness", "Back pain", "Joint pain or swelling", "Muscle pain (myalgia)", "Weakness or limited range of motion"]
}

# Dictionary to store responses
responses = {}

def speak(text):
    """Converts text to speech and reads it aloud."""
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def get_default_microphone():
    """Automatically selects the built-in microphone instead of Bluetooth."""
    for index, name in enumerate(sr.Microphone.list_microphone_names()):
        if "Realtek" in name or "Microphone Array" in name:
            print(f"Using microphone: {name} (Index {index})")
            return index
    print("No built-in microphone detected. Using system default.")
    return None  # If no built-in mic is found, default to None (system default)

def recognize_speech():
    """Listens for a spoken response and converts it to text."""
    recognizer = sr.Recognizer()
    mic_index = get_default_microphone()  # Automatically detect built-in mic

    if mic_index is None:
        print("No built-in microphone found. Using system default.")
        mic_index = None  # Default mic

    with sr.Microphone(device_index=mic_index) as source:
        print(f"Listening with microphone index {mic_index}...")

        # Reduce delay before listening
        recognizer.adjust_for_ambient_noise(source, duration=1.0)

        print("Listening now...")
        try:
            audio = recognizer.listen(source, timeout=15)  # More time to speak
            text = recognizer.recognize_google(audio).lower().strip()
            print(f"You said: {text}")

            # Directly map common responses
            response_map = {
                "positive": "Positive", "pos": "Positive", "yes": "Positive", "affirmative": "Positive",
                "negative": "Negative", "neg": "Negative", "no": "Negative"
            }
            if text in response_map:
                return response_map[text]

            # Use Ollama if response is unclear
            print("Interpreting response with Ollama...")
            ollama_response = ollama.chat(
                model="llama3.1",
                messages=[{"role": "user", "content": f'User said "{text}". Does this mean "positive" or "negative"? Reply only with one word.'}]
            )
            interpreted_text = ollama_response['message']['content'].strip().lower()
            print(f"Ollama interpreted response as: {interpreted_text}")

            # Validate Ollama's response
            if interpreted_text in response_map:
                return response_map[interpreted_text]

            # Ask again if response is unclear
            print("Please repeat your response.")
            speak("I didn't understand. Please say positive or negative.")
            return retry_recognition(recognizer, source)

        except sr.UnknownValueError:
            print("I didn't catch that. Please repeat.")
            speak("I didn't catch that. Please repeat.")
            return retry_recognition(recognizer, source)
        except sr.RequestError:
            print("Speech Recognition service unavailable.")
            return "Error"
        except sr.WaitTimeoutError:
            print("No response detected. Please try again.")
            speak("No response detected. Please try again.")
            return retry_recognition(recognizer, source)

def retry_recognition(recognizer, source):
    """Retries speech recognition only once if the first attempt fails."""
    try:
        print("Listening again...")
        audio = recognizer.listen(source, timeout=15)
        text = recognizer.recognize_google(audio).lower().strip()
        print(f"You said: {text}")

        response_map = {
            "positive": "Positive", "pos": "Positive", "yes": "Positive", "affirmative": "Positive",
            "negative": "Negative", "neg": "Negative", "no": "Negative"
        }
        return response_map.get(text, "Unclear")
    
    except sr.UnknownValueError:
        print("Could not understand again. Moving on.")
        speak("Could not understand again. Moving on.")
        return "Unclear"
    except sr.WaitTimeoutError:
        print("No response again. Moving on.")
        speak("No response again. Moving on.")
        return "Unclear"

def conduct_ros():
    """Conducts the Review of Systems (ROS) examination."""
    speak("Beginning Review of Systems examination.")

    for section, symptoms in review_of_systems.items():
        speak(f"Let's begin with the {section} section.")
        responses[section] = {}

        for symptom in symptoms:
            speak(f"Is there any {symptom}?")
            response = recognize_speech()

            responses[section][symptom] = response

    # Print and summarize responses
    speak("Review of Systems examination complete. Here are the results.")
    print("\n--- ROS Results ---")
    for section, symptoms in responses.items():
        print(f"\n{section} Review:")
        for symptom, result in symptoms.items():
            print(f"- {symptom}: {result}")

    return responses

if __name__ == "__main__":
    responses = conduct_ros()


