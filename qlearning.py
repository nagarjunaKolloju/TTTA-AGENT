# import modules
from os import stat
from typing import Tuple
import pygame
import numpy as np
import sys
import numpy.random
from pygame.locals import *
from numpy import linalg as LA
pygame.init()

n = int(input("Enter the Size of board: "))

screen_height = n*100
screen_width = n*100
line_width = 6
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Tic Tac Toe')

# define colours
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)

# define font
font = pygame.font.SysFont(None, 40)

# define variables
clicked = False
player = 1
pos = (0, 0)
markers = []
game_over = False
winner = 0
policy = []
# setup a rectangle for "Play Again" Option
again_rect = Rect(screen_width // 2 - 80, screen_height // 2, 160, 50)

# create empty 3 x 3 list to represent the grid
for x in range(n):
    row = [0] * n
    markers.append(row)

markers = np.array(markers)
markersCopy = markers[:]
# base Case
stateMap = [0]
# rewardMap = [0]


def boardToDec(board, action=False):
    mul = 3
    if(action):
        mul = n
    listEle = board.flatten()
    decimal = 0
    power = 1
    for i in range(np.size(listEle)):
        decimal += power*listEle[i]
        power *= mul
    return decimal


def decToBoard(decimal):
    listEle = list(np.base_repr(decimal, base=3))
    listEle.reverse()
    board = np.array(listEle, dtype=int)
    board = np.pad(board, (0, (n*n)-board.size))
    board.resize((n, n))
    return board


def zeroesPos(board):
    zPos = []
    for i in range(n):
        for j in range(n):
            if(board[i, j] == 0):
                zPos.append([i, j])
    return zPos


def boardStatus(markers):
    winnerLocal = 0

    # check - columns
    sumCol = 0
    sumRow = 0
    markers[markers == 2] = -1
    for i in range(n):
        for j in range(n):
            sumRow += markers[i][j]
        if(sumRow == n):
            winnerLocal = 1
        elif(sumRow == -n):
            winnerLocal = 2
        sumRow = 0

    for i in range(n):
        for j in range(n):
            sumCol += markers[j][i]
        if(sumCol == n):
            winnerLocal = 1
        elif(sumCol == -n):
            winnerLocal = 2
        sumCol = 0
    # check cross
    sumLeftDiagnol = 0
    sumRightDiagnol = 0
    for i in range(0, n):
        sumLeftDiagnol += markers[i][i]

    for i in range(n-1, -1, -1):
        sumRightDiagnol += markers[n-i-1][i]

    if sumLeftDiagnol == n or sumRightDiagnol == n:
        winnerLocal = 1

    elif sumLeftDiagnol == -n or sumRightDiagnol == -n:
        winnerLocal = 2

    # check for tie
    if winnerLocal == 0:
        tie = True
        for row in markers:
            for i in row:
                if i == 0:
                    tie = False
        # if it is a tie, then call game over and set winner to 0 (no one)
        if tie == True:
            winnerLocal = -1
    # 1x,2o,0normal,-1tie
    markers[markers == -1] = 2
    return winnerLocal

# reward -


def rewardFunction(rewardMap, PTFArray):
    for cs in range(len(stateMap)):
        board = decToBoard(stateMap[cs])
        terminalNo = boardStatus(board)
        if(terminalNo == 1 or terminalNo == 2):
            for x in zeroesPos(board):
                PTFArray[cs][boardToDec(np.array(x), True)][0] = 1
                rewardMap[cs][boardToDec(np.array(x), True)][:] = 100
            # board[a[0]][a[1]] = 0
            continue
        # if(terminalNo == 1):
        #     rewardMap[cs][]
        for a in zeroesPos(board):
            board[a[0]][a[1]] = 1
            if(len(zeroesPos(board)) == 0):
                PTFArray[cs][boardToDec(np.array(a), True)][0] = 1
                if(boardStatus(board) == 1):
                    rewardMap[cs][boardToDec(np.array(a), True)][:] = 100
                if(boardStatus(board) == -1):
                    rewardMap[cs][boardToDec(np.array(x), True)][:] = 10
                continue
            possProb = 1/len(zeroesPos(board))
            for o in zeroesPos(board):

                board[o[0]][o[1]] = 2
                ns = stateMap.index(boardToDec(board))
                if(boardStatus(board) == 1):
                    rewardMap[cs][boardToDec(np.array(a), True)][ns] = 100
                if(boardStatus(board) == 2):
                    rewardMap[cs][boardToDec(np.array(a), True)][ns] = -100
                PTFArray[cs][boardToDec(np.array(a), True)][ns] = possProb
                board[o[0]][o[1]] = 0
            board[a[0]][a[1]] = 0
    return


def baseSpace(board):
    zPos = list(zeroesPos(board))

    for x in zPos:
        board[x[0]][x[1]] = 1
        zPosCopy = zPos[:]
        zPosCopy.remove(x)
        # remaining pos
        for y in zPosCopy:
            board[y[0]][y[1]] = 2
            board
            decimal = boardToDec(board, False)
            if(decimal not in stateMap):
                stateMap.append(decimal)
            board[y[0]][y[1]] = 0
        board[x[0]][x[1]] = 0
    return


def generateSpace(startPos):
    for x in range(startPos, len(stateMap)):
        board = decToBoard(stateMap[x])
        baseSpace(board)
    return


def qLearning(qTable, stateMap, actionStates, rewardMap, PTFArray):
    global policy
    cs = 0
    for _ in range(300000):
        zPos = zeroesPos(decToBoard(stateMap[cs]))
        actionPos = np.random.choice(range(len(zPos)), 1)[0]
        action = zPos[actionPos]
        action = boardToDec(np.array(action), True)
        ns = np.random.choice(
            range(len(stateMap)), 1, p=PTFArray[cs][action])[0]

        qTable[cs][action] = qTable[cs][action] + 0.3 * \
            (rewardMap[cs][action]
             [ns] + 0.1 * np.max(qTable[ns, :]) - qTable[cs][action])
        cs = ns

    print("done")
    for i in range(len(stateMap)):
        action = -1
        maxVal = -sys.maxsize-1
        for a in zeroesPos(decToBoard(stateMap[i])):
            if(qTable[i][boardToDec(np.array(a), True)] > maxVal):
                action = a
                maxVal = qTable[i][boardToDec(np.array(a), True)]
        policy.append(a)
    return


    # configSpace
    # empty Space
baseSpace(markersCopy)
start = 1
end = len(stateMap)
for i in range(int((n*n)/2) - 1):
    generateSpace(start)
    start = end
    end = len(stateMap)
    # print(start, end)

actionStates = n*n
PTFArray = np.zeros((len(stateMap), actionStates, len(stateMap)))
rewardMap = np.zeros((len(stateMap), actionStates, len(stateMap)))
qTable = np.zeros(((len(stateMap)), actionStates))
rewardFunction(rewardMap, PTFArray)
qLearning(qTable, stateMap, actionStates, rewardMap, PTFArray)


def draw_board():
    bg = (255, 255, 210)
    grid = (50, 50, 50)
    screen.fill(bg)
    for x in range(1, n):
        pygame.draw.line(screen, grid, (0, 100 * x),
                         (screen_width, 100 * x), line_width)
        pygame.draw.line(screen, grid, (100 * x, 0),
                         (100 * x, screen_height), line_width)


def draw_markers():
    x_pos = 0
    for x in markers:
        y_pos = 0
        for y in x:
            if y == 1:
                pygame.draw.line(screen, red, (x_pos * 100 + 15, y_pos * 100 + 15),
                                 (x_pos * 100 + 85, y_pos * 100 + 85), line_width)
                pygame.draw.line(screen, red, (x_pos * 100 + 85, y_pos * 100 + 15),
                                 (x_pos * 100 + 15, y_pos * 100 + 85), line_width)
            if y == -1:
                pygame.draw.circle(
                    screen, green, (x_pos * 100 + 50, y_pos * 100 + 50), 38, line_width)
            y_pos += 1
        x_pos += 1


def check_game_over():
    global game_over
    global winner

    # check - columns
    sumCol = 0
    sumRow = 0

    for i in range(n):
        for j in range(n):
            sumRow += markers[i][j]
        if(sumRow == n):
            winner = 1
            game_over = True
        if(sumRow == -n):
            winner = 2
            game_over = True
        sumRow = 0

    for i in range(n):
        for j in range(n):
            sumCol += markers[j][i]
        if(sumCol == n):
            winner = 1
            game_over = True
        if(sumCol == -n):
            winner = 2
            game_over = True
        sumCol = 0
    # check cross
    sumLeftDiagnol = 0
    sumRightDiagnol = 0
    for i in range(0, n):
        sumLeftDiagnol += markers[i][i]

    for i in range(n-1, -1, -1):
        sumRightDiagnol += markers[n-i-1][i]

    if sumLeftDiagnol == n or sumRightDiagnol == n:
        winner = 1
        game_over = True

    if sumLeftDiagnol == -n or sumRightDiagnol == -n:
        winner = 2
        game_over = True

    # check for tie
    if game_over == False:
        tie = True
        for row in markers:
            for i in row:
                if i == 0:
                    tie = False
        # if it is a tie, then call game over and set winner to 0 (no one)
        if tie == True:
            game_over = True
            winner = 0


def draw_game_over(winner):
    # print("in")
    global player1Win, player2Win
    if winner != 0:
        # if(winner == 1):
        #     player1Win += 1
        # if(winner == 2):
        #     player2Win += 1
        end_text = "Player " + str(winner) + " wins!"
    elif winner == 0:
        end_text = "You have tied!"

    end_img = font.render(end_text, True, blue)
    pygame.draw.rect(screen, green, (screen_width // 2 -
                     100, screen_height // 2 - 60, 200, 50))
    screen.blit(end_img, (screen_width // 2 - 100, screen_height // 2 - 50))

    again_text = 'Play Again?'
    again_img = font.render(again_text, True, blue)
    pygame.draw.rect(screen, green, again_rect)
    screen.blit(again_img, (screen_width // 2 - 80, screen_height // 2 + 10))


# main loop

# main loop

run = True
noOfGames = 0
wins = 0
loss = 0
ties = 0
while noOfGames < 1000:

    # draw board and markers first
    draw_board()
    draw_markers()

    # handle events
    for event in pygame.event.get():
        # handle game exit
        if event.type == pygame.QUIT:
            run = False
        # run new game
    while game_over == False:
        markers[markers == -1] = 2
        cs = stateMap.index(boardToDec(markers))
        action = policy[cs]
        # print(decToBoard(stateMap[cs]))
        # print(action)
        markers[action[0]][action[1]] = 1
        action = boardToDec(np.array(action), True)
        zPos = zeroesPos(markers)
        if(len(zPos) > 0):

            # print(action)
            # print(PTFArray[cs][action])
            nsIdx = np.random.choice(
                range(len(stateMap)), 1, p=PTFArray[cs][action])
            markers[markers == 2] = -1
            check_game_over()
            if(game_over == True):
                break
            nsVal = stateMap[nsIdx[0]]
            markers = decToBoard(nsVal)
            markers[markers == 2] = -1
            check_game_over()
        else:
            markers[markers == 2] = -1
            check_game_over()

    # check if game has been won
    if game_over == True:
        draw_game_over(winner)
        # check for mouseclick to see if we clicked on Play Again
        # if event.type == pygame.MOUSEBUTTONDOWN and clicked == False:
        #     clicked = True
        # if event.type == pygame.MOUSEBUTTONUP and clicked == True:
        #     clicked = False
        #     pos = pygame.mouse.get_pos()
        #     if again_rect.collidepoint(pos):
        # reset variables
        if(winner == 1):
            wins += 1
        elif (winner == 2):
            loss += 1
        elif (winner == 0):
            ties += 1
        game_over = False
        player = 1
        pos = (0, 0)
        markers = []
        winner = 0
        clicked = True
        # create empty 3 x 3 list to represent the grid
        for x in range(n):
            row = [0] * n
            markers.append(row)
        markers = np.array(markers)
        markersCopy = markers[:]
        # base Case
        noOfGames += 1
    # update display
    pygame.display.update()

pygame.quit()

print("GAMES PLAYED: ", noOfGames)

print("WIN PERCENTAGE: ", (wins/noOfGames)*100)
print("LOSS PERCENTAGE: ", (loss/noOfGames)*100)
if(loss > 0):
    print("WIN/LOSS Ratio: ", (wins+ties/loss))
else:
    print("Since there are is loss, the ratio WIN/LOSS Ratio is approx 1")
