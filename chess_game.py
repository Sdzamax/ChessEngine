# [IMPORTS AND INIT]
import chess
import chess.engine
import random
import sys

ENGINE_DEPTH = 3  # You can increase this for stronger play

def evaluate_board(board):
    """Simple evaluation function."""
    if board.is_checkmate():
        return -9999 if board.turn else 9999
    if board.is_stalemate() or board.is_insufficient_material():
        return 0

    # Piece values
    piece_values = {
        chess.PAWN: 100,
        chess.KNIGHT: 320,
        chess.BISHOP: 330,
        chess.ROOK: 500,
        chess.QUEEN: 900,
        chess.KING: 20000
    }

    value = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            color_sign = 1 if piece.color == chess.WHITE else -1
            value += color_sign * piece_values[piece.piece_type]

    return value

def score_move(move, board):
    """Discourage early non-castling king moves."""
    piece = board.piece_at(move.from_square)
    if piece and piece.piece_type == chess.KING:
        if board.is_castling(move):
            return 10  # Allow castling
        return -100  # Discourage early king movement
    return 0

def order_moves(board):
    """Order moves to prioritize good ones."""
    moves = list(board.legal_moves)
    moves.sort(key=lambda move: score_move(move, board), reverse=True)
    return moves

def minimax(board, depth, alpha, beta, maximizing):
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)

    if maximizing:
        max_eval = -float('inf')
        for move in order_moves(board):
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float('inf')
        for move in order_moves(board):
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval

def find_best_move(board, depth=ENGINE_DEPTH):
    best_move = None
    best_value = -float('inf') if board.turn else float('inf')

    for move in order_moves(board):
        board.push(move)
        board_value = minimax(board, depth - 1, -float('inf'), float('inf'), not board.turn)
        board.pop()

        if board.turn:
            if board_value > best_value:
                best_value = board_value
                best_move = move
        else:
            if board_value < best_value:
                best_value = board_value
                best_move = move

    return best_move

def print_board(board):
    print(board)
    print()

def player_move(board):
    while True:
        try:
            user_input = input("Your move (e.g. e2e4): ").strip()
            move = chess.Move.from_uci(user_input)
            if move in board.legal_moves:
                return move
            else:
                print("Illegal move. Try again.")
        except Exception:
            print("Invalid input. Format should be like e2e4.")

def ai_move(board):
    move = find_best_move(board, depth=ENGINE_DEPTH)
    if move is None:
        print("AI resigns or has no legal moves.")
        return
    print(f"AI plays: {move}")
    board.push(move)

def main():
    board = chess.Board()
    print("Welcome to the Chess AI!")
    print("You are playing White. Enter moves in UCI format (e.g. e2e4).")
    print_board(board)

    while not board.is_game_over():
        if board.turn == chess.WHITE:
            move = player_move(board)
            board.push(move)
        else:
            ai_move(board)

        print_board(board)

    print("Game Over:", board.result())

if __name__ == "__main__":
    main()
