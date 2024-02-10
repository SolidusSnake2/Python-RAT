# Python-RAT (ALPHA V. 1.0)

Warning! This software is for educational purposes only.

User guide:

[1] Commands list:

    $dir [directory path]                   get file list in a directory
    
    $run [file path]                        start file on the target system

    $del [file path]                        remove a file from the target system

    $shutdown [mode]                        mode 1 = full shutdown , mode 2 = restart

    $changetarget [local directory path]    sets a local directory in which downloaded files will be stored

    $get [file path]                        downloads a file on the target system

    $send [local file path]                 sends a file from the local system to the target system's Temp folder

    $change_client [client_ID]              changes the target system

    $getip                                  prints the Local and public ip of the target system

    $netstat                                creates and opens a txt file with the netstat content of the target system

    $blockmouse                             block the target system's mouse cursor

    $unblockmouse                           unblocks the mouse of the target system

    $blockkeyboard                          block the target system's keyboard input

    $startkeylogger {ALPHA}                 starts the keylogger function

    $stopkeylogger                          blocks the keylogger function and prints out the logs

    $startstream                            starts the screenshare of the target system's screen

    $startcamera                            starts the webcam of the target system

    $startmic                               listens to the target system's mic

    $stopmic                                stops listening to the target system's mic

    $soundboard                             starts the soundboard that will play any mp3  and ogg files on the target system, any file  

    can be imported by putting it into the Soundboard folder in the server modules folder

    $clients                                displays a list of connected clients (The number in bracket's is the corresponding ID)



...
