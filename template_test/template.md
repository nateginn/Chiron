# Setting Up and Running the Patient Narrative Script

This guide will help you set up and run the Patient Narrative Script on a computer without an IDE.

## 1. Add the Script to the Correct File Location

1. **Create a Directory for the Script:**
   - Create a folder on your computer, for example, `C:\PatientNarrative`.

2. **Save the Script:**
   - Open a simple text editor like Notepad.
   - Copy the entire script provided below and paste it into the text editor.
   - Save the file in the newly created folder as `generate_narrative.py`.

## 2. Set Up a Desktop Shortcut to Run the Script

1. **Create a Shortcut:**
   - Right-click on your desktop and select `New > Shortcut`.
   - In the "Type the location of the item" field, enter the following command:
     ```plaintext
     pythonw C:\PatientNarrative\generate_narrative.py
     ```
     - Note: `pythonw` is used instead of `python` to run the script without opening a command prompt window.

2. **Name the Shortcut:**
   - Click `Next`, then give your shortcut a name, such as "Run Patient Narrative Script".
   - Click `Finish`.

3. **Ensure Python is Installed:**
   - Make sure Python is installed on the computer. If not, download and install it from [python.org](https://www.python.org/downloads/).
   - Add Python to the system PATH during installation to ensure it can be run from any directory.

## 3. Open a Text Editor with the Output

1. **Modify the Script to Save and Open the Output:**
   - Update the script to open the output text file in a text editor like Notepad after generating the narrative. Here’s a snippet you can add to the end of your script:
     ```python
     import subprocess

     # Open the output file in Notepad
     subprocess.run(['notepad.exe', txt_path])
     ```

2. **Ensure the Script Opens the Output:**
   - Ensure that the script includes the subprocess call to open the output text file in Notepad after it finishes writing the narrative.

## Final Script with Notepad Opening

Save the following script as `generate_narrative.py` in the `C:\PatientNarrative` directory:

```python
import json
import os
import subprocess

def load_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def generate_narrative(data, patient_name):
    narrative = f"The patient {patient_name} presents stating that their chief complaints today are "
    
    complaints = []
    details = []

    for area, info in data["pain_data"].items():
        complaints.append(f"{area} pain")
        detail = (
            f"For the {area} pain, the patient is rating their pain level as {info['scale']}. "
            f"They describe the pain as being {', '.join(info['descriptiveTerms'])} and note that the frequency is {info['comparison']} since their last visit."
        )
        details.append(detail)

    narrative += ', '.join(complaints) + ".\n\n" + "\n\n".join(details)
    
    return narrative

def process_files_in_directory(directory):
    # Get a list of all files in the directory
    all_files = os.listdir(directory)
    
    # Filter out the JSON files
    json_files = [f for f in all_files if f.endswith('.json')]
    
    no_new_files = True
    
    for json_file in json_files:
        # Determine the base name for comparison
        base_name = os.path.splitext(json_file)[0]
        txt_file = f"{base_name}.txt"
        
        # Check if the corresponding TXT file exists
        if txt_file not in all_files:
            no_new_files = False
            # Load the JSON data
            json_path = os.path.join(directory, json_file)
            data = load_json(json_path)
            
            # Extract patient's name
            patient_name = ' '.join(base_name.split('_')[:2])
            
            # Generate the narrative
            narrative = generate_narrative(data, patient_name)
            
            # Write the narrative to the TXT file
            txt_path = os.path.join(directory, txt_file)
            with open(txt_path, 'w') as f:
                f.write(narrative)
            
            print(f"Narrative has been written to {txt_path}")
            
            # Open the output file in Notepad
            subprocess.run(['notepad.exe', txt_path])
    
    if no_new_files:
        print("No new files to transcribe.")

# Specify the directory to search
directory_path = '.'  # The current directory

# Process the files in the specified directory
process_files_in_directory(directory_path)
