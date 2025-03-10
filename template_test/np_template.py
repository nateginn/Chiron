import json
import os
import tkinter as tk
from tkinter import messagebox, Listbox, Scrollbar, Button, Frame
import subprocess

def safe_get(data, key, default="??"):
    if isinstance(data, dict) and key in data:
        value = data[key]
        if isinstance(value, list):
            return ", ".join(map(str, value))
        return str(value) if value is not None else default
    return default

def generate_narrative(data):
    template = (
        "The patient, {Legal_Name}, presented for a consultation, examination, and initial treatment on {Date_of_Visit}. "
        "The patient had no difficulty completing the paperwork and was alert and cooperative during the history taking, and examination. "
        "The initial injury occurred on {Date_of_Injury}. "
        "The patient {Previous_Symptoms} experienced similar symptoms before. "
        "The patient presents that their chief complaint is {Areas_of_Pain} pain. "
        "They are rating their pain level at {Pain_Rating}/10. "
        "The patient is experiencing {Symptoms_Descriptions} which they did not have prior to the injury. "
        "Activities which are provocative to the injury include {Activities_that_Increase_Pain}. "
        "Activities which are palliative include {Activities_that_Relieve_Pain}. "
        "The patient has {MRI_or_XRay} had a MRI/X-Ray.\n\n"
        "The patient's previous medical history is as follows. "
        "Before coming into our practice, the patient visited their family physician, {Primary_Physician} for this condition. "
        "The patient {Pregnancy_Status} pregnant. "
        "The patient's medications include {Medications}. "
        "The patient is allergic to {Allergies}. "
        "The patient had {Previous_Surgeries} surgery. "
        "The patient {Metal_Implants} have metal implants. "
        "The patient has a personal history of {Personal_History}."
    )

    symptoms = [k for k, v in data.get("Symptoms_Descriptions", {}).items() if v == "Yes"]
    personal_history = data.get("Personal_History", [])

    narrative_data = {
        "Legal_Name": safe_get(data, "Legal_Name"),
        "Date_of_Visit": safe_get(data, "Date_of_Visit"),
        "Date_of_Injury": safe_get(data, "Date_of_Injury"),
        "Previous_Symptoms": "has" if safe_get(data, "Previous_Symptoms") == "Yes" else "has not",
        "Areas_of_Pain": safe_get(data, "Areas_of_Pain"),
        "Pain_Rating": safe_get(data, "Pain_Rating"),
        "Symptoms_Descriptions": ", ".join(symptoms) if symptoms else "no additional symptoms",
        "Activities_that_Increase_Pain": safe_get(data, "Activities_that_Increase_Pain"),
        "Activities_that_Relieve_Pain": safe_get(data, "Activities_that_Relieve_Pain"),
        "MRI_or_XRay": "has" if safe_get(data, "MRI_or_XRay") == "Yes" else "has not",
        "Primary_Physician": safe_get(data, "Primary_Physician"),
        "Pregnancy_Status": "is" if safe_get(data, "Pregnancy_Status") == "Yes" else "is not",
        "Medications": safe_get(data, "Medications"),
        "Allergies": safe_get(data, "Allergies"),
        "Previous_Surgeries": safe_get(data, "Previous_Surgeries"),
        "Metal_Implants": "does" if safe_get(data, "Metal_Implants") == "Yes" else "does not",
        "Personal_History": ", ".join(personal_history) if personal_history else "no significant medical conditions"
    }

    narrative = template.format(**narrative_data)
    return narrative

def load_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON in {file_path}: {e}")
        return None
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None

def process_file(file_path):
    data = load_json(file_path)
    if data is None:
        return None
    
    narrative = generate_narrative(data)
    
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    txt_file = f"{base_name}.txt"
    txt_path = os.path.join(os.path.dirname(file_path), txt_file)
    
    try:
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(narrative)
        return txt_file
    except Exception as e:
        print(f"Error writing to {txt_path}: {e}")
        return None

def list_json_files(directory):
    return [f for f in os.listdir(directory) if f.endswith('_np.json')]

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
    if txt_file:
        messagebox.showinfo("Transcription Completed", f"Transcribed {json_file} to {txt_file}.")
    else:
        messagebox.showerror("Transcription Failed", f"Failed to transcribe {json_file}.")
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
root.title("New Patient Narrative Generator")

# Set the directory path
directory_path = r"C:\Users\nginn\OneDrive\Desktop\New patient Intake files"

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