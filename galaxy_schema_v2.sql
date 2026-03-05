-- ============================================
-- GALAXY SCHEMA FOR SUPERSTORE DATA WAREHOUSE
-- ============================================
-- Compatible with PostgreSQL
-- 2 Fact Tables: SalesFact, ReturnsFact
-- 5 Shared Dimensions: Customers, Products, DimDate, DimStore, DimShipMode
-- ============================================

-- ============================================
-- DIMENSION TABLES
-- ============================================

-- Customers Dimension (with surrogate key)
DROP TABLE IF EXISTS Customers CASCADE;
CREATE TABLE Customers (
    CustomerKey SERIAL PRIMARY KEY,
    CustomerID VARCHAR(50),
    CustomerName VARCHAR(255),
    Segment VARCHAR(50),
    Country VARCHAR(100),
    City VARCHAR(100),
    State VARCHAR(100),
    PostalCode VARCHAR(20),
    Region VARCHAR(50)
);

-- Products Dimension (with surrogate key)
DROP TABLE IF EXISTS Products CASCADE;
CREATE TABLE Products (
    ProductKey SERIAL PRIMARY KEY,
    ProductID VARCHAR(50),
    Category VARCHAR(100),
    SubCategory VARCHAR(100),
    ProductName VARCHAR(255)
);

-- Date Dimension
DROP TABLE IF EXISTS DimDate CASCADE;
CREATE TABLE DimDate (
    DateKey INTEGER PRIMARY KEY,
    CalendarDate DATE,
    Year INTEGER,
    Quarter INTEGER,
    Month INTEGER,
    Day INTEGER,
    Weekday VARCHAR(20),
    FiscalYear INTEGER,
    FiscalQuarter INTEGER
);

-- Store Dimension
DROP TABLE IF EXISTS DimStore CASCADE;
CREATE TABLE DimStore (
    StoreID INTEGER PRIMARY KEY,
    StoreName VARCHAR(100),
    Region VARCHAR(50),
    City VARCHAR(100),
    State VARCHAR(100)
);

-- Ship Mode Dimension
DROP TABLE IF EXISTS DimShipMode CASCADE;
CREATE TABLE DimShipMode (
    ShipMode VARCHAR(50) PRIMARY KEY
);

-- ============================================
-- FACT TABLE 1: SalesFact
-- ============================================

DROP TABLE IF EXISTS SalesFact CASCADE;
CREATE TABLE SalesFact (
    SalesFactKey SERIAL PRIMARY KEY,
    OrderID VARCHAR(50) NOT NULL,
    OrderDate DATE,
    ShipDate DATE,
    ShipMode VARCHAR(50),
    CustomerID VARCHAR(50),
    ProductID VARCHAR(50),
    StoreID INTEGER,
    Sales NUMERIC(12,2),
    Quantity INTEGER,
    Discount NUMERIC(5,2),
    Profit NUMERIC(12,2),
    ShippingCost NUMERIC(12,2),
    OrderStatus VARCHAR(50)
);

-- ============================================
-- FACT TABLE 2: ReturnsFact
-- ============================================

DROP TABLE IF EXISTS ReturnsFact CASCADE;
CREATE TABLE ReturnsFact (
    ReturnsFactKey SERIAL PRIMARY KEY,
    ReturnID VARCHAR(50) NOT NULL,
    OrderID VARCHAR(50),
    ReturnDate DATE,
    CustomerID VARCHAR(50),
    ProductID VARCHAR(50),
    StoreID INTEGER,
    OriginalSales NUMERIC(12,2),
    ReturnAmount NUMERIC(12,2),
    ReturnReason VARCHAR(100),
    ReturnStatus VARCHAR(50),
    RefundProcessed DATE
);

-- ============================================
-- INDEXES FOR PERFORMANCE
-- ============================================

CREATE INDEX idx_sales_order ON SalesFact(OrderID);
CREATE INDEX idx_sales_customer ON SalesFact(CustomerID);
CREATE INDEX idx_sales_product ON SalesFact(ProductID);
CREATE INDEX idx_sales_date ON SalesFact(OrderDate);

CREATE INDEX idx_returns_order ON ReturnsFact(OrderID);
CREATE INDEX idx_returns_customer ON ReturnsFact(CustomerID);
CREATE INDEX idx_returns_product ON ReturnsFact(ProductID);

CREATE INDEX idx_customers_id ON Customers(CustomerID);
CREATE INDEX idx_products_id ON Products(ProductID);

-- ============================================
-- FOREIGN KEYS
-- ============================================

ALTER TABLE SalesFact 
    ADD CONSTRAINT fk_sales_shipmode FOREIGN KEY (ShipMode) REFERENCES DimShipMode(ShipMode);

ALTER TABLE SalesFact 
    ADD CONSTRAINT fk_sales_customer FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID);

ALTER TABLE SalesFact 
    ADD CONSTRAINT fk_sales_product FOREIGN KEY (ProductID) REFERENCES Products(ProductID);

ALTER TABLE SalesFact 
    ADD CONSTRAINT fk_sales_store FOREIGN KEY (StoreID) REFERENCES DimStore(StoreID);

ALTER TABLE ReturnsFact 
    ADD CONSTRAINT fk_returns_customer FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID);

ALTER TABLE ReturnsFact 
    ADD CONSTRAINT fk_returns_product FOREIGN KEY (ProductID) REFERENCES Products(ProductID);

ALTER TABLE ReturnsFact 
    ADD CONSTRAINT fk_returns_store FOREIGN KEY (StoreID) REFERENCES DimStore(StoreID);

-- ============================================
-- SCHEMA SUMMARY
-- ============================================

SELECT 'GALAXY SCHEMA CREATED' AS Status;
SELECT 'FACT TABLES: SalesFact (transactions), ReturnsFact (returns)' AS FactTables;
SELECT 'DIMENSIONS: Customers, Products, DimDate, DimStore, DimShipMode' AS Dimensions;
