import pygame
import socket
import chess
import io
import base64

pygame.init()
pygame.font.init()

WIDTH, HEIGHT = 600, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Real Multiplayer Chess Client")

WHITE_SQUARE = (240, 217, 181)
BLACK_SQUARE = (181, 136, 99)
HIGHLIGHT_COLOR = (130, 151, 105)

chess_board = chess.Board()
selected_square = None
last_applied_move = None
player_role = None  

PIECE_IMAGES = {}

# Keeping your exact structure intact so nothing breaks
SPRITE_DATA = {
    "P": b"placeholder", "R": b"placeholder", "N": b"placeholder", "B": b"placeholder", "Q": b"placeholder", "K": b"placeholder",
    "p": b"placeholder", "r": b"placeholder", "n": b"placeholder", "b": b"placeholder", "q": b"placeholder", "k": b"placeholder"
}

def load_piece_sprites():
    square_size = WIDTH // 8
    
    # We build ultra-crisp vector shapes on a massive 4x supersampled canvas,
    # then scale it down with smooth anti-aliasing so it looks incredibly sharp.
    SCALE = 4
    s = square_size * SCALE
    
    for symbol in ["P", "R", "N", "B", "Q", "K", "p", "r", "n", "b", "q", "k"]:
        try:
            surf = pygame.Surface((s, s), pygame.SRCALPHA)
            
            # Premium color palette: Cream white vs Deep Charcoal
            color = (245, 242, 235) if symbol.isupper() else (45, 45, 48)
            outline = (30, 30, 30) if symbol.isupper() else (240, 240, 245)
            lw = 3 * SCALE  # Scale line width for the high-res canvas
            
            p_type = symbol.upper()
            
            # --- HIGH DEFINITION VECTOR SILHOUETTE DRAWING ---
            if p_type == "P":  # PAWN
                pygame.draw.ellipse(surf, color, (int(s*0.25), int(s*0.72), int(s*0.5), int(s*0.16)))
                pygame.draw.ellipse(surf, outline, (int(s*0.25), int(s*0.72), int(s*0.5), int(s*0.16)), lw)
                
                body = [(s*0.32, s*0.75), (s*0.68, s*0.75), (s*0.58, s*0.42), (s*0.42, s*0.42)]
                pygame.draw.polygon(surf, color, body)
                pygame.draw.polygon(surf, outline, body, lw)
                
                pygame.draw.circle(surf, color, (s//2, int(s*0.35)), int(s*0.16))
                pygame.draw.circle(surf, outline, (s//2, int(s*0.35)), int(s*0.16), lw)

            elif p_type == "R":  # ROOK
                pygame.draw.rect(surf, color, (int(s*0.22), int(s*0.35), int(s*0.56), int(s*0.5)))
                pygame.draw.rect(surf, outline, (int(s*0.22), int(s*0.35), int(s*0.56), int(s*0.5)), lw)
                
                pygame.draw.rect(surf, color, (int(s*0.18), int(s*0.22), int(s*0.64), int(s*0.15)))
                pygame.draw.rect(surf, outline, (int(s*0.18), int(s*0.22), int(s*0.64), int(s*0.15)), lw)
                
                # Dynamic Castle Cutouts
                for cx in [int(s*0.32), int(s*0.58)]:
                    pygame.draw.rect(surf, (0,0,0,0), (cx, int(s*0.22), int(s*0.1), int(s*0.08)))

            elif p_type == "N":  # KNIGHT
                points = [(s*0.22, s*0.8), (s*0.78, s*0.8), (s*0.72, s*0.55), (s*0.52, s*0.4), 
                          (s*0.68, s*0.22), (s*0.48, s*0.12), (s*0.26, s*0.25), (s*0.22, s*0.48), (s*0.38, s*0.58)]
                pygame.draw.polygon(surf, color, points)
                pygame.draw.polygon(surf, outline, points, lw)
                
                eye_color = (20, 20, 20) if symbol.isupper() else (250, 250, 250)
                pygame.draw.circle(surf, eye_color, (int(s*0.44), int(s*0.26)), int(s*0.03))

            elif p_type == "B":  # BISHOP
                pygame.draw.ellipse(surf, color, (int(s*0.22), int(s*0.75), int(s*0.56), int(s*0.13)))
                pygame.draw.ellipse(surf, outline, (int(s*0.22), int(s*0.75), int(s*0.56), int(s*0.13)), lw)
                
                pygame.draw.ellipse(surf, color, (int(s*0.28), int(s*0.25), int(s*0.44), int(s*0.54)))
                pygame.draw.ellipse(surf, outline, (int(s*0.28), int(s*0.25), int(s*0.44), int(s*0.54)), lw)
                
                # Mitre Cross
                pygame.draw.rect(surf, color, (int(s*0.46), int(s*0.14), int(s*0.08), int(s*0.13)))
                pygame.draw.rect(surf, color, (int(s*0.38), int(s*0.18), int(s*0.24), int(s*0.05)))

            elif p_type == "Q":  # QUEEN
                q_points = [(s*0.18, s*0.78), (s*0.82, s*0.78), (s*0.88, s*0.32), (s*0.68, s*0.52), 
                            (s*0.5, s*0.2), (s*0.32, s*0.52), (s*0.12, s*0.32)]
                pygame.draw.polygon(surf, color, q_points)
                pygame.draw.polygon(surf, outline, q_points, lw)
                
                for crown_x, crown_y in [(int(s*0.12), int(s*0.32)), (int(s*0.5), int(s*0.2)), (int(s*0.88), int(s*0.32))]:
                    pygame.draw.circle(surf, color, (crown_x, crown_y), int(s*0.04))
                    pygame.draw.circle(surf, outline, (crown_x, crown_y), int(s*0.04), int(lw//1.5))

            elif p_type == "K":  # KING
                pygame.draw.rect(surf, color, (int(s*0.22), int(s*0.35), int(s*0.56), int(s*0.46)))
                pygame.draw.rect(surf, outline, (int(s*0.22), int(s*0.35), int(s*0.56), int(s*0.46)), lw)
                
                pygame.draw.rect(surf, color, (int(s*0.45), int(s*0.14), int(s*0.1), int(s*0.23)))
                pygame.draw.rect(surf, color, (int(s*0.36), int(s*0.2), int(s*0.28), int(s*0.07)))
                pygame.draw.rect(surf, outline, (int(s*0.45), int(s*0.14), int(s*0.1), int(s*0.23)), int(lw//1.5))
                pygame.draw.rect(surf, outline, (int(s*0.36), int(s*0.2), int(s*0.28), int(s*0.07)), int(lw//1.5))

            # Downsample the high-res surface using smoothscale to get perfectly anti-aliased sharp edges
            PIECE_IMAGES[symbol] = pygame.transform.smoothscale(surf, (square_size, square_size))
        except Exception as e:
            print(f"Failed parsing local data asset for: {symbol} - {e}")

load_piece_sprites()

def draw_board():
    square_size = WIDTH // 8
    for row in range(8):
        for col in range(8):
            # --- PERSPECTIVE FLIP LOGIC ---
            display_row = 7 - row if player_role == "Player 2" else row
            display_col = 7 - col if player_role == "Player 2" else col
            
            chess_row = 7 - display_row
            chess_col = display_col
            square_idx = chess.square(chess_col, chess_row)
            
            color = WHITE_SQUARE if (display_row + display_col) % 2 == 0 else BLACK_SQUARE
            if selected_square == square_idx:
                color = HIGHLIGHT_COLOR
                
            pygame.draw.rect(WIN, color, (col * square_size, row * square_size, square_size, square_size))
            
            piece = chess_board.piece_at(square_idx)
            if piece:
                sym = piece.symbol()
                if sym in PIECE_IMAGES:
                    WIN.blit(PIECE_IMAGES[sym], (col * square_size, row * square_size))

def get_square_under_mouse():
    mouse_pos = pygame.mouse.get_pos()
    col = mouse_pos[0] // (WIDTH // 8)
    row = mouse_pos[1] // (HEIGHT // 8)
    
    # --- PERSPECTIVE MOUSE CLICK FLIP ---
    if player_role == "Player 2":
        col = 7 - col
        row = 7 - row
        
    chess_row = 7 - row
    return chess.square(col, chess_row)

def main():
    global selected_square, last_applied_move, player_role
    run = True
    clock = pygame.time.Clock()

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect(("localhost", 5555))
        player_role = client_socket.recv(2048).decode()
        print(f"Connected to match server successfully as: {player_role}")
    except Exception as e:
        print(f"Could not connect to server: {e}")
        run = False

    while run:
        clock.tick(60)
        
        try:
            client_socket.send(str.encode("GET"))
            server_response = client_socket.recv(2048).decode("utf-8")
            
            if server_response != "No moves yet" and not server_response.startswith("Acknowledged"):
                if server_response != last_applied_move:
                    move = chess.Move.from_uci(server_response)
                    if move in chess_board.legal_moves:
                        chess_board.push(move)
                        last_applied_move = server_response
        except Exception as e:
            pass

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                square_clicked = get_square_under_mouse()
                
                if selected_square is not None:
                    move = chess.Move(selected_square, square_clicked)
                    
                    piece = chess_board.piece_at(selected_square)
                    if piece and piece.piece_type == chess.PAWN:
                        if chess.square_rank(square_clicked) in [0, 7]:
                            move.promotion = chess.QUEEN
                    
                    if move in chess_board.legal_moves:
                        chess_board.push(move)
                        move_uci = move.uci()
                        last_applied_move = move_uci
                        
                        try:
                            client_socket.send(str.encode(move_uci))
                            client_socket.recv(2048)
                        except Exception as e:
                            print(f"Failed sending move: {e}")
                            
                    selected_square = None
                else:
                    is_white_turn = chess_board.turn == chess.WHITE
                    if is_white_turn and player_role != "Player 1":
                        continue
                    if not is_white_turn and player_role != "Player 2":
                        continue
                        
                    piece = chess_board.piece_at(square_clicked)
                    if piece:
                        if (piece.color == chess.WHITE and player_role == "Player 1") or \
                           (piece.color == chess.BLACK and player_role == "Player 2"):
                            selected_square = square_clicked

        WIN.fill((255, 255, 255))
        draw_board()
        pygame.display.update()

    client_socket.close()
    pygame.quit()

if __name__ == "__main__":
    main()