import socketio
import threading

sio = socketio.Client()
game_id = "fd9a0d4f-39da-4c91-bfdc-252d9231658d"

def place_square(square):
    sio.emit("client_place_square", {"game_id": game_id, "square": square})

# Menghubungkan ke server
sio.connect('https://usc-tictactocket.chals.io')

# Mengirim permintaan bersamaan untuk kotak yang berbeda
threads = []
for square in [0, 1, 2]:  # Misalnya baris pertama
    t = threading.Thread(target=place_square, args=(square,))
    threads.append(t)
    t.start()

# Menunggu semua thread selesai
for t in threads:
    t.join()
