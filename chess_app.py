import streamlit as st
import chess
import chess.svg
import base64

# ==========================================
# 1. UI CONFIGURATION
# ==========================================
st.set_page_config(page_title="Interactive Chess Arena", page_icon="♔", layout="centered")
st.title("♔ Autonomous Chess Arena")
st.caption("Click-to-Move Interactive Grid Powered Natively by Python-Chess")

# Session state initialization
if "board" not in st.session_state:
    st.session_state.board = chess.Board()
if "selected_square" not in st.session_state:
    st.session_state.selected_square = None
if "move_log" not in st.session_state:
    st.session_state.move_log = []

board = st.session_state.board

# ==========================================
# 2. MATCH METADATA & CONTROL PANEL
# ==========================================
with st.sidebar:
    st.header("⚙️ Game Controls")
    st.markdown(f"**Turn:** {'⚪ White' if board.turn == chess.WHITE else '⚫ Black'}")
    st.markdown(f"**Moves Played:** {len(board.move_stack)}")
    
    if st.session_state.selected_square is not None:
        sq_name = chess.square_name(st.session_state.selected_square)
        st.info(f"📍 Selected Piece Row/Col: **{sq_name.upper()}**")
        if st.button("❌ Cancel Selection", use_container_width=True):
            st.session_state.selected_square = None
            st.rerun()
    else:
        st.warning("🎯 Click any piece on the board below to select it.")

    st.markdown("---")
    if st.button("🔄 Reset Board", use_container_width=True, type="secondary"):
        st.session_state.board = chess.Board()
        st.session_state.selected_square = None
        st.session_state.move_log = []
        st.rerun()

# ==========================================
# 3. INTERACTIVE CLICK-GRID GENERATION
# ==========================================
# We build a functional 8x8 button grid overlapping the logic coordinates
cols_labels = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']

st.write("### ♟️ Click Piece -> Then Click Target Square")

# Render board from rank 8 down to 1
for rank in range(7, -1, -1):
    grid_cols = st.columns(8)
    for file in range(8):
        square_idx = chess.square(file, rank)
        piece = board.piece_at(square_idx)
        
        # Determine button label based on chess piece symbol
        btn_label = piece.symbol() if piece else "·"
        
        # Color styling logic for selection highlights
        if st.session_state.selected_square == square_idx:
            btn_label = f"⭐ {btn_label}"
            
        # Trigger interactive logic on square tap
        if grid_cols[file].button(btn_label, key=f"sq_{rank}_{file}", use_container_width=True):
            if st.session_state.selected_square is None:
                # First click: Select the source piece
                if piece and piece.color == board.turn:
                    st.session_state.selected_square = square_idx
                    st.rerun()
                else:
                    st.error("It's not your piece's turn!")
            else:
                # Second click: Execute move to target destination
                source_sq = st.session_state.selected_square
                target_sq = square_idx
                proposed_move = chess.Move(source_sq, target_sq)
                
                # Handle automatic pawn promotion to Queen
                if piece and piece.piece_type == chess.PAWN and rank in [0, 7]:
                    proposed_move.promotion = chess.QUEEN
                
                if proposed_move in board.legal_moves:
                    board.push(proposed_move)
                    st.session_state.move_log.append(proposed_move.uci())
                    st.toast(f"Move {proposed_move.uci()} applied successfully!")
                else:
                    st.error("❌ Illegal Move Attempted!")
                
                # Reset selection state
                st.session_state.selected_square = None
                st.rerun()

st.markdown("---")

# ==========================================
# 4. LIVE MOVE FEED
# ==========================================
if st.session_state.move_log:
    st.markdown("### 📋 Game Notation History")
    st.info(", ".join(st.session_state.move_log))
