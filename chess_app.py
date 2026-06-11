import streamlit as st
import chess
import chess.svg
import base64

# ==========================================
# 1. UI HEADER CONFIGURATION
# ==========================================
st.set_page_config(page_title="Chess Engine Sandbox", page_icon="♔", layout="centered")
st.title("♔ Autonomous Chess Arena")
st.caption("Pure SVG rendering driven by your backend python-chess rules")

# Initialize central board state in memory
if "sandbox_board" not in st.session_state:
    st.session_state.sandbox_board = chess.Board()
    st.session_state.move_log = []

board = st.session_state.sandbox_board

# ==========================================
# 2. SIDEBAR ENGINE METADATA & INPUT
# ==========================================
with st.sidebar:
    st.header("⚙️ Match Controller")
    st.markdown(f"**Active Turn:** {'⚪ White' if board.turn == chess.WHITE else '⚫ Black'}")
    st.markdown(f"**Total Moves:** {len(board.move_stack)}")
    st.markdown(f"**Checkmate:** {'⚠️ YES' if board.is_checkmate() else '❌ No'}")
    
    st.markdown("---")
    
    # Text input fallback for maximum reliability across Python 3.14
    st.subheader("♟️ Input Next Move")
    user_move = st.text_input("Enter UCI Move (e.g., e2e4, g1f3):", key="move_input_field").strip()
    
    if st.button("🚀 Submit Move", use_container_width=True, type="primary"):
        if user_move:
            try:
                proposed_move = chess.Move.from_uci(user_move)
                if proposed_move in board.legal_moves:
                    board.push(proposed_move)
                    st.session_state.move_log.append(user_move)
                    st.toast(f"Move {user_move} applied!", icon="✅")
                    st.rerun()
                else:
                    st.error("❌ Illegal move for this position!")
            except Exception:
                st.error("❌ Invalid syntax! Use format like e2e4.")

    if st.button("🔄 Reset Match Board", use_container_width=True, type="secondary"):
        st.session_state.sandbox_board = chess.Board()
        st.session_state.move_log = []
        st.rerun()

# ==========================================
# 3. DIRECT SVG BOARD RENDERING (Zero Bugs)
# ==========================================
# Generates high-res vector graphics on the fly
board_svg = chess.svg.board(board=board, size=450)
b64_svg = base64.b64encode(board_svg.encode('utf-8')).decode('utf-8')

# Centering the board natively via HTML injection
st.markdown(
    f'<div style="display: flex; justify-content: center;">'
    f'<img src="data:image/svg+xml;base64,{b64_svg}" width="450"/>'
    f'</div>',
    unsafe_allow_html=True
)

st.markdown("---")

# ==========================================
# 4. LIVE MOVE FEED
# ==========================================
if st.session_state.move_log:
    st.markdown("### 📋 Game Notation History")
    st.info(", ".join(st.session_state.move_log))
