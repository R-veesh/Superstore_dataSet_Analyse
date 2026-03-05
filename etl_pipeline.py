import csv
import sqlite3
from datetime import datetime
import os

class ETLPipeline:
    def __init__(self, db_path='superstore.db'):
        self.db_path = db_path
        self.source_files = {
            'customers': 'customers.csv',
            'products': 'products.csv',
            'sales': 'sales.csv',
            'dim_store': 'DimStore.csv',
            'dim_ship_mode': 'DimShipMode.csv',
            'dim_date': 'DimDate.csv'
        }
    
    def extract(self, file_path):
        """Extract data from CSV files"""
        data = []
        print(f"Extracting data from {file_path}...")
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
        print(f"  Extracted {len(data)} records")
        return data
    
    def transform_customers(self, data):
        """Transform customer data"""
        print("Transforming customer data...")
        transformed = []
        for row in data:
            transformed.append({
                'CustomerID': row['CustomerID'],
                'CustomerName': row['CustomerName'],
                'Segment': row['Segment'],
                'Country': row['Country'],
                'City': row['City'],
                'State': row['State'],
                'PostalCode': row['PostalCode'],
                'Region': row['Region']
            })
        return transformed
    
    def transform_products(self, data):
        """Transform product data"""
        print("Transforming product data...")
        transformed = []
        for row in data:
            transformed.append({
                'ProductID': row['ProductID'],
                'Category': row['Category'],
                'SubCategory': row['SubCategory'],
                'ProductName': row['ProductName']
            })
        return transformed
    
    def transform_sales(self, data):
        """Transform sales data"""
        print("Transforming sales data...")
        transformed = []
        for row in data:
            transformed.append({
                'RowID': int(row['RowID']),
                'OrderID': row['OrderID'],
                'OrderDate': row['OrderDate'],
                'ShipDate': row['ShipDate'],
                'ShipMode': row['ShipMode'],
                'CustomerID': row['CustomerID'],
                'ProductID': row['ProductID'],
                'Sales': float(row['Sales']),
                'Quantity': int(row['Quantity']),
                'Discount': float(row['Discount']),
                'Profit': float(row['Profit'])
            })
        return transformed
    
    def transform_dim_date(self, data):
        """Transform date dimension data"""
        print("Transforming date dimension data...")
        transformed = []
        for row in data:
            transformed.append({
                'DateKey': int(row['DateKey']),
                'CalendarDate': row['CalendarDate'],
                'Year': int(row['Year']),
                'Quarter': int(row['Quarter']),
                'Month': int(row['Month']),
                'Day': int(row['Day']),
                'Weekday': row['Weekday'],
                'FiscalYear': int(row['FiscalYear']),
                'FiscalQuarter': int(row['FiscalQuarter'])
            })
        return transformed
    
    def transform_dim_store(self, data):
        """Transform store dimension data"""
        print("Transforming store dimension data...")
        transformed = []
        for row in data:
            transformed.append({
                'StoreID': int(row['StoreID']),
                'StoreName': row['StoreName'],
                'Region': row['Region'],
                'City': row['City'],
                'State': row['State']
            })
        return transformed
    
    def transform_dim_ship_mode(self, data):
        """Transform ship mode dimension data"""
        print("Transforming ship mode dimension data...")
        transformed = []
        for row in data:
            transformed.append({
                'ShipMode': row['ShipMode']
            })
        return transformed
    
    def load_to_database(self, table_name, data, columns):
        """Load transformed data to database"""
        print(f"Loading {len(data)} records to {table_name}...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        placeholders = ','.join(['?'] * len(columns))
        insert_sql = f"INSERT OR REPLACE INTO {table_name} ({','.join(columns)}) VALUES ({placeholders})"
        
        for row in data:
            values = [row.get(col) for col in columns]
            cursor.execute(insert_sql, values)
        
        conn.commit()
        conn.close()
        print(f"  Loaded {len(data)} records to {table_name}")
    
    def create_warehouse_schema(self):
        """Create data warehouse schema"""
        print("\nCreating data warehouse schema...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DROP TABLE IF EXISTS Customers")
        cursor.execute("""
            CREATE TABLE Customers (
                CustomerID TEXT PRIMARY KEY,
                CustomerName TEXT,
                Segment TEXT,
                Country TEXT,
                City TEXT,
                State TEXT,
                PostalCode TEXT,
                Region TEXT
            )
        """)
        
        cursor.execute("DROP TABLE IF EXISTS Products")
        cursor.execute("""
            CREATE TABLE Products (
                ProductID TEXT PRIMARY KEY,
                Category TEXT,
                SubCategory TEXT,
                ProductName TEXT
            )
        """)
        
        cursor.execute("DROP TABLE IF EXISTS DimDate")
        cursor.execute("""
            CREATE TABLE DimDate (
                DateKey INTEGER PRIMARY KEY,
                CalendarDate DATE,
                Year INTEGER,
                Quarter INTEGER,
                Month INTEGER,
                Day INTEGER,
                Weekday TEXT,
                FiscalYear INTEGER,
                FiscalQuarter INTEGER
            )
        """)
        
        cursor.execute("DROP TABLE IF EXISTS DimStore")
        cursor.execute("""
            CREATE TABLE DimStore (
                StoreID INTEGER PRIMARY KEY,
                StoreName TEXT,
                Region TEXT,
                City TEXT,
                State TEXT
            )
        """)
        
        cursor.execute("DROP TABLE IF EXISTS DimShipMode")
        cursor.execute("""
            CREATE TABLE DimShipMode (
                ShipMode TEXT PRIMARY KEY
            )
        """)
        
        cursor.execute("DROP TABLE IF EXISTS SalesFact")
        cursor.execute("""
            CREATE TABLE SalesFact (
                RowID INTEGER PRIMARY KEY,
                OrderID TEXT,
                OrderDate TEXT,
                ShipDate TEXT,
                ShipMode TEXT,
                CustomerID TEXT,
                ProductID TEXT,
                Sales REAL,
                Quantity INTEGER,
                Discount REAL,
                Profit REAL,
                FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID),
                FOREIGN KEY (ProductID) REFERENCES Products(ProductID)
            )
        """)
        
        conn.commit()
        conn.close()
        print("Schema created successfully!")
    
    def run_full_etl(self):
        """Run the complete ETL pipeline"""
        print("=" * 60)
        print("ETL PIPELINE STARTED")
        print("=" * 60)
        start_time = datetime.now()
        
        print("\n--- EXTRACT PHASE ---")
        customers_raw = self.extract(self.source_files['customers'])
        products_raw = self.extract(self.source_files['products'])
        sales_raw = self.extract(self.source_files['sales'])
        dim_date_raw = self.extract(self.source_files['dim_date'])
        dim_store_raw = self.extract(self.source_files['dim_store'])
        dim_ship_mode_raw = self.extract(self.source_files['dim_ship_mode'])
        
        print("\n--- TRANSFORM PHASE ---")
        customers_transformed = self.transform_customers(customers_raw)
        products_transformed = self.transform_products(products_raw)
        sales_transformed = self.transform_sales(sales_raw)
        dim_date_transformed = self.transform_dim_date(dim_date_raw)
        dim_store_transformed = self.transform_dim_store(dim_store_raw)
        dim_ship_mode_transformed = self.transform_dim_ship_mode(dim_ship_mode_raw)
        
        print("\n--- LOAD PHASE ---")
        self.create_warehouse_schema()
        
        self.load_to_database('Customers', customers_transformed, 
                            ['CustomerID', 'CustomerName', 'Segment', 'Country', 'City', 'State', 'PostalCode', 'Region'])
        self.load_to_database('Products', products_transformed,
                            ['ProductID', 'Category', 'SubCategory', 'ProductName'])
        self.load_to_database('DimDate', dim_date_transformed,
                            ['DateKey', 'CalendarDate', 'Year', 'Quarter', 'Month', 'Day', 'Weekday', 'FiscalYear', 'FiscalQuarter'])
        self.load_to_database('DimStore', dim_store_transformed,
                            ['StoreID', 'StoreName', 'Region', 'City', 'State'])
        self.load_to_database('DimShipMode', dim_ship_mode_transformed,
                            ['ShipMode'])
        self.load_to_database('SalesFact', sales_transformed,
                            ['RowID', 'OrderID', 'OrderDate', 'ShipDate', 'ShipMode', 'CustomerID', 'ProductID', 'Sales', 'Quantity', 'Discount', 'Profit'])
        
        end_time = datetime.now()
        print("\n" + "=" * 60)
        print("ETL PIPELINE COMPLETED")
        print(f"Total execution time: {end_time - start_time}")
        print("=" * 60)
    
    def generate_data_quality_report(self):
        """Generate data quality report"""
        print("\n--- DATA QUALITY REPORT ---")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        tables = ['Customers', 'Products', 'SalesFact', 'DimDate', 'DimStore', 'DimShipMode']
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"{table}: {count} records")
            
            cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE rowid IS NULL")
            nulls = cursor.fetchone()[0]
            if nulls > 0:
                print(f"  WARNING: {nulls} rows with NULL values")
        
        conn.close()


if __name__ == "__main__":
    etl = ETLPipeline()
    etl.run_full_etl()
    etl.generate_data_quality_report()
