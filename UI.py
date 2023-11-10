import tkinter as tk
from tkinter import ttk
import struct
import yaml

# Read PRZT file
file_path = 'przt_0.list'  # Update this with your file path

# Function to read PRZT file and return entries
def read_przt_file(file_path):
    with open(file_path, 'rb') as file:
        data = file.read()
        header = struct.unpack('<II', data[:8])
        num_entries = header[1]
        entries = []
        for i in range(num_entries):
            entry_offset = 8 + i * 24
            entry = struct.unpack('<HBBBBBBBBBBHhHhHh', data[entry_offset:entry_offset + 24])
            entries.append(entry)
        return entries

entries = read_przt_file(file_path)

# Function to update text boxes based on selected entry
def update_text_boxes(event):
    selected_index = entry_combobox.current()
    if selected_index >= 0:
        entry = entries[selected_index]
        for i, text_box in enumerate(text_boxes):
            text_box.delete(0, tk.END)
            text_box.insert(0, entry[i])


# Function to gather any changes made and write them back to the file
def on_save_changes():
    entry_index = entry_combobox.current()
    try:
        # If an entry is selected, update its data from text boxes
        if entry_index >= 0:
            new_entry_data = []
            for i, text_box in enumerate(text_boxes):
                value = text_box.get()
                if i == 0:  # ID is an unsigned short
                    new_entry_data.append(int(value))
                elif 10 <= i <= 16:  # Last seven values are signed shorts
                    new_entry_data.append(int(value))
                else:  # Assuming the rest are unsigned bytes
                    new_entry_data.append(int(value))

            # Update the specific entry in the entries list
            entries[entry_index] = tuple(new_entry_data)

        # Save all changes in the 'entries' list to the file
        with open(file_path, 'r+b') as file:
            for index, entry in enumerate(entries):
                binary_data = struct.pack('<HBBBBBBBBBBHhHhHh', *entry)
                entry_offset = 8 + index * 24
                file.seek(entry_offset)
                file.write(binary_data)

        print("All changes saved to file.")
    except ValueError:
        print("Error: One or more fields contain non-integer values.")
    except Exception as e:
        print(f"An error occurred: {e}")

def mass_edit_window():
    # Function to update all entries with the new value
    def save_mass_edit():
        selected_label_index = label_combobox.current()

        if selected_label_index == -1:
            print("Please select a label to update!")
            return
        
        try:
            new_value = mass_edit_text_box.get()

            # Validate and convert the new value
            if selected_label_index == 0:  # ID is an unsigned short
                new_value = int(new_value)
            elif 10 <= selected_label_index <= 16:  # Last seven values are signed shorts
                new_value = int(new_value)
            else:  # Other values are unsigned bytes
                new_value = int(new_value)

            # Update entries in the list
            for index in range(len(entries)):
                entry_list = list(entries[index])
                entry_list[selected_label_index] = new_value
                entries[index] = tuple(entry_list)

            # Optionally, update the GUI if needed
            update_text_boxes(None)  # Update the GUI with new values

            print("Entries updated in GUI. Use 'Save' to write to file.")
        except ValueError:
            print("Error: The new value must be an integer.")
        except Exception as e:
            print(f"An error occurred: {e}")

    # Create a new window for mass edit
    mass_edit_win = tk.Toplevel(root)
    mass_edit_win.title("Mass Edit")

    # Create a frame with padding in the Mass Edit window
    mass_edit_frame = tk.Frame(mass_edit_win, padx=10, pady=10)
    mass_edit_frame.pack(fill=tk.BOTH, expand=True)

    # Dropdown for selecting a label
    label_combobox = ttk.Combobox(mass_edit_frame, values=labels)  # Add to mass_edit_frame
    label_combobox.pack()

    # Editable text box for new value
    mass_edit_text_box = tk.Entry(mass_edit_frame)  # Add to mass_edit_frame
    mass_edit_text_box.pack()

    # Save button
    save_button = tk.Button(mass_edit_frame, text="Apply", command=save_mass_edit)  # Add to mass_edit_frame
    save_button.pack()

# Function to export all entries to an OpenKH compatible YML file, does not overwrite the origional file
def export_as_yaml():
    try:
        entry_index = entry_combobox.current()
        # Update the current entry in the entries list with data from text boxes, if an entry is selected
        if entry_index >= 0:
            new_entry_data = []
            for i, text_box in enumerate(text_boxes):
                value = text_box.get()
                if i == 0:  # ID is an unsigned short
                    new_entry_data.append(int(value))
                elif 10 <= i <= 16:  # Last seven values are signed shorts
                    new_entry_data.append(int(value))
                else:  # Assuming the rest are unsigned bytes
                    new_entry_data.append(int(value))

            entries[entry_index] = tuple(new_entry_data)

        # Export the data to a dictionary with the correct name and formatting
        yaml_data = []
        for entry in entries:
            entry_dict = {
            "Id": entry[0],
            "SmallHpOrbs": entry[1],
            "BigHpOrbs": entry[2],
            "BigMoneyOrbs": entry[3],
            "MediumMoneyOrbs": entry[4],
            "SmallMoneyOrbs": entry[5],
            "SmallMpOrbs": entry[6],
            "BigMpOrbs": entry[7],
            "SmallDriveOrbs": entry[8],
            "BigDriveOrbs": entry[9],
            "Item1": entry[11],
            "Item1Percentage": entry[12],
            "Item2": entry[13],
            "Item2Percentage": entry[14],
            "Item3": entry[15],
            "Item3Percentage": entry[16]
        }
            yaml_data.append(entry_dict)

        # Write the YML data to a file
        with open('przt.yml', 'w') as file:
            yaml.dump(yaml_data, file, sort_keys=False)

        print("Data exported as YAML.")
    except ValueError:
        print("Error: One or more fields contain non-integer values.")
    except Exception as e:
        print(f"An error occurred: {e}")


# Tkinter GUI setup
root = tk.Tk()
root.title("PRZT File Editor")

# Set the window icon
root.iconbitmap('loot.ico')  # Replace with the path to your icon file

# Create a frame with padding
main_frame = tk.Frame(root, padx=10, pady=10)  # Padding of 10 pixels
main_frame.pack(fill=tk.BOTH, expand=True)  # Fill and expand within the root window

# Dropdown for selecting an entry
entry_combobox = ttk.Combobox(main_frame, values=[f"Entry {i + 1}" for i in range(len(entries))])
entry_combobox.pack()
entry_combobox.bind("<<ComboboxSelected>>", update_text_boxes)

# Labels and text boxes for entry fields
labels = ["ID", "Small HP Orbs", "Big HP Orbs", "Big Money Orbs", "Medium Money Orbs", "Small Money Orbs", 
          "Small MP Orbs", "Big MP Orbs", "Small Drive Orbs", "Big Drive Orbs", "Padding", 
          "Item 1", "Item 1 Drop Percentage", "Item 2", "Item 2 Drop Percentage", 
          "Item 3", "Item 3 Drop Percentage"]

text_boxes = []
for label in labels:
    tk.Label(main_frame, text=label).pack()  # Add to main_frame
    text_box = tk.Entry(main_frame)  # Add to main_frame
    text_box.pack()
    text_boxes.append(text_box)
    
# Creating a menu bar
menubar = tk.Menu(root)
root.config(menu=menubar)

# Add a File menu
file_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="File", menu=file_menu)

# Add 'Save Changes' menu option to File menu
file_menu.add_command(label="Save", command=on_save_changes)

# Add 'Export as YML' menu option to File menu
file_menu.add_command(label="Export as YML", command=export_as_yaml)

# Add an Edit menu
edit_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="Edit", menu=edit_menu)

# Add 'Mass Edit' menu option to Edit menu
edit_menu.add_command(label="Mass Edit", command=mass_edit_window)


root.mainloop()