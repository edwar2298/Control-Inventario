import customtkinter
from database import DatabaseManager
from .edit_product import EditProductWindow

class ViewInventoryFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        self.db = DatabaseManager()

        # Search Bar
        self.search_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.search_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        self.label_title = customtkinter.CTkLabel(self.search_frame, text="Inventario", font=customtkinter.CTkFont(size=24, weight="bold"))
        self.label_title.pack(side="left")

        self.btn_search = customtkinter.CTkButton(self.search_frame, text="Buscar", width=100, command=self.perform_search)
        self.btn_search.pack(side="right", padx=(10, 0))
        
        self.entry_search = customtkinter.CTkEntry(self.search_frame, placeholder_text="Buscar por nombre o categoría...", width=300)
        self.entry_search.pack(side="right")
        self.entry_search.bind("<Return>", lambda event: self.perform_search())

        # Scrollable Frame for items
        self.scrollable_frame = customtkinter.CTkScrollableFrame(self, label_text="Productos")
        self.scrollable_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.refresh_data()

    def perform_search(self):
        query = self.entry_search.get()
        self.refresh_data(query)

    def refresh_data(self, query=""):
        # Clear existing items
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        if query:
            products = self.db.search_products(query)
        else:
            products = self.db.get_all_products()
        
        # Headers
        headers = ["ID", "Nombre", "Categoría", "Precio", "Cantidad", "Proveedor", "Acciones"]
        for i, header in enumerate(headers):
            label = customtkinter.CTkLabel(self.scrollable_frame, text=header, font=customtkinter.CTkFont(weight="bold"))
            label.grid(row=0, column=i, padx=5, pady=5)

        # Data Rows
        for row_idx, product in enumerate(products, start=1):
            # product elements: id, name, category, price, quantity, min_stock, supplier
            # Database might return diverse lengths depending on migration state vs query
            p_id, name, category, price, quantity = product[:5]
            min_stock = product[5] if len(product) > 5 else 5
            supplier = product[6] if len(product) > 6 else "General"
            
            # Low Stock Alert
            text_color = "red" if quantity <= min_stock else ("gray10", "gray90")
            font_weight = "bold" if quantity <= min_stock else "normal"

            customtkinter.CTkLabel(self.scrollable_frame, text=str(p_id), text_color=text_color, font=customtkinter.CTkFont(weight=font_weight)).grid(row=row_idx, column=0, padx=5, pady=2)
            customtkinter.CTkLabel(self.scrollable_frame, text=name, text_color=text_color, font=customtkinter.CTkFont(weight=font_weight)).grid(row=row_idx, column=1, padx=5, pady=2)
            customtkinter.CTkLabel(self.scrollable_frame, text=category, text_color=text_color).grid(row=row_idx, column=2, padx=5, pady=2)
            customtkinter.CTkLabel(self.scrollable_frame, text=f"${price}", text_color=text_color).grid(row=row_idx, column=3, padx=5, pady=2)
            customtkinter.CTkLabel(self.scrollable_frame, text=str(quantity), text_color=text_color, font=customtkinter.CTkFont(weight=font_weight)).grid(row=row_idx, column=4, padx=5, pady=2)
            customtkinter.CTkLabel(self.scrollable_frame, text=supplier, text_color=text_color).grid(row=row_idx, column=5, padx=5, pady=2)
            
            btn_edit = customtkinter.CTkButton(self.scrollable_frame, text="Editar", width=60, fg_color="blue", hover_color="darkblue",
                                                 command=lambda id=p_id: self.open_edit_window(id))
            btn_edit.grid(row=row_idx, column=6, padx=5, pady=2)

            btn_delete = customtkinter.CTkButton(self.scrollable_frame, text="Eliminar", width=60, fg_color="red", hover_color="darkred",
                                                 command=lambda id=p_id: self.delete_item(id))
            btn_delete.grid(row=row_idx, column=7, padx=5, pady=2)

    def open_edit_window(self, product_id):
        EditProductWindow(self, product_id, on_close_callback=self.refresh_data)

    def delete_item(self, product_id):
        self.db.delete_product(product_id)
        self.refresh_data()
