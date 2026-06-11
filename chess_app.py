import streamlit as st
import chess
import base64

# Setup
st.set_page_config(page_title="Pro Chess Arena", layout="centered")
st.title("♟️ Professional Chess Arena")

if "board" not in st.session_state:
    st.session_state.board = chess.Board()

# Generate SVG Board using python-chess (Native)
def get_svg(board):
    return chess.svg.board(board=board, size=500)

st.info("System Ready. Use terminal input for moves (UCI format) while the backend maintains the board.")

# Move input logic
move = st.text_input("Enter Move (e.g., e2e4):")
if st.button("Submit Move"):
    try:
        st.session_state.board.push_uci(move)
        st.rerun()
    except:
        st.error("Illegal move, bhai!")

# Display
svg = get_svg(st.session_state.board)
st.image(f"data:image/svg+xml;base64,{base64.b64encode(svg.encode()).decode()}", use_container_width=True)

if st.button("Reset"):
    st.session_state.board = chess.Board()
    st.rerun()
