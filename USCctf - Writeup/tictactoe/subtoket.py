import socketio
import time

sio = socketio.Client()

SERVER_URL = "https://usc-tictacbingo.chals.io"  # Ganti dengan URL server sebenarnya

game_id = None  # Ganti dengan game_id yang sebenarnya

@sio.event
def connect():
    print("Terhubung ke server")
    # Mengirim event untuk memulai permainan baru
    sio.emit('client_new_game')

@sio.on('server_new_game')
def on_new_game(data):
    global game_id
    print(f'data dari server_new_game: {data}')
    game_id = data['game_id']
    print(f"Permainan baru dimulai dengan ID: {game_id}")
    print("Menunggu giliran Anda untuk memulai...")
    send_forced_win()

def send_forced_win():
    winning_squares = [6, 7, 8, 0, 1, 2, 3, 5, 4]
    
    for square in winning_squares:
        sio.emit('client_place_square', {
            'game_id': game_id,
            'square': square
        })
        print(f"Sent move for square {square}")
        time.sleep(0)  # Jeda singkat untuk menghindari pengiriman terlalu cepat

    print("Forced winning moves sent to the server.")

@sio.on('server_board_update')
def on_board_update(data):
    # Menampilkan status papan
    board = ["X" if x == 0 else "O" if x == 1 else " " for x in data['board']]
    for i in range(0, 9, 3):
        print(f"{board[i]} | {board[i+1]} | {board[i+2]}")
    
    if data['winner'] == 0:
        print(f"Flag: {data['flag']}")
        print("Anda menang! Mungkin Anda mendapatkan flag.")
    elif data['winner'] == 1:
        print("Anda kalah...")
    elif data['winner'] == 3:
        print("Permainan seri.")
    elif data['turn'] == 0:  # Giliran pemain
        print("Giliran Anda")

@sio.event
def disconnect():
    print("Terputus dari server")

@sio.event
def connect_error():
    print("Koneksi gagal!")

sio.connect(SERVER_URL, wait_timeout=10)

sio.wait()
