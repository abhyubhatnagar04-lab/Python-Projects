import sys
import time
from PyQt5.QtWidgets import (QApplication, QWidget, QGridLayout, QLineEdit, 
                             QPushButton, QVBoxLayout, QHBoxLayout, QLabel)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIntValidator

class SudokuGame(QWidget):
    def __init__(self):
        super().__init__()
        # 0 represents empty editable cells
        self.starting_board = [
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
        self.grid_cells = [[None for _ in range(9)] for _ in range(9)]
        
        # NEW: Generate the solution key right at the start based on original clues
        self.solution_key = [row[:] for row in self.starting_board]
        self.solve_backtrack(self.solution_key)
        
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("Interactive Sudoku Game")
        self.resize(500, 550)
        
        main_layout = QVBoxLayout()
        
        # Create 9x9 Grid layout for Sudoku cells
        grid_layout = QGridLayout()
        grid_layout.setSpacing(2) # Tight layout mimicking a real board
        
        # Validator to restrict input to single digits 1-9
        only_digits = QIntValidator(1, 9)
        
        for row in range(9):
            for col in range(9):
                cell = QLineEdit()
                cell.setAlignment(Qt.AlignCenter)
                cell.setFont(QFont("Arial", 16, QFont.Bold))
                cell.setValidator(only_digits)
                cell.setMaxLength(1)
                
                # Visual styling: Make grid square blocks distinct
                # Darker borders for the 3x3 box boundaries
                top = 3 if row % 3 == 0 and row != 0 else 1
                left = 3 if col % 3 == 0 and col != 0 else 1
                
                val = self.starting_board[row][col]
                if val != 0:
                    # Pre-filled starting numbers are locked and styled differently
                    cell.setText(str(val))
                    cell.setReadOnly(True)
                    cell.setStyleSheet(f"background-color: #E0E0E0; color: #333; border-top: {top}px solid black; border-left: {left}px solid black; border-bottom: 1px solid #A0A0A0; border-right: 1px solid #A0A0A0;")
                else:
                    # User playable cells
                    cell.setStyleSheet(f"background-color: #FFFFFF; color: #0055FF; border-top: {top}px solid black; border-left: {left}px solid black; border-bottom: 1px solid #A0A0A0; border-right: 1px solid #A0A0A0;")
                
                grid_layout.addWidget(cell, row, col)
                self.grid_cells[row][col] = cell
                
        main_layout.addLayout(grid_layout)
        
        # Action Buttons Layout
        btn_layout = QHBoxLayout()
        
        self.solve_btn = QPushButton("Auto-Solve Board")
        self.solve_btn.clicked.connect(self.trigger_solver)
        btn_layout.addWidget(self.solve_btn)
        
        self.check_btn = QPushButton("Check My Answers")
        self.check_btn.clicked.connect(self.check_player_answers)
        btn_layout.addWidget(self.check_btn)
        
        main_layout.addLayout(btn_layout)
        
        self.status_label = QLabel("Status: Play mode! Fill in the blue numbers.")
        self.status_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.status_label)
        
        self.setLayout(main_layout)

    # --- CORE LOGIC RESOLVER HOOKED TO ENGINE ---
    def get_current_board_state(self):
        """Reads integers out of the visual grid setup"""
        current_matrix = []
        for r in range(9):
            row_data = []
            for c in range(9):
                text = self.grid_cells[r][c].text()
                row_data.append(int(text) if text != "" else 0)
            current_matrix.append(row_data)
        return current_matrix

    def is_valid(self, b, num, pos):
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

    def find_empty(self, b):
        for i in range(9):
            for j in range(9):
                if b[i][j] == 0: return (i, j)
        return None

    def solve_backtrack(self, b):
        find = self.find_empty(b)
        if not find: return True
        row, col = find
        for i in range(1, 10):
            if self.is_valid(b, i, (row, col)):
                b[row][col] = i
                if self.solve_backtrack(b): return True
                b[row][col] = 0
        return False

    def trigger_solver(self):
        """Runs the backtracking tool and fills the UI cells instantly"""
        board_state = self.get_current_board_state()
        start = time.time()
        if self.solve_backtrack(board_state):
            elapsed = time.time() - start
            for r in range(9):
                for c in range(9):
                    self.grid_cells[r][c].setText(str(board_state[r][c]))
            self.status_label.setText(f"Solved by backtracking engine in {elapsed:.4f} seconds!")
        else:
            self.status_label.setText("Error: Current configuration has conflicts and cannot be solved.")

    def check_player_answers(self):
        """Compares user inputs directly against the pre-calculated valid solution key"""
        b = self.get_current_board_state()
        
        for r in range(9):
            for c in range(9):
                # Only check editable cells where the user actually entered a number
                if self.starting_board[r][c] == 0 and b[r][c] != 0:
                    # If their entry doesn't match the master solution, it's definitely a mistake
                    if b[r][c] != self.solution_key[r][c]:
                        self.status_label.setText(f"Found a mistake! Check cell at Row {r+1}, Column {c+1}.")
                        return
        
        if self.find_empty(b) is None:
            self.status_label.setText("Congratulations! You perfectly solved the Sudoku board! 🎉")
        else:
            self.status_label.setText("Looking good so far! No current mistakes found. Keep going!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    game = SudokuGame()
    game.show()
    sys.exit(app.exec_())