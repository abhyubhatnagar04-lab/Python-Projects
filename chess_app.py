import streamlit as st
import chess

# ==========================================
# 1. UI CONFIGURATION & STYLING
# ==========================================
st.set_page_config(page_title="Premium Chess Arena", page_icon="♔", layout="centered")
st.title("♔ Autonomous Chess Arena")
st.caption("Responsive Click-to-Move Matrix — High-Contrast Tournament Theme")

# Custom CSS for high-quality professional board colors
st.markdown("""
    <style>
    /* Dark square styling */
    div.stButton > button.css-dark-sq, div.stButton > button[key^="dark_"] {
        background-color: #b58863 !important;
        color: #f0d9b5 !important;
        font-size: 28px !important;
        height: 55px !important;
        width: 100% !important;
        border: none !important;
        border-radius: 0px !important;
    }
    /* Light square styling */
    div.stButton > button.css-light-sq, div.stButton > button[key^="light_"] {
        background-color: #f0d9b5 !important;
        color: #b58863 !important;
        font-size: 28px !important;
        height: 55px !important;
        width: 100% !important;
        border: none !important;
        border-radius: 0px !important;
    }
    /* Hover effects for clean feedback */
    div.stButton > button:hover {
        border: 2px solid #ffcc00 !important;
        cursor: pointer;
    }
    /* Grid alignment fix */
    div[data-testid="stHorizontalBlock"] {
        gap: 0px !important;
        margin-bottom: 0px !important;
    }
    </style>
""", unsafe_allow_html=True)

# Unicode dictionary for premium stylized pieces
UNICODE_PIECES = {
    'R': '♜', 'N': '♞', 'B': '♝', 'Q': '♛', 'K': '♚', 'P': '♟',
    'r': '♖', 'n': '♘', 'b': '♗', 'q': '♕', 'k': '♔', 'p': '♙',
    '.': ' '
}

# Session state initialization
if "board" not in st.session_state:
    st.session_state.board = chess.Board()
if "selected_square" not in st.session_state:
    st.session_state.selected_square = None
if "move_log" not in st.session_state:
    st.session_state.move_log = []

board = st.session_state.board

# ==========================================
# 2. SIDEBAR METADATA
# ==========================================
with st.sidebar:
    st.header("⚙️ Match Controller")
    st.markdown(f"**Turn:** {'⚪ White' if board.turn == chess.WHITE else '⚫ Black'}")
    st.markdown(f"**Moves Played:** {len(board.move_stack)}")
    
    if st.session_state.selected_square is not None:
        sq_name = chess.square_name(st.session_state.selected_square)
        st.info(f"🎯 Selected: **{sq_name.upper()}**")
        if st.button("❌ Cancel Selection", use_container_width=True):
            st.session_state.selected_square = None
            st.rerun()
    else:
        st.warning("💡 Click a piece to select, then click destination.")

    st.markdown("---")
    if st.button("🔄 Reset Board Matrix", use_container_width=True, type="secondary"):
        st.session_state.board = chess.Board()
        st.session_state.selected_square = None
        st.session_state.move_log = []
        st.rerun()

# ==========================================
# 3. INTERACTIVE 8x8 GRID GENERATION
# ==========================================
st.write("### ♟️ Game Board")

# Container for perfect board centering
board_container = st.container()
with board_container:
    for rank in range(7, -1, -1):
        grid_cols = st.columns(8)
        for file in range(8):
            square_idx = chess.square(file, rank)
            piece = board.piece_at(square_idx)
            
            # Get symbol
            symbol = UNICODE_PIECES[piece.symbol()] if piece else " "
            
            # Selection marker overlay
            if st.session_state.selected_square == square_idx:
                symbol = f"⭐"
            
            # Alternate board square colors natively
            is_dark = (rank + file) % 2 == 0
            sq_type = "dark" if is_dark else "light"
            
            # Render bulletproof native button
            if grid_cols[file].button(symbol, key=f"{sq_type}_{rank}_{file}", use_container_width=True):
                if st.session_state.selected_square is None:
                    # First click: Select
                    if piece and piece.color == board.turn:
                        st.session_state.selected_square = square_idx
                        st.rerun()
                    else:
                        st.error("Not your turn!")
                else:
                    # Second click: Move execution
                    source_sq = st.session_state.selected_square
                    target_sq = square_idx
                    proposed_move = chess.Move(source_sq, target_sq)
                    
                    # Pawn promotion
                    moving_piece = board.piece_at(source_sq)
                    if moving_piece and moving_piece.piece_type == chess.PAWN and rank in [0, 7]:
                        proposed_move.promotion = chess.QUEEN
                        
                    if proposed_move in board.legal_moves:
                        board.push(proposed_move)
                        st.session_state.move_log.append(proposed_move.uci())
                        st.toast(f"Applied: {proposed_move.uci()}", icon="⚔️")
                    else:
                        st.error("❌ Illegal Move!")
                    
                    st.session_state.selected_square = None
                    st.rerun()

st.markdown("---")

# ==========================================
# 4. MATCH HISTORY
# ==========================================
if st.session_state.move_log:
    st.markdown("### 📋 Match History")
    st.info(", ".join(st.session_state.move_log))
