import streamlit as st
import chess
from stchess import board as render_web_board

# ==========================================
# 1. UI HEADER CONFIGURATION
# ==========================================
st.set_page_config(page_title="Chess Engine Sandbox", page_icon="♔", layout="centered")
st.title("♔ Autonomous Chess Arena")
st.caption("Interactive browser sandbox driven by your python-chess engine rules")

# Initialize a central board state in memory (No network socket needed)
if "sandbox_board" not in st.session_state:
    st.session_state.sandbox_board = chess.Board()
    st.session_state.move_log = []

board = st.session_state.sandbox_board

# ==========================================
# 2. SIDEBAR ENGINE METADATA
# ==========================================
with st.sidebar:
    st.header("⚙️ Match Controller")
    
    # Quick indicators for your presentation
    st.markdown(f"**Active Turn:** {'⚪ White' if board.turn == chess.WHITE else '⚫ Black'}")
    st.markdown(f"**Total Moves Played:** {len(board.move_stack)}")
    st.markdown(f"**Checkmate State:** {board.is_checkmate()}")
    
    st.markdown("---")
    if st.button("🔄 Reset Match Board", use_container_width=True, type="secondary"):
        st.session_state.sandbox_board = chess.Board()
        st.session_state.move_log = []
        st.rerun()

# ==========================================
# 3. BROWSER GRID RENDERING
# ==========================================
# Determines board orientation based on current turn
current_orientation = "white" if board.turn == chess.WHITE else "black"

move_data = render_web_board(
    fen=board.fen(),
    orientation=current_orientation,
    key="sandbox_chess_canvas"
)

# ==========================================
# 4. ENGINE MOVE VALIDATION LOOP
# ==========================================
if move_data and "history" in move_data and len(move_data["history"]) > 0:
    raw_last_move = move_data["history"][-1]
    
    # Check if this move is already in our history stack to prevent loops
    if len(st.session_state.move_log) == 0 or raw_last_move != st.session_state.move_log[-1]:
        try:
            proposed_move = chess.Move.from_uci(raw_last_move)
            if proposed_move in board.legal_moves:
                board.push(proposed_move)
                st.session_state.move_log.append(raw_last_move)
                st.rerun()
        except Exception:
            pass

# ==========================================
# 5. LIVE MOVE FEED
# ==========================================
if st.session_state.move_log:
    st.markdown("### 📋 Game Notation History")
    st.caption(", ".join(st.session_state.move_log))
