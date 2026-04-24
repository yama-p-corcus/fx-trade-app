APP_STYLESHEET = """
QWidget {
    background-color: #f6fbf7;
    color: #223228;
    font-family: "Yu Gothic UI", "Segoe UI", sans-serif;
    font-size: 13px;
}

QMainWindow, QDialog {
    background-color: #f6fbf7;
}

QFrame#card {
    background: white;
    border: 1px solid #d7e8db;
    border-radius: 14px;
}

QPushButton {
    background-color: #3f8f63;
    color: white;
    border: none;
    border-radius: 10px;
    padding: 10px 16px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #367a54;
}

QPushButton:disabled {
    background-color: #a3c6ae;
    color: #edf5ef;
}

QPushButton[variant="secondary"] {
    background-color: #e8f2eb;
    color: #2d5f41;
    border: 1px solid #b8d3c0;
}

QPushButton[variant="danger"] {
    background-color: #cf5f5f;
}

QLineEdit, QTextEdit, QDateEdit, QTimeEdit, QDoubleSpinBox, QSpinBox, QComboBox, QTableWidget, QCalendarWidget {
    background: white;
    border: 1px solid #cddfcf;
    border-radius: 10px;
    padding: 6px 8px;
}

QHeaderView::section {
    background-color: #edf7ef;
    color: #284232;
    padding: 8px;
    border: none;
    border-bottom: 1px solid #d7e8db;
    font-weight: 600;
}

QTableWidget {
    gridline-color: #e3eee5;
    selection-background-color: #d8efde;
    selection-color: #1e3325;
}

QLabel[role="title"] {
    font-size: 24px;
    font-weight: 700;
    color: #294734;
}

QLabel[role="subtitle"] {
    color: #597261;
}
"""
