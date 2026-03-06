-- =============================================
-- MySQL Data Warehouse - Load CSV to Staging Tables
-- Run this in MySQL Workbench or mysql command line
-- =============================================

-- Enable local file loading (MySQL only)
SET GLOBAL local_infile = 1;

-- =============================================
-- STEP 1: Create Staging Tables (Drop if exists)
-- =============================================

-- Staging Customers (NO PRIMARY KEY - CSV has duplicate customer_ids)
DROP TABLE IF EXISTS staging_customers;
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

-- Staging Products (NO PRIMARY KEY - load via Python for special chars)
DROP TABLE IF EXISTS staging_products;
CREATE TABLE staging_products (
    product_id VARCHAR(50),
    category VARCHAR(100),
    subcategory VARCHAR(100),
    product_name LONGTEXT
);

-- Staging Stores
DROP TABLE IF EXISTS staging_stores;
CREATE TABLE staging_stores (
    store_id INT,
    store_name VARCHAR(100),
    region VARCHAR(50),
    city VARCHAR(100),
    state VARCHAR(100)
);

-- Staging Date
DROP TABLE IF EXISTS staging_date;
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

-- Staging ShipMode
DROP TABLE IF EXISTS staging_shipmode;
CREATE TABLE staging_shipmode (
    ship_mode VARCHAR(50)
);

-- Staging Sales
DROP TABLE IF EXISTS staging_sales;
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

-- Staging Orders
DROP TABLE IF EXISTS staging_orders;
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

-- =============================================
-- STEP 2: Load CSV files into staging tables
-- =============================================

-- 1. Customers
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/Customers.csv'
INTO TABLE staging_customers
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

-- 2. Products (Use Python - see below for special characters)

-- 3. Stores
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/DimStore.csv'
INTO TABLE staging_stores
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

-- 4. Date
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/DimDate.csv'
INTO TABLE staging_date
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

-- 5. ShipMode
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/DimShipMode.csv'
INTO TABLE staging_shipmode
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

-- 6. Sales
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/Fact_Sales.csv'
INTO TABLE staging_sales
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

-- 7. Orders
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/Fact_Orders.csv'
INTO TABLE staging_orders
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

-- =============================================
-- STEP 2b: Load Products via Python (handles special characters)
-- =============================================
/*
Run this Python script to load Products:
import csv
import subprocess

with open('C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/Products.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        sql = f"INSERT INTO staging_products (product_id, category, subcategory, product_name) VALUES ('{row['ProductID']}', '{row['Category']}', '{row['SubCategory']}', '{row['ProductName'].replace(\"'\", \"''\")}')"
        subprocess.run(['mysql', '-u', 'root', '-p5533', 'superstore', '-e', sql])
*/

-- =============================================
-- STEP 3: Verify data loaded
-- =============================================
SELECT 'staging_customers' AS table_name, COUNT(*) AS cnt FROM staging_customers UNION ALL
SELECT 'staging_products', COUNT(*) FROM staging_products UNION ALL
SELECT 'staging_stores', COUNT(*) FROM staging_stores UNION ALL
SELECT 'staging_date', COUNT(*) FROM staging_date UNION ALL
SELECT 'staging_shipmode', COUNT(*) FROM staging_shipmode UNION ALL
SELECT 'staging_sales', COUNT(*) FROM staging_sales UNION ALL
SELECT 'staging_orders', COUNT(*) FROM staging_orders;

-- =============================================
-- STEP 4: Create Dimension Tables
-- =============================================

-- Dim_Customer
DROP TABLE IF EXISTS dim_customer;
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

-- Dim_Product
DROP TABLE IF EXISTS dim_product;
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

-- Dim_Store
DROP TABLE IF EXISTS dim_store;
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

-- Dim_Date
DROP TABLE IF EXISTS dim_date;
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

-- Dim_ShipMode
DROP TABLE IF EXISTS dim_shipmode;
CREATE TABLE dim_shipmode (
    shipmode_key INT AUTO_INCREMENT PRIMARY KEY,
    ship_mode VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_ship_mode (ship_mode)
);

INSERT IGNORE INTO dim_shipmode (ship_mode)
SELECT DISTINCT ship_mode
FROM staging_shipmode;

-- =============================================
-- STEP 5: Create Fact Tables
-- =============================================

-- Fact_Sales (Line Item Level)
DROP TABLE IF EXISTS fact_sales;
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

-- Fact_Orders (Order Level)
DROP TABLE IF EXISTS fact_orders;
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

-- =============================================
-- STEP 6: Create Indexes
-- =============================================

CREATE INDEX idx_customer_id ON dim_customer(customer_id);
CREATE INDEX idx_product_id ON dim_product(product_id);
CREATE INDEX idx_date_calendar ON dim_date(calendar_date);
CREATE INDEX idx_shipmode ON dim_shipmode(ship_mode);

CREATE INDEX idx_fact_sales_order_date ON fact_sales(order_date_key);
CREATE INDEX idx_fact_sales_customer ON fact_sales(customer_key);
CREATE INDEX idx_fact_sales_product ON fact_sales(product_key);

CREATE INDEX idx_fact_orders_order_date ON fact_orders(order_date_key);
CREATE INDEX idx_fact_orders_customer ON fact_orders(customer_key);

-- =============================================
-- STEP 7: Verify All Tables
-- =============================================
SELECT 'Dimension Tables' AS type, 'dim_customer' AS table_name, COUNT(*) AS cnt FROM dim_customer
UNION ALL SELECT '', 'dim_product', COUNT(*) FROM dim_product
UNION ALL SELECT '', 'dim_store', COUNT(*) FROM dim_store
UNION ALL SELECT '', 'dim_date', COUNT(*) FROM dim_date
UNION ALL SELECT '', 'dim_shipmode', COUNT(*) FROM dim_shipmode
UNION ALL SELECT 'Fact Tables', 'fact_sales', COUNT(*) FROM fact_sales
UNION ALL SELECT '', 'fact_orders', COUNT(*) FROM fact_orders;
