#import modules
from os import stat
import pygame,numpy as np,numpy.random
from pygame.locals import *

pygame.init()

n = int(input("Enter the Size of borad: "))

screen_height = n*100
screen_width = n*100
line_width = 6
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Tic Tac Toe')

#define colours
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)

#define font
font = pygame.font.SysFont(None, 40)

#define variables
clicked = True
player = 1
pos = (0,0)
markers = []
game_over = False
winner = 0

#setup a rectangle for "Play Again" Option
again_rect = Rect(screen_width // 2 - 80, screen_height // 2, 160, 50)

#create empty 3 x 3 list to represent the grid
for x in range (n):
	row = [0] * n
	markers.append(row)

markers = np.array(markers)
markersCopy = markers[:]
# base Case
stateMap = [0]

def boardToDec(board,action = False):
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
	listEle = list(np.base_repr(decimal,base=3))
	listEle.reverse()
	board = np.array(listEle,dtype=int)
	board = np.pad(board,(0,(n*n)-board.size))
	board.resize((n,n))
	return board



def zeroesPos(board):
	zPos = []
	for i in range(n):
		for j in range(n):
			if(board[i,j] == 0):
				zPos.append([i,j])
	return zPos

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
			decimal = boardToDec(board)
			if(decimal not in stateMap):
				stateMap.append(decimal)
			board[y[0]][y[1]] = 0
		board[x[0]][x[1]] = 0
	return

def generateSpace(startPos):
	for x in range(startPos,len(stateMap)):
		board = decToBoard(stateMap[x])
		baseSpace(board)
	return


def ptf(PTFArray):
	for cs in range(len(stateMap)):
		board = decToBoard(stateMap[cs])
		boardCopy = board[:]
		zPos = zeroesPos(boardCopy)
		if(len(zPos) <= 1):
				continue
		for x in zPos:
			boardCopy[x[0]][x[1]] = 1
			zPosCopy = zPos[:]
			zPosCopy.remove(x)
			possProb = 1
			if(len(zPos) > 1):
				possProb = 1/(len(zPos)-1)
			for o in zPosCopy:
				boardCopy[o[0]][o[1]] = 2
				nsVal = boardToDec(boardCopy)
				ns = stateMap.index(nsVal)
				PTFArray[cs][boardToDec(np.array(x),True)][ns] = possProb
				boardCopy[o[0]][o[1]] = 0
			boardCopy[x[0]][x[1]] = 0
	return

def randomPolicyGenerate():
	policy = []
	for i in range(len(stateMap)):
		board = decToBoard(stateMap[i])
		zPos = zeroesPos(board)
		if(len(zPos) > 0):
			actionPos = np.random.choice(range(len(zPos)),1)[0]
			action = zPos[actionPos]
			policy.append(np.array(action))
	policy = np.array(policy)
	return policy
	
# configSpace
# empty Space
baseSpace(markersCopy)
start = 1
end = len(stateMap)
for i in range(int((n*n)/2) -1):
	generateSpace(start)
	start = end
	end = len(stateMap)

print("All States: " + str(len(stateMap)))
actionStates = n*n
PTFArray = np.zeros((len(stateMap),actionStates,len(stateMap)))
ptf(PTFArray)
policy = randomPolicyGenerate()

def draw_board():
	bg = (255, 255, 210)
	grid = (50, 50, 50)
	screen.fill(bg)
	for x in range(1,n):
		pygame.draw.line(screen, grid, (0, 100 * x), (screen_width,100 * x), line_width)
		pygame.draw.line(screen, grid, (100 * x, 0), (100 * x, screen_height), line_width)

def draw_markers():
	x_pos = 0
	for x in markers:
		y_pos = 0
		for y in x:
			if y == 1:
				pygame.draw.line(screen, red, (x_pos * 100 + 15, y_pos * 100 + 15), (x_pos * 100 + 85, y_pos * 100 + 85), line_width)
				pygame.draw.line(screen, red, (x_pos * 100 + 85, y_pos * 100 + 15), (x_pos * 100 + 15, y_pos * 100 + 85), line_width)
			if y == -1:
				pygame.draw.circle(screen, green, (x_pos * 100 + 50, y_pos * 100 + 50), 38, line_width)
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
	#check cross
	sumLeftDiagnol = 0
	sumRightDiagnol = 0
	for i in range(0,n):
		sumLeftDiagnol += markers[i][i]

	for i in range(n-1,-1,-1):
		sumRightDiagnol += markers[n-i-1][i] 
	
	if sumLeftDiagnol == n or sumRightDiagnol == n:
		winner = 1
		game_over = True
	
	if sumLeftDiagnol == -n or sumRightDiagnol == -n:
		winner = 2
		game_over = True

	#check for tie
	if game_over == False:
		tie = True
		for row in markers:
			for i in row:
				if i == 0:
					tie = False
		#if it is a tie, then call game over and set winner to 0 (no one)
		if tie == True:
			game_over = True
			winner = 0



def draw_game_over(winner):

	if winner != 0:
		end_text = "Player " + str(winner) + " wins!"
	elif winner == 0:
		end_text = "You have tied!"

	end_img = font.render(end_text, True, blue)
	pygame.draw.rect(screen, green, (screen_width // 2 - 100, screen_height // 2 - 60, 200, 50))
	screen.blit(end_img, (screen_width // 2 - 100, screen_height // 2 - 50))

	again_text = 'Play Again?'
	again_img = font.render(again_text, True, blue)
	pygame.draw.rect(screen, green, again_rect)
	screen.blit(again_img, (screen_width // 2 - 80, screen_height // 2 + 10))


#main loop

run = True

while run:

	#draw board and markers first
	draw_board()
	draw_markers()

	#handle events
	for event in pygame.event.get():
		#handle game exit
		if event.type == pygame.QUIT:
			run = False
		#run new game
		if game_over == False:
			markers[markers == -1] = 2
			cs = stateMap.index(boardToDec(markers))
			action = policy[cs]
			markers[action[0]][action[1]] = 1
			action = boardToDec(np.array(action),True)
			zPos = zeroesPos(markers)
			if(len(zPos) > 0):
				nsIdx = np.random.choice(range(len(stateMap)),1,p = PTFArray[cs][action])
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

	#check if game has been won
	if game_over == True:
		draw_game_over(winner)
		#check for mouseclick to see if we clicked on Play Again
		if event.type == pygame.MOUSEBUTTONDOWN and clicked == False:
			clicked = True
		if event.type == pygame.MOUSEBUTTONUP and clicked == True:
			clicked = False
			pos = pygame.mouse.get_pos()
			if again_rect.collidepoint(pos):
				#reset variables
				game_over = False
				player = 1
				pos = (0,0)
				markers = []
				winner = 0
				clicked = True
				#create empty 3 x 3 list to represent the grid
				for x in range (n):
					row = [0] * n
					markers.append(row)
				markers = np.array(markers)
				markersCopy = markers[:]
			# base Case
				


	#update display
	pygame.display.update()

pygame.quit()
