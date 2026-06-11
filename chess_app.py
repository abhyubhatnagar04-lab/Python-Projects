import streamlit as st
import chess
import chess.svg
import base64

st.set_page_config(page_title="Pro Chess Engine", layout="centered")
st.title("♟️ Autonomous Grandmaster Arena")

if "board" not in st.session_state:
    st.session_state.board = chess.Board()
if "source" not in st.session_state:
    st.session_state.source = None

# 1. Custom SVG board generator with clean click targets
def get_interactive_svg(board):
    # Hum SVG ko string format me lenge
    svg = chess.svg.board(board=board, size=500, coordinates=True)
    # SVG me hum 'onclick' javascript inject karenge
    svg = svg.replace("<svg", '<svg id="chess-board"')
    return svg

st.markdown("### ♟️ Click on any piece to select, then click target square")

# Display area
board_svg = get_interactive_svg(st.session_state.board)
# Hum yahan 'st.components.v1.html' ka use karenge taaki SVG native click events trigger kare
import streamlit.components.v1 as components

# Logic to handle clicks
click_js = """
<script>
    const board = document.getElementById('chess-board');
    board.addEventListener('click', function(e) {
        // Logic to calculate square from pixel click (500px board / 8 = 62.5px per cell)
        const rect = board.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        const file = Math.floor(x / 62.5);
        const rank = 7 - Math.floor(y / 62.5);
        const square = rank * 8 + file;
        
        window.parent.postMessage({type: 'streamlit:setComponentValue', value: square}, '*');
    });
</script>
"""

# Render
clicked_sq = components.html(board_svg + click_js, height=520, width=520)

# Backend logic processor
if clicked_sq is not None:
    sq = int(clicked_sq)
    if st.session_state.source is None:
        if st.session_state.board.piece_at(sq):
            st.session_state.source = sq
            st.toast(f"Selected: {chess.square_name(sq)}")
    else:
        move = chess.Move(st.session_state.source, sq)
        if move in st.session_state.board.legal_moves:
            st.session_state.board.push(move)
            st.session_state.source = None
            st.rerun()
        else:
            st.session_state.source = None
            st.toast("Illegal move, bhai!")
