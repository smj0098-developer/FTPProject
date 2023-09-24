import datetime
import os
import socket
from colorama import Fore

# the code below is used for encryption
def encrypt(data):
    return data[::-1]
# encryption finished
# the code below is used for decryption
def decrypt(data):
    return data[::-1]
# decryption finished

def authenticate(password, client_socket) -> bool:
    if password == "123456":
        response = "correct"
        # send 'correct' to the client, so that they know they have been authorized
        client_socket.sendall(encrypt(response).encode('ascii'))
        return True
    else:
        response = "incorrect"
        # send 'incorrect' to the client, so that they know they have not been authorized
        client_socket.sendall(encrypt(response).encode('ascii'))
        print(Fore.RED, "*the client has entered a wrong password*", Fore.RESET)
        return False

# whenever a true fetch command is received
# the infoSend function sends files' info to the client
def infoSend(thisFile):
    info = ""
    # file name with extension
    file_loc = os.path.basename("files/" + thisFile)
    # file name without extension
    filename = os.path.splitext(file_loc)[0] + os.path.splitext(file_loc)[1]
    info += "fileName: " + filename
    filestats = os.stat("files/" + thisFile)
    info += " | size: " + str(filestats.st_size) + " bytes"
    # file modification timestamp of a file
    m_time = os.path.getmtime("files/" + filename)
    # convert timestamp into DateTime object
    dt_m = datetime.datetime.fromtimestamp(m_time)
    # file creation timestamp in float
    c_time = os.path.getctime("files/" + filename)
    # convert creation timestamp into DateTime object
    dt_c = datetime.datetime.fromtimestamp(c_time)
    # if the file has never been modified, just print its creation time
    if m_time == c_time:
        info += " | file creation time: " + str(dt_c)
    else:
        info += " | file creation time: " + str(dt_c)
        info += " | last modification time: " + str(dt_m)

    return info


# the if below does not matter. It checks for the name of the file we are in.
if __name__ == '__main__':
    # Defining Socket
    host = '127.0.0.1'
    port = 8080
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    sock.listen()
    # Establishing Connections
    print('Initiating clients')

    conn = sock.accept()
    print('Connected with the client')

    # the serverSide code does not run further unless the auth variable is set to True
    auth = False
    while not auth:
        authData = decrypt(conn[0].recv(1024)).decode()
        # the authenticate function returns True if the user is authorized. Otherwise, false is returned.
        auth = authenticate(authData, conn[0])
    print(Fore.LIGHTGREEN_EX, "The user has been authenticated", Fore.RESET)

    while True:
        if auth:
            data = decrypt(conn[0].recv(1024)).decode()
            # check if the data received is not empty
            if len(data) != 0:
                listOfCommands = data.split(" ")

                # if the client wants to upload something and enters a true upload command pattern
                if listOfCommands[0] == "upload" and len(listOfCommands) == 2:
                    requestedFile = listOfCommands[1]
                    fileData = decrypt(conn[0].recv(1024))

                    with open("files/" + requestedFile, 'wb') as file:
                        file.write(fileData)
                    print(Fore.LIGHTGREEN_EX, f"File '{requestedFile}' uploaded successfully.", Fore.RESET)

                # if the client wants to download something and enters a true download command pattern
                elif listOfCommands[0] == "download" and len(listOfCommands) == 2:
                    requestedFile = listOfCommands[1]
                    try:
                        with open("files/" + requestedFile, 'rb') as file:
                            conn[0].send(bytes(encrypt("downloadConfirmed"), 'ascii'))
                            file_data = file.read()

                        # Send the file contents
                        conn[0].sendall(encrypt(file_data))
                        print(Fore.LIGHTGREEN_EX, "the file has been downloaded", Fore.RESET)

                    except FileNotFoundError:
                        conn[0].send(bytes(encrypt("downloadNotConfirmed"), 'ascii'))
                        print(Fore.RED, "*Download error: the file " +
                              requestedFile + " does not exist in the server", Fore.RESET)
                        continue

                # if the client wants to parallelize a file and the pattern for para command is true
                elif listOfCommands[0] == "para" and len(listOfCommands) == 2:
                    requestedFile = listOfCommands[1]
                    try:
                        with open("files/" + requestedFile, 'rb') as file:
                            conn[0].send(bytes(encrypt("SameFileHere"), 'ascii'))
                            fileData = decrypt(conn[0].recv(1024))
                            try:
                                with open("files/" + requestedFile, 'wb') as fileToParallelize:
                                    fileToParallelize.write(fileData)
                                    print(Fore.LIGHTGREEN_EX, "the file " + requestedFile + " has been parallelized",
                                          Fore.RESET)
                                    conn[0].send(bytes(encrypt("successfullyParallelized"), 'ascii'))
                            except FileNotFoundError:
                                print("could not write to file while paralleling")


                    except FileNotFoundError:
                        conn[0].send(bytes(encrypt("SameFileNotHere"), 'ascii'))

                # if the client wants to fetch information of files and the command pattern is true
                elif listOfCommands[0] == "fetch" and len(listOfCommands) == 1:
                    print("fetching files' info from the server ...")
                    listOfFiles = os.listdir('files')
                    conn[0].send(bytes(encrypt(str(len(listOfFiles))), 'ascii'))
                    for fileName in listOfFiles:
                        try:
                            conn[0].send(bytes(encrypt(infoSend(fileName)), 'ascii'))
                        except FileNotFoundError:
                            pass

                # if the command pattern entered by the client is false and does not match any valid command
                else:
                    print(Fore.RED, "invalid command: the client must pay attention to acceptable input patterns",
                          Fore.RESET)

            if data == "close":
                break

    # Closing all Connections
    conn[0].close()
    print("connection closed")
