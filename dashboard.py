import customtkinter
from database import DatabaseManager
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class DashboardFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        self.db = DatabaseManager()

        self.label_title = customtkinter.CTkLabel(self, text="Resumen General", font=customtkinter.CTkFont(size=24, weight="bold"))
        self.label_title.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        # Container for cards
        self.cards_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.cards_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        
        # Info Cards
        self.card_total_items = self.create_info_card(self.cards_frame, "Total Productos", "0")
        self.card_total_items.grid(row=0, column=0, padx=10, pady=10)
        
        self.card_total_value = self.create_info_card(self.cards_frame, "Valor Inventario", "$0.00")
        self.card_total_value.grid(row=0, column=1, padx=10, pady=10)

        self.card_low_stock = self.create_info_card(self.cards_frame, "Alertas Stock Bajo", "0", fg_color="firebrick")
        self.card_low_stock.grid(row=1, column=0, padx=10, pady=10)
        
        self.card_top_selling = self.create_info_card(self.cards_frame, "Más Vendido", "-")
        self.card_top_selling.grid(row=1, column=1, padx=10, pady=10)

        # Chart Frame
        self.chart_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.chart_frame.grid(row=2, column=0, columnspan=2, padx=20, pady=10, sticky="nsew")
        self.grid_rowconfigure(2, weight=1)

        self.refresh_stats()

    def create_info_card(self, parent, title, value, fg_color=None):
        color = fg_color if fg_color else ("gray85", "gray20")
        card = customtkinter.CTkFrame(parent, fg_color=color, corner_radius=10)
        
        label_title = customtkinter.CTkLabel(card, text=title, font=customtkinter.CTkFont(size=14, weight="bold"))
        label_title.pack(padx=20, pady=(15, 5))
        
        label_value = customtkinter.CTkLabel(card, text=value, font=customtkinter.CTkFont(size=22, weight="bold"), text_color="dodgerblue" if not fg_color else "white")
        label_value.pack(padx=20, pady=(0, 15))
        
        # Store reference to update later
        card.value_label = label_value
        return card

    def refresh_stats(self):
        stats = self.db.get_inventory_stats()
        self.card_total_items.value_label.configure(text=str(stats["total_items"]))
        self.card_total_value.value_label.configure(text=f"${stats['total_value']:,.2f}")
        
        # New Stats
        low_stock_products = self.db.get_low_stock_products()
        self.card_low_stock.value_label.configure(text=f"{len(low_stock_products)} Productos")
        
        top_selling = self.db.get_top_selling_products(limit=1)
        if top_selling:
            best_product, total_qty = top_selling[0]
            self.card_top_selling.value_label.configure(text=f"{best_product}\n({total_qty} un.)")
        else:
            self.card_top_selling.value_label.configure(text="Sin datos")
            
        self.update_chart()

    def update_chart(self):
        # Clear previous chart if exists
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        # Get Data
        data = self.db.get_daily_sales_last_7_days()
        if not data:
            return

        dates = [d[0] for d in data]
        totals = [d[1] for d in data]

        # Create Figure
        fig, ax = plt.subplots(figsize=(6, 3), dpi=100)
        # Set background color to match typical dark theme or neutral
        fig.patch.set_facecolor('#242424') # Dark gray
        ax.set_facecolor('#242424')
        
        bars = ax.bar(dates, totals, color='#1f6aa5')
        
        # Style
        ax.tick_params(axis='x', colors='white', rotation=45)
        ax.tick_params(axis='y', colors='white')
        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white') 
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.set_title("Ventas Últimos 7 Días", color='white', fontsize=10, weight='bold')
        
        plt.tight_layout()

        # Canvas
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
