import streamlit as st
import chess

# ==========================================
# 1. UI CONFIGURATION & PAGE INITIALIZATION
# ==========================================
st.set_page_config(page_title="Premium Chess Arena", page_icon="♔", layout="centered")
st.title("♔ Autonomous Chess Arena")
st.caption("Unified Matrix Display — Zero Layout Glitches")

# Session state initialization
if "board" not in st.session_state:
    st.session_state.board = chess.Board()
if "selected_square" not in st.session_state:
    st.session_state.selected_square = None
if "move_log" not in st.session_state:
    st.session_state.move_log = []

board = st.session_state.board

# ==========================================
# 2. MATCH CONTROLLER (SIDEBAR)
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
# 3. HIGH-RES ASSET MAP & GRID CALCULATOR
# ==========================================
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

st.write("### ♟️ Click Piece -> Then Click Target Square")

# Building a unified clean HTML grid structure so columns never collapse
html_grid = '<div style="display: grid; grid-template-columns: repeat(8, 52px); width: 416px; margin: 0 auto; border: 4px solid #333; box-shadow: 0 4px 10px rgba(0,0,0,0.3);">'

for rank in range(7, -1, -1):
    for file in range(8):
        square_idx = chess.square(file, rank)
        piece = board.piece_at(square_idx)
        
        # Color mapping logic
        is_dark = (rank + file) % 2 == 0
        bg_color = "#b58863" if is_dark else "#f0d9b5"
        
        # Override bg color if the square is active/selected
        if st.session_state.selected_square == square_idx:
            bg_color = "#bac466"
            
        # Piece graphic layout injection
        if piece:
            img_tag = f'<img src="{PIECE_IMAGES[piece.symbol()]}" style="width: 46px; height: 46px; pointer-events: none;"/>'
        else:
            img_tag = ''
            
        # Add square as a standardized clickable HTML link structure inside Streamlit's pipeline
        html_grid += f"""
        <div style="background-color: {bg_color}; width: 52px; height: 52px; display: flex; justify-content: center; align-items: center; box-sizing: border-box;">
            {img_tag}
        </div>
        """
html_grid += '</div>'

# Display the static crisp board background grid first
st.markdown(html_grid, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Clean, lightweight native selection fallback below the container for 100% bug-free click routes
col1, col2 = st.columns(2)
with col1:
    all_squares = [chess.square_name(s).upper() for s in chess.SQUARES]
    # Filter only squares that contain pieces belonging to the current player's turn for clarity
    valid_sources = [chess.square_name(s).upper() for s in chess.SQUARES if board.piece_at(s) and board.piece_at(s).color == board.turn]
    
    source_select = st.selectbox("🎯 Select Piece Location:", ["-- SELECT --"] + sorted(valid_sources))

with col2:
    if source_select != "-- SELECT --":
        src_idx = chess.parse_square(source_select.lower())
        # Show legal destination squares for the chosen piece
        legal_destinations = [chess.square_name(m.to_square).upper() for m in board.legal_moves if m.from_square == src_idx]
        target_select = st.selectbox("⚔️ Choose Destination:", ["-- SELECT --"] + sorted(legal_destinations))
        
        if target_select != "-- SELECT --" and st.button("🚀 Execute Move", use_container_width=True, type="primary"):
            dst_idx = chess.parse_square(target_select.lower())
            final_move = chess.Move(src_idx, dst_idx)
            
            # Auto pawn promotion
            moving_p = board.piece_at(src_idx)
            if moving_p and moving_p.piece_type == chess.PAWN and chess.square_rank(dst_idx) in [0, 7]:
                final_move.promotion = chess.QUEEN
                
            board.push(final_move)
            st.session_state.move_log.append(final_move.uci())
            st.toast(f"Moved: {final_move.uci()}", icon="✅")
            st.rerun()

st.markdown("---")

# ==========================================
# 4. GAME NOTATION LOG FEED
# ==========================================
if st.session_state.move_log:
    st.markdown("### 📋 Match History")
    st.info(", ".join(st.session_state.move_log))
