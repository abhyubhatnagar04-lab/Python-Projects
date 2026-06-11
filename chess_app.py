import streamlit as st
from streamlit_chess_viewer import chess_viewer
import chess

st.set_page_config(page_title="Grandmaster Arena", layout="wide")
st.title("♟️ Professional Chess Interface")

if "board" not in st.session_state:
    st.session_state.board = chess.Board()

# Logic to handle moves from the viewer
move = chess_viewer(st.session_state.board.fen())

if move:
    try:
        st.session_state.board.push_san(move)
        st.rerun()
    except:
        pass

st.sidebar.info("Drag and drop to play. No typing required.")
if st.sidebar.button("Reset Game"):
    st.session_state.board = chess.Board()
    st.rerun()
