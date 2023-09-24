import socket
from colorama import Fore
import os

# the code below is used for encryption
def encrypt(data):
    return data[::-1]
# encryption finished
# the code below is used for decryption
def decrypt(data):
    return data[::-1]
# decryption finished


# Creating Client Socket
if __name__ == '__main__':
    host = '127.0.0.1'
    port = 8080

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connecting with Server
    sock.connect((host, port))
    print("you can ask for some information about a list of files in the server: write 'fetch' to do so")
    print("you can parallelize a file with the server: write 'para' + file's name")
    print("you can upload a file to the server: write 'upload' file's name")
    print("you can download a file from the server: write 'download' file's name\n")
    print("but before anything, you must write your password\n")

# auth is set to False in order to prevent the client to use the system unless they are authorized
    auth = False
    while True:

        msg = input('now, write your message :').strip()
        try:
            # split the command into pieces
            listOfCommands = msg.split(" ")
            if auth:
                # if the client wants to upload something and enters a true upload command pattern
                if listOfCommands[0] == "upload" and len(listOfCommands) == 2:
                    requestedFile = listOfCommands[1]

                    try:
                        with open("files/"+requestedFile, 'rb') as file:
                            sock.send(bytes(encrypt(msg), 'ascii'))
                            file_data = file.read()
                        # Send the file contents
                        sock.sendall(encrypt(file_data))

                    except FileNotFoundError:
                        print(Fore.RED, "*no such file exists*", Fore.RESET)
                        continue
                # if the client wants to upload something but the pattern for upload command is wrong
                elif listOfCommands[0] == "upload":
                    print(Fore.RED, "this is not a true upload command", Fore.RESET)
                # end of upload phase
                # download phase start
                # if the client wants to download something and enters a true download command pattern
                elif listOfCommands[0] == "download" and len(listOfCommands)==2:
                    sock.send(bytes(encrypt(msg), 'ascii'))
                    response = decrypt(sock.recv(1024)).decode('ascii')
                    if response=="downloadConfirmed":
                        downloadedFileData = decrypt(sock.recv(1024))
                        with open("files/"+listOfCommands[1], 'wb') as file:
                            file.write(downloadedFileData)
                        print(Fore.LIGHTGREEN_EX,"the file has been downloaded",Fore.RESET)
                    elif response=="downloadNotConfirmed":

                        print(Fore.RED,"could not download the file",Fore.RESET)
                        print(Fore.RED,"the file does not exist to be downloaded",Fore.RESET)
                # if the client wants to download something but the pattern for download command is wrong
                elif listOfCommands[0] == "download":
                    print(Fore.RED, "this is not a true download command", Fore.RESET)
                # end of download phase
                # start of parallelization phase
                # if the client wants to parallelize a file and the pattern for para command is true
                elif listOfCommands[0] == "para" and len(listOfCommands)==2:
                    haveFile = False
                    try:
                        with open("files/" + listOfCommands[1], 'rb') as file:
                            pass
                        haveFile = True
                    except FileNotFoundError:
                        haveFile = False
                        print(Fore.RED, "could not find the file in clientSide to parallelize", Fore.RESET)
                    if haveFile:
                        sock.send(bytes(encrypt("para "+listOfCommands[1]),'ascii'))
                        paraResponse = decrypt(sock.recv(1024)).decode()
                        if paraResponse=="SameFileHere":
                            try:
                                with open("files/" + listOfCommands[1], 'rb') as file:
                                    file_data = file.read()
                                    sock.sendall(encrypt(file_data))
                                    paraOrNot = decrypt(sock.recv(1024)).decode()
                                    if paraOrNot=="successfullyParallelized":
                                        print(Fore.LIGHTGREEN_EX, "the file has been parallelized",
                                              Fore.RESET)
                            except FileNotFoundError:
                                pass
                                # this error has already been taken care of

                        elif paraResponse=="SameFileNotHere":
                            print(Fore.RED,"the server does not have this file",Fore.RESET)
                # if the client wants to parallelize a file but the pattern for para command is False
                elif listOfCommands[0] == "para":
                    print(Fore.RED, "this is not a true parallelization command", Fore.RESET)
                # end of parallelization phase
                elif listOfCommands[0] == "fetch" and len(listOfCommands)==1:
                    print("-------------------------------------------")
                    print("fetching files' info from the server ...")
                    sock.send(bytes(encrypt("fetch"),'ascii'))
                    fetchResponse = decrypt(sock.recv(1024)).decode('ascii')
                    for fileNumber in range(int(fetchResponse)):
                        fetchedFile = decrypt(sock.recv(1024)).decode('ascii')
                        print(fetchedFile)
                    print("-------------------------------------------")
                else:
                    sock.send(bytes(encrypt(msg), 'ascii'))


# the else below sends data until authentication is done
            else:
                sock.send(bytes(encrypt(msg), 'ascii'))
                response = decrypt(sock.recv(1024)).decode('ascii')
                if response == "incorrect":
                    print(Fore.RED, "not a valid password", Fore.RESET)

                elif response == "correct":
                    auth = True
                    print(Fore.LIGHTGREEN_EX, "you are connected to the server", Fore.RESET)

        except IOError:
            print("connection missed")
            break
