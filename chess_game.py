import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 600, 600
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)  # For highlighting selected piece

# Initialize screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess Game")
clock = pygame.time.Clock()

# Load piece images (replace with actual paths)
pieces = {
    'wp': pygame.image.load('white_pawn.png'),
    'wR': pygame.image.load('white_rook.png'),
    'wN': pygame.image.load('white_knight.png'),
    'wB': pygame.image.load('white_bishop.png'),
    'wQ': pygame.image.load('white_queen.png'),
    'wK': pygame.image.load('white_king.png'),
    'bp': pygame.image.load('black_pawn.png'),
    'bR': pygame.image.load('black_rook.png'),
    'bN': pygame.image.load('black_knight.png'),
    'bB': pygame.image.load('black_bishop.png'),
    'bQ': pygame.image.load('black_queen.png'),
    'bK': pygame.image.load('black_king.png'),
}

# Chess board representation
board = [
    ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
    ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
    ['', '', '', '', '', '', '', ''],
    ['', '', '', '', '', '', '', ''],
    ['', '', '', '', '', '', '', ''],
    ['', '', '', '', '', '', '', ''],
    ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
    ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR'],
]

# Variables for piece movement
selected_piece = None
selected_row, selected_col = None, None
current_player = 'w'  # Start with white

# Draw the board
def draw_board():
    for row in range(ROWS):
        for col in range(COLS):
            color = WHITE if (row + col) % 2 == 0 else BLACK
            pygame.draw.rect(screen, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

# Draw the pieces
def draw_pieces():
    for row in range(ROWS):
        for col in range(COLS):
            piece = board[row][col]
            if piece:
                screen.blit(pieces[piece], (col * SQUARE_SIZE, row * SQUARE_SIZE))

# Highlight selected piece
def highlight_square(row, col):
    pygame.draw.rect(screen, GREEN, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 3)

# Check if a move is valid
def is_valid_move(piece, start_row, start_col, end_row, end_col):
    # Get the piece type and color
    piece_type = piece[1]
    piece_color = piece[0]

    # Calculate row and column differences
    row_diff = end_row - start_row
    col_diff = end_col - start_col

    # Pawn movement
    if piece_type == 'p':
        if piece_color == 'w':  # White pawn
            if start_row == 6:  # First move
                if row_diff == -1 or row_diff == -2:
                    return True
            else:
                if row_diff == -1:
                    return True
        else:  # Black pawn
            if start_row == 1:  # First move
                if row_diff == 1 or row_diff == 2:
                    return True
            else:
                if row_diff == 1:
                    return True
        return False

    # Rook movement
    if piece_type == 'R':
        if start_row == end_row or start_col == end_col:
            return True
        return False

    # Knight movement
    if piece_type == 'N':
        if abs(row_diff) == 2 and abs(col_diff) == 1:
            return True
        if abs(row_diff) == 1 and abs(col_diff) == 2:
            return True
        return False

    # Bishop movement
    if piece_type == 'B':
        if abs(row_diff) == abs(col_diff):
            return True
        return False

    # Queen movement
    if piece_type == 'Q':
        if start_row == end_row or start_col == end_col or abs(row_diff) == abs(col_diff):
            return True
        return False

    # King movement
    if piece_type == 'K':
        # Castling
        if abs(col_diff) == 2 and row_diff == 0:
            if start_col == 4:  # King is in the starting position
                if col_diff == 2:  # Kingside castling
                    rook_col = 7
                    if board[start_row][rook_col] == f'{piece_color}R':
                        if not board[start_row][5] and not board[start_row][6]:
                            return True
                elif col_diff == -2:  # Queenside castling
                    rook_col = 0
                    if board[start_row][rook_col] == f'{piece_color}R':
                        if not board[start_row][1] and not board[start_row][2] and not board[start_row][3]:
                            return True
        return abs(row_diff) <= 1 and abs(col_diff) <= 1

    return False

# Check if the king is in check
def is_in_check(board, player):
    king_pos = None
    opponent = 'b' if player == 'w' else 'w'

    # Find the king's position
    for row in range(ROWS):
        for col in range(COLS):
            if board[row][col] == f'{player}K':
                king_pos = (row, col)
                break
        if king_pos:
            break

    if not king_pos:
        return False

    # Check if any opponent's piece can attack the king
    for row in range(ROWS):
        for col in range(COLS):
            piece = board[row][col]
            if piece and piece[0] == opponent:
                if is_valid_move(piece, row, col, king_pos[0], king_pos[1]):
                    return True

    return False

# Check if the player is in checkmate
def is_checkmate(board, player):
    if not is_in_check(board, player):
        return False

    # Check if any move can get the king out of check
    for row in range(ROWS):
        for col in range(COLS):
            piece = board[row][col]
            if piece and piece[0] == player:
                for new_row in range(ROWS):
                    for new_col in range(COLS):
                        if is_valid_move(piece, row, col, new_row, new_col):
                            # Simulate the move
                            temp_board = [row[:] for row in board]
                            temp_board[new_row][new_col] = piece
                            temp_board[row][col] = ''

                            if not is_in_check(temp_board, player):
                                return False
    return True

# Main game loop
def main():
    global selected_piece, selected_row, selected_col, current_player

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Mouse click event
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                col = x // SQUARE_SIZE
                row = y // SQUARE_SIZE

                # Select a piece only if it belongs to the current player
                if board[row][col] and board[row][col][0] == current_player:
                    selected_piece = board[row][col]
                    selected_row, selected_col = row, col

            # Mouse release event
            if event.type == pygame.MOUSEBUTTONUP:
                if selected_piece:
                    x, y = pygame.mouse.get_pos()
                    new_col = x // SQUARE_SIZE
                    new_row = y // SQUARE_SIZE

                    # Check if the move is valid
                    if is_valid_move(selected_piece, selected_row, selected_col, new_row, new_col):
                        # Simulate the move
                        temp_board = [row[:] for row in board]
                        temp_board[new_row][new_col] = selected_piece
                        temp_board[selected_row][selected_col] = ''

                        # Handle castling
                        if selected_piece[1] == 'K' and abs(new_col - selected_col) == 2:
                            if new_col > selected_col:  # Kingside castling
                                rook_col = 7
                                temp_board[new_row][5] = temp_board[new_row][rook_col]
                                temp_board[new_row][rook_col] = ''
                            else:  # Queenside castling
                                rook_col = 0
                                temp_board[new_row][3] = temp_board[new_row][rook_col]
                                temp_board[new_row][rook_col] = ''

                        # Check if the move leaves the king in check
                        if not is_in_check(temp_board, current_player):
                            # Capture the opponent's piece if the square is occupied
                            if board[new_row][new_col] and board[new_row][new_col][0] != selected_piece[0]:
                                print(f"Captured {board[new_row][new_col]}!")

                            # Move the piece
                            board[selected_row][selected_col] = ''
                            board[new_row][new_col] = selected_piece

                            # Handle castling
                            if selected_piece[1] == 'K' and abs(new_col - selected_col) == 2:
                                if new_col > selected_col:  # Kingside castling
                                    rook_col = 7
                                    board[new_row][5] = board[new_row][rook_col]
                                    board[new_row][rook_col] = ''
                                else:  # Queenside castling
                                    rook_col = 0
                                    board[new_row][3] = board[new_row][rook_col]
                                    board[new_row][rook_col] = ''

                            # Check for checkmate
                            opponent = 'b' if current_player == 'w' else 'w'
                            if is_checkmate(board, opponent):
                                print(f"Checkmate! {current_player.upper()} wins!")
                                pygame.quit()
                                sys.exit()

                            # Switch turns
                            current_player = 'b' if current_player == 'w' else 'w'
                        else:
                            print("Invalid move: King is in check!")
                    else:
                        print("Invalid move!")

                    # Reset selection
                    selected_piece = None
                    selected_row, selected_col = None, None

        # Draw the board and pieces
        draw_board()
        draw_pieces()

        # Highlight selected piece
        if selected_piece:
            highlight_square(selected_row, selected_col)

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
