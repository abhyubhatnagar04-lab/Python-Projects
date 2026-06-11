import streamlit as st
import chess
import chess.svg
import base64

# ==========================================
# 1. UI SETUP & ANIMATED OVERLAY
# ==========================================
st.set_page_config(page_title="Pro Chess Engine", layout="centered")
st.title("♟️ Autonomous Grandmaster Arena")
st.markdown("<style>#chess-board { transition: transform 0.3s ease; }</style>", unsafe_allow_html=True)

if "board" not in st.session_state:
    st.session_state.board = chess.Board()

board = st.session_state.board

# ==========================================
# 2. ANIMATED SVG RENDERING
# ==========================================
# Hum board ko high-quality vector me generate karte hain
def get_board_svg(board):
    return chess.svg.board(board=board, size=480, coordinates=True)

# Visual state handling
col1, col2 = st.columns([2, 1])

with col1:
    # SVG render jo browser me animate hota hai
    board_svg = get_board_svg(board)
    st.image(f"data:image/svg+xml;base64,{base64.b64encode(board_svg.encode()).decode()}", use_container_width=True)

with col2:
    st.subheader("Match Console")
    move = st.text_input("Enter Move (e.g., e2e4):")
    if st.button("Play Move"):
        try:
            board.push_san(move) if len(move) > 4 else board.push_uci(move)
            st.rerun()
        except:
            st.error("Invalid move, bhai!")

# History Section
st.write("---")
st.write("### Game Log")
st.code(board.move_stack)
