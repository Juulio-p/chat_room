import socket
from threading import Thread

JOIN_REJECT_FLAG =0
HISTORY_SIZE = 100
 #Want to limit the history size to avoid any weird behavior




# Create and Bind a TCP Server Socket
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host_name = socket.gethostname()
s_ip = socket.gethostbyname(host_name)
port = 18000
serverSocket.bind((host_name, port))

# Outputs Bound Contents
print("Socket Bound")
print("Server IP: ", s_ip, " Server Port:", port)



serverSocket.listen(10)

# Creates a set of clients
client_List = set()
client_usernames = {} #tracking the usernames 

len_client = len(client_List)
msgList = []

# Function to constantly listen for an client's incoming messages and sends them to the other clients
def clientWatch(cs):
    PAYLOAD =""
    adminFlag = 0
    newJoin =True
    while True:
        try:
            # Constantly listens for incoming message from a client
            msg = cs.recv(1024).decode()

            if newJoin == True:
                cs.send(("----------Chatlog----------\n").encode())
                for x in msgList:
                    cs.send((x + "\n").encode())
                cs.send(("\n----------EndLog----------\n").encode())

            if msg == "1":
                #Want this format 1. Cool at IP: 192.168.1.5 and port: 3546543.
                client_List.remove(cs)
                NUMBER =  len(client_List)
                if NUMBER <= 0:
                    PAYLOAD ="" # No users the payload is empty
                else:
                    PAYLOAD = f"There are {NUMBER} active users in the chatroom:\n"
                    for i, client in enumerate(client_List): # so we dont count current ip
                        client_ip, client_port = client.getpeername()  # Get IP and port of the client
                        PAYLOAD += f"{i + 1}. Client at IP: {client_ip} and port: {client_port}\n"
                cs.send(PAYLOAD.encode()) # this sends it to the client
                print("Displaying chatroom stats")
                break
            elif msg.startswith("1,"):  # now for our second condition
                parts = msg.split(",", 1)  # Split the flag and username
                user_name = parts[1]
                NUMBER =  len(client_List)
                if NUMBER >= 4: 
                    JOIN_REJECT_FLAG =1
                    PAYLOAD = "Too many User, goodbye"
                    cs.send(PAYLOAD.encode())
                    print("Client Disconnected")
                    client_List.remove(cs)
                elif user_name in client_usernames.values():
                    PAYLOAD= "The server rejects the join request. Another user is using this username." 
                else:
                    newJoin = False
                    client_usernames[cs] = user_name 
                    client_List.add(cs)  
                    PAYLOAD = f"Welcome {user_name}! You have joined the chat."
                cs.send(PAYLOAD.encode())  
                continue            
            
            # if user enters admin as user name set admin Flag to 1, let server and client know admin connected
            if msg == "admin":
                adminFlag = 1
                print("Admin Connected")
                adminMsg = "Type 'viewall' to view all recorded messages"
                cs.send(adminMsg.encode())

                continue
            # if q is entered remove the client from the client list and close connection
            if msg == "q":
                print("Client Disconnected")
                client_List.remove(cs)
                len_client = len_client-1 
                cs.close()
                break

            if msg == "a":
                with open(dest, 'wb') as file:  # Open destination file in binary write mode
                    while True:
                        data = cs.recv(1024)
                        if data == b"END_OF_FILE":  # Check for the end-of-file marker
                            break
                    file.write(data)  # Write the received chunk to the file
                print("File received successfully.")
                



        except Exception as e:
            print("Error")
            client_List.remove(cs)

        # splits of last word of message (due to username and time being sent)
        newMsg = msg.split()
        # print(newMsg[-1])
        # checks if user is an admin and has entered 'viewall', sends messageList to the admin client
        if adminFlag and newMsg[-1] == "viewall":
            print("Admin Accessed Chat Log")
            cs.send(("----------Chatlog----------").encode())
            for x in msgList:
                # print(x)
                cs.send((x + "\n").encode())

            cs.send(("\n----------EndLog----------").encode())
            continue

        # Iterates through clients and sends the message to all connected clients
        msgList.append(msg)
        for client_socket in client_List:
            client_socket.send(msg.encode())

while True:
    # Continues to listen / accept new clients
   
    client_socket, client_address = serverSocket.accept()
    print(client_address, "Connected!")
    # Adds the client's socket to the client set
    client_List.add(client_socket)
    newJoin = False



    # Create a thread that listens for each client's messages
    t = Thread(target=clientWatch, args=(client_socket,))

    # Make a daemon so thread ends when main thread ends
    t.daemon = True

    t.start()

# Close out clients
for cs in client_List:
    cs.close()
# Close socket
s.close()
