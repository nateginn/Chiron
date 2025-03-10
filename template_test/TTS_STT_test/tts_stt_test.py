# tts_stt_test/tts_stt_test.py

import ollama
import pyttsx3

# Define the color mapping
color_map = {
    1: "Red",
    2: "Blue",
    3: "Green",
    4: "Purple",
    5: "Yellow",
    6: "Orange",
    7: "Pink",
    8: "Brown",
    9: "Black",
    10: "White"
}

def get_color(number):
    """Returns the color associated with a given number."""
    return color_map.get(number, "I don't have a color for that number.")

def generate_response(number):
    """Asks the LLM to respond to the color question."""
    prompt = f"What color is associated with number {number}? The color list is {color_map}."
    
    response = ollama.chat(model="llama3.1", messages=[{"role": "user", "content": prompt}])
    
    if 'message' in response:
        text_response = response['message']['content']
    else:
        text_response = f"Number {number} is {get_color(number)}."

    print(text_response)  # Display in terminal
    return text_response

def speak(text):
    """Converts text to speech using pyttsx3."""
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def main():
    """Main function to ask user for a number and respond verbally."""
    try:
        user_input = int(input("Enter a number: "))  # Get user input
        response = generate_response(user_input)  # Get LLM response
        speak(response)  # Convert to speech
    except ValueError:
        print("Please enter a valid number.")

if __name__ == "__main__":
    main()
