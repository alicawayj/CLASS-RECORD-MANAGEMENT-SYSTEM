import customtkinter as ctk
from tkinter import messagebox
import sqlite3


class LoginScreenMixin:
    def login_screen(self):
        """Create login screen interface with password visibility toggle"""
        self.clear_window()

        main_container = ctk.CTkFrame(self.root, fg_color=("gray95", "gray15"))
        main_container.pack(fill="both", expand=True)

        # Left panel with branding
        left_frame = ctk.CTkFrame(main_container, fg_color=("#2E8B57", "#1F5E3A"), width=400)
        left_frame.pack(side="left", fill="both", expand=False)
        left_frame.pack_propagate(False)

        brand_content = ctk.CTkFrame(left_frame, fg_color="transparent")
        brand_content.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            brand_content,
            text="📚",
            font=("Arial", 64),
            text_color="white"
        ).pack(pady=10)

        ctk.CTkLabel(
            brand_content,
            text="CLASS RECORD",
            font=("Arial", 28, "bold"),
            text_color="white"
        ).pack(pady=5)

        ctk.CTkLabel(
            brand_content,
            text="Management System",
            font=("Arial", 16),
            text_color="white"
        ).pack(pady=5)

        # Right panel with login form
        right_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        right_frame.pack(side="right", fill="both", expand=True, padx=80)

        form_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        form_frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            form_frame,
            text="Good Day!, Sir Meo, Sir Yno, Sir Harold",
            font=("Arial", 24, "bold"),
            text_color="#2E8B57"
        ).pack(pady=20)

        ctk.CTkLabel(
            form_frame,
            text="Teacher Login Portal",
            font=("Arial", 18),
            text_color=("gray50", "gray70")
        ).pack(pady=5)

        # Teacher ID input
        ctk.CTkLabel(form_frame, text="Teacher ID", font=("Arial", 14)).pack(anchor="w", pady=(20, 5))
        self.teacher_id_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Enter your teacher ID",
            width=300,
            height=45,
            font=("Arial", 14)
        )
        self.teacher_id_entry.pack(pady=5)
        self.teacher_id_entry.insert(0, "T001")  # Default for testing

        # Password input with visibility toggle
        ctk.CTkLabel(form_frame, text="Password", font=("Arial", 14)).pack(anchor="w", pady=(20, 5))
        
        password_frame = ctk.CTkFrame(form_frame, fg_color="transparent", width=300, height=45)
        password_frame.pack(pady=5)
        password_frame.pack_propagate(False)
        
        self.teacher_password_entry = ctk.CTkEntry(
            password_frame,
            placeholder_text="Enter your password",
            show="•",
            width=240,
            height=45,
            font=("Arial", 14)
        )
        self.teacher_password_entry.pack(side="left", fill="both", expand=True)
        self.teacher_password_entry.insert(0, "password123")  # Default password
        
        self.show_password_var = ctk.BooleanVar(value=False)
        self.show_password_btn = ctk.CTkButton(
            password_frame,
            text="👁",
            width=45,
            height=45,
            fg_color="transparent",
            hover_color=("gray80", "gray30"),
            command=self.toggle_password_visibility,
            text_color="black"
        )
        self.show_password_btn.pack(side="right")

        # Login button
        login_btn = ctk.CTkButton(
            form_frame,
            text="Sign In",
            command=self.check_login,
            width=300,
            height=45,
            font=("Arial", 16, "bold"),
            fg_color=("#2E8B57", "#1F5E3A"),
            hover_color=("#1F5E3A", "#2E8B57"),
            corner_radius=8
        )
        login_btn.pack(pady=30)

        # Enter key support
        self.root.bind('<Return>', lambda event: self.check_login())

    def toggle_password_visibility(self):
        """Toggle between showing and hiding password"""
        if self.show_password_var.get():
            self.teacher_password_entry.configure(show="")
            self.show_password_btn.configure(text="🔒", text_color="black")
            self.show_password_var.set(False)
        else:
            self.teacher_password_entry.configure(show="•")
            self.show_password_btn.configure(text="👁", text_color="black")
            self.show_password_var.set(True)

    def simple_hash_password(self, password):
        """Simple password hashing using character shifting"""
        if not password:
            return ""
        
        # Simple transformation: shift each character by its position
        hash_result = ""
        for i, char in enumerate(password):
            # Shift character by its position + 5
            shifted_char = chr((ord(char) + i + 5) % 256)
            hash_result += shifted_char
        
        return hash_result

    def check_login(self):
        """Authenticate teacher credentials against database"""
        teacher_id = self.teacher_id_entry.get()
        password = self.teacher_password_entry.get()

        if not teacher_id or not password:
            messagebox.showerror("Login Error", "Please enter both teacher ID and password!")
            return

        # Hash password for comparison
        password_hash = self.simple_hash_password(password)

        # Verify credentials in database
        conn = sqlite3.connect("class_records.db")
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM teachers WHERE teacher_id = ? AND password_hash = ?",
            (teacher_id, password_hash)
        )
        teacher = cur.fetchone()
        conn.close()

        if teacher:
            self.current_user = teacher
            self.main_screen()  # Proceed to main dashboard
        else:
            messagebox.showerror("Login Error", "Invalid teacher ID or password.")