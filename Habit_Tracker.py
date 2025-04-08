import sys
import json
import datetime
from datetime import date
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QListWidget,
                             QListWidgetItem, QDialog, QLineEdit, QTabWidget,
                             QCalendarWidget, QMessageBox)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QColor

class Habit:
    def __init__(self, name, description="", color="#4299e1"):
        self.id = str(hash(name + str(datetime.datetime.now())))
        self.name = name
        self.description = description
        self.created_at = date.today().isoformat()
        self.completed_dates = []
        self.streak_count = 0
        self.color = color
       
    def complete_today(self):
        today = date.today().isoformat()
        if today not in self.completed_dates:
            self.completed_dates.append(today)
            self.calculate_streak()
            return True
        return False
   
    def uncomplete_today(self):
        today = date.today().isoformat()
        if today in self.completed_dates:
            self.completed_dates.remove(today)
            self.calculate_streak()
            return True
        return False
   
    def calculate_streak(self):
        # Simple streak calculation
        streak = 0
        sorted_dates = sorted(self.completed_dates)
       
        if not sorted_dates:
            self.streak_count = 0
            return
           
        today = date.today()
        for i in range(len(sorted_dates)-1, -1, -1):
            date_obj = date.fromisoformat(sorted_dates[i])
            days_diff = (today - date_obj).days
           
            if days_diff == streak:
                streak += 1
            else:
                break
               
        self.streak_count = streak

class HabitForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Habit")
        self.setMinimumWidth(300)
       
        layout = QVBoxLayout()
       
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Habit Name")
       
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Description (optional)")
       
        self.save_button = QPushButton("Save Habit")
        self.save_button.clicked.connect(self.accept)
       
        layout.addWidget(QLabel("Habit Name:"))
        layout.addWidget(self.name_input)
        layout.addWidget(QLabel("Description:"))
        layout.addWidget(self.desc_input)
        layout.addWidget(self.save_button)
       
        self.setLayout(layout)
       
    def get_habit_data(self):
        return {
            "name": self.name_input.text(),
            "description": self.desc_input.text()
        }

class HabitItem(QWidget):
    def __init__(self, habit, on_complete=None, on_delete=None):
        super().__init__()
        self.habit = habit
        self.on_complete = on_complete
        self.on_delete = on_delete
       
        layout = QHBoxLayout()
       
        # Color indicator
        self.color_label = QLabel()
        self.color_label.setFixedSize(20, 20)
        self.color_label.setStyleSheet(f"background-color: {habit.color}; border-radius: 10px;")
       
        # Habit info
        info_layout = QVBoxLayout()
        self.name_label = QLabel(habit.name)
        self.name_label.setStyleSheet("font-weight: bold; font-size: 14px;")
       
        self.streak_label = QLabel(f"Streak: {habit.streak_count} days")
       
        info_layout.addWidget(self.name_label)
        if habit.description:
            self.desc_label = QLabel(habit.description)
            self.desc_label.setStyleSheet("color: gray;")
            info_layout.addWidget(self.desc_label)
        info_layout.addWidget(self.streak_label)
       
        # Buttons
        self.complete_button = QPushButton("Complete")
        self.complete_button.clicked.connect(self.toggle_complete)
       
        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(lambda: self.on_delete(self.habit.id))
       
        today = date.today().isoformat()
        if today in habit.completed_dates:
            self.complete_button.setText("Completed ✓")
            self.complete_button.setStyleSheet("background-color: #68D391;")
       
        layout.addWidget(self.color_label)
        layout.addLayout(info_layout, 1)
        layout.addWidget(self.complete_button)
        layout.addWidget(self.delete_button)
       
        self.setLayout(layout)
       
    def toggle_complete(self):
        today = date.today().isoformat()
        if today in self.habit.completed_dates:
            self.habit.uncomplete_today()
            self.complete_button.setText("Complete")
            self.complete_button.setStyleSheet("")
        else:
            self.habit.complete_today()
            self.complete_button.setText("Completed ✓")
            self.complete_button.setStyleSheet("background-color: #68D391;")
           
        self.streak_label.setText(f"Streak: {self.habit.streak_count} days")
       
        if self.on_complete:
            self.on_complete()

class HabitTracker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Habit Tracker")
        self.setMinimumSize(800, 600)
       
        self.habits = []
        self.load_habits()
       
        # Create main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
       
        # Create tab widget
        self.tabs = QTabWidget()
       
        # Today tab
        self.today_tab = QWidget()
        today_layout = QVBoxLayout()
       
        # Add habit button
        add_button = QPushButton("Add New Habit")
        add_button.clicked.connect(self.show_add_habit_form)
        today_layout.addWidget(add_button)
       
        # Habits list
        self.habit_list = QListWidget()
        self.update_habit_list()
        today_layout.addWidget(self.habit_list)
       
        self.today_tab.setLayout(today_layout)
       
        # Calendar tab
        self.calendar_tab = QWidget()
        calendar_layout = QVBoxLayout()
        self.calendar = QCalendarWidget()
        calendar_layout.addWidget(self.calendar)
        self.calendar_tab.setLayout(calendar_layout)
       
        # Stats tab
        self.stats_tab = QWidget()
        stats_layout = QVBoxLayout()
        stats_layout.addWidget(QLabel("Stats will be shown here"))
        self.stats_tab.setLayout(stats_layout)
       
        # Add tabs to tab widget
        self.tabs.addTab(self.today_tab, "Today")
        self.tabs.addTab(self.calendar_tab, "Calendar")
        self.tabs.addTab(self.stats_tab, "Stats")
       
        main_layout.addWidget(self.tabs)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
       
    def load_habits(self):
        try:
            with open("habits.json", "r") as file:
                habits_data = json.load(file)
                for habit_data in habits_data:
                    habit = Habit(habit_data["name"], habit_data.get("description", ""))
                    habit.id = habit_data["id"]
                    habit.created_at = habit_data["created_at"]
                    habit.completed_dates = habit_data["completed_dates"]
                    habit.streak_count = habit_data["streak_count"]
                    habit.color = habit_data.get("color", "#4299e1")
                    self.habits.append(habit)
        except (FileNotFoundError, json.JSONDecodeError):
            # Create sample habits if no file exists
            sample_habits = [
                Habit("Morning Meditation", "10 minutes of mindfulness", "#9F7AEA"),
                Habit("Read a Book", "At least 20 pages", "#F6AD55"),
                Habit("Exercise", "30 minutes workout", "#F56565")
            ]
            self.habits = sample_habits
           
    def save_habits(self):
        habits_data = []
        for habit in self.habits:
            habits_data.append({
                "id": habit.id,
                "name": habit.name,
                "description": habit.description,
                "created_at": habit.created_at,
                "completed_dates": habit.completed_dates,
                "streak_count": habit.streak_count,
                "color": habit.color
            })
           
        with open("habits.json", "w") as file:
            json.dump(habits_data, file)
           
    def update_habit_list(self):
        self.habit_list.clear()
        for habit in self.habits:
            item = QListWidgetItem()
            habit_widget = HabitItem(
                habit,
                on_complete=lambda: self.save_habits(),
                on_delete=self.delete_habit
            )
            item.setSizeHint(habit_widget.sizeHint())
           
            self.habit_list.addItem(item)
            self.habit_list.setItemWidget(item, habit_widget)
   
    def show_add_habit_form(self):
        form = HabitForm(self)
        result = form.exec_()
       
        if result == QDialog.Accepted:
            data = form.get_habit_data()
            if data["name"]:
                habit = Habit(data["name"], data["description"])
                self.habits.append(habit)
                self.save_habits()
                self.update_habit_list()
            else:
                QMessageBox.warning(self, "Invalid Input", "Habit name cannot be empty!")
   
    def delete_habit(self, habit_id):
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            "Are you sure you want to delete this habit?",
            QMessageBox.Yes | QMessageBox.No
        )
       
        if reply == QMessageBox.Yes:
            self.habits = [h for h in self.habits if h.id != habit_id]
            self.save_habits()
            self.update_habit_list()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HabitTracker()
    window.show()
    sys.exit(app.exec_())

