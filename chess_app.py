import streamlit as st
import socket
import chess
from stchess import board as render_web_board # <-- Updated this import line

# ==========================================
# 1. UI HEADER CONFIGURATION
# ==========================================
st.set_page_config(page_title="Multiplayer Chess Arena", page_icon="♔", layout="centered")
st.title("♔ Real-Time Multiplayer Chess")
st.caption("Connected to your multi-threaded backend socket server")

# ==========================================
# 2. MATCH SERVER SOCKET CONNECTION
# ==========================================
# Initialize persistent session states
if "socket_conn" not in st.session_state:
    try:
        # Connects to your running server loop
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(("localhost", 5555))
        role = client_socket.recv(1024).decode("utf-8")
        
        st.session_state.socket_conn = client_socket
        st.session_state.player_role = role
        st.session_state.local_board = chess.Board()
        st.session_state.last_move = None
    except Exception as e:
        st.error(f"⚠️ Connection Error: Could not bind to match server. Ensure server.py is running! ({e})")
        st.stop()

# Short-hand variables for readability
client_socket = st.session_state.socket_conn
player_role = st.session_state.player_role
board = st.session_state.local_board

# Display player identity badge on screen
if player_role == "Player 1":
    st.success("⚪ **You are Player 1 (White Pieces)**")
else:
    st.info("⚫ **You are Player 2 (Black Pieces)**")

# ==========================================
# 3. LIVE SERVER BACKGROUND SYNC
# ==========================================
try:
    # Query your server.py for the latest broadcasted move
    client_socket.send(str.encode("GET"))
    server_response = client_socket.recv(1024).decode("utf-8")
    
    if server_response != "No moves yet" and not server_response.startswith("Acknowledged"):
        if server_response != st.session_state.last_move:
            move = chess.Move.from_uci(server_response)
            if move in board.legal_moves:
                board.push(move)
                st.session_state.last_move = server_response
except Exception as e:
    st.sidebar.error(f"Data sync dropped: {e}")

# ==========================================
# 4. BROWSER GRID RENDERING & MOVE INTERACTION
# ==========================================
# Render the chess component inside the web browser canvas
board_orientation = "white" if player_role == "Player 1" else "black"
move_data = render_web_board(
    fen=board.fen(),
    orientation=board_orientation,
    key="interactive_chess_canvas"
)

# Handle move calculations when a player drops a piece on the web canvas
if move_data and "history" in move_data and len(move_data["history"]) > 0:
    # Extract the last move made by the user in UCI notation (e.g., 'e2e4')
    raw_last_move = move_data["history"][-1]
    
    # Check if turn matches role player constraints
    is_white_turn = board.turn == chess.WHITE
    is_valid_turn = (is_white_turn and player_role == "Player 1") or (not is_white_turn and player_role == "Player 2")
    
    if is_valid_turn and raw_last_move != st.session_state.last_move:
        try:
            proposed_move = chess.Move.from_uci(raw_last_move)
            if proposed_move in board.legal_moves:
                # Push locally to keep UI crisp
                board.push(proposed_move)
                st.session_state.last_move = raw_last_move
                
                # Broadcast the move string through your server.py thread loop
                client_socket.send(str.encode(raw_last_move))
                client_socket.recv(1024) # Clear acknowledgement response
                st.rerun()
        except Exception as e:
            pass

# ==========================================
# 5. SIDEBAR UTILITY CONTROLS
# ==========================================
with st.sidebar:
    st.subheader("📋 Match Metadata")
    st.text(f"Server Route: localhost:5555")
    st.text(f"Turn: {'White' if board.turn == chess.WHITE else 'Black'}")
    
    if st.button("🔄 Sync Server State", use_container_width=True, type="primary"):
        st.rerun()
