import sqlite3
from typing import List, Tuple, Optional
import datetime
import hashlib

class DatabaseManager:
    def __init__(self, db_name="inventory.db"):
        self.db_name = db_name
        self.initialize_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_name)

    def initialize_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    price REAL NOT NULL,
                    quantity INTEGER NOT NULL,
                    min_stock INTEGER DEFAULT 5,
                    supplier TEXT DEFAULT 'General'
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS movements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    movement_type TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    timestamp TEXT NOT NULL,
                    description TEXT,
                    customer TEXT DEFAULT '',
                    unit_price REAL DEFAULT 0.0,
                    FOREIGN KEY (product_id) REFERENCES products (id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL
                )
            """)
            conn.commit()
            
            # Migration check for existing tables
            self._migrate_db(conn)
            
            # Ensure default admin exists
            self.create_default_admin()

    def _migrate_db(self, conn):
        cursor = conn.cursor()
        
        # Products table migration
        cursor.execute("PRAGMA table_info(products)")
        p_columns = [info[1] for info in cursor.fetchall()]
        
        if "min_stock" not in p_columns:
            cursor.execute("ALTER TABLE products ADD COLUMN min_stock INTEGER DEFAULT 5")
        if "supplier" not in p_columns:
            cursor.execute("ALTER TABLE products ADD COLUMN supplier TEXT DEFAULT 'General'")
            
        # Movements table migration
        cursor.execute("PRAGMA table_info(movements)")
        m_columns = [info[1] for info in cursor.fetchall()]
        
        if "customer" not in m_columns:
            cursor.execute("ALTER TABLE movements ADD COLUMN customer TEXT DEFAULT ''")
        if "unit_price" not in m_columns:
            cursor.execute("ALTER TABLE movements ADD COLUMN unit_price REAL DEFAULT 0.0")

        conn.commit()

    def create_default_admin(self):
        # Create admin user if table is empty
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT count(*) FROM users")
            if cursor.fetchone()[0] == 0:
                # Default: admin / admin123
                pwd_hash = hashlib.sha256("admin123".encode()).hexdigest()
                cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", ("admin", pwd_hash))
                conn.commit()

    def authenticate_user(self, username, password) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            pwd_hash = hashlib.sha256(password.encode()).hexdigest()
            cursor.execute("SELECT id FROM users WHERE username = ? AND password_hash = ?", (username, pwd_hash))
            return cursor.fetchone() is not None

    def record_movement(self, product_id: int, movement_type: str, quantity: int, description: str = "", customer: str = "", unit_price: float = 0.0):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("INSERT INTO movements (product_id, movement_type, quantity, timestamp, description, customer, unit_price) VALUES (?, ?, ?, ?, ?, ?, ?)",
                           (product_id, movement_type, quantity, timestamp, description, customer, unit_price))
            conn.commit()
            
    def record_sale(self, product_id: int, quantity: int, customer: str, unit_price: float) -> bool:
        # Check stock first
        current = self.get_product_by_id(product_id)
        if not current: return False
        
        current_qty = current[4]
        if current_qty < quantity:
            return False
            
        # Update stock
        new_qty = current_qty - quantity
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE products SET quantity = ? WHERE id = ?", (new_qty, product_id))
            conn.commit()
            
        # Record movement
        self.record_movement(product_id, "VENTA", quantity, f"Venta a {customer}", customer, unit_price)
        return True

    def add_product(self, name: str, category: str, price: float, quantity: int, min_stock: int = 5, supplier: str = "General") -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO products (name, category, price, quantity, min_stock, supplier) VALUES (?, ?, ?, ?, ?, ?)",
                           (name, category, price, quantity, min_stock, supplier))
            product_id = cursor.lastrowid
            conn.commit()
        
        # Record initial entry
        self.record_movement(product_id, "ENTRADA", quantity, "Inventario Inicial")

    def get_all_products(self) -> List[Tuple]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products")
            return cursor.fetchall()

    def get_product_by_id(self, product_id: int) -> Optional[Tuple]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
            return cursor.fetchone()

    def search_products(self, query: str) -> List[Tuple]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            wildcard_query = f"%{query}%"
            cursor.execute("SELECT * FROM products WHERE name LIKE ? OR category LIKE ?", (wildcard_query, wildcard_query))
            return cursor.fetchall()
            
    def get_inventory_stats(self) -> dict:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*), SUM(price * quantity) FROM products")
            count, total_value = cursor.fetchone()
            return {
                "total_items": count if count else 0,
                "total_value": total_value if total_value else 0.0
            }

    def get_low_stock_products(self) -> List[Tuple]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Assuming min_stock column exists, else default 5
            cursor.execute("SELECT * FROM products WHERE quantity <= min_stock")
            return cursor.fetchall()
            
    def get_top_selling_products(self, limit=5) -> List[Tuple]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Sum 'quantity' from movements of type 'SALIDA' group by product
            cursor.execute("""
                SELECT p.name, SUM(m.quantity) as total_sold 
                FROM movements m
                JOIN products p ON m.product_id = p.id
                WHERE m.movement_type = 'SALIDA'
                GROUP BY m.product_id
                ORDER BY total_sold DESC
                LIMIT ?
            """, (limit,))
            return cursor.fetchall()
            
    def get_daily_sales_last_7_days(self) -> List[Tuple]:
        # Returns list of (date_str, total_amount)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # SQLite date function usage: date(timestamp) gets YYYY-MM-DD
            # We want specific range. 
            # Note: 'now' timezone might be UTC.
            cursor.execute("""
                SELECT date(timestamp) as sale_date, SUM(quantity * unit_price) as daily_total
                FROM movements 
                WHERE movement_type = 'VENTA' 
                  AND timestamp >= date('now', '-6 days')
                GROUP BY sale_date
                ORDER BY sale_date ASC
            """)
            return cursor.fetchall()
            
    def get_sales_history(self) -> List[Tuple]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT m.timestamp, p.name, m.quantity, m.unit_price, (m.quantity * m.unit_price) as total, m.customer 
                FROM movements m
                JOIN products p ON m.product_id = p.id
                WHERE m.movement_type = 'VENTA'
                ORDER BY m.timestamp DESC
            """)
            return cursor.fetchall()

    def update_product(self, product_id: int, name: str, category: str, price: float, quantity: int, min_stock: int = 5, supplier: str = "General") -> None:
        current_data = self.get_product_by_id(product_id)
        if current_data:
            old_qty = current_data[4] # Index 4 is quantity
            diff = quantity - old_qty
            
            if diff != 0:
                movement_type = "ENTRADA" if diff > 0 else "SALIDA" # Simple logic, can be refined
                description = "Ajuste manual de inventario"
                # If specifically tracking sales vs adjustments could be passed as arg, but simpler for now
                if diff < 0: movement_type = "SALIDA" # Or AJUSTE
                
                self.record_movement(product_id, "AJUSTE", abs(diff), f"Cambio de {old_qty} a {quantity}")

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE products 
                SET name = ?, category = ?, price = ?, quantity = ?, min_stock = ?, supplier = ?
                WHERE id = ?
            """, (name, category, price, quantity, min_stock, supplier, product_id))
            conn.commit()

    def delete_product(self, product_id: int) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
            conn.commit()
