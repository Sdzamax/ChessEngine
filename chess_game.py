import pygame
import chess
import sys

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 480, 480
SQUARE_SIZE = WIDTH // 8

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_BROWN = (240, 217, 181)
DARK_BROWN = (181, 136, 99)

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Chess Engine')

# Initialize the chess board
game_board = chess.Board()

# Unicode symbols for chess pieces
PIECE_UNICODE = {
    chess.PAWN:   {'w': '\u265F', 'b': '\u265F'},
    chess.KNIGHT: {'w': '\u265E', 'b': '\u265E'},
    chess.BISHOP: {'w': '\u265D', 'b': '\u265D'},
    chess.ROOK:   {'w': '\u265C', 'b': '\u265C'},
    chess.QUEEN:  {'w': '\u265B', 'b': '\u265B'},
    chess.KING:   {'w': '\u265A', 'b': '\u265A'},
}

# Try to use a font that supports chess pieces, fall back to Arial if not available
try:
    font = pygame.font.SysFont('Segoe UI Symbol', SQUARE_SIZE - 10)
except:
    font = pygame.font.SysFont('Arial', SQUARE_SIZE - 10)

selected_square = None
user_turn = True

def draw_board(screen):
    for row in range(8):
        for col in range(8):
            color = LIGHT_BROWN if (row + col) % 2 == 0 else DARK_BROWN
            pygame.draw.rect(screen, color, pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def draw_pieces(screen, board):
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            col = chess.square_file(square)
            row = 7 - chess.square_rank(square)
            color = 'w' if piece.color == chess.WHITE else 'b'
            symbol = PIECE_UNICODE[piece.piece_type][color]
            text = font.render(symbol, True, WHITE if color == 'w' else BLACK)
            text_rect = text.get_rect(center=(col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2))
            screen.blit(text, text_rect)

def get_square_under_mouse(pos):
    x, y = pos
    col = x // SQUARE_SIZE
    row = y // SQUARE_SIZE
    square = chess.square(col, 7 - row)
    return square

def ai_move(board):
    import random
    moves = list(board.legal_moves)
    if moves:
        move = random.choice(moves)
        board.push(move)

def main():
    global selected_square, user_turn
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and user_turn and not game_board.is_game_over():
                pos = pygame.mouse.get_pos()
                square = get_square_under_mouse(pos)
                piece = game_board.piece_at(square)
                if selected_square is None:
                    # Select a piece
                    if piece and piece.color == chess.WHITE:
                        selected_square = square
                else:
                    # Try to make a move
                    move = chess.Move(selected_square, square)
                    if move in game_board.legal_moves:
                        game_board.push(move)
                        user_turn = False
                        selected_square = None
                    else:
                        # Deselect if invalid
                        selected_square = None

        draw_board(screen)
        draw_pieces(screen, game_board)
        # Highlight selected square
        if selected_square is not None:
            col = chess.square_file(selected_square)
            row = 7 - chess.square_rank(selected_square)
            pygame.draw.rect(screen, (0, 255, 0), pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 3)
        pygame.display.flip()

        # AI move
        if not user_turn and not game_board.is_game_over():
            ai_move(game_board)
            user_turn = True

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main() 