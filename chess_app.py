import streamlit as st
import chess
from streamlit_chess_viewer import chess_viewer

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
    
    st.markdown(f"**Active Turn:** {'⚪ White' if board.turn == chess.WHITE else '⚫ Black'}")
    st.markdown(f"**Total Moves Played:** {len(board.move_stack)}")
    st.markdown(f"**Checkmate State:** {'⚠️ Yes' if board.is_checkmate() else '❌ No'}")
    
    st.markdown("---")
    
    # Manual text entry fallback for maximum reliability across Python 3.14
    st.subheader("♟️ Input Next Move")
    user_move = st.text_input("Enter UCI Move (e.g., e2e4, g1f3):", key="move_input_field").strip()
    
    if st.button("🚀 Submit Move", use_container_width=True, type="primary"):
        if user_move:
            try:
                proposed_move = chess.Move.from_uci(user_move)
                if proposed_move in board.legal_moves:
                    board.push(proposed_move)
                    st.session_state.move_log.append(user_move)
                    st.success(f"Move {user_move} applied successfully!")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("❌ Illegal move for the current board state!")
            except Exception:
                st.error("❌ Invalid format! Please use standard UCI syntax (e.g., e2e4).")

    if st.button("🔄 Reset Match Board", use_container_width=True, type="secondary"):
        st.session_state.sandbox_board = chess.Board()
        st.session_state.move_log = []
        st.rerun()

# ==========================================
# 3. BROWSER GRID RENDERING
# ==========================================
# Renders the board as a beautiful, static SVG asset generated directly by python-chess
chess_viewer(fen=board.fen())

# ==========================================
# 4. LIVE MOVE FEED
# ==========================================
if st.session_state.move_log:
    st.markdown("### 📋 Game Notation History")
    st.info(", ".join(st.session_state.move_log))
