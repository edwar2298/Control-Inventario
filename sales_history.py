import customtkinter
from database import DatabaseManager
from tkinter import filedialog, messagebox
import openpyxl
from openpyxl.styles import Font, PatternFill

class SalesHistoryFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        self.db = DatabaseManager()

        self.label_title = customtkinter.CTkLabel(self, text="Historial de Ventas", font=customtkinter.CTkFont(size=24, weight="bold"))
        self.label_title.grid(row=0, column=0, padx=20, pady=20, sticky="w")
        
        # Refresh Button
        self.btn_refresh = customtkinter.CTkButton(self, text="Actualizar", command=self.refresh_data, width=100)
        self.btn_refresh.grid(row=0, column=0, padx=(0, 140), pady=20, sticky="e")

        # Export Button
        self.btn_export = customtkinter.CTkButton(self, text="Exportar a Excel", command=self.export_to_excel, width=120, fg_color="green", hover_color="darkgreen")
        self.btn_export.grid(row=0, column=0, padx=20, pady=20, sticky="e")

        # Scrollable Frame for items
        self.scrollable_frame = customtkinter.CTkScrollableFrame(self, label_text="Registro de Transacciones")
        self.scrollable_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.refresh_data()

    def refresh_data(self):
        # Clear existing items
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        sales = self.db.get_sales_history()
        # Columns: timestamp, name, quantity, unit_price, total, customer
        
        # Headers
        headers = ["Fecha", "Producto", "Cantidad", "Precio Unit.", "Total", "Cliente"]
        for i, header in enumerate(headers):
            label = customtkinter.CTkLabel(self.scrollable_frame, text=header, font=customtkinter.CTkFont(weight="bold"))
            label.grid(row=0, column=i, padx=5, pady=5)

        # Data Rows
        for row_idx, sale in enumerate(sales, start=1):
            ts, name, qty, price, total, customer = sale
            
            customtkinter.CTkLabel(self.scrollable_frame, text=ts).grid(row=row_idx, column=0, padx=5, pady=2)
            customtkinter.CTkLabel(self.scrollable_frame, text=name).grid(row=row_idx, column=1, padx=5, pady=2)
            customtkinter.CTkLabel(self.scrollable_frame, text=str(qty)).grid(row=row_idx, column=2, padx=5, pady=2)
            customtkinter.CTkLabel(self.scrollable_frame, text=f"${price:,.2f}").grid(row=row_idx, column=3, padx=5, pady=2)
            customtkinter.CTkLabel(self.scrollable_frame, text=f"${total:,.2f}", font=customtkinter.CTkFont(weight="bold")).grid(row=row_idx, column=4, padx=5, pady=2)
            customtkinter.CTkLabel(self.scrollable_frame, text=customer).grid(row=row_idx, column=5, padx=5, pady=2)
            
    def export_to_excel(self):
        sales = self.db.get_sales_history()
        if not sales:
            messagebox.showwarning("Sin datos", "No hay ventas para exportar.")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Archivos Excel", "*.xlsx"), ("Todos los archivos", "*.*")],
            title="Guardar Historial de Ventas"
        )

        if filename:
            try:
                # Create Workbook and Active Sheet
                wb = openpyxl.Workbook()
                ws = wb.active
                ws.title = "Historial Ventas"

                # Define Headers
                headers = ["Fecha y Hora", "Producto", "Cantidad", "Precio Unitario", "Total Venta", "Cliente"]
                ws.append(headers)

                # Style Headers (Bold + Light Blue Background)
                header_font = Font(bold=True, color="FFFFFF")
                header_fill = PatternFill(start_color="337AB7", end_color="337AB7", fill_type="solid")
                
                for cell in ws[1]:
                    cell.font = header_font
                    cell.fill = header_fill
                
                # Write Data
                for row in sales:
                    ws.append(row)

                # Auto-adjust column widths
                for col in ws.columns:
                    max_length = 0
                    column = col[0].column_letter # Get the column name
                    for cell in col:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = (max_length + 2)
                    ws.column_dimensions[column].width = adjusted_width

                # Save File
                wb.save(filename)
                
                messagebox.showinfo("Éxito", f"Archivo Excel exportado correctamente:\n{filename}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{e}")
