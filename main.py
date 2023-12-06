import copy
import sys
import pygame
import random
import numpy as np

# Import constants from the constants module
from constants.constants import *

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('TIC TAC TOE AI')
screen.fill(BG_COLOR)


class Board:

    def __init__(self):
        # Initialize the game board
        self.squares = np.zeros((ROWS, COLS))
        self.empty_sqrs = self.squares  # [squares]
        self.marked_sqrs = 0

    def final_state(self, show=False):
        '''
        @return 0 if there is no win yet
        @return 1 if player 1 wins
        @return 2 if player 2 wins
        '''

        # Check for vertical wins
        for col in range(COLS):
            if self.squares[0][col] == self.squares[1][col] == self.squares[2][col] != 0:
                if show:
                    color = CIRC_COLOR if self.squares[0][col] == 2 else CROSS_COLOR
                    iPos = (col * SQSIZE + SQSIZE // 2, 20)
                    fPos = (col * SQSIZE + SQSIZE // 2, HEIGHT - 20)
                    pygame.draw.line(screen, color, iPos, fPos, LINE_WIDTH)
                return self.squares[0][col]

        # Check for horizontal wins
        for row in range(ROWS):
            if self.squares[row][0] == self.squares[row][1] == self.squares[row][2] != 0:
                if show:
                    color = CIRC_COLOR if self.squares[row][0] == 2 else CROSS_COLOR
                    iPos = (20, row * SQSIZE + SQSIZE // 2)
                    fPos = (WIDTH - 20, row * SQSIZE + SQSIZE // 2)
                    pygame.draw.line(screen, color, iPos, fPos, LINE_WIDTH)
                return self.squares[row][0]

        # Check for descending diagonal
        if self.squares[0][0] == self.squares[1][1] == self.squares[2][2] != 0:
            if show:
                color = CIRC_COLOR if self.squares[1][1] == 2 else CROSS_COLOR
                iPos = (20, 20)
                fPos = (WIDTH - 20, HEIGHT - 20)
                pygame.draw.line(screen, color, iPos, fPos, CROSS_WIDTH)
            return self.squares[1][1]

        # Check for ascending diagonal
        if self.squares[2][0] == self.squares[1][1] == self.squares[0][2] != 0:
            if show:
                color = CIRC_COLOR if self.squares[1][1] == 2 else CROSS_COLOR
                iPos = (20, HEIGHT - 20)
                fPos = (WIDTH - 20, 20)
                pygame.draw.line(screen, color, iPos, fPos, CROSS_WIDTH)
            return self.squares[1][1]

        # No win yet
        return 0

    def mark_sqr(self, row, col, player):
        # Mark a square on the board
        self.squares[row][col] = player
        self.marked_sqrs += 1

    def empty_sqr(self, row, col):
        # Check if a square is empty
        return self.squares[row][col] == 0

    def get_empty_sqrs(self):
        # Get a list of empty squares
        empty_sqrs = []
        for row in range(ROWS):
            for col in range(COLS):
                if self.empty_sqr(row, col):
                    empty_sqrs.append((row, col))

        return empty_sqrs

    def isfull(self):
        # Check if the board is full
        return self.marked_sqrs == 9

    def isempty(self):
        # Check if the board is empty
        return self.marked_sqrs == 0


class AI:

    def __init__(self, level=1, player=2):
        # Initialize the AI with a specified level and player
        self.level = level
        self.player = player

    # --- RANDOM ---

    def rnd(self, board):
        # Make a random move
        empty_sqrs = board.get_empty_sqrs()
        idx = random.randrange(0, len(empty_sqrs))

        return empty_sqrs[idx]  # (row, col)

    # --- MINIMAX ---

    def minimax(self, board, maximizing):

        # Terminal case
        case = board.final_state()

        # Player 1 wins
        if case == 1:
            return 1, None  # eval, move

        # Player 2 wins
        if case == 2:
            return -1, None

        # Draw
        elif board.isfull():
            return 0, None

        if maximizing:
            max_eval = -100
            best_move = None
            empty_sqrs = board.get_empty_sqrs()

            for (row, col) in empty_sqrs:
                temp_board = copy.deepcopy(board)
                temp_board.mark_sqr(row, col, 1)
                eval = self.minimax(temp_board, False)[0]
                if eval > max_eval:
                    max_eval = eval
                    best_move = (row, col)

            return max_eval, best_move

        elif not maximizing:
            min_eval = 100
            best_move = None
            empty_sqrs = board.get_empty_sqrs()

            for (row, col) in empty_sqrs:
                temp_board = copy.deepcopy(board)
                temp_board.mark_sqr(row, col, self.player)
                eval = self.minimax(temp_board, True)[0]
                if eval < min_eval:
                    min_eval = eval
                    best_move = (row, col)

            return min_eval, best_move

    def eval(self, main_board):
        # Evaluate the best move using minimax algorithm
        if self.level == 0:
            # Random choice
            eval = 'random'
            move = self.rnd(main_board)
        else:
            # Minimax algorithm choice
            eval, move = self.minimax(main_board, False)

        print(f'AI has chosen to mark the square in pos {move} with an eval of: {eval}')

        return move  # row, col


class Game:

    def __init__(self):
        # Initialize the game
        self.board = Board()
        self.ai = AI()
        self.player = 1  # 1-cross  #2-circles
        self.gamemode = 'ai'  # pvp or ai
        self.running = True
        self.show_lines()

    # --- DRAW METHODS ---

    def show_lines(self):
        # Display game lines
        screen.fill(BG_COLOR)

        # Vertical
        pygame.draw.line(screen, LINE_COLOR, (SQSIZE, 0), (SQSIZE, HEIGHT), LINE_WIDTH)
        pygame.draw.line(screen, LINE_COLOR, (WIDTH - SQSIZE, 0), (WIDTH - SQSIZE, HEIGHT), LINE_WIDTH)

        # Horizontal
        pygame.draw.line(screen, LINE_COLOR, (0, SQSIZE), (WIDTH, SQSIZE), LINE_WIDTH)
        pygame.draw.line(screen, LINE_COLOR, (0, HEIGHT - SQSIZE), (WIDTH, HEIGHT - SQSIZE), LINE_WIDTH)

    def draw_fig(self, row, col):
        # Draw cross or circle based on player
        if self.player == 1:
            # Draw cross
            # Descending line
            start_desc = (col * SQSIZE + OFFSET, row * SQSIZE + OFFSET)
            end_desc = (col * SQSIZE + SQSIZE - OFFSET, row * SQSIZE + SQSIZE - OFFSET)
            pygame.draw.line(screen, CROSS_COLOR, start_desc, end_desc, CROSS_WIDTH)
            # Ascending line
            start_asc = (col * SQSIZE + OFFSET, row * SQSIZE + SQSIZE - OFFSET)
            end_asc = (col * SQSIZE + SQSIZE - OFFSET, row * SQSIZE + OFFSET)
            pygame.draw.line(screen, CROSS_COLOR, start_asc, end_asc, CROSS_WIDTH)

        elif self.player == 2:
            # Draw circle
            center = (col * SQSIZE + SQSIZE // 2, row * SQSIZE + SQSIZE // 2)
            pygame.draw.circle(screen, CIRC_COLOR, center, RADIUS, CIRC_WIDTH)

    def make_move(self, row, col):
        # Mark a square and draw the player's symbol
        self.board.mark_sqr(row, col, self.player)
        self.draw_fig(row, col)
        self.next_turn()

    def next_turn(self):
        # Switch to the next player's turn
        self.player = self.player % 2 + 1

    def change_gamemode(self):
        # Change the game mode between PvP and AI
        self.gamemode = 'ai' if self.gamemode == 'pvp' else 'pvp'

    def isover(self):
        # Check if the game is over
        return self.board.final_state(show=True) != 0 or self.board.isfull()

    def reset(self):
        # Reset the game
        self.__init__()


def main():
    # Initialize the game and AI
    game = Game()
    board = game.board
    ai = game.ai

    while True:

        # Pygame events
        for event in pygame.event.get():

            # Quit event
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Keydown event
            if event.type == pygame.KEYDOWN:

                # Change game mode
                if event.key == pygame.K_g:
                    game.change_gamemode()

                # Restart game
                if event.key == pygame.K_r:
                    game.reset()
                    board = game.board
                    ai = game.ai

                # Set AI level to 0 (random moves)
                if event.key == pygame.K_0:
                    ai.level = 0

                # Set AI level to 1 (minimax algorithm)
                if event.key == pygame.K_1:
                    ai.level = 1

            # Click event
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                row = pos[1] // SQSIZE
                col = pos[0] // SQSIZE

                # Human player marks a square
                if board.empty_sqr(row, col) and game.running:
                    game.make_move(row, col)

                    if game.isover():
                        game.running = False

        # AI's initial move
        if game.gamemode == 'ai' and game.player == ai.player and game.running:

            # Update the screen
            pygame.display.update()

            # AI makes a move
            row, col = ai.eval(board)
            game.make_move(row, col)

            if game.isover():
                game.running = False

        pygame.display.update()


main()
