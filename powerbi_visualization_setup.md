# Power BI Visualization Setup Guide

## Exported Data Files

All data has been exported from MySQL to CSV files for Power BI import.

### File Location
```
D:\DW\cw\powerbi_exports\
```

### Files Available

| File | Rows | Description |
|------|------|-------------|
| dim_customer.csv | 793 | Customer dimension |
| dim_product.csv | 1,862 | Product dimension |
| dim_store.csv | 4 | Store dimension |
| dim_date.csv | 1,434 | Date dimension |
| dim_shipmode.csv | 4 | Ship mode dimension |
| fact_sales.csv | 39,976 | Sales transactions |
| fact_orders.csv | 20,036 | Order aggregations |

---

## How to Import into Power BI

### Step 1: Open Power BI
1. Launch Power BI Desktop
2. Click "Get Data" → "More..."

### Step 2: Select Data Source
1. Choose "Folder" to import all files at once
2. Or choose "Text/CSV" for individual files

### Step 3: Connect to Files
1. Browse to: `D:\DW\cw\powerbi_exports\`
2. Select all CSV files
3. Click "Combine" → "Combine & Transform"

### Step 4: Create Data Model
Power BI will automatically detect relationships. If not, create them:

---

## Required Relationships

Create these relationships in Power BI Model view:

```
fact_sales → dim_customer (customer_key)
fact_sales → dim_product (product_key)
fact_sales → dim_store (store_key)
fact_sales → dim_date (order_date_key)
fact_sales → dim_shipmode (shipmode_key)

fact_orders → dim_customer (customer_key)
fact_orders → dim_date (order_date_key)
fact_orders → dim_shipmode (shipmode_key)
fact_orders → dim_store (store_key)
```

---

## 10 Visualizations to Create

### 1. Regional Sales Performance (Map)
- **Visual:** Filled Map
- **Fields:** Region, Sum of Sales
- **Purpose:** Show sales by region

### 2. Category Revenue Analysis (Bar Chart)
- **Visual:** Bar Chart
- **Fields:** Category, Sum of Sales
- **Purpose:** Compare sales by product category

### 3. Quarterly Sales Trend (Line Chart)
- **Visual:** Line Chart
- **Fields:** Year, Quarter, Sum of Sales
- **Purpose:** Show sales over time

### 4. Customer Segment Analysis (Pie Chart)
- **Visual:** Pie Chart
- **Fields:** Segment, Sum of Sales
- **Purpose:** Show sales by customer segment

### 5. Shipping Mode Preferences (Bar Chart)
- **Visual:** Horizontal Bar Chart
- **Fields:** Ship Mode, Count of Orders
- **Purpose:** Show shipping preferences

### 6. Top Products by Profit (Treemap)
- **Visual:** Treemap
- **Fields:** Product Name, Sum of Profit
- **Purpose:** Highlight most profitable products

### 7. Monthly Sales Heatmap (Matrix)
- **Visual:** Matrix
- **Fields:** Month, Weekday, Sum of Sales
- **Purpose:** Show sales intensity by time

### 8. Discount Impact Analysis (Scatter)
- **Visual:** Scatter Chart
- **Fields:** Discount, Profit, Quantity
- **Purpose:** Show discount impact on profit

### 9. Customer Geographic Distribution (Map)
- **Visual:** Filled Map
- **Fields:** State, Count of Customers
- **Purpose:** Show customer concentration

### 10. Year-over-Year Comparison (Waterfall)
- **Visual:** Waterfall Chart
- **Fields:** Year, Sales
- **Purpose:** Show growth trends

---

## Sample DAX Measures

Create these measures in Power BI:

```DAX
Total Sales = SUM(fact_sales[sales])
Total Profit = SUM(fact_sales[profit])
Average Order Value = AVERAGE(fact_orders[total_sales])
Profit Margin = DIVIDE([Total Profit], [Total Sales])
```

---

## Export Complete Files

All 7 CSV files are ready in:
```
D:\DW\cw\powerbi_exports\
```

Total data: ~70,000 rows ready for analysis!



## next
Would you like me to help you create specific visualizations or export any additional data?