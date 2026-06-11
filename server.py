import socket
from _thread import start_new_thread

server = "localhost"
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    print(str(e))

s.listen(2)
print("Server Started, Waiting for a connection...")

latest_move = "No moves yet"

def threaded_client(conn, player):
    global latest_move
    # Send identity string down to the client on handshake
    conn.send(str.encode(player))
    
    while True:
        try:
            data = conn.recv(2048).decode("utf-8")
            if not data:
                print(f"{player} disconnected.")
                break
                
            if data == "GET":
                reply = latest_move
            else:
                print(f"Broadcast: {player} -> {data}")
                latest_move = data
                reply = f"Acknowledged {player}"
                
            conn.sendall(str.encode(reply))
        except Exception as e:
            print(f"Error handling {player}: {e}")
            break

    print(f"Lost connection from {player}")
    conn.close()

player_count = 0
while True:
    conn, addr = s.accept()
    print("Connected to:", addr)
    
    if player_count == 0:
        p = "Player 1"
        player_count += 1
    else:
        p = "Player 2"
        player_count = 0
        
    start_new_thread(threaded_client, (conn, p))