import customtkinter
from database import DatabaseManager

class AddProductFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        self.db = DatabaseManager()

        self.label_title = customtkinter.CTkLabel(self, text="Agregar Nuevo Producto", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.label_title.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        # Form Fields
        self.entry_name = customtkinter.CTkEntry(self, placeholder_text="Nombre del Producto", width=300)
        self.entry_name.grid(row=1, column=0, padx=20, pady=10, sticky="w")

        self.entry_category = customtkinter.CTkEntry(self, placeholder_text="Categoría", width=300)
        self.entry_category.grid(row=2, column=0, padx=20, pady=10, sticky="w")

        self.entry_price = customtkinter.CTkEntry(self, placeholder_text="Precio", width=300)
        self.entry_price.grid(row=3, column=0, padx=20, pady=10, sticky="w")

        self.entry_quantity = customtkinter.CTkEntry(self, placeholder_text="Cantidad", width=300)
        self.entry_quantity.grid(row=4, column=0, padx=20, pady=10, sticky="w")

        self.entry_min_stock = customtkinter.CTkEntry(self, placeholder_text="Stock Mínimo (Alerta)", width=300)
        self.entry_min_stock.grid(row=5, column=0, padx=20, pady=10, sticky="w")

        self.entry_supplier = customtkinter.CTkEntry(self, placeholder_text="Proveedor", width=300)
        self.entry_supplier.grid(row=6, column=0, padx=20, pady=10, sticky="w")

        # Buttons
        # Buttons
        self.btn_save = customtkinter.CTkButton(self, text="Guardar Producto", command=self.save_product)
        self.btn_save.grid(row=7, column=0, padx=20, pady=20, sticky="w")
        
        self.label_status = customtkinter.CTkLabel(self, text="")
        self.label_status.grid(row=8, column=0, padx=20, pady=0, sticky="w")

    def save_product(self):
        name = self.entry_name.get()
        category = self.entry_category.get()
        price = self.entry_price.get()
        quantity = self.entry_quantity.get()
        min_stock = self.entry_min_stock.get()
        supplier = self.entry_supplier.get()

        if not name or not price or not quantity:
            self.label_status.configure(text="Error: Complete todos los campos", text_color="red")
            return

        try:
            price = float(price)
            quantity = int(quantity)
            min_stock = int(min_stock) if min_stock else 5
            supplier = supplier if supplier else "General"
            
            self.db.add_product(name, category, price, quantity, min_stock, supplier)
            self.label_status.configure(text="Producto guardado exitosamente!", text_color="green")
            self.clear_form()
        except ValueError:
            self.label_status.configure(text="Error: Precio debe ser número y cantidad entero", text_color="red")

    def clear_form(self):
        self.entry_name.delete(0, 'end')
        self.entry_category.delete(0, 'end')
        self.entry_price.delete(0, 'end')
        self.entry_quantity.delete(0, 'end')
        self.entry_min_stock.delete(0, 'end')
        self.entry_supplier.delete(0, 'end')
