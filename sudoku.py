import streamlit as st
import time

# ==========================================
# 1. CORE ENGINE LOGIC (Your Exact Code)
# ==========================================
STARTING_BOARD = [
    [7, 8, 0, 4, 0, 0, 1, 2, 0],
    [6, 0, 0, 0, 7, 5, 0, 0, 9],
    [0, 0, 0, 6, 0, 1, 0, 7, 8],
    [0, 0, 7, 0, 4, 0, 2, 6, 0],
    [0, 0, 1, 0, 5, 0, 9, 3, 0],
    [9, 0, 4, 0, 6, 0, 0, 0, 5],
    [0, 7, 0, 3, 0, 0, 0, 1, 2],
    [1, 2, 0, 0, 0, 7, 4, 0, 0],
    [0, 4, 9, 2, 0, 6, 0, 0, 7]
]

def is_valid(b, num, pos):
    row, col = pos
    for j in range(9):
        if b[row][j] == num and col != j: return False
    for i in range(9):
        if b[i][col] == num and row != i: return False
    box_x, box_y = col // 3, row // 3
    for i in range(box_y * 3, box_y * 3 + 3):
        for j in range(box_x * 3, box_x * 3 + 3):
            if b[i][j] == num and (i, j) != pos: return False
    return True

def find_empty(b):
    for i in range(9):
        for j in range(9):
            if b[i][j] == 0: return (i, j)
    return None

def solve_backtrack(b):
    find = find_empty(b)
    if not find: return True
    row, col = find
    for i in range(1, 10):
        if is_valid(b, i, (row, col)):
            b[row][col] = i
            if solve_backtrack(b): return True
            b[row][col] = 0
    return False

# Generate master solution key once
if "solution_key" not in st.session_state:
    master_key = [row[:] for row in STARTING_BOARD]
    solve_backtrack(master_key)
    st.session_state.solution_key = master_key

# Initialize matrix state
if "current_matrix" not in st.session_state:
    st.session_state.current_matrix = [row[:] for row in STARTING_BOARD]

# ==========================================
# 2. CALLBACK FUNCTIONS (The Button Fix)
# ==========================================
def run_auto_solve():
    temp_board = [row[:] for row in STARTING_BOARD]
    start_time = time.time()
    if solve_backtrack(temp_board):
        elapsed = time.time() - start_time
        # Clear specific widget states from memory
        for r in range(9):
            for c in range(9):
                if f"cell_{r}_{c}" in st.session_state:
                    del st.session_state[f"cell_{r}_{c}"]
        st.session_state.current_matrix = temp_board
        st.session_state.solve_msg = f"✅ Solved by backtracking engine in {elapsed:.4f} seconds!"

def run_reset_board():
    for r in range(9):
        for c in range(9):
            if f"cell_{r}_{c}" in st.session_state:
                del st.session_state[f"cell_{r}_{c}"]
    st.session_state.current_matrix = [row[:] for row in STARTING_BOARD]
    if "solve_msg" in st.session_state:
        del st.session_state.solve_msg

# ==========================================
# 3. STATE INTERFACE RUNTIME & CSS
# ==========================================
st.set_page_config(page_title="Web Sudoku Engine", page_icon="🧩", layout="centered")
st.title("🧩 Autonomous Sudoku Solver")
st.caption("Interactive browser version of your PyQt5 engine layout")

st.markdown("""
    <style>
    div[data-testid="stHorizontalBlock"] {
        gap: 4px !important;
    }
    input {
        text-align: center !important;
        font-weight: bold !important;
        font-size: 20px !important;
        height: 42px !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 4. INTERACTIVE 9x9 GRID RENDERING
# ==========================================
for r in range(9):
    cols = st.columns(9)
    for c in range(9):
        original_val = STARTING_BOARD[r][c]
        current_val = st.session_state.current_matrix[r][c]
        
        if original_val != 0:
            cols[c].markdown(
                f"<div style='text-align:center; background-color:#E0E0E0; border-radius:4px; padding:8px; font-weight:bold; font-size:18px; color:#333;'>{original_val}</div>", 
                unsafe_allow_html=True
            )       
        else:
            val_str = str(current_val) if current_val != 0 else ""
            user_entry = cols[c].text_input(
                "", 
                value=val_str, 
                max_chars=1, 
                key=f"cell_{r}_{c}", 
                label_visibility="collapsed"
            )
            # Soft fallback update during manual typing
            if user_entry.isdigit() and 1 <= int(user_entry) <= 9:
                st.session_state.current_matrix[r][c] = int(user_entry)
            elif user_entry == "":
                st.session_state.current_matrix[r][c] = 0

st.markdown("---")

# ==========================================
# 5. ACTION TRIGGERS WITH DIRECT CALLBACKS
# ==========================================
btn_col1, btn_col2, btn_col3 = st.columns(3)

# Hooking click events directly to the memory modifier functions
btn_col1.button("🤖 Auto-Solve Board", use_container_width=True, on_click=run_auto_solve)

if btn_col2.button("🔍 Check My Answers", use_container_width=True):
    matrix = st.session_state.current_matrix
    error_found = False
    
    for r in range(9):
        for c in range(9):
            if STARTING_BOARD[r][c] == 0 and matrix[r][c] != 0:
                if matrix[r][c] != st.session_state.solution_key[r][c]:
                    st.error(f"❌ Mistake found at Row {r+1}, Column {c+1}!")
                    error_found = True
                    break
        if error_found: break
        
    if not error_found:
        if find_empty(matrix) is None:
            st.balloons()
            st.success("🎉 Congratulations! You perfectly solved the Sudoku board!")
        else:
            st.info("👍 Looking good so far! No mistakes found. Keep filling!")

btn_col3.button("🔄 Reset Board", use_container_width=True, type="secondary", on_click=run_reset_board)

# Display solve processing duration message if active
if "solve_msg" in st.session_state:
    st.info(st.session_state.solve_msg)
