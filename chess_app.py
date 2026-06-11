import streamlit as st
import chess

st.set_page_config(page_title="Chess Arena", layout="centered")
st.title("♟️ Professional Chess Arena")

# CSS: Button ko pura invisible/absolute ghost bana diya hai
st.markdown("""
    <style>
    .stButton > button {
        background: transparent !important;
        border: none !important;
        height: 50px !important;
        width: 100% !important;
        color: transparent !important;
    }
    .stButton > button:hover { background: rgba(255, 255, 255, 0.2) !important; }
    div[data-testid="column"] { padding: 0 !important; margin: 0 !important; }
    </style>
""", unsafe_allow_html=True)

if "board" not in st.session_state:
    st.session_state.board = chess.Board()
if "source" not in st.session_state:
    st.session_state.source = None

# Piece Unicode (Size badha diya taaki board pe dikhe)
PIECES = {'P': '♙', 'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔',
          'p': '♟', 'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚'}

board = st.session_state.board
for rank in range(7, -1, -1):
    cols = st.columns(8)
    for file in range(8):
        sq = chess.square(file, rank)
        piece = board.piece_at(sq)
        bg = "#b58863" if (rank + file) % 2 == 0 else "#f0d9b5"
        
        # Piece display logic
        symbol = PIECES.get(piece.symbol(), " ") if piece else " "
        
        with cols[file]:
            # Div ke andar Piece dikha rahe hain, button upar invisible hai
            st.markdown(f'<div style="background-color:{bg}; height:50px; display:flex; align-items:center; justify-content:center; font-size:30px;">{symbol}</div>', unsafe_allow_html=True)
            if st.button(" ", key=f"sq_{sq}"):
                if st.session_state.source is None:
                    if piece and piece.color == board.turn:
                        st.session_state.source = sq
                else:
                    move = chess.Move(st.session_state.source, sq)
                    if move in board.legal_moves:
                        board.push(move)
                    st.session_state.source = None
                    st.rerun()

if st.button("Reset Game"):
    st.session_state.board = chess.Board()
    st.rerun()
