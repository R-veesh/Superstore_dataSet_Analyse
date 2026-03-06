# Supabase Data Warehouse Setup Guide

This document provides SQL commands to create staging tables, dimension tables, and fact tables in Supabase, along with instructions to load data from CSV files.

---

## Part 1: Staging Tables

Create staging tables in Supabase to load data from CSV files.

### 1.1 Staging_Customers
```sql
CREATE TABLE staging_customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    customer_name VARCHAR(255),
    segment VARCHAR(50),
    country VARCHAR(100),
    city VARCHAR(100),
    state VARCHAR(100),
    postal_code VARCHAR(20),
    region VARCHAR(50)
);
```

### 1.2 Staging_Products
```sql
CREATE TABLE staging_products (
    product_id VARCHAR(50) PRIMARY KEY,
    category VARCHAR(100),
    subcategory VARCHAR(100),
    product_name VARCHAR(500)
);
```

### 1.3 Staging_Stores
```sql
CREATE TABLE staging_stores (
    store_id INT PRIMARY KEY,
    store_name VARCHAR(100),
    region VARCHAR(50),
    city VARCHAR(100),
    state VARCHAR(100)
);
```

### 1.4 Staging_Date
```sql
CREATE TABLE staging_date (
    date_key INT PRIMARY KEY,
    calendar_date TIMESTAMP,
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
    ship_mode VARCHAR(50) PRIMARY KEY
);
```

### 1.6 Staging_Sales
```sql
CREATE TABLE staging_sales (
    row_id INT PRIMARY KEY,
    order_id VARCHAR(50),
    order_date TIMESTAMP,
    ship_date TIMESTAMP,
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
    order_id VARCHAR(50) PRIMARY KEY,
    order_date TIMESTAMP,
    ship_date TIMESTAMP,
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

| CSV File | Staging Table | Description |
|----------|---------------|-------------|
| `Customers.csv` | `staging_customers` | Customer master data |
| `Products.csv` | `staging_products` | Product catalog |
| `DimStore.csv` | `staging_stores` | Store/region information |
| `DimDate.csv` | `staging_date` | Date dimension data |
| `DimShipMode.csv` | `staging_shipmode` | Shipping modes |
| `Fact_Sales.csv` | `staging_sales` | Sales transactions (line items) |
| `Fact_Orders.csv` | `staging_orders` | Order-level aggregations |

---

## Part 3: Load Data from CSV to Staging Tables

Use Supabase Dashboard or SQL to import CSV data:

### Option 1: Via Supabase Dashboard
1. Go to **Supabase Dashboard** > **Your Project** > **Table Editor**
2. Select the staging table
3. Click **Import Data** > **Upload CSV**
4. Select the corresponding CSV file from `powerbi_data/` folder
5. Configure import settings (first row as header: YES)
6. Click **Import**

### Option 2: Via SQL (using COPY)
```sql
-- Run this in Supabase SQL Editor
-- Make sure your CSV files are accessible via URL or local path

COPY staging_customers FROM 'powerbi_data/Customers.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');
COPY staging_products FROM 'powerbi_data/Products.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');
COPY staging_stores FROM 'powerbi_data/DimStore.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');
COPY staging_date FROM 'powerbi_data/DimDate.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');
COPY staging_shipmode FROM 'powerbi_data/DimShipMode.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');
COPY staging_sales FROM 'powerbi_data/Fact_Sales.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');
COPY staging_orders FROM 'powerbi_data/Fact_Orders.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');
```

---

## Part 4: Dimension Tables

Create dimension tables with surrogate keys.

### 4.1 Dim_Customer
```sql
CREATE TABLE dim_customer (
    customer_key SERIAL PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    customer_name VARCHAR(255),
    segment VARCHAR(50),
    country VARCHAR(100),
    city VARCHAR(100),
    state VARCHAR(100),
    postal_code VARCHAR(20),
    region VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Populate from staging
INSERT INTO dim_customer (customer_id, customer_name, segment, country, city, state, postal_code, region)
SELECT DISTINCT 
    customer_id,
    customer_name,
    segment,
    country,
    city,
    state,
    postal_code,
    region
FROM staging_customers
ON CONFLICT (customer_id) DO NOTHING;
```

### 4.2 Dim_Product
```sql
CREATE TABLE dim_product (
    product_key SERIAL PRIMARY KEY,
    product_id VARCHAR(50) NOT NULL,
    category VARCHAR(100),
    subcategory VARCHAR(100),
    product_name VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Populate from staging
INSERT INTO dim_product (product_id, category, subcategory, product_name)
SELECT DISTINCT 
    product_id,
    category,
    subcategory,
    product_name
FROM staging_products
ON CONFLICT (product_id) DO NOTHING;
```

### 4.3 Dim_Store
```sql
CREATE TABLE dim_store (
    store_key SERIAL PRIMARY KEY,
    store_id INT NOT NULL,
    store_name VARCHAR(100),
    region VARCHAR(50),
    city VARCHAR(100),
    state VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Populate from staging
INSERT INTO dim_store (store_id, store_name, region, city, state)
SELECT DISTINCT 
    store_id,
    store_name,
    region,
    city,
    state
FROM staging_stores
ON CONFLICT (store_id) DO NOTHING;
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

-- Populate from staging
INSERT INTO dim_date (date_key, calendar_date, year, quarter, month, day, weekday, fiscal_year, fiscal_quarter)
SELECT DISTINCT 
    date_key,
    DATE(calendar_date),
    year,
    quarter,
    month,
    day,
    weekday,
    fiscal_year,
    fiscal_quarter
FROM staging_date
ON CONFLICT (date_key) DO NOTHING;
```

### 4.5 Dim_ShipMode
```sql
CREATE TABLE dim_shipmode (
    shipmode_key SERIAL PRIMARY KEY,
    ship_mode VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Populate from staging
INSERT INTO dim_shipmode (ship_mode)
SELECT DISTINCT ship_mode
FROM staging_shipmode
ON CONFLICT (ship_mode) DO NOTHING;
```

---

## Part 5: Fact Tables

### 5.1 Fact_Sales (Line Item Level)
```sql
CREATE TABLE fact_sales (
    sales_key SERIAL PRIMARY KEY,
    row_id INT,
    order_id VARCHAR(50),
    order_date_key INT REFERENCES dim_date(date_key),
    ship_date_key INT REFERENCES dim_date(date_key),
    customer_key INT REFERENCES dim_customer(customer_key),
    product_key INT REFERENCES dim_product(product_key),
    store_key INT REFERENCES dim_store(store_key),
    shipmode_key INT REFERENCES dim_shipmode(shipmode_key),
    sales DECIMAL(10,2),
    quantity INT,
    discount DECIMAL(5,2),
    profit DECIMAL(10,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Populate from staging with foreign key lookups
INSERT INTO fact_sales (
    row_id,
    order_id,
    order_date_key,
    ship_date_key,
    customer_key,
    product_key,
    store_key,
    shipmode_key,
    sales,
    quantity,
    discount,
    profit
)
SELECT 
    s.row_id,
    s.order_id,
    d_order.date_key,
    d_ship.date_key,
    c.customer_key,
    p.product_key,
    st.store_key,
    sm.shipmode_key,
    s.sales,
    s.quantity,
    s.discount,
    s.profit
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
    order_key SERIAL PRIMARY KEY,
    order_id VARCHAR(50) NOT NULL,
    order_date_key INT REFERENCES dim_date(date_key),
    ship_date_key INT REFERENCES dim_date(date_key),
    customer_key INT REFERENCES dim_customer(customer_key),
    shipmode_key INT REFERENCES dim_shipmode(shipmode_key),
    store_key INT REFERENCES dim_store(store_key),
    total_sales DECIMAL(10,2),
    total_quantity INT,
    total_discount DECIMAL(10,2),
    total_profit DECIMAL(10,4),
    product_count INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Populate from staging orders with foreign key lookups
INSERT INTO fact_orders (
    order_id,
    order_date_key,
    ship_date_key,
    customer_key,
    shipmode_key,
    store_key,
    total_sales,
    total_quantity,
    total_discount,
    total_profit,
    product_count
)
SELECT 
    o.order_id,
    d_order.date_key,
    d_ship.date_key,
    c.customer_key,
    sm.shipmode_key,
    st.store_key,
    o.sales,
    o.quantity,
    o.discount,
    o.profit,
    o.product_count
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
-- Indexes for dimension tables
CREATE INDEX idx_customer_id ON dim_customer(customer_id);
CREATE INDEX idx_product_id ON dim_product(product_id);
CREATE INDEX idx_date_calendar ON dim_date(calendar_date);
CREATE INDEX idx_shipmode ON dim_shipmode(ship_mode);

-- Indexes for fact_sales table
CREATE INDEX idx_fact_sales_order_date ON fact_sales(order_date_key);
CREATE INDEX idx_fact_sales_customer ON fact_sales(customer_key);
CREATE INDEX idx_fact_sales_product ON fact_sales(product_key);
CREATE INDEX idx_fact_sales_sales ON fact_sales(sales);

-- Indexes for fact_orders table
CREATE INDEX idx_fact_orders_order_date ON fact_orders(order_date_key);
CREATE INDEX idx_fact_orders_customer ON fact_orders(customer_key);
CREATE INDEX idx_fact_orders_sales ON fact_orders(total_sales);
```

---

## Part 7: Verify Data

```sql
-- Check record counts
SELECT 'staging_customers' AS table_name, COUNT(*) AS record_count FROM staging_customers
UNION ALL
SELECT 'staging_products', COUNT(*) FROM staging_products
UNION ALL
SELECT 'staging_stores', COUNT(*) FROM staging_stores
UNION ALL
SELECT 'staging_date', COUNT(*) FROM staging_date
UNION ALL
SELECT 'staging_shipmode', COUNT(*) FROM staging_shipmode
UNION ALL
SELECT 'staging_sales', COUNT(*) FROM staging_sales
UNION ALL
SELECT 'staging_orders', COUNT(*) FROM staging_orders
UNION ALL
SELECT 'dim_customer', COUNT(*) FROM dim_customer
UNION ALL
SELECT 'dim_product', COUNT(*) FROM dim_product
UNION ALL
SELECT 'dim_store', COUNT(*) FROM dim_store
UNION ALL
SELECT 'dim_date', COUNT(*) FROM dim_date
UNION ALL
SELECT 'dim_shipmode', COUNT(*) FROM dim_shipmode
UNION ALL
SELECT 'fact_sales', COUNT(*) FROM fact_sales
UNION ALL
SELECT 'fact_orders', COUNT(*) FROM fact_orders;
```

---

## Summary

| Table Type | Table Name | Source CSV |
|------------|------------|------------|
| Staging | `staging_customers` | Customers.csv |
| Staging | `staging_products` | Products.csv |
| Staging | `staging_stores` | DimStore.csv |
| Staging | `staging_date` | DimDate.csv |
| Staging | `staging_shipmode` | DimShipMode.csv |
| Staging | `staging_sales` | Fact_Sales.csv |
| Staging | `staging_orders` | Fact_Orders.csv |
| Dimension | `dim_customer` | staging_customers |
| Dimension | `dim_product` | staging_products |
| Dimension | `dim_store` | staging_stores |
| Dimension | `dim_date` | staging_date |
| Dimension | `dim_shipmode` | staging_shipmode |
| Fact | `fact_sales` | staging_sales (line item level) |
| Fact | `fact_orders` | staging_orders (order level) |
