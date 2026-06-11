import streamlit as st
import chess
import chess.svg
import base64
import streamlit.components.v1 as components

# ==========================================
# 1. UI CONFIGURATION
# ==========================================
st.set_page_config(page_title="Premium Chess Arena", page_icon="♔", layout="centered")
st.title("♔ Autonomous Chess Arena")
st.caption("Interactive Premium SVG Canvas Driven Natively by Backend Logic")

# Session state initialization
if "board" not in st.session_state:
    st.session_state.board = chess.Board()
if "selected_square" not in st.session_state:
    st.session_state.selected_square = None
if "move_log" not in st.session_state:
    st.session_state.move_log = []

board = st.session_state.board

# ==========================================
# 2. SIDEBAR METADATA & RESET
# ==========================================
with st.sidebar:
    st.header("⚙️ Match Controller")
    st.markdown(f"**Turn:** {'⚪ White' if board.turn == chess.WHITE else '⚫ Black'}")
    st.markdown(f"**Moves Played:** {len(board.move_stack)}")
    
    if st.session_state.selected_square is not None:
        sq_name = chess.square_name(st.session_state.selected_square)
        st.info(f"🎯 Selected Square: **{sq_name.upper()}**")
        if st.button("❌ Clear Selection", use_container_width=True):
            st.session_state.selected_square = None
            st.rerun()
            
    st.markdown("---")
    if st.button("🔄 Reset Board Matrix", use_container_width=True, type="secondary"):
        st.session_state.board = chess.Board()
        st.session_state.selected_square = None
        st.session_state.move_log = []
        st.rerun()

# ==========================================
# 3. HIGH-RES SVG & NATIVE HTML INTERACTION
# ==========================================
fill_dict = {}
if st.session_state.selected_square is not None:
    fill_dict = {st.session_state.selected_square: "rgba(255, 204, 0, 0.6)"}

# Generate official high-res chess pieces & board vectors
board_svg = chess.svg.board(
    board=board,
    size=440,
    fill=fill_dict,
    coordinates=True
)

# Convert SVG to HTML Injection friendly script
svg_html = f"""
<div id="chess-board-container" style="width: 440px; height: 440px; cursor: pointer; margin: auto;">
    {board_svg}
</div>

<script>
    // Native JavaScript to capture the precise click coordinates on the SVG
    const container = document.getElementById('chess-board-container');
    container.addEventListener('click', function(e) {{
        const rect = container.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        // Calculate files (a-h) and ranks (1-8) based on canvas pixels
        // Standard chess padding accounts for ~18px margins for labels
        const margin = 19; 
        const cellSize = (440 - (margin * 2)) / 8;
        
        if (x > margin && x < 440 - margin && y > margin && y < 440 - margin) {{
            const file = Math.floor((x - margin) / cellSize);
            const rank = 7 - Math.floor((y - margin) / cellSize);
            
            // Send coordinates back to Streamlit components system
            const squareIndex = rank * 8 + file;
            window.parent.postMessage({{
                type: 'streamlit:setComponentValue',
                value: squareIndex
            }}, '*');
        }}
    }});
</script>
"""

st.write("### ♟️ Click Piece -> Click Target Square")

# Render the HTML Component container securely
# Streamlit components listen natively to postMessage updates
clicked_square = components.html(svg_html, height=450, width=450)

# Process clicks efficiently inside Streamlit's state architecture
if clicked_square is not None:
    # A click was captured!
    square_idx = int(clicked_square)
    
    if st.session_state.selected_square is None:
        # First click: Selection
        piece = board.piece_at(square_idx)
        if piece and piece.color == board.turn:
            st.session_state.selected_square = square_idx
            st.rerun()
    else:
        # Second click: Execution
        source_sq = st.session_state.selected_square
        target_sq = square_idx
        proposed_move = chess.Move(source_sq, target_sq)
        
        # Automatic queen promotion handling
        moving_piece = board.piece_at(source_sq)
        if moving_piece and moving_piece.piece_type == chess.PAWN and chess.square_rank(target_sq) in [0, 7]:
            proposed_move.promotion = chess.QUEEN
            
        if proposed_move in board.legal_moves:
            board.push(proposed_move)
            st.session_state.move_log.append(proposed_move.uci())
            st.toast(f"Moved: {proposed_move.uci()}", icon="⚔️")
            
        st.session_state.selected_square = None
        st.rerun()

st.markdown("---")

# ==========================================
# 4. MATCH HISTORY
# ==========================================
if st.session_state.move_log:
    st.markdown("### 📋 Match History")
    st.info(", ".join(st.session_state.move_log))
