import streamlit as st
import chess
import chess.svg
import base64

# Sandbox layout - Isme koi bahar ki CSS ghus nahi sakti
def render_sandbox_chess():
    if "board" not in st.session_state: st.session_state.board = chess.Board()
    
    # SVG Board
    svg = chess.svg.board(board=st.session_state.board, size=400)
    
    # HTML + JS sandbox (Bahar ki CSS ka ispe asar nahi hoga)
    html_code = f"""
    <div id="board-container" style="width: 400px;">{svg}</div>
    <script>
        document.getElementById('board-container').addEventListener('click', (e) => {{
            // Pixel calculation logic for independent board
            const rect = e.target.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            const file = Math.floor(x / 50);
            const rank = 7 - Math.floor(y / 50);
            const sq = rank * 8 + file;
            window.parent.postMessage({{type: 'click', sq: sq}}, '*');
        }});
    </script>
    """
    return html_code

st.title("♟️ Isolated Chess Agent")
# Component render
clicked_data = st.components.v1.html(render_sandbox_chess(), height=420)
