import json
import os
import tkinter as tk
from tkinter import messagebox, Listbox, Scrollbar, Button, Frame
import subprocess

def load_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def generate_narrative(data):
    template = (
        "On {Date}, the patient was injured in an auto accident. In the patient's words, they described the incident as {Brief Description of Accident}. "
        "After the immediate collision, there {Secondary Collisions} a secondary collision. "
        "The patient {Recall Striking} recall striking things inside the vehicle. "
        "The patient's vehicle was a {Vehicle Make} {Vehicle Model} and was going {Vehicle Speed} MPH. "
        "The other vehicle was a {Other Vehicle Model} and was going approximately {Other Vehicle Speed} MPH. "
        "The vehicle had {Vehicle Damage} damage, after the accident the patient's car was {Vehicle Drivable} drivable. "
        "The patient was the {Driver or Passenger} in the vehicle. "
        "The police {Police Arrival} arrive. "
        "Following the car accident, the patient went to the ER/Urgent Care or was hospitalized: {ER Visit}. "
        "At the time of the accident, the visibility was {Visibility}. "
        "The accident occurred at {Time of Day} when the road conditions were {Road Conditions}. "
        "At the time of the impact, the patient was looking {Looking Direction}. "
        "The patient's foot {Foot on Brake} on the brake. "
        "During the collision, the patient {Braced for Impact}. "
        "The patient was {Wearing Seatbelt} wearing a seat belt. "
        "The airbags {Airbag Deploy}. "
        "The patient's headrest {Headrest Adjustment}."
    )

    narrative_data = {
        "Date": data.get('Date', '??'),
        "Brief Description of Accident": data.get('Brief Description of Accident', '??'),
        "Secondary Collisions": "was" if data.get('Describe any Secondary Collisions', '??') != "No other." else "was not",
        "Recall Striking": "did" if data.get('Do you recall striking anything inside the vehicle', '??') == "Yes" else "did not",
        "Vehicle Make": data['Type of Vehicle you were in'].get('Make', '??'),
        "Vehicle Model": data['Type of Vehicle you were in'].get('Model', '??'),
        "Vehicle Speed": data['Type of Vehicle you were in'].get('Estimated Speed', '??'),
        "Other Vehicle Model": data['Type of Vehicle the Other Driver Was In'].get('Model', '??'),
        "Other Vehicle Speed": data['Type of Vehicle the Other Driver Was In'].get('Estimated Speed', '??'),
        "Vehicle Damage": data.get('Describe Damage to Vehicle', '??'),
        "Vehicle Drivable": data.get('After the Accident Vehicle Drivable', '??'),
        "Driver or Passenger": data.get('Were you Driver or Passenger', '??'),
        "Police Arrival": "did" if data.get('Did Police Arrive', '??') == "Yes" else "did not",
        "ER Visit": data.get('ER/Urgent Care/Hospitalizations Related to Crash', '??'),
        "Visibility": data.get('Visibility', '??'),
        "Time of Day": data.get('Time of Day', '??'),
        "Road Conditions": data.get('Road Conditions', '??'),
        "Looking Direction": data.get('Looking Direction at Time of Impact', '??'),
        "Foot on Brake": "was" if data.get('Was Your Foot on the Brake', '??') == "Yes" else "was not",
        "Braced for Impact": "was braced" if data.get('Were You Braced for Impact', '??') == "Yes" else "was not braced",
        "Wearing Seatbelt": "" if data.get('Wearing Seatbelt', '??') == "Yes" else "not",
        "Airbag Deploy": "deployed" if data.get('Did Your Airbag Deploy', '??') == "Yes" else "did not deploy",
        "Headrest Adjustment": data.get('Headrest Adjustment', '??')
    }

    narrative = template.format(**narrative_data)
    return narrative

def process_file(file_path):
    data = load_json(file_path)
    narrative = generate_narrative(data)
    
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    txt_file = f"{base_name}.txt"
    txt_path = os.path.join(os.path.dirname(file_path), txt_file)
    
    with open(txt_path, 'w') as f:
        f.write(narrative)
    
    return txt_file

def list_json_files(directory):
    return [f for f in os.listdir(directory) if f.endswith('_autoq.json')]

def open_txt_file(file_path):
    subprocess.run(['notepad.exe', file_path])

def transcribe_selected_file():
    if not listbox.curselection():
        messagebox.showinfo("No Selection", "Please select a file to transcribe.")
        return
    
    index = listbox.curselection()[0]
    json_file = listbox.get(index)
    json_path = os.path.join(directory_path, json_file)
    
    txt_file = process_file(json_path)
    messagebox.showinfo("Transcription Completed", f"Transcribed {json_file} to {txt_file}.")
    refresh_file_list()

def refresh_file_list():
    json_files = list_json_files(directory_path)
    listbox.delete(0, tk.END)
    for file in json_files:
        listbox.insert(tk.END, file)

def on_select(evt):
    if not listbox.curselection():
        return
    index = listbox.curselection()[0]
    json_file = listbox.get(index)
    base_name = os.path.splitext(json_file)[0]
    txt_file = f"{base_name}.txt"
    txt_path = os.path.join(directory_path, txt_file)
    
    if os.path.exists(txt_path):
        root.after(100, open_txt_file, txt_path)
    else:
        messagebox.showinfo("File Not Found", f"{txt_file} has not been generated yet. Please transcribe the file first.")

# Set up the main application window
root = tk.Tk()
root.title("Auto Accident Narrative Generator")

# Set the directory path to the 'autoq' subdirectory
directory_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'autoq')

# Create the directory if it doesn't exist
os.makedirs(directory_path, exist_ok=True)

# Create a frame for the listbox and scrollbar
frame = Frame(root)
frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Set up the listbox to display JSON files
listbox = Listbox(frame, width=50, height=20)
listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar = Scrollbar(frame, orient="vertical")
scrollbar.config(command=listbox.yview)
scrollbar.pack(side=tk.RIGHT, fill="y")

listbox.config(yscrollcommand=scrollbar.set)
listbox.bind('<<ListboxSelect>>', on_select)

# Set up the buttons
transcribe_button = Button(root, text="Transcribe Selected File", command=transcribe_selected_file)
transcribe_button.pack(side=tk.TOP, fill=tk.X)

refresh_button = Button(root, text="Refresh File List", command=refresh_file_list)
refresh_button.pack(side=tk.TOP, fill=tk.X)

# Initialize the listbox with JSON files
refresh_file_list()

# Run the application
root.mainloop()