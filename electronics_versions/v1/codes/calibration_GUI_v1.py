#
# Calibration GUI for Bach-o-mat electronics v1
#
# GitHub repository:
# https://github.com/Hruodbhert/Bach-o-mat/
#
# Authors: Giulio and Roberto Faure Ragani
#
# A.D. 2025
#

from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import serial
from serial.tools import list_ports



def resize_viewport(event):
    # Set viewport2 size in order to fit the dimensions of canvas2
    new_width = event.width
    new_height = event.height
    canvas2.itemconfig(canvas_window, width=new_width, height=new_height)

def only_numbers(char):
    return char.isdigit()

def is_white(n):
    return 0 if n % 12 in {2, 4, 7, 9, 11} else 1
    
def note_name(n):
    return notes[n%12] + " " + str((n//12)+1) # The first octave of the organ is number 1 following italian rules, while it is 2 following english rules (so change the +1 in +2 depending on the convention you want to use)

class DitoClass:
    def __init__(self, i, parent):
        self.i = i  # Servo number
        self.state = 0  # Servo default state: 0 = not pressing the key
        self.bg = "white" if is_white(i + 1) else "black"
        self.fg = "black" if is_white(i + 1) else "white"
        
        self.frame = Frame(parent, bg=self.bg, padx=10, pady=10)
        
        self.frame.grid(row=is_white(self.i+1), column=self.i, padx=5, pady=5)

        Label(self.frame, text="Servo " + str(self.i+1), bg=self.bg, fg=self.fg).grid(row=0, column=0, columnspan=3, pady=5)
        Label(self.frame, text=note_name(self.i), bg=self.bg, fg=self.fg).grid(row=1, column=0, columnspan=3, pady=5)

        self.off_angle_txt = Entry(self.frame, validate='key', validatecommand=vcmd, width=9)
        self.off_angle_txt.insert(0, "0")
        self.delta_angle_txt = Entry(self.frame, validate='key', validatecommand=vcmd, width=9)
        self.delta_angle_txt.insert(0, "0")
        
        Label(self.frame, text="Off Angle", bg=self.bg, fg=self.fg).grid(row=2, column=0, columnspan=3)
        
        Button(self.frame, text="-", command=lambda: self.update_value(self.off_angle_txt, -1)).grid(row=3, column=0)
        self.off_angle_txt.grid(row=3, column=1)
        Button(self.frame, text="+", command=lambda: self.update_value(self.off_angle_txt, 1)).grid(row=3, column=2)
        
        Label(self.frame, text="Delta Angle", bg=self.bg, fg=self.fg).grid(row=4, column=0, columnspan=3)
        
        Button(self.frame, text="-", command=lambda: self.update_value(self.delta_angle_txt, -1)).grid(row=5, column=0)
        self.delta_angle_txt.grid(row=5, column=1)
        Button(self.frame, text="+", command=lambda: self.update_value(self.delta_angle_txt, 1)).grid(row=5, column=2)
        
        self.press_button = Button(self.frame, text="Premi", command=self.set_state)
        self.press_button.grid(row=6, column=0, columnspan=3, pady=5)
        
        Button(self.frame, text="Applica", command=lambda: self.set_angles()).grid(row=7, column=0, columnspan=3, pady=5)
        Button(self.frame, text="Applica e Salva", command=lambda: self.save_angles()).grid(row=8, column=0, columnspan=3, pady=5)
        
        servo_entries.append((self.off_angle_txt, self.delta_angle_txt))
        
    def set_state(self):
        self.state = not self.state  # Changes the state
        button_text = "Rilascia" if self.state else "Premi"
        self.press_button.config(text=button_text)  # Updates the text on the button
        
        # Send the command
        serial_send_data(1, self.i, self.state)
    
    def set_angles(self):
        serial_send_data(2, self.i, int(self.off_angle_txt.get()), int(self.delta_angle_txt.get()))
    
    def save_angles(self):
        serial_send_data(3, self.i, int(self.off_angle_txt.get()), int(self.delta_angle_txt.get()))

    def update_value(self, entry, delta):
        current_value = entry.get()
        if current_value == "":
            current_value = "0"
        new_value = max(0, int(current_value) + delta)
        entry.delete(0, END)
        entry.insert(0, str(new_value))

class CommandMenuClass:
    def __init__(self, parent): 
        self.bg = "white"
        self.fg = "black"
        self.frame = Frame(parent, bg=self.bg, padx=10, pady=10)
        self.frame.grid(row=0, column=1, sticky="nsew", pady=20)
        
        Label(self.frame, text="Comandi generali", bg=self.bg, fg=self.fg).grid(row=0, column=0, columnspan=4, pady=5)
        Label(self.frame, text="Off Angles", bg=self.bg, fg=self.fg).grid(row=1, column=0, columnspan=4, pady=5)
        Label(self.frame, text="Delta Angles", bg=self.bg, fg=self.fg).grid(row=5, column=0, columnspan=4, pady=5)
        
        # Angles' buttons
        button_config = [
            ("Off Angles", 2, "off_angles"),
            ("Delta Angles", 6, "delta_angles")
        ]
        for label, start_row, angle_type in button_config:
            for i, val in enumerate([-10, -1, +1, +10]):
                Button(self.frame, text=str(val), command=lambda v=val, a=angle_type: update_all_values(a, v, "all")).grid(row=start_row, column=i)
                Button(self.frame, text=str(val), bg="black", fg="white", command=lambda v=val, a=angle_type: update_all_values(a, v, "black")).grid(row=start_row+1, column=i)
                Button(self.frame, text=str(val), bg="white", fg="black", command=lambda v=val, a=angle_type: update_all_values(a, v, "white")).grid(row=start_row+2, column=i)
        #
        
        # "Apply" and "Apply ad Save" buttons
        Button(self.frame, text="Applica", command=set_all_angles).grid(row=9, column=0, columnspan=4, pady=15)
        Button(self.frame, text="Applica e Salva", command=save_all_angles).grid(row=10, column=0, columnspan=4, pady=5)
        
        # Create and place the ComboBox to choose the serial port
        self.serial_port_cb = ttk.Combobox(self.frame, width=30)
        self.serial_port_cb.grid(row=11, column=0, columnspan=4, pady=5)
        self.serial_port_cb.bind('<<ComboboxSelected>>', self.connect_to_selected_serial_port)
        
        Button(self.frame, text="Aggiorna Porte Seriali", command=self.update_serial_ports).grid(row=12, column=0, columnspan=4, pady=5)
        
        self.update_serial_ports()
        self.connect_to_selected_serial_port()
        
    def update_serial_ports(self):
        ports = [port.device for port in list_ports.comports()]
        self.serial_port_cb['values'] = ports
        if ports:
            self.serial_port_cb.current(0)  # selection, by default, of the first available port
        else:
            self.serial_port_cb.set('Nessuna porta trovata')

    def connect_to_selected_serial_port(self, event=None):
        selected_port = self.serial_port_cb.get()
        try:
            global ser
            ser = serial.Serial(selected_port, 9600)
            print(f"Connesso a {selected_port}")
        except Exception as e:
            print(f"Errore nella connessione a {selected_port}: {e}")
    
def serial_send_data(operation, servo_num, data_1, data_2=None):
    #
    # Send data to servo motors through serial communication
    #
    # Args:
        # operation (int):
            # 1 -> push/release the key
            # 2 -> apply angles
            # 3 -> apply and save angles
        # servo_num (int): number of the servo (first servo has number 0)
        # data_1 (int):
            # for operation=1
                # 1 -> push
                # 0 -> release
            # in the other cases data_1 is off_angle
        # data_2 (int, optional): delta_angle
    
    try:
        operation_bytes = operation.to_bytes(1, 'big')
        servo_num_bytes = servo_num.to_bytes(1, 'big')
        data_1_bytes = data_1.to_bytes(1, 'big')

        # Message building
        message = operation_bytes + servo_num_bytes + data_1_bytes

        if data_2 is not None:
            data_2_bytes = data_2.to_bytes(1, 'big')
            message += data_2_bytes

        # Send
        ser.write(message)

    except serial.SerialException as e:
        print(f"Errore nell'invio dei dati: {e}")
    except ValueError as e:
        print(f"Errore nella conversione dei dati in byte: {e}")

def update_all_values(selected_entry, delta, colour):
    for el in servo:
        if colour == "all" or (is_white(el.i + 1) and colour == "white") or (not(is_white(el.i + 1)) and colour == "black"):
            if selected_entry == "off_angles":
                el.update_value(el.off_angle_txt, delta)
            else:
                el.update_value(el.delta_angle_txt, delta)

def set_all_angles():
    for el in servo:
        el.set_angles()

def save_all_angles():
    for el in servo:
        el.save_angles()

def save_entries():
    filepath = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if not filepath:
        return
    with open(filepath, "w") as file:
        for off_angle_entry, delta_angle_entry in servo_entries:
            file.write(off_angle_entry.get() + ", " + delta_angle_entry.get() + "\n")

def load_entries():
    filepath = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if not filepath:
        return
    with open(filepath, "r") as file:
        for line, (off_angle_entry, delta_angle_entry) in zip(file, servo_entries):
            off_angle, delta_angle = line.strip().split(", ")
            off_angle_entry.delete(0, END)
            off_angle_entry.insert(0, off_angle)
            delta_angle_entry.delete(0, END)
            delta_angle_entry.insert(0, delta_angle)

def on_frame_configure(event=None):
    canvas1.configure(scrollregion=canvas1.bbox("all"))


root = Tk()
root.title("Calibrazione Organista elettromeccanico")
vcmd = (root.register(only_numbers), '%S')

servo_entries = []

notes = ["Do", "Do#", "Re", "Re#", "Mi", "Fa", "Fa#", "Sol", "Sol#", "La", "La#", "Si"] # Versione in italiano
# notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]             # English version

# Create a PanedWindow with vertical alignment
paned_window = PanedWindow(root, orient=VERTICAL, sashrelief=RAISED, sashwidth=6)
paned_window.pack(fill=BOTH, expand=True)

# First canvas and its container
frame1 = Frame(paned_window)  # Container for the first canvas and its scrollbar
canvas1 = Canvas(frame1, bg="lightgrey")
scrollbar1 = Scrollbar(frame1, orient="horizontal", command=canvas1.xview)
canvas1.configure(xscrollcommand=scrollbar1.set)
canvas1.pack(side="top", fill="both", expand=True)
scrollbar1.pack(side="bottom", fill="x")
paned_window.add(frame1, stretch="always")

viewport1 = Frame(canvas1, bg="lightgrey")
canvas_window = canvas1.create_window((0, 0), window=viewport1, anchor="nw")

# Second canvas and its container
frame2 = Frame(paned_window)  # Container for the second canvas and its scrollbar
canvas2 = Canvas(frame2, bg="lightgrey")
canvas2.pack(side="bottom", fill="both", expand=True)
paned_window.add(frame2, stretch="never")

viewport2 = Frame(canvas2, bg="lightgrey")
canvas_window = canvas2.create_window((0, 0), window=viewport2, anchor="nw")

# Setting the "spacer" columns around the central frame for the control panel
viewport2.grid_columnconfigure(0, weight=1)
viewport2.grid_columnconfigure(2, weight=1)

viewport1.bind("<Configure>", on_frame_configure)
canvas2.bind("<Configure>", resize_viewport)  # Updates viewport2 size when canvas2 is resized


menubar = Menu(root)
root.config(menu=menubar)
file_menu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Salva", command=save_entries)
file_menu.add_command(label="Carica", command=load_entries)

servo = [DitoClass(i, viewport1) for i in range(58)]
commandmenu = CommandMenuClass(viewport2)

root.mainloop()