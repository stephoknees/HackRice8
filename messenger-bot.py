# Python libraries that we need to import for our bot
from flask import Flask, request
from pymessenger.bot import Bot  # pymessenger is a Python wrapper for the Facebook Messenger API
import json
import random
import re

app = Flask(__name__)  # This is how we create an instance of the Flask class for our app

word = re.compile('[a-z]+\s*?[a-z]+')
digit = re.compile('[0-8]')

ACCESS_TOKEN = 'EAAEya8OM1ZAkBAKR35lXGw9NaJgLYvvDvpjZAn91Lkmx1Yl8nSKhg8t0JwXNLdC1YqnQN3DtNz5c1uHSi15A1JprsorCZCCbv9O' \
               'tyeWqv0we43oQvZBZB2BOtwKXJdyl9o7HFwSIyf6W6sRf482lM6B1ssEt5zi4bdg5j6aLIYnsLPMs0lwOd'
VERIFY_TOKEN = 'TESTINGTOKEN'  # Replace 'VERIFY_TOKEN' with your verify token
bot = Bot(ACCESS_TOKEN)  # Create an instance of the bot
board = [['.  ', '|', '  ', '|', '  '], ['---', '---', '---'], ['  ', '|', '', '|', '  '],
         ['---', '---', '---'], ['  ', '|', '  ', '|', '  ']]
pieces = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']
first_move = True
rID = ''
rem_pieces = [0, 1, 2, 3, 4, 5, 6, 7, 8]
rem_corner_pieces = [0, 2, 6, 8]
move_count = 0
insertUser = False
win = 'none'


def verify_fb_token(token_sent):
    # Verifies that the token sent by Facebook matches the token sent locally
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Verification not authorized'


# Send text message to recipient
def send_message(recipient_id, response):
    bot.send_text_message(recipient_id, response)  # Sends the 'response' parameter to the user
    return "Message sent"


# This endpoint will receive messages 
@app.route("/", methods=['GET', 'POST'])
def receive_message():
    global rID
    global first_move
    # Handle GET requests
    if request.method == 'GET':
        token_sent = request.args.get("hub.verify_token")  # Facebook requires a verify token when receiving messages
        return verify_fb_token(token_sent)

    # Handle POST requests
    else:
        output = request.get_json()  # get whatever message a user sent the bot
        for event in output['entry']:
            messaging = event['messaging']
            for message in messaging:
                if 'message' in message:
                    recipient_id = message['sender']['id']
                    # Facebook Messenger ID for user so we know where to send response back to
                    rID = recipient_id
                    if word.match(message['message'].get('text').lower()):
                        if "play" in message['message'].get('text').lower():
                            if first_move:
                                send_message(recipient_id, "Type in a number between 0 to 8 (You are 'O').")
                            else:
                                send_message(recipient_id, "A game is in progress. Please type 'new game' to restart.")
                        elif "new game" in message['message'].get('text').lower():
                            initTicTacToe()
                            first_move = True
                            send_message(recipient_id, "New game initialized. Please type play.")
                        else:
                            send_message(recipient_id, "Invalid input. Please enter a number "
                                                       "from 0 to 8 or a valid command [play, new game]")
                    elif message['message'].get('text').isdigit() and digit.match(message['message'].get('text')):
                        if first_move:
                            first_move = False
                            initTicTacToe()
                        send_message(rID, insert_piece((message['message'].get('text')), "User"))
                        checkWinner()
                        if win == 'X':
                            send_message(recipient_id, 'I win!')
                        else:
                            insert_comp_piece()
                            if move_count < 9:
                                send_message(recipient_id, 'Please enter your next move.')
                        checkWinner()
                        if win == 'O':
                            send_message(recipient_id, 'You win!')
                        print_board()
                    else:
                        send_message(recipient_id, 'Invalid input. Please enter a digit or a valid command')

    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


def initTicTacToe():
    global board
    global pieces
    global rem_pieces
    global rem_corner_pieces
    global move_count

    rem_pieces = [0, 1, 2, 3, 4, 5, 6, 7, 8]
    rem_corner_pieces = [0, 2, 6, 8]
    move_count = 0
    board = [['  ', '|', '  ', '|', '  '], ['---', '---', '---'], ['  ', '|', '  ', '|', '  '],
             ['---', '---', '---'], ['  ', '|', '  ', '|', '  ']]
    pieces = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']


def insert_piece(piece, player):
    """
    Inserts a piece into the existing board.

    Param: board -> Existing board.
           pieces -> A user/computer entered string, indicated by "Row Column"
                    So "3 2" would be an piece inserted onto the 3rd row, 2nd column

           player -> An indicator for the player. "Comp" would be computer,
                     "Player" would be the human player.

    Return: None. Just updates the pieces array.
    """

    global insertUser
    global rem_pieces
    global move_count

    if int(piece) not in rem_pieces:
        insertUser = False
        return_str = "Sorry, this spot is already taken. Please try again."

    # determine which piece, X or O to insert
    else:
        if player == "Comp":
            pieceNum = 'X'
        else:
            pieceNum = 'O'
            insertUser = True

        # The row, column number
        pieceRow = 2 * (int(piece) // 3)
        pieceCol = 2 * (int(piece) % 3)

        # update the board now
        board[pieceRow][pieceCol] = pieceNum

        # update the list of pieces currently on board
        pieces[int(piece)] = pieceNum

        if int(piece) in rem_pieces:
            rem_pieces.remove(int(piece))
        if int(piece) in rem_corner_pieces:
            rem_corner_pieces.remove(int(piece))
        move_count += 1
        return_str = str(player) + " placed a piece in position at " + str(piece)
    return return_str


# separate function for when the computer inserts a piece - it calls the insert piece function above
def insert_comp_piece():
    global move_count
    if insertUser and move_count != 9:
        if move_count < 4:
            send_message(rID, insert_piece(str(random.choice(rem_corner_pieces)), "Comp"))
        else:
            send_message(rID, insert_piece(str(random.choice(rem_pieces)), "Comp"))


# print board function returns a string of what board looks like after insertion
def print_board():
    newboard = "."
    for i in range(len(board)):
        for j in board[i]:
            newboard += j
        newboard += '\n'
    send_message(rID, newboard)


#  method for determining who won
def checkWinner():
    global win
    if (pieces[0] == pieces[1]) and (pieces[1] == pieces[2]):
        # send_message(rID, str(pieces[0]) + " Won!")
        win = str(pieces[0])
    elif (pieces[3] == pieces[4]) and (pieces[4] == pieces[5]):
        # send_message(rID, str(pieces[3]) + " Won!")
        win = str(pieces[3])
    elif (pieces[6] == pieces[7]) and (pieces[7] == pieces[8]):
        # send_message(rID, str(pieces[6]) + " Won!")
        win = str(pieces[6])
    elif (pieces[0] == pieces[3]) and (pieces[3] == pieces[6]):
        # send_message(str(pieces[0]) + "Won!")
        win = str(pieces[0])
    elif (pieces[1] == pieces[4]) and (pieces[4] == pieces[7]):
        # send_message(str(pieces[1]) + " Won!")
        win = str(pieces[1])
    elif (pieces[2] == pieces[5]) and (pieces[5] == pieces[8]):
        # send_message(rID, str(pieces[2]) + " Won!")
        win = str(pieces[2])
    elif (pieces[0] == pieces[4]) and (pieces[4] == pieces[8]):
        # send_message(rID, str(pieces[0]) + " Won!")
        win = str(pieces[0])
    elif (pieces[2] == pieces[4]) and (pieces[4] == pieces[6]):
        # send_message(rID, str(pieces[2]) + " Won!")
        win = str(pieces[2])
    else:
        win = 'none'
    if win == 'none' and move_count == 9:
        send_message(rID, "Draw!")


# Ensures that the below code is only evaluated when the file is executed, and ignored if the file is imported
if __name__ == "__main__":
    app.run(debug=True)  # Runs application
