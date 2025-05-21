import socket, os
from threading import Thread
from datetime import datetime

#implemented variables
JOIN_REQUEST_FLAG=0
REPORT_REQUEST_FLAG=0 # number of users in chat, should be from 0-3
# Sets the preselected IP and port for the chat server
# Eneter your machine's IP address for the host_name. Alternatively, you can enter "localhost"
host_name = "192.168.0.31" 
port = 18000

# Creates the TCP socket
new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("Connecting to", host_name, port, "...")
new_socket.connect((host_name, port))
print("Connected.")


# Prompts the client for a username
print("Type lowercase 'q' at anytime to quit!")
selected_option = input( "Please select one of the following options:\n1. Get a report of the chatroom from the server.\n2. Request to join the chatroom.\n3. Quit the program.\n ")

if selected_option == "1":
    REPORT_REQUEST_FLAG = 1
    new_socket.send(f"{REPORT_REQUEST_FLAG}".encode())
    name=""


elif selected_option == "2":
    JOIN_REQUEST_FLAG = 1
    while True:
        name = input("Enter your username: ")
        msg = f"{JOIN_REQUEST_FLAG},{name}"
        new_socket.send(msg.encode())
        # Wait for a response from the server
        messageback = new_socket.recv(1024).decode()
        # Check if the server rejected the username
        if "The server rejects the join request" in messageback:
            print(messageback)  # Print the rejection message once
        else:
            print("welcome to the chat!")
            break

elif selected_option == "3":
    exit()


# Thread to listen for messages from the server
def listen_for_messages():
    while True:
        message = new_socket.recv(1024).decode()
        print("\n" + message)


t = Thread(target=listen_for_messages)

t.daemon = True

t.start()

# if user is an admin send the admin name before appending time and username
if name == "admin":
    print("Welcome Administrator")
    new_socket.send(name.encode())

while True:
    # Recieves input from the user for a message
    to_send = input()

    # Allows the user to exit the chat room
    if to_send.lower() == "q":
        new_socket.send(to_send.encode())
        exit()

    if to_send.lower() =="a":
        new_socket.send(to_send.encode())
        file_location= input("Please enter a file path, where the file is located:")
        with open(file_location, 'rb') as file:  # Open the file in binary mode
            while chunk := file.read(1024):
                new_socket.send(chunk)
        new_socket.send(b"END_OF_FILE")
        print("File sent successfully.")
        
        file = open(file_location,'r')
        text = file.read()
        print(text)
        new_socket.send(file.encode()) # sending file to server

        #want to add this result = os.path.exists("file_name") #giving the name of the file as a parameter.




    # Appends the username and time to the clients message
    to_send = name + ": " + to_send
    date_now = datetime.now().strftime("[%H:%M] ")
    to_send = date_now + to_send

    # Sends the message to the server
    new_socket.send(to_send.encode())

# close the socket
new_socket.close()
