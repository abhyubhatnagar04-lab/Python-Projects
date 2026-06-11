import streamlit as st
import chess

st.set_page_config(page_title="Chess Arena", layout="centered")
st.title("♟️ Professional Chess Arena")

# CSS to make buttons invisible/transparent and fit perfectly in the grid
st.markdown("""
    <style>
    div[data-testid="column"] { padding: 0px !important; }
    .stButton > button {
        width: 100% !important;
        height: 50px !important;
        padding: 0 !important;
        border: none !important;
        background: transparent !important;
    }
    .sq-light { background-color: #f0d9b5; }
    .sq-dark { background-color: #b58863; }
    </style>
""", unsafe_allow_html=True)

if "board" not in st.session_state:
    st.session_state.board = chess.Board()
if "source" not in st.session_state:
    st.session_state.source = None

# Piece Unicode
PIECES = {'P': '♙', 'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔',
          'p': '♟', 'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚'}

# Board Rendering
board = st.session_state.board
for rank in range(7, -1, -1):
    cols = st.columns(8)
    for file in range(8):
        sq = chess.square(file, rank)
        piece = board.piece_at(sq)
        bg = "sq-dark" if (rank + file) % 2 == 0 else "sq-light"
        
        # Display piece if exists
        symbol = PIECES.get(piece.symbol(), " ") if piece else " "
        
        # Render button
        with cols[file]:
            st.markdown(f'<div class="{bg}">', unsafe_allow_html=True)
            if st.button(symbol, key=f"sq_{sq}"):
                if st.session_state.source is None:
                    if piece and piece.color == board.turn:
                        st.session_state.source = sq
                else:
                    move = chess.Move(st.session_state.source, sq)
                    if move in board.legal_moves:
                        board.push(move)
                    st.session_state.source = None
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

if st.button("Reset Game"):
    st.session_state.board = chess.Board()
    st.rerun()
