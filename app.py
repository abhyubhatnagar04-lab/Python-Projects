import sys
import csv
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, 
                             QVBoxLayout, QHBoxLayout, QComboBox, QCheckBox, 
                             QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView)

class AdvancedSchedulerUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("Camp Activity Scheduler Pro")
        self.resize(600, 650)
        
        main_layout = QVBoxLayout()
        
        # --- SECTION 1: DROPDOWNS ---
        settings_layout = QHBoxLayout()
        
        group_label = QLabel("Number of Groups:")
        self.group_dropdown = QComboBox()
        self.group_dropdown.addItems(["3", "4", "5"])
        
        week_label = QLabel("Select Week:")
        self.week_dropdown = QComboBox()
        self.week_dropdown.addItems(["Week 1", "Week 2", "Week 3"])
        
        settings_layout.addWidget(group_label)
        settings_layout.addWidget(self.group_dropdown)
        settings_layout.addWidget(week_label)
        settings_layout.addWidget(self.week_dropdown)
        main_layout.addLayout(settings_layout)
        
        # --- SECTION 2: ACTIVITY CHECKBOXES ---
        activity_group = QGroupBox("Available Activities")
        activity_layout = QVBoxLayout()
        
        self.activities = {
            "Soccer": QCheckBox("Soccer"),
            "Basketball": QCheckBox("Basketball"),
            "Tennis": QCheckBox("Tennis"),
            "Lacrosse": QCheckBox("Lacrosse"),
            "Football": QCheckBox("Football")
        }
        
        for checkbox in self.activities.values():
            checkbox.setChecked(True)
            activity_layout.addWidget(checkbox)
            
        activity_group.setLayout(activity_layout)
        main_layout.addWidget(activity_group)
        
        # --- SECTION 3: GENERATE BUTTON ---
        self.generate_btn = QPushButton("Generate & Display Schedule")
        self.generate_btn.clicked.connect(self.handle_generation)
        main_layout.addWidget(self.generate_btn)
        
        # --- SECTION 4: IN-APP VISUAL TABLE DISPLAY ---
        self.table = QTableWidget()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        main_layout.addWidget(self.table)
        
        self.status_label = QLabel("Status: Idle. Ready to generate.")
        self.status_label.setWordWrap(True)
        main_layout.addWidget(self.status_label)
        
        self.setLayout(main_layout)

    # --- SECTION 5: BACKTRACKING LOGIC WITH ROTATION ---
    def solve_schedule(self, groups, periods, allowed_activities, schedule, group_idx, period_idx):
        # Base Case: All slots assigned
        if group_idx == len(groups):
            return True
            
        # Calculate next coordinates
        next_group = group_idx + 1 if period_idx == len(periods) - 1 else group_idx
        next_period = 0 if period_idx == len(periods) - 1 else period_idx + 1
        
        current_group = groups[group_idx]
        current_period = periods[period_idx]
        
        # If it's Period 3, it's globally locked for Lunch. Skip to next slot!
        if current_period == "Period 3 (Lunch)":
            schedule[current_group][current_period] = "LUNCH 🍔"
            return self.solve_schedule(groups, periods, allowed_activities, schedule, next_group, next_period)
        
        # Try assigning activities
        for activity in allowed_activities:
            conflict = False
            
            # CONSTRAINT 1 (Vertical): Is another group doing this sport in this exact period?
            for other_group in groups:
                if schedule[other_group][current_period] == activity:
                    conflict = True
                    break
            
            # CONSTRAINT 2 (Horizontal): Has THIS group already done this sport in a different period today?
            if not conflict:
                for p in periods:
                    if schedule[current_group][p] == activity:
                        conflict = True
                        break
            
            # If it passes both rules, assign it temporarily
            if not conflict:
                schedule[current_group][current_period] = activity
                
                if self.solve_schedule(groups, periods, allowed_activities, schedule, next_group, next_period):
                    return True
                
                # Backtrack if it causes an issue down the line
                schedule[current_group][current_period] = None
                
        return False

    def handle_generation(self):
        num_groups = int(self.group_dropdown.currentText())
        week_name = self.week_dropdown.currentText()
        
        groups = [f"Group {i+1}" for i in range(num_groups)]
        periods = ["Period 1", "Period 2", "Period 3 (Lunch)", "Period 4"]
        
        active_activities = [name for name, cb in self.activities.items() if cb.isChecked()]
        
        if len(active_activities) < num_groups:
            self.status_label.setText("Error: Need more activities checked than total groups!")
            return
            
        # Initialize matrix
        schedule_matrix = {g: {p: None for p in periods} for g in groups}
        
        success = self.solve_schedule(groups, periods, active_activities, schedule_matrix, 0, 0)
        
        if success:
            # Populate UI Table
            self.table.setRowCount(len(groups))
            self.table.setColumnCount(len(periods))
            self.table.setHorizontalHeaderLabels(periods)
            self.table.setVerticalHeaderLabels(groups)
            
            for row_idx, group in enumerate(groups):
                for col_idx, period in enumerate(periods):
                    item_text = schedule_matrix[group][period]
                    self.table.setItem(row_idx, col_idx, QTableWidgetItem(item_text))
            
            # Export CSV backend safely with UTF-8 encoding
            filename = f"schedule_{week_name.lower().replace(' ', '_')}.csv"
            with open(filename, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["Camp Group"] + periods)
                for group in groups:
                    row = [group] + [schedule_matrix[group][p] for p in periods]
                    writer.writerow(row)
                    
            self.status_label.setText(f"Success! Balanced schedule built and saved to {filename}")
        else:
            self.status_label.setText("Could not resolve a perfect rotation schedule. Try checking more available activities.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = AdvancedSchedulerUI()
    ex.show()
    sys.exit(app.exec_())