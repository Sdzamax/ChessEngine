import pygame
import chess
import sys
import random
from math import inf

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 480, 480
SQUARE_SIZE = WIDTH // 8
ENGINE_DEPTH = 5  # Adjust this value to change AI strength (higher = stronger but slower)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_BROWN = (240, 217, 181)
DARK_BROWN = (181, 136, 99)
HIGHLIGHT = (100, 255, 100, 150)  # Semi-transparent green
LEGAL_MOVE_HIGHLIGHT = (100, 200, 100, 150)  # Semi-transparent light green

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Chess Engine')

# Initialize the chess board
game_board = chess.Board()

# Unicode symbols for chess pieces
PIECE_UNICODE = {
    chess.PAWN: {'w': '\u2659', 'b': '\u265F'},
    chess.KNIGHT: {'w': '\u2658', 'b': '\u265E'},
    chess.BISHOP: {'w': '\u2657', 'b': '\u265D'},
    chess.ROOK: {'w': '\u2656', 'b': '\u265C'},
    chess.QUEEN: {'w': '\u2655', 'b': '\u265B'},
    chess.KING: {'w': '\u2654', 'b': '\u265A'},
}

# Piece values for evaluation
PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000
}

# Try to use a font that supports chess pieces, fall back to Arial if not available
try:
    font = pygame.font.SysFont('Segoe UI Symbol', SQUARE_SIZE - 10)
except:
    font = pygame.font.SysFont('Arial', SQUARE_SIZE - 10)

selected_square = None
user_turn = True
legal_moves = []

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

def evaluate_board(board):
    """
    Evaluate the board position from the perspective of the current player.
    Positive scores favor the current player.
    """
    if board.is_checkmate():
        return -inf if board.turn == chess.WHITE else inf
    
    if board.is_game_over():
        return 0
    
    score = 0
    
    # Material evaluation
    for piece_type in PIECE_VALUES:
        score += len(board.pieces(piece_type, chess.WHITE)) * PIECE_VALUES[piece_type]
        score -= len(board.pieces(piece_type, chess.BLACK)) * PIECE_VALUES[piece_type]
    
    # Add perspective - positive is good for current player
    if board.turn == chess.BLACK:
        score = -score
    
    # Mobility - number of legal moves
    mobility = len(list(board.legal_moves))
    score += mobility * 0.1
    
    # Center control - bonus for controlling center squares
    center_squares = [chess.D4, chess.E4, chess.D5, chess.E5]
    for square in center_squares:
        if board.is_attacked_by(chess.WHITE, square):
            score += 5
        if board.is_attacked_by(chess.BLACK, square):
            score -= 5
    
    return score

def minimax(board, depth, alpha, beta, maximizing_player):
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)
    
    if maximizing_player:
        max_eval = -inf
        for move in board.legal_moves:
            board.push(move)
            eval = minimax(board, depth-1, alpha, beta, False)
            board.pop()
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = inf
        for move in board.legal_moves:
            board.push(move)
            eval = minimax(board, depth-1, alpha, beta, True)
            board.pop()
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval

def find_best_move(board, depth=3):
    best_move = None
    best_value = -inf if board.turn == chess.WHITE else inf
    
    for move in board.legal_moves:
        board.push(move)
        board_value = minimax(board, depth-1, -inf, inf, board.turn == chess.BLACK)
        board.pop()
        
        if board.turn == chess.WHITE:
            if board_value > best_value:
                best_value = board_value
                best_move = move
        else:
            if board_value < best_value:
                best_value = board_value
                best_move = move
    
    return best_move if best_move else random.choice(list(board.legal_moves))

def ai_move(board):
    if board.is_game_over():
        return
    
    best_move = find_best_move(board, depth=ENGINE_DEPTH)
    board.push(best_move)

def main():
    global selected_square, user_turn, legal_moves
    running = True
    
    # Create a transparent surface for highlights
    highlight_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and user_turn and not game_board.is_game_over():
                pos = pygame.mouse.get_pos()
                square = get_square_under_mouse(pos)
                piece = game_board.piece_at(square)
                
                if selected_square is None:
                    # Select a piece (only your color)
                    if piece and piece.color == game_board.turn:
                        selected_square = square
                        legal_moves = [move for move in game_board.legal_moves if move.from_square == square]
                else:
                    # Try to make a move
                    move = chess.Move(selected_square, square)
                    if move in game_board.legal_moves:
                        game_board.push(move)
                        user_turn = False
                    selected_square = None
                    legal_moves = []
        
        draw_board(screen)
        
        # Highlight legal moves
        if selected_square is not None:
            for move in legal_moves:
                col = chess.square_file(move.to_square)
                row = 7 - chess.square_rank(move.to_square)
                highlight_surface.fill(LEGAL_MOVE_HIGHLIGHT)
                screen.blit(highlight_surface, (col * SQUARE_SIZE, row * SQUARE_SIZE))
        
        # Highlight selected square
        if selected_square is not None:
            col = chess.square_file(selected_square)
            row = 7 - chess.square_rank(selected_square)
            highlight_surface.fill(HIGHLIGHT)
            screen.blit(highlight_surface, (col * SQUARE_SIZE, row * SQUARE_SIZE))
        
        draw_pieces(screen, game_board)
        pygame.display.flip()

        # AI move
        if not user_turn and not game_board.is_game_over():
            ai_move(game_board)
            user_turn = True

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()