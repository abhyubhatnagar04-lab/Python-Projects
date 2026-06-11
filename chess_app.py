import streamlit as st
import chess
import chess.svg
import base64

st.set_page_config(page_title="Click-to-Move Chess", layout="centered")
st.title("♔ Autonomous Chess Arena")

# Initialize Session State
if "board" not in st.session_state:
    st.session_state.board = chess.Board()
if "source" not in st.session_state:
    st.session_state.source = None

# Game Logic Fragment (Fixed for 2026 Streamlit)
@st.fragment
def render_board():
    board = st.session_state.board
    
    # 8x8 Grid
    for rank in range(7, -1, -1):
        cols = st.columns(8)
        for file in range(8):
            sq = chess.square(file, rank)
            piece = board.piece_at(sq)
            
            # Button Label (Piece or empty)
            label = piece.symbol() if piece else " "
            
            if cols[file].button(label, key=f"sq_{sq}"):
                if st.session_state.source is None:
                    # First click: Select
                    if piece and piece.color == board.turn:
                        st.session_state.source = sq
                else:
                    # Second click: Move
                    move = chess.Move(st.session_state.source, sq)
                    
                    # Handle Pawn Promotion (Auto Queen)
                    if piece and piece.piece_type == chess.PAWN and (rank == 0 or rank == 7):
                        move.promotion = chess.QUEEN
                    
                    if move in board.legal_moves:
                        board.push(move)
                    
                    st.session_state.source = None
                    st.rerun()

    # Display Board
    svg = chess.svg.board(board=board, size=400)
    st.image(f"data:image/svg+xml;base64,{base64.b64encode(svg.encode()).decode()}", use_container_width=True)

render_board()

if st.button("Reset Game"):
    st.session_state.board = chess.Board()
    st.rerun()
