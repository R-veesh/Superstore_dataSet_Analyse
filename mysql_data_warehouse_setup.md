# MySQL Data Warehouse Setup Guide

This document provides SQL commands to create staging tables, dimension tables, and fact tables in MySQL, along with instructions to load data from CSV files.

---

## Part 1: Staging Tables

Create staging tables in MySQL to load data from CSV files.

### 1.1 Staging_Customers
**Note:** NO PRIMARY KEY - CSV has duplicate customer_ids with different addresses
```sql
CREATE TABLE staging_customers (
    customer_id VARCHAR(50),
    customer_name VARCHAR(255),
    segment VARCHAR(50),
    country VARCHAR(100),
    city VARCHAR(100),
    state VARCHAR(100),
    postal_code VARCHAR(20),
    region VARCHAR(100)
);
```

### 1.2 Staging_Products
**Note:** Use LONGTEXT for product_name due to long product names with special characters
```sql
CREATE TABLE staging_products (
    product_id VARCHAR(50),
    category VARCHAR(100),
    subcategory VARCHAR(100),
    product_name LONGTEXT
);
```

### 1.3 Staging_Stores
```sql
CREATE TABLE staging_stores (
    store_id INT,
    store_name VARCHAR(100),
    region VARCHAR(50),
    city VARCHAR(100),
    state VARCHAR(100)
);
```

### 1.4 Staging_Date
```sql
CREATE TABLE staging_date (
    date_key INT,
    calendar_date DATETIME,
    year INT,
    quarter INT,
    month INT,
    day INT,
    weekday VARCHAR(20),
    fiscal_year INT,
    fiscal_quarter INT
);
```

### 1.5 Staging_ShipMode
```sql
CREATE TABLE staging_shipmode (
    ship_mode VARCHAR(50)
);
```

### 1.6 Staging_Sales
```sql
CREATE TABLE staging_sales (
    row_id INT,
    order_id VARCHAR(50),
    order_date DATETIME,
    ship_date DATETIME,
    ship_mode VARCHAR(50),
    customer_id VARCHAR(50),
    product_id VARCHAR(50),
    sales DECIMAL(10,2),
    quantity INT,
    discount DECIMAL(5,2),
    profit DECIMAL(10,4)
);
```

### 1.7 Staging_Orders
```sql
CREATE TABLE staging_orders (
    order_id VARCHAR(50),
    order_date DATETIME,
    ship_date DATETIME,
    ship_mode VARCHAR(50),
    customer_id VARCHAR(50),
    sales DECIMAL(10,2),
    quantity INT,
    discount DECIMAL(10,2),
    profit DECIMAL(10,4),
    product_count INT
);
```

---

## Part 2: CSV to Staging Table Mapping

| CSV File | Staging Table | Rows Loaded | Notes |
|----------|---------------|-------------|-------|
| `Customers.csv` | `staging_customers` | 4,910 | NO PRIMARY KEY (duplicates) |
| `Products.csv` | `staging_products` | 1,896 | Use Python to load (special chars) |
| `DimStore.csv` | `staging_stores` | 4 | |
| `DimDate.csv` | `staging_date` | 1,434 | |
| `DimShipMode.csv` | `staging_shipmode` | 4 | |
| `Fact_Sales.csv` | `staging_sales` | 9,994 | |
| `Fact_Orders.csv` | `staging_orders` | 5,009 | |

---

## Part 3: Load Data from CSV to Staging Tables

### Important Notes:
1. Enable local file loading: `SET GLOBAL local_infile = 1;`
2. Products CSV has special characters - use Python script to load
3. Customers CSV has duplicate IDs - no PRIMARY KEY on staging table

### Load Customers, Stores, Date, ShipMode, Sales, Orders:
```sql
-- Enable local file loading
SET GLOBAL local_infile = 1;

-- Customers
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/Customers.csv'
INTO TABLE staging_customers
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

-- Stores
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/DimStore.csv'
INTO TABLE staging_stores
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

-- Date
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/DimDate.csv'
INTO TABLE staging_date
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

-- ShipMode
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/DimShipMode.csv'
INTO TABLE staging_shipmode
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

-- Sales
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/Fact_Sales.csv'
INTO TABLE staging_sales
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

-- Orders
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/Fact_Orders.csv'
INTO TABLE staging_orders
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;
```

### Load Products (Python - handles special characters):
```python
import csv
import subprocess

with open('C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/Products.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        sql = f"""INSERT INTO staging_products (product_id, category, subcategory, product_name) 
        VALUES ('{row['ProductID']}', '{row['Category']}', '{row['SubCategory']}', '{row['ProductName'].replace("'", "''")}')"""
        subprocess.run([
            'C:/Program Files/MySQL/MySQL Server 8.0/bin/mysql.exe',
            '-u', 'root', '-p5533', 'superstore',
            '-e', sql
        ], capture_output=True)

print(f'Loaded products')
```

---

## Part 4: Dimension Tables

Create dimension tables with surrogate keys.

### 4.1 Dim_Customer
```sql
CREATE TABLE dim_customer (
    customer_key INT AUTO_INCREMENT PRIMARY KEY,
    customer_id VARCHAR(50),
    customer_name VARCHAR(255),
    segment VARCHAR(50),
    country VARCHAR(100),
    city VARCHAR(100),
    state VARCHAR(100),
    postal_code VARCHAR(20),
    region VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_customer_id (customer_id)
);

INSERT IGNORE INTO dim_customer (customer_id, customer_name, segment, country, city, state, postal_code, region)
SELECT DISTINCT customer_id, customer_name, segment, country, city, state, postal_code, region
FROM staging_customers;
```

### 4.2 Dim_Product
```sql
CREATE TABLE dim_product (
    product_key INT AUTO_INCREMENT PRIMARY KEY,
    product_id VARCHAR(50),
    category VARCHAR(100),
    subcategory VARCHAR(100),
    product_name LONGTEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_product_id (product_id)
);

INSERT IGNORE INTO dim_product (product_id, category, subcategory, product_name)
SELECT DISTINCT product_id, category, subcategory, product_name
FROM staging_products;
```

### 4.3 Dim_Store
```sql
CREATE TABLE dim_store (
    store_key INT AUTO_INCREMENT PRIMARY KEY,
    store_id INT,
    store_name VARCHAR(100),
    region VARCHAR(50),
    city VARCHAR(100),
    state VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_store_id (store_id)
);

INSERT IGNORE INTO dim_store (store_id, store_name, region, city, state)
SELECT DISTINCT store_id, store_name, region, city, state
FROM staging_stores;
```

### 4.4 Dim_Date
```sql
CREATE TABLE dim_date (
    date_key INT PRIMARY KEY,
    calendar_date DATE,
    year INT,
    quarter INT,
    month INT,
    day INT,
    weekday VARCHAR(20),
    fiscal_year INT,
    fiscal_quarter INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT IGNORE INTO dim_date (date_key, calendar_date, year, quarter, month, day, weekday, fiscal_year, fiscal_quarter)
SELECT DISTINCT date_key, DATE(calendar_date), year, quarter, month, day, weekday, fiscal_year, fiscal_quarter
FROM staging_date;
```

### 4.5 Dim_ShipMode
```sql
CREATE TABLE dim_shipmode (
    shipmode_key INT AUTO_INCREMENT PRIMARY KEY,
    ship_mode VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_ship_mode (ship_mode)
);

INSERT IGNORE INTO dim_shipmode (ship_mode)
SELECT DISTINCT ship_mode
FROM staging_shipmode;
```

---

## Part 5: Fact Tables

### 5.1 Fact_Sales (Line Item Level)
```sql
CREATE TABLE fact_sales (
    sales_key INT AUTO_INCREMENT PRIMARY KEY,
    row_id INT,
    order_id VARCHAR(50),
    order_date_key INT,
    ship_date_key INT,
    customer_key INT,
    product_key INT,
    store_key INT,
    shipmode_key INT,
    sales DECIMAL(10,2),
    quantity INT,
    discount DECIMAL(5,2),
    profit DECIMAL(10,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO fact_sales (
    row_id, order_id, order_date_key, ship_date_key, customer_key, product_key, store_key, shipmode_key, sales, quantity, discount, profit
)
SELECT 
    s.row_id, s.order_id, d_order.date_key, d_ship.date_key,
    c.customer_key, p.product_key, st.store_key, sm.shipmode_key,
    s.sales, s.quantity, s.discount, s.profit
FROM staging_sales s
LEFT JOIN dim_customer c ON s.customer_id = c.customer_id
LEFT JOIN dim_product p ON s.product_id = p.product_id
LEFT JOIN dim_date d_order ON DATE(s.order_date) = d_order.calendar_date
LEFT JOIN dim_date d_ship ON DATE(s.ship_date) = d_ship.calendar_date
LEFT JOIN dim_shipmode sm ON s.ship_mode = sm.ship_mode
LEFT JOIN dim_store st ON 1=1;
```

### 5.2 Fact_Orders (Order Level Aggregation)
```sql
CREATE TABLE fact_orders (
    order_key INT AUTO_INCREMENT PRIMARY KEY,
    order_id VARCHAR(50),
    order_date_key INT,
    ship_date_key INT,
    customer_key INT,
    shipmode_key INT,
    store_key INT,
    total_sales DECIMAL(10,2),
    total_quantity INT,
    total_discount DECIMAL(10,2),
    total_profit DECIMAL(10,4),
    product_count INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO fact_orders (
    order_id, order_date_key, ship_date_key, customer_key, shipmode_key, store_key,
    total_sales, total_quantity, total_discount, total_profit, product_count
)
SELECT 
    o.order_id, d_order.date_key, d_ship.date_key, c.customer_key, sm.shipmode_key, st.store_key,
    o.sales, o.quantity, o.discount, o.profit, o.product_count
FROM staging_orders o
LEFT JOIN dim_customer c ON o.customer_id = c.customer_id
LEFT JOIN dim_date d_order ON DATE(o.order_date) = d_order.calendar_date
LEFT JOIN dim_date d_ship ON DATE(o.ship_date) = d_ship.calendar_date
LEFT JOIN dim_shipmode sm ON o.ship_mode = sm.ship_mode
LEFT JOIN dim_store st ON 1=1;
```

---

## Part 6: Create Indexes for Performance

```sql
-- Dimension tables
CREATE INDEX idx_customer_id ON dim_customer(customer_id);
CREATE INDEX idx_product_id ON dim_product(product_id);
CREATE INDEX idx_date_calendar ON dim_date(calendar_date);
CREATE INDEX idx_shipmode ON dim_shipmode(ship_mode);

-- Fact tables
CREATE INDEX idx_fact_sales_order_date ON fact_sales(order_date_key);
CREATE INDEX idx_fact_sales_customer ON fact_sales(customer_key);
CREATE INDEX idx_fact_sales_product ON fact_sales(product_key);

CREATE INDEX idx_fact_orders_order_date ON fact_orders(order_date_key);
CREATE INDEX idx_fact_orders_customer ON fact_orders(customer_key);
```

---

## Part 7: Verify Data

```sql
-- Staging tables
SELECT 'staging_customers' AS table_name, COUNT(*) AS cnt FROM staging_customers UNION ALL
SELECT 'staging_products', COUNT(*) FROM staging_products UNION ALL
SELECT 'staging_stores', COUNT(*) FROM staging_stores UNION ALL
SELECT 'staging_date', COUNT(*) FROM staging_date UNION ALL
SELECT 'staging_shipmode', COUNT(*) FROM staging_shipmode UNION ALL
SELECT 'staging_sales', COUNT(*) FROM staging_sales UNION ALL
SELECT 'staging_orders', COUNT(*) FROM staging_orders;

-- Dimension tables
SELECT 'dim_customer' AS table_name, COUNT(*) AS cnt FROM dim_customer UNION ALL
SELECT 'dim_product', COUNT(*) FROM dim_product UNION ALL
SELECT 'dim_store', COUNT(*) FROM dim_store UNION ALL
SELECT 'dim_date', COUNT(*) FROM dim_date UNION ALL
SELECT 'dim_shipmode', COUNT(*) FROM dim_shipmode;

-- Fact tables
SELECT 'fact_sales' AS table_name, COUNT(*) AS cnt FROM fact_sales UNION ALL
SELECT 'fact_orders', COUNT(*) FROM fact_orders;
```

---

## Part 8: Implementation Results

### Staging Tables Loaded:
| Table | Rows |
|-------|------|
| staging_customers | 4,910 |
| staging_products | 1,896 |
| staging_stores | 4 |
| staging_date | 1,434 |
| staging_shipmode | 4 |
| staging_sales | 9,994 |
| staging_orders | 5,009 |

### Dimension Tables Created:
| Table | Rows |
|-------|------|
| dim_customer | 793 |
| dim_product | 1,862 |
| dim_store | 4 |
| dim_date | 1,434 |
| dim_shipmode | 4 |

### Fact Tables Created:
| Table | Rows |
|-------|------|
| fact_sales | 39,976 |
| fact_orders | 20,036 |

---

## Summary

| Table Type | Table Name | Source CSV | Rows |
|------------|------------|------------|------|
| Staging | `staging_customers` | Customers.csv | 4,910 |
| Staging | `staging_products` | Products.csv | 1,896 |
| Staging | `staging_stores` | DimStore.csv | 4 |
| Staging | `staging_date` | DimDate.csv | 1,434 |
| Staging | `staging_shipmode` | DimShipMode.csv | 4 |
| Staging | `staging_sales` | Fact_Sales.csv | 9,994 |
| Staging | `staging_orders` | Fact_Orders.csv | 5,009 |
| Dimension | `dim_customer` | staging_customers | 793 |
| Dimension | `dim_product` | staging_products | 1,862 |
| Dimension | `dim_store` | staging_stores | 4 |
| Dimension | `dim_date` | staging_date | 1,434 |
| Dimension | `dim_shipmode` | staging_shipmode | 4 |
| Fact | `fact_sales` | staging_sales + dimensions | 39,976 |
| Fact | `fact_orders` | staging_orders + dimensions | 20,036 |

---

## Key Differences: PostgreSQL vs MySQL

| Feature | PostgreSQL | MySQL |
|---------|------------|-------|
| Auto Increment | `SERIAL` | `INT AUTO_INCREMENT` |
| UPSERT | `ON CONFLICT DO NOTHING` | `INSERT IGNORE` |
| Load CSV | `COPY` | `LOAD DATA INFILE` |
| Date Type | `TIMESTAMP` | `DATETIME` |
| Long Text | `TEXT` | `LONGTEXT` |

---

## Common Errors and Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| Error 1290 | secure_file_priv restriction | Use allowed folder or `SET GLOBAL local_infile = 1` |
| Error 1062 | Duplicate primary key | Remove PRIMARY KEY from staging, use INSERT IGNORE |
| Error 1406 | Data too long | Use LONGTEXT instead of VARCHAR |
| Error 1062 (duplicate) | Table has data | TRUNCATE table before loading |
