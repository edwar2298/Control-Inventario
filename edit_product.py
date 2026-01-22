import customtkinter
from database import DatabaseManager

class EditProductWindow(customtkinter.CTkToplevel):
    def __init__(self, master, product_id, on_close_callback=None):
        super().__init__(master)
        self.title("Editar Producto")
        self.geometry("400x450")
        self.resizable(False, False)
        
        self.db = DatabaseManager()
        self.product_id = product_id
        self.on_close_callback = on_close_callback

        # Make modal
        self.transient(master)
        self.grab_set()

        self.label_title = customtkinter.CTkLabel(self, text=f"Editar Producto #{product_id}", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.label_title.pack(pady=20)

        # Form Fields
        self.entry_name = customtkinter.CTkEntry(self, placeholder_text="Nombre", width=300)
        self.entry_name.pack(pady=10)

        self.entry_category = customtkinter.CTkEntry(self, placeholder_text="Categoría", width=300)
        self.entry_category.pack(pady=10)

        self.entry_price = customtkinter.CTkEntry(self, placeholder_text="Precio", width=300)
        self.entry_price.pack(pady=10)

        self.entry_quantity = customtkinter.CTkEntry(self, placeholder_text="Cantidad", width=300)
        self.entry_quantity.pack(pady=10)

        self.entry_min_stock = customtkinter.CTkEntry(self, placeholder_text="Stock Mínimo", width=300)
        self.entry_min_stock.pack(pady=10)

        self.entry_supplier = customtkinter.CTkEntry(self, placeholder_text="Proveedor", width=300)
        self.entry_supplier.pack(pady=10)

        # Buttons
        self.btn_save = customtkinter.CTkButton(self, text="Guardar Cambios", command=self.save_changes)
        self.btn_save.pack(pady=20)
        
        self.label_status = customtkinter.CTkLabel(self, text="")
        self.label_status.pack(pady=5)

        self.load_product_data()

    def load_product_data(self):
        product = self.db.get_product_by_id(self.product_id)
        if product:
            # product: (id, name, category, price, quantity, min_stock, supplier)
            # Safe unpacking based on potentially new schema
            p_id, name, category, price, quantity = product[:5]
            min_stock = product[5] if len(product) > 5 else 5
            supplier = product[6] if len(product) > 6 else "General"

            self.entry_name.insert(0, name)
            self.entry_category.insert(0, category)
            self.entry_price.insert(0, str(price))
            self.entry_quantity.insert(0, str(quantity))
            self.entry_min_stock.insert(0, str(min_stock))
            self.entry_supplier.insert(0, supplier)
        else:
            self.label_status.configure(text="Error: Producto no encontrado", text_color="red")
            self.btn_save.configure(state="disabled")

    def save_changes(self):
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
            
            self.db.update_product(self.product_id, name, category, price, quantity, min_stock, supplier)
            
            if self.on_close_callback:
                self.on_close_callback()
                
            self.destroy()
        except ValueError:
            self.label_status.configure(text="Error: Precio/Cantidad inválidos", text_color="red")
