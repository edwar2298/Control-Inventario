import customtkinter
from views.app import App
from views.login import LoginWindow

if __name__ == "__main__":
    customtkinter.set_appearance_mode("System")
    customtkinter.set_default_color_theme("blue")

    app = App()
    
    # Hide main app initially
    app.withdraw()
    
    # Show Login
    def show_app():
        app.deiconify()
        
    def logout():
        app.withdraw()
        LoginWindow(app, on_success=show_app)

    app.set_logout_command(logout)
        
    login = LoginWindow(app, on_success=show_app)
    
    app.mainloop()
