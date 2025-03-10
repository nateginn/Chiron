import json
import os
import random
import subprocess
import tkinter as tk
from tkinter import messagebox, Listbox, Scrollbar, Button, Frame

def load_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def generate_narrative(data, patient_name, template=None):
    templates = [
        (
            f"The patient {patient_name} presents stating that their chief complaints today are {{complaints}}. "
            "They describe the {area} pain as {descriptions}, with an intensity of {scale}. "
            "Currently, they are experiencing this pain {frequency}. "
            "The severity of this pain is {comparison} compared to their previous visit."
        ),
        (
            f"{patient_name} reports today with the main issues of {{complaints}}. "
            "For the {area} pain, they rate it at {scale}. "
            "They say the pain feels {descriptions} and has been {frequency}, and {comparison} since the last appointment."
        ),
        (
            f"Chief complaints for {patient_name} today include {{complaints}}. "
            "The pain in their {area} is described as {descriptions}, with a pain intensity of {scale}. "
            "The frequency of this pain is {frequency}. "
            "The severity of this pain is {comparison} since their last visit."
        )
    ]

    # Select a template randomly if none is provided
    if template is None:
        template = random.choice(templates)
    else:
        template = templates[template]
    
    complaints = ', '.join([f"{area} pain" for area in data["pain_data"].keys() if area != "new_injury"])
    narrative = template.replace("{complaints}", complaints)
    
    details = []

    first = True
    for area, info in data["pain_data"].items():
        if area == "new_injury":
            new_injury_narrative = (
                f"The patient also reports a new injury at {info['location']} which occurred on {info['date']}. "
                f"They describe the injury as {info['description']} and have been treating it with {info['treatment']}."
            )
            details.append(new_injury_narrative)
            continue

        if first:
            detail = narrative.format(
                area=area,
                scale=info['scale'],
                descriptions=', '.join(info['descriptiveTerms']),
                frequency=info['frequency'],
                comparison=info['comparison']
            )
            first = False
        else:
            detail = (
                "The patient also describes the {area} pain as {descriptions}, "
                "with an intensity of {scale}. "
                "Currently, they are experiencing this pain {frequency}. "
                "The severity of this pain is {comparison} since their last visit."
            ).format(
                area=area,
                scale=info['scale'],
                descriptions=', '.join(info['descriptiveTerms']),
                frequency=info['frequency'],
                comparison=info['comparison']
            )
        details.append(detail)

    return "\n\n".join(details)

def process_files_in_directory(directory, template=None):
    # Get a list of all files in the directory
    all_files = os.listdir(directory)
    
    # Filter out the JSON files
    json_files = [f for f in all_files if f.endswith('.json')]
    
    transcribed_files = []

    for json_file in json_files:
        # Determine the base name for comparison
        base_name = os.path.splitext(json_file)[0]
        txt_file = f"{base_name}.txt"
        
        # Check if the corresponding TXT file exists
        if txt_file not in all_files:
            # Load the JSON data
            json_path = os.path.join(directory, json_file)
            data = load_json(json_path)
            
            # Extract patient's name
            patient_name = data.get('patient_name', 'Unknown Patient')
            
            # Generate the narrative
            narrative = generate_narrative(data, patient_name, template)
            
            # Write the narrative to the TXT file
            txt_path = os.path.join(directory, txt_file)
            with open(txt_path, 'w') as f:
                f.write(narrative)
            
            transcribed_files.append(txt_file)
    
    return transcribed_files

def list_txt_files(directory):
    return [f for f in os.listdir(directory) if f.endswith('.txt')]

def open_txt_file(file_path):
    subprocess.run(['notepad.exe', file_path])

def transcribe_files():
    transcribed_files = process_files_in_directory(directory_path)
    if transcribed_files:
        messagebox.showinfo("Transcription Completed", f"Transcribed {len(transcribed_files)} files.")
    else:
        messagebox.showinfo("No New Files", "No new files to transcribe.")
    refresh_file_list()

def refresh_file_list():
    txt_files = list_txt_files(directory_path)
    listbox.delete(0, tk.END)
    for file in txt_files:
        listbox.insert(tk.END, file)

def on_select(evt):
    w = evt.widget
    if w.curselection():
        index = int(w.curselection()[0])
        value = w.get(index)
        file_path = os.path.join(directory_path, value)
        root.after(100, open_txt_file, file_path)

# Set up the main application window
root = tk.Tk()
root.title("Patient Narrative Transcriber")

directory_path = '.'  # The current directory

# Create a frame for the listbox and scrollbar
frame = Frame(root)
frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Set up the listbox to display TXT files
listbox = Listbox(frame, width=50, height=20)
listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar = Scrollbar(frame, orient="vertical")
scrollbar.config(command=listbox.yview)
scrollbar.pack(side=tk.LEFT, fill="y")

listbox.config(yscrollcommand=scrollbar.set)
listbox.bind('<<ListboxSelect>>', on_select)

# Set up the buttons
transcribe_button = Button(root, text="Transcribe JSON Files", command=transcribe_files)
transcribe_button.pack(side=tk.TOP, fill=tk.X)

refresh_button = Button(root, text="Refresh File List", command=refresh_file_list)
refresh_button.pack(side=tk.TOP, fill=tk.X)

# Initialize the listbox with TXT files
refresh_file_list()

# Run the application
root.mainloop()
