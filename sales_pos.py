import customtkinter
from database import DatabaseManager
import os
import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import subprocess, platform

class SalesPOSFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        self.db = DatabaseManager()

        self.label_title = customtkinter.CTkLabel(self, text="Registrar Nueva Venta", font=customtkinter.CTkFont(size=24, weight="bold"))
        self.label_title.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        # Layout Split
        self.form_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.form_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        # Product Selection
        self.label_product = customtkinter.CTkLabel(self.form_frame, text="Producto:", font=customtkinter.CTkFont(weight="bold"))
        self.label_product.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.product_var = customtkinter.StringVar(value="Seleccione un producto")
        self.product_menu = customtkinter.CTkOptionMenu(self.form_frame, variable=self.product_var, width=300)
        self.product_menu.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        # Quantity
        self.label_qty = customtkinter.CTkLabel(self.form_frame, text="Cantidad:", font=customtkinter.CTkFont(weight="bold"))
        self.label_qty.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        
        self.entry_qty = customtkinter.CTkEntry(self.form_frame, placeholder_text="1", width=300)
        self.entry_qty.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        # Customer
        self.label_customer = customtkinter.CTkLabel(self.form_frame, text="Cliente / Empresa:", font=customtkinter.CTkFont(weight="bold"))
        self.label_customer.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        
        self.entry_customer = customtkinter.CTkEntry(self.form_frame, placeholder_text="Nombre del Cliente", width=300)
        self.entry_customer.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        # Action Buttons
        self.btn_sell = customtkinter.CTkButton(self.form_frame, text="Confirmar Venta", command=self.process_sale, fg_color="green", hover_color="darkgreen", height=40)
        self.btn_sell.grid(row=3, column=1, padx=10, pady=20, sticky="ew")

        self.label_status = customtkinter.CTkLabel(self.form_frame, text="", font=customtkinter.CTkFont(size=14))
        self.label_status.grid(row=4, column=1, padx=10, pady=0, sticky="w")
        
        # Product Map (Name -> ID)
        self.product_map = {}
        self.refresh_products()

    def refresh_products(self):
        products = self.db.get_all_products()
        self.product_map = {f"{p[1]} (Stock: {p[4]})": p for p in products}
        
        menus = list(self.product_map.keys())
        if menus:
            self.product_menu.configure(values=menus)
            self.product_var.set(menus[0])
        else:
            self.product_menu.configure(values=["Sin productos"])
            self.product_var.set("Sin productos")

    def process_sale(self):
        selection = self.product_var.get()
        if selection not in self.product_map:
            self.label_status.configure(text="Error: Seleccione un producto válido", text_color="red")
            return

        product_data = self.product_map[selection]
        p_id = product_data[0]
        p_name = product_data[1]
        p_price = product_data[3]
        
        try:
            qty = int(self.entry_qty.get())
            if qty <= 0: raise ValueError
        except ValueError:
            self.label_status.configure(text="Error: Cantidad inválida", text_color="red")
            return

        customer = self.entry_customer.get()
        if not customer:
            self.label_status.configure(text="Error: Ingrese nombre del cliente", text_color="red")
            return

        # Attempt Purchase
        success = self.db.record_sale(p_id, qty, customer, p_price)
        
        if success:
            total = p_price * qty
            self.label_status.configure(text=f"¡Venta Exitosa! Total: ${total:,.2f}", text_color="green")
            
            # Generate Invoice
            self.generate_invoice(p_name, qty, p_price, total, customer)
            
            self.entry_qty.delete(0, 'end')
            self.refresh_products() # Update stock in menu
        else:
            self.label_status.configure(text="Error: Stock insuficiente", text_color="red")

    def generate_invoice(self, product_name, quantity, unit_price, total, customer):
        try:
            if not os.path.exists("invoices"):
                os.makedirs("invoices")
                
            timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"invoices/Factura_{timestamp_str}_{customer.replace(' ', '_')}.pdf"
            
            c = canvas.Canvas(filename, pagesize=letter)
            width, height = letter
            
            # Header
            c.setFont("Helvetica-Bold", 24)
            c.drawString(50, height - 50, "Inventario Store - FACTURA")
            
            c.setFont("Helvetica", 12)
            c.drawString(50, height - 80, f"Fecha: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
            c.drawString(50, height - 100, f"Cliente: {customer}")
            
            c.line(50, height - 120, width - 50, height - 120)
            
            # Details
            y = height - 150
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, "Producto")
            c.drawString(300, y, "Cant.")
            c.drawString(400, y, "Precio Unit.")
            c.drawString(500, y, "Total")
            
            y -= 25
            c.setFont("Helvetica", 12)
            c.drawString(50, y, product_name)
            c.drawString(300, y, str(quantity))
            c.drawString(400, y, f"${unit_price:,.2f}")
            c.drawString(500, y, f"${total:,.2f}")
            
            # Footer
            c.line(50, y - 50, width - 50, y - 50)
            c.setFont("Helvetica-Bold", 14)
            c.drawString(400, y - 80, f"TOTAL A PAGAR: ${total:,.2f}")
            
            c.setFont("Helvetica-Oblique", 10)
            c.drawString(50, 50, "Gracias por su compra. Documento generado automáticamente.")
            
            c.save()
            
            # Open the file
            if platform.system() == 'Windows':
                os.startfile(filename)
            else:
                 # Generic fallback (e.g. linux)
                subprocess.call(('xdg-open', filename))
                
        except Exception as e:
            print(f"Error generando factura: {e}")
            self.label_status.configure(text=f"Venta OK. Error PDF: {e}", text_color="orange")
