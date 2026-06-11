import streamlit as st
import chess

# ==========================================
# 1. UI CONFIGURATION & TOURNAMENT GRID STYLING
# ==========================================
st.set_page_config(page_title="Premium Chess Arena", page_icon="♔", layout="centered")
st.title("♔ Autonomous Chess Arena")
st.caption("Clean Graphical Matrix — Professional Asset Presentation")

# Heavy styling to make text buttons look like clean, invisible grid helpers
st.markdown("""
    <style>
    /* Dark squares text and background override */
    div.stButton > button[key^="btn_dark_"] {
        background-color: #b58863 !important;
        color: rgba(240, 217, 181, 0.4) !important; /* Extremely faint dot color */
        border: none !important;
        border-radius: 0px !important;
        height: 32px !important;
        font-size: 14px !important;
        font-weight: bold !important;
    }
    /* Light squares text and background override */
    div.stButton > button[key^="btn_light_"] {
        background-color: #f0d9b5 !important;
        color: rgba(181, 136, 99, 0.4) !important; /* Extremely faint dot color */
        border: none !important;
        border-radius: 0px !important;
        height: 32px !important;
        font-size: 14px !important;
        font-weight: bold !important;
    }
    /* Hover highlight feedback */
    div.stButton > button:hover {
        border: 2px solid #ffcc00 !important;
        background-color: rgba(255, 204, 0, 0.3) !important;
    }
    /* Eliminate padding bloat between ranks */
    div[data-testid="stHorizontalBlock"] {
        gap: 0px !important;
        margin-bottom: 0px !important;
        background-color: #e0d6cd;
    }
    div[data-testid="column"] {
        padding: 2px !important;
        text-align: center !important;
        box-sizing: border-box;
    }
    /* Box container background colors */
    .chess-cell-box {
        padding: 4px;
        border-radius: 2px;
        transition: all 0.2s;
    }
    </style>
""", unsafe_allow_html=True)

# High-quality vector graphics links for pieces
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
# 2. SIDEBAR INFORMATION PANEL
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
        st.warning("💡 Click a piece row tile to select, then click target square.")

    st.markdown("---")
    if st.button("🔄 Reset Board Matrix", use_container_width=True, type="secondary"):
        st.session_state.board = chess.Board()
        st.session_state.selected_square = None
        st.session_state.move_log = []
        st.rerun()

# ==========================================
# 3. GRAPHICAL 8x8 GRID WITH CLEAN LABELS
# ==========================================
st.write("### ♟️ Click Piece -> Then Click Target Square")

for rank in range(7, -1, -1):
    grid_cols = st.columns(8)
    for file in range(8):
        square_idx = chess.square(file, rank)
        piece = board.piece_at(square_idx)
        
        is_dark = (rank + file) % 2 == 0
        bg_color = "#b58863" if is_dark else "#f0d9b5"
        sq_type = "dark" if is_dark else "light"
        
        # FIXED: Replacing clunky coordinate text with a subtle dot or selection star
        is_selected = st.session_state.selected_square == square_idx
        btn_caption = "🟢" if is_selected else "•" 
        
        img_url = PIECE_IMAGES[piece.symbol()] if piece else EMPTY_SQUARE
        
        with grid_cols[file]:
            st.markdown(
                f'<div class="chess-cell-box" style="background-color: {bg_color};">', 
                unsafe_allow_html=True
            )
            st.image(img_url, width=44)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Interactive action trigger block
            if grid_cols[file].button(btn_caption, key=f"btn_{sq_type}_{rank}_{file}", use_container_width=True):
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
# 4. GAME NOTATION LOG FEED
# ==========================================
if st.session_state.move_log:
    st.markdown("### 📋 Match History")
    st.info(", ".join(st.session_state.move_log))
