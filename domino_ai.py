import random
from collections import Counter

full_set = []
test_set = []
stockpieces = []
computerpieces = []
playerpieces = []
temp = []
dominosnake = []
x = 0
moveleft = True
player_next_turn = 1
reverse = False
ai = {}


def ai_scoring(com, dom):
    ai.clear()
    combo = com + dom
    freq_counter = Counter(c for _list in combo for c in _list)
    for i in com:
        a, b = i[0], i[1]
        ai[i[0], i[1]] = freq_counter[a] + freq_counter[b]


def snake_format():
    snake_length = len(dominosnake)
    if snake_length <= 6:
        print(*dominosnake, sep=" ")
    else:
        print(f'{dominosnake[0]}{dominosnake[1]}{dominosnake[2]}...{dominosnake[-3]}{dominosnake[-2]}{dominosnake[-1]}')


def counts(lst, x):
    count = 0
    for i in range(len(lst)):
        for j in range(2):
            if lst[i][j] == x:
                count = count + 1
    return count


def check_set_match():
    test_set.reverse()

    if test_set in full_set and test_set != [x, x]:
        test_set.reverse()
        full_set.remove(test_set)
    test_set.clear()


def status_board():
    print("=" * 70)
    print("Stock size:", len(stockpieces))
    print("Computer pieces:", len(computerpieces), '\n')
    snake_format()
    print()
    print("Your pieces:")
    for count, value in enumerate(playerpieces):
        print(f'{count + 1}:{value}')
    print()


def end_game():
    global player_next_turn
    if len(playerpieces) == 0:
        status_board()
        print("Status: The game is over. You won!")
        exit()
    elif len(computerpieces) == 0:
        status_board()
        print("Status: The game is over. The computer won!")
        exit()
    elif dominosnake[0][0] == dominosnake[len(dominosnake) - 1][1] and counts(dominosnake, dominosnake[0][0]) == 8:
        status_board()
        print("Status: The game is over. It's a draw!")
        exit()
    else:
        if player_next_turn == 1:

            status_board()
            print("Status: Computer is about to make a move. Press Enter to continue...")
            input()
            computer_playing()

        elif player_next_turn == 0:

            status_board()
            print("Status: It's your turn to make a move. Enter your command.")
            player_playing()


def is_legal(position, moveleft):
    global reverse

    a = playerpieces[position - 1]
    if len(dominosnake) == 1:
        if moveleft:
            if a[0] == dominosnake[0][0]:
                reverse = True
                return True, reverse
            elif a[1] == dominosnake[0][0]:
                reverse = False
                return True, reverse
            else:
                print(f'Illegal move. Please try again')
                return False
        elif not moveleft:
            if a[0] == dominosnake[0][1]:
                reverse = False
                return True, reverse
            elif a[1] == dominosnake[0][1]:
                reverse = True
                return True, reverse
            else:
                print(f'Illegal move. Please try again')
                return False
    else:
        if moveleft:
            if a[0] == dominosnake[0][0]:
                # a = a[::-1]
                reverse = True
                return True, reverse
            elif a[1] == dominosnake[0][0]:
                reverse = False
                return True, reverse
            else:
                print(f'Illegal move. Please try again')
                return False
        elif not moveleft:
            if a[0] == dominosnake[len(dominosnake) - 1][1]:
                reverse = False
                return True, reverse
            elif a[1] == dominosnake[len(dominosnake) - 1][1]:
                reverse = True
                return True, reverse
            else:
                print(f'Illegal move. Please try again')
                return False


def moving_pieces(position, place, player, reverse):

    if position == 0:
        if len(stockpieces) != 0:
            player.append(stockpieces.pop())
            end_game()
    else:
        if not place:
            if reverse:
                y = player.pop(position - 1)
                y = y[::-1]
                dominosnake.insert(len(dominosnake), y)
            else:
                dominosnake.insert(len(dominosnake), player.pop(position - 1))

        elif place:
            if reverse:
                y = player.pop(position - 1)
                y = y[::-1]
                dominosnake.insert(0, y)
            else:
                dominosnake.insert(0, player.pop(position - 1))


for i in range(7):
    for j in range(7):
        test_set.append(i)
        test_set.append(j)
        full_set.append([i, j])
        check_set_match()

    x += 1

a = 28

for i in range(14):
    item = random.randrange(1, a)
    a -= 1
    stockpieces.append(full_set.pop(item))

a = 14

for i in range(7):
    item = random.randrange(1, a)
    a -= 1
    computerpieces.append(full_set.pop(item))

playerpieces.extend(full_set)
full_set.clear()

temp = computerpieces + playerpieces
status = "It's your turn to make a move. Enter your command."

if list(filter(lambda x: x[0] == x[1], temp)) is None:
    no_doubles = max(list(filter(lambda x: x[0] != x[1], temp)))
    dominosnake.append(no_doubles)
    if no_doubles in computerpieces:
        index = computerpieces.index(no_doubles)
        del computerpieces[index]

    else:
        index = playerpieces.index(no_doubles)
        del playerpieces[index]
        status = "Computer is about to make a move. Press Enter to continue..."

else:
    doubles = max(list(filter(lambda x: x[0] == x[1], temp)))
    dominosnake.append(doubles)
    if doubles in computerpieces:
        index = computerpieces.index(doubles)
        del computerpieces[index]

    else:
        index = playerpieces.index(doubles)
        del playerpieces[index]
        status = "Computer is about to make a move. Press Enter to continue..."


def player_playing():
    global player_next_turn
    global reverse
    global moveleft
    player_next_turn = 1
    while True:
        try:
            move = input()
            if "-" in move[0]:
                moveleft = True
                move = move.lstrip("-")
                if move.isalpha() or int(move) > len(playerpieces):
                    print("Invalid input. Please try again..")
                else:
                    move = int(move)
                    if move == 0 and len(stockpieces) != 0:
                        playerpieces.append(stockpieces.pop())
                        end_game()

                    result = is_legal(move, moveleft)
                    if not result:
                        continue
                    elif result:
                        moving_pieces(move, moveleft, playerpieces, reverse)
                        end_game()
                        break

            elif "-" not in move[0]:
                moveleft = False
                if move.isalpha() or int(move) > len(playerpieces):
                    print("Invalid input. Please try again..")
                else:
                    move = int(move)
                    if move == 0 and len(stockpieces) != 0:
                        playerpieces.append(stockpieces.pop())
                        end_game()
                    result = is_legal(move, moveleft)
                    if not result:
                        continue
                    elif result:
                        moving_pieces(move, moveleft, playerpieces, reverse)
                        end_game()
                        break

        except (ValueError, NameError, IndexError):
            print("Invalid input. Please try again..")


def computer_playing():
    global player_next_turn
    player_next_turn = 0
    while True:
        counter = 0
        ai_scoring(computerpieces, dominosnake)
        for w in sorted(ai, key=ai.get, reverse=True):
            computers_number = list(w)
            if computers_number[0] == dominosnake[0][0]:
                ab = computers_number[::-1]
                dominosnake.insert(0, ab)
                computerpieces.remove(computers_number)
                end_game()

            elif computers_number[1] == dominosnake[0][0]:
                dominosnake.insert(0, computers_number)
                computerpieces.remove(computers_number)
                end_game()

            elif computers_number[0] == dominosnake[len(dominosnake) - 1][1]:
                dominosnake.insert(len(dominosnake), computers_number)
                computerpieces.remove(computers_number)
                end_game()

            elif computers_number[1] == dominosnake[len(dominosnake) - 1][1]:
                ab = computers_number[::-1]
                dominosnake.insert(len(dominosnake), ab)
                computerpieces.remove(computers_number)
                end_game()

            counter += 1

        if counter == len(ai):
            computerpieces.append(stockpieces.pop())
            end_game()


status_board()

print("Status:", status)
if status == "It's your turn to make a move. Enter your command.":
    player_next_turn = 1
    player_playing()

elif status == "Computer is about to make a move. Press Enter to continue...":
    input()
    player_next_turn = 0
    computer_playing()

