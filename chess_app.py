import streamlit as st
import chess

# ==========================================
# 1. UI CONFIGURATION & PROFESSIONAL STYLING
# ==========================================
st.set_page_config(page_title="Premium Chess Arena", page_icon="♔", layout="centered")
st.title("♔ Autonomous Chess Arena")
st.caption("Professional Graphical Board — 100% Fail-Proof Click Mechanics")

# Injecting clean CSS to load beautiful background blocks and size the image buttons
st.markdown("""
    <style>
    /* Dark square styling */
    div.stButton > button.css-dark-sq, div.stButton > button[key^="dark_"] {
        background-color: #b58863 !important;
        height: 60px !important;
        width: 100% !important;
        border: none !important;
        border-radius: 0px !important;
        padding: 0 !important;
    }
    /* Light square styling */
    div.stButton > button.css-light-sq, div.stButton > button[key^="light_"] {
        background-color: #f0d9b5 !important;
        height: 60px !important;
        width: 100% !important;
        border: none !important;
        border-radius: 0px !important;
        padding: 0 !important;
    }
    /* Hover highlight */
    div.stButton > button:hover {
        border: 3px solid #ffcc00 !important;
    }
    /* Grid alignment fix */
    div[data-testid="stHorizontalBlock"] {
        gap: 0px !important;
        margin-bottom: 0px !important;
    }
    </style>
""", unsafe_allow_html=True)

# Wikimedia commons links for standard high-quality chess pieces
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

# Session state initialization
if "board" not in st.session_state:
    st.session_state.board = chess.Board()
if "selected_square" not in st.session_state:
    st.session_state.selected_square = None
if "move_log" not in st.session_state:
    st.session_state.move_log = []

board = st.session_state.board

# ==========================================
# 2. SIDEBAR GAME CONTROLLER
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
# 3. INTERACTIVE BOARD GENERATION
# ==========================================
st.write("### ♟️ Click Piece -> Then Click Target Square")

# Render 8x8 functional grid
for rank in range(7, -1, -1):
    grid_cols = st.columns(8)
    for file in range(8):
        square_idx = chess.square(file, rank)
        piece = board.piece_at(square_idx)
        
        # Alternate background colors
        is_dark = (rank + file) % 2 == 0
        sq_type = "dark" if is_dark else "light"
        
        # Visual styling configuration
        if st.session_state.selected_square == square_idx:
            # Highlight selected piece border natively via markdown label
            btn_content = "⭐"
        elif piece:
            # Embed image URL directly into the button layout using HTML
            img_url = PIECE_IMAGES[piece.symbol()]
            btn_content = f'<img src="{img_url}" width="45" height="45"/>'
        else:
            btn_content = " "
            
        # Execute button rendering
        if grid_cols[file].button(btn_content, key=f"{sq_type}_{rank}_{file}", use_container_width=True):
            if st.session_state.selected_square is None:
                # First click: Select Piece
                if piece and piece.color == board.turn:
                    st.session_state.selected_square = square_idx
                    st.rerun()
                else:
                    st.error("Not your turn / Empty square!")
            else:
                # Second click: Move Execution
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
                    st.error("❌ Illegal Move!")
                
                st.session_state.selected_square = None
                st.rerun()

st.markdown("---")

# ==========================================
# 4. NOTATION LOG FEED
# ==========================================
if st.session_state.move_log:
    st.markdown("### 📋 Match History")
    st.info(", ".join(st.session_state.move_log))
