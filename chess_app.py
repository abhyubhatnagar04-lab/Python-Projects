import streamlit as st
import chess

# ==========================================
# 1. UI CONFIGURATION & BOARD STYLING
# ==========================================
st.set_page_config(page_title="Premium Chess Arena", page_icon="♔", layout="centered")
st.title("♔ Autonomous Chess Arena")
st.caption("Clean Graphical Matrix — High-Resolution Asset Rendering")

# Minimal CSS to align grid cells smoothly
st.markdown("""
    <style>
    div[data-testid="stHorizontalBlock"] {
        gap: 0px !important;
        margin-bottom: 0px !important;
    }
    div[data-testid="column"] {
        padding: 0px !important;
        text-align: center !important;
    }
    /* Highlight effect for selections */
    .selected-sq {
        border: 3px solid #ffcc00 !important;
        box-sizing: border-box;
    }
    </style>
""", unsafe_allow_html=True)

# Wikimedia high-quality chess pieces URLs
PIECE_IMAGES = {
    'P': 'https://upload.wikimedia.org/wikipedia/commons/4/45/Chess_plt45.svg',
    'R': 'https://upload.wikimedia.org/wikipedia/commons/7/72/Chess_rlt45.svg',
    'N': 'https://upload.wikimedia.org/wikipedia/commons/7/70/Chess_nlt45.svg',
    'B': 'https://upload.wikimedia.org/wikipedia/commons/b/b1/Chess_blt45.svg',
    'Q': 'https://upload.wikimedia.org/wikipedia/commons/1/15/Chess_qlt45.svg',
    'K': 'https://upload.wikimedia.org/wikipedia/commons/4/42/Chess_klt45.svg',
    'p': 'https://upload.wikimedia.org/wikipedia/commons/c/c7/Chess_pdt45.svg',
    'r': 'https://upload.wikimedia.org/wikipedia/commons/f/ff/Chess_rdt45.svg',
    'n': 'https://upload.wikimedia.org/wikipedia/commons/e/ef/Chess_ndt45.svg',
    'b': 'https://upload.wikimedia.org/wikipedia/commons/9/98/Chess_bdt45.svg',
    'q': 'https://upload.wikimedia.org/wikipedia/commons/4/47/Chess_qdt45.svg',
    'k': 'https://upload.wikimedia.org/wikipedia/commons/f/f0/Chess_kdt45.svg'
}

# Fallback transparent placeholder for empty squares so layout stays intact
EMPTY_SQUARE = "https://upload.wikimedia.org/wikipedia/commons/c/ca/1x1.png"

# Session state initialization
if "board" not in st.session_state:
    st.session_state.board = chess.Board()
if "selected_square" not in st.session_state:
    st.session_state.selected_square = None
if "move_log" not in st.session_state:
    st.session_state.move_log = []

board = st.session_state.board

# ==========================================
# 2. SIDEBAR METADATA PANEL
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
        st.warning("💡 Click a piece to select, then click target square.")

    st.markdown("---")
    if st.button("🔄 Reset Board Matrix", use_container_width=True, type="secondary"):
        st.session_state.board = chess.Board()
        st.session_state.selected_square = None
        st.session_state.move_log = []
        st.rerun()

# ==========================================
# 3. GRAPHICAL 8x8 GRID VIA ST.IMAGE
# ==========================================
st.write("### ♟️ Click Piece -> Then Click Target Square")

for rank in range(7, -1, -1):
    grid_cols = st.columns(8)
    for file in range(8):
        square_idx = chess.square(file, rank)
        piece = board.piece_at(square_idx)
        
        # Get appropriate piece asset URL
        img_url = PIECE_IMAGES[piece.symbol()] if piece else EMPTY_SQUARE
        
        # Render clean image directly using Streamlit's native image container
        # We use st.button with an overlay or a helper text below it for solid activation
        is_selected = st.session_state.selected_square == square_idx
        btn_caption = "⭐" if is_selected else f"{chess.square_name(square_idx).upper()}"
        
        with grid_cols[file]:
            st.image(img_url, width=48)
            # Small structural button directly under the asset for 100% click reliability
            if st.button(btn_caption, key=f"btn_{rank}_{file}", use_container_width=True):
                if st.session_state.selected_square is None:
                    # First click: Selection
                    if piece and piece.color == board.turn:
                        st.session_state.selected_square = square_idx
                        st.rerun()
                    else:
                        st.toast("⚠️ Select your own active color piece!", icon="👀")
                else:
                    # Second click: Execution
                    source_sq = st.session_state.selected_square
                    target_sq = square_idx
                    proposed_move = chess.Move(source_sq, target_sq)
                    
                    # Pawn promotion logic
                    moving_piece = board.piece_at(source_sq)
                    if moving_piece and moving_piece.piece_type == chess.PAWN and rank in [0, 7]:
                        proposed_move.promotion = chess.QUEEN
                        
                    if proposed_move in board.legal_moves:
                        board.push(proposed_move)
                        st.session_state.move_log.append(proposed_move.uci())
                        st.toast(f"Moved: {proposed_move.uci()}", icon="⚔️")
                    else:
                        st.toast("❌ Illegal Move Attempted!", icon="🚫")
                    
                    st.session_state.selected_square = None
                    st.rerun()

st.markdown("---")

# ==========================================
# 4. GAME LOG FEED
# ==========================================
if st.session_state.move_log:
    st.markdown("### 📋 Match History")
    st.info(", ".join(st.session_state.move_log))
