import re
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QSpacerItem, QSizePolicy, QHeaderView, QGroupBox, QFormLayout, QMessageBox, QScrollArea
)
from PyQt5.QtCore import Qt
from database import Database  # Ensure you have a Database class for database operations
from dialogs import AboutDialog  # Import the AboutDialog

class LibraryManagementSystem(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Library Management System")
        self.setGeometry(70, 100, 1200, 800)

        self.db = Database()
        self.currently_updating = False
        self.selected_book_id = None  # Initialize selected_book_id as None
        self.initUI()

    def initUI(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()

        self.setStyleSheet("background-color: black; color: white;")

        # Header Section with 'ABOUT' button
        header_layout = QHBoxLayout()
        header = self.create_header()
        about_button = self.create_about_button()

        header_layout.addWidget(header, 1)
        header_layout.addWidget(about_button)

        main_layout.addLayout(header_layout)

        # Body Section
        body_layout = QVBoxLayout()
        content_area = self.create_content_area()
        body_layout.addWidget(content_area)
        main_layout.addLayout(body_layout)

        main_widget.setLayout(main_layout)

        self.load_books()

    def create_header(self):
        header = QLabel("LIMKOKWING UNIVERSITY LIBRARY MANAGEMENT SYSTEM")
        header.setStyleSheet(
            "font-size: 33px; font-weight: bold; color: white; padding: 16px; background-color: gray; border-radius: 12px;")
        header.setAlignment(Qt.AlignCenter)
        return header

    def create_about_button(self):
        button = QPushButton("ABOUT")
        button.setFixedSize(100, 30)
        button.setStyleSheet(
            """
            font-size: 10px;
            padding: 8px;
            background-color: blue;
            color: white;
            border: none;
            border-radius: 10px;
            """
        )
        button.clicked.connect(self.show_about)
        return button

    def create_content_area(self):
        content_area = QWidget()
        content_layout = QHBoxLayout()

        # Group box with form inputs, including borders
        form_group_box = QGroupBox("Book Details")
        form_group_box.setStyleSheet(""" 
            background-color: #333; 
            border-radius: 10px; 
            padding: 10px;
            border-left: 3px solid white;
            border-right: 3px solid white;
            border-top: 3px solid white;
        """)
        form_layout = QFormLayout()

        # Input Fields
        self.title_input = self.create_input_field("Enter Book Title")
        form_layout.addRow("Title:", self.title_input)

        self.author_input = self.create_input_field("Enter Author Name")
        form_layout.addRow("Author:", self.author_input)

        self.isbn_input = self.create_input_field("Enter ISBN")
        form_layout.addRow("ISBN:", self.isbn_input)

        self.genre_input = self.create_input_field("Enter Genre")
        form_layout.addRow("Genre:", self.genre_input)

        self.year_input = self.create_input_field("Enter Year of Publication")
        form_layout.addRow("Year:", self.year_input)

        form_group_box.setLayout(form_layout)

        # Buttons Section with consistent styling
        button_layout = QVBoxLayout()
        clear_button = self.create_button("CLEAR FIELDS", "blue", self.clear_fields)
        button_layout.addWidget(clear_button)

        add_button = self.create_button("ADD BOOK", "green", self.add_book)
        button_layout.addWidget(add_button)

        update_button = self.create_button("UPDATE BOOK", "orange", self.update_book)
        button_layout.addWidget(update_button)

        delete_button = self.create_button("DELETE BOOK", "red", self.delete_book)
        button_layout.addWidget(delete_button)

        # Search Book section
        self.search_input = self.create_input_field("Enter title or ISBN to search")
        self.search_input.setVisible(False)  # Hide the search field initially
        search_button = self.create_button("SEARCH BOOK", "purple", self.toggle_search_field)
        button_layout.addWidget(search_button)

        # Back button to return to all books
        self.back_button = self.create_button("BACK TO ALL", "gray", self.load_books)
        self.back_button.setVisible(False)  # Initially hidden
        button_layout.addWidget(self.back_button)

        button_layout.setAlignment(Qt.AlignTop)
        form_layout.addRow(button_layout)

        # Table with Scroll (same borders as form)
        self.table = self.create_table()

        # Add Table to Scroll Area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.table)
        scroll_area.setStyleSheet(""" 
            border-left: 3px solid black;
            border-right: 3px solid black;
            border-bottom: 3px solid black;
        """)

        content_layout.addWidget(form_group_box, 1)
        content_layout.addWidget(scroll_area, 2)

        content_area.setLayout(content_layout)
        return content_area

    def create_input_field(self, placeholder_text):
        input_field = QLineEdit()
        input_field.setPlaceholderText(placeholder_text)
        input_field.setFixedWidth(250)
        input_field.setStyleSheet(
            "font-size: 16px; padding: 10px; border-radius: 5px; border: 1px solid white; color: white; background-color: black;")
        return input_field

    def create_button(self, text, color, action):
        button = QPushButton(text)
        button.setStyleSheet(f"padding: 8px; background-color: {color}; color: white; font-size: 12px; border-radius: 5px;")
        button.setFixedSize(150, 35)
        button.clicked.connect(action)
        return button

    def create_table(self):
        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels(["ID", "Title", "Author", "ISBN", "Genre", "Year"])
        table.setStyleSheet("background-color:black; color: white; font-size: 13px; border: 1px white;")

        # Set the header text color to black
        header = table.horizontalHeader()
        header.setStyleSheet("color: black; background-color: white;")

        # Set the row number text color to black
        vertical_header = table.verticalHeader()
        vertical_header.setStyleSheet("color: black; background-color: white;")

        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.itemSelectionChanged.connect(self.populate_fields_for_update)
        return table

    def load_books(self):
        query = "SELECT id, title, author, isbn, genre, year FROM books"
        books = self.db.fetch_all(query)
        self.table.setRowCount(0)
        for row_data in books:
            row_number = self.table.rowCount()
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

        self.back_button.setVisible(False)  # Hide the back button when showing all books

    def add_book(self):
        title = self.title_input.text()
        author = self.author_input.text()
        isbn = self.isbn_input.text()
        genre = self.genre_input.text()
        year = self.year_input.text()

        if not title or not author or not isbn:
            QMessageBox.warning(self, "Input Error", "Title, Author, and ISBN are required!")
            return

        # Check if Title, Author, and Genre contain digits (invalid input)
        if any(char.isdigit() for char in title) or any(char.isdigit() for char in author) or any(char.isdigit() for char in genre):
            QMessageBox.warning(self, "Input Error", "Title, Author, and Genre should not contain numbers!")
            return

        # Check if ISBN contains alphabetic characters
        if any(char.isalpha() for char in isbn):
            QMessageBox.warning(self, "Input Error", "ISBN should only contain numbers!")
            return

        # Check if Year contains non-numeric characters
        if not year.isdigit():
            QMessageBox.warning(self, "Input Error", "Year should only contain numbers!")
            return

        query = "INSERT INTO books (title, author, isbn, genre, year) VALUES (?, ?, ?, ?, ?)"
        parameters = (title, author, isbn, genre, year)
        try:
            self.db.execute_query(query, parameters)
            QMessageBox.information(self, "Success", "Book added successfully!")
            self.load_books()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def update_book(self):
        if not self.selected_book_id:
            QMessageBox.warning(self, "Update Error", "Select a book to update!")
            return

        title = self.title_input.text()
        author = self.author_input.text()
        isbn = self.isbn_input.text()
        genre = self.genre_input.text()
        year = self.year_input.text()

        if not title or not author or not isbn:
            QMessageBox.warning(self, "Input Error", "Title, Author, and ISBN are required!")
            return

        # Check if Title, Author, and Genre contain digits (invalid input)
        if any(char.isdigit() for char in title) or any(char.isdigit() for char in author) or any(char.isdigit() for char in genre):
            QMessageBox.warning(self, "Input Error", "Title, Author, and Genre should not contain numbers!")
            return

        # Check if ISBN contains alphabetic characters
        if any(char.isalpha() for char in isbn):
            QMessageBox.warning(self, "Input Error", "ISBN should only contain numbers!")
            return

        # Check if Year contains non-numeric characters
        if not year.isdigit():
            QMessageBox.warning(self, "Input Error", "Year should only contain numbers!")
            return

        query = "UPDATE books SET title = ?, author = ?, isbn = ?, genre = ?, year = ? WHERE id = ?"
        parameters = (title, author, isbn, genre, year, self.selected_book_id)
        try:
            self.db.execute_query(query, parameters)
            QMessageBox.information(self, "Success", "Book updated successfully!")
            self.load_books()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def delete_book(self):
        if not self.selected_book_id:
            QMessageBox.warning(self, "Delete Error", "Select a book to delete!")
            return

        confirm = QMessageBox.question(self, "Delete Book", "Are you sure you want to delete this book?",
                                       QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            query = "DELETE FROM books WHERE id = ?"
            parameters = (self.selected_book_id,)
            try:
                self.db.execute_query(query, parameters)
                QMessageBox.information(self, "Success", "Book deleted successfully!")
                self.load_books()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def populate_fields_for_update(self):
        selected_row = self.table.currentRow()
        if selected_row != -1:
            self.selected_book_id = self.table.item(selected_row, 0).text()
            self.title_input.setText(self.table.item(selected_row, 1).text())
            self.author_input.setText(self.table.item(selected_row, 2).text())
            self.isbn_input.setText(self.table.item(selected_row, 3).text())
            self.genre_input.setText(self.table.item(selected_row, 4).text())
            self.year_input.setText(self.table.item(selected_row, 5).text())

    def toggle_search_field(self):
        if self.search_input.isVisible():
            search_query = self.search_input.text()
            if search_query.strip():
                # Perform search
                query = """
                    SELECT id, title, author, isbn, genre, year 
                    FROM books 
                    WHERE title LIKE ? OR isbn LIKE ?
                """
                search_param = f"%{search_query}%"
                books = self.db.fetch_all(query, (search_param, search_param))
                self.table.setRowCount(0)
                for row_data in books:
                    row_number = self.table.rowCount()
                    self.table.insertRow(row_number)
                    for column_number, data in enumerate(row_data):
                        self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))
                self.back_button.setVisible(True)  # Show the back button to return to all books
            else:
                QMessageBox.warning(self, "Search Error", "Please enter a search query!")
        else:
            self.search_input.setVisible(True)

    def load_books(self):
        query = "SELECT id, title, author, isbn, genre, year FROM books"
        books = self.db.fetch_all(query)
        self.table.setRowCount(0)
        for row_data in books:
            row_number = self.table.rowCount()
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

        self.back_button.setVisible(False)  # Hide the back button when showing all books
        self.search_input.setVisible(False)  # Hide the search field when showing all books
        self.search_input.clear()

    def show_about(self):
        about_dialog = AboutDialog()
        about_dialog.exec_()

    def clear_fields(self):
        self.title_input.clear()
        self.author_input.clear()
        self.isbn_input.clear()
        self.genre_input.clear()
        self.year_input.clear()

