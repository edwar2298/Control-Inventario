import customtkinter
from database import DatabaseManager

class LoginWindow(customtkinter.CTkToplevel):
    def __init__(self, master, on_success):
        super().__init__(master)
        self.title("Inicio de Sesión - Inventario")
        self.geometry("400x450")
        self.resizable(False, False)
        
        self.on_success = on_success
        self.db = DatabaseManager()

        # Center logic
        # You can center it manually or rely on OS. CTk centers nicely usually.
        
        # UI Elements
        self.frame = customtkinter.CTkFrame(self, corner_radius=10)
        self.frame.pack(pady=40, padx=40, fill="both", expand=True)

        self.label_title = customtkinter.CTkLabel(self.frame, text="Bienvenido", font=customtkinter.CTkFont(size=26, weight="bold"))
        self.label_title.pack(pady=(40, 20))

        self.entry_user = customtkinter.CTkEntry(self.frame, placeholder_text="Usuario", width=220)
        self.entry_user.pack(pady=10)
        
        self.entry_pass = customtkinter.CTkEntry(self.frame, placeholder_text="Contraseña", show="*", width=220)
        self.entry_pass.pack(pady=10)
        self.entry_pass.bind("<Return>", lambda e: self.attempt_login())

        self.btn_login = customtkinter.CTkButton(self.frame, text="Ingresar", width=220, command=self.attempt_login)
        self.btn_login.pack(pady=30)
        
        self.label_error = customtkinter.CTkLabel(self.frame, text="", text_color="red")
        self.label_error.pack(pady=5)
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def attempt_login(self):
        user = self.entry_user.get()
        pwd = self.entry_pass.get()
        
        if self.db.authenticate_user(user, pwd):
            self.destroy()
            self.on_success()
        else:
            self.label_error.configure(text="Credenciales incorrectas")

    def on_closing(self):
        self.master.destroy() # Exit entire app
