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

Below are the ten target visuals with step‑by‑step instructions for building each one, the DAX measures you’ll need, and a reminder of which exported table provides the required columns.

### Understanding the tables in the export

| Table (CSV)      | Purpose                                | Key columns used here |
|------------------|----------------------------------------|-----------------------|
| **fact_sales**   | Transaction‑level facts                | sales, profit, discount, quantity, customer_key, product_key, shipmode_key, store_key, order_date_key |
| **fact_orders**  | Order aggregates                       | total_sales, order_id, customer_key, shipmode_key, order_date_key |
| **dim_customer** | Customer dimension                     | customer_key, region, segment, state |
| **dim_product**  | Product details                        | product_key, category, product_name |
| **dim_date**     | Calendar dates (calendar_date)         | calendar_date, year, quarter, month, weekday |
| **dim_shipmode** | Shipping mode lookup                   | shipmode_key, ship_mode |
| **dim_store**    | Store/location dimension               | store_key, store_name, store_id |

All of the tables are loaded from `D:\DW\cw\powerbi_exports\` when you import the folder.

---

### 1. Regional Sales Performance (Filled Map)

1. Add a **Filled map** visual.
2. Drag `dim_customer[region]` into **Location**.
3. Put a measure in **Values** – use `Sales by Region` or simply `Total Sales`.
4. (Optional) add `Total Sales` to **Tooltips** for hover details.
5. Set the `Data category` on `region` to **Region** if Power BI doesn’t geocode it automatically.

> **DAX used:**
> ```DAX
> Sales by Region =
>     CALCULATE([Total Sales], ALLEXCEPT(dim_customer, dim_customer[region]))
> ```

### 2. Category Revenue Analysis (Bar Chart)

1. Insert a **Clustered bar chart** (horizontal or vertical).
2. **Axis**: `dim_product[category]`.
3. **Values**: `Total Sales` or `Sales by Category`.
4. Optionally add `Total Profit` to Tooltips or a secondary value.

> `Sales by Category` measure:
> ```DAX
> Sales by Category =
>     CALCULATE([Total Sales], ALLEXCEPT(dim_product, dim_product[category]))
> ```

### 3. Quarterly Sales Trend (Line Chart)

1. Make sure you have `Year`/`Quarter` available (see the helper formulas or add columns to `dim_date`).
2. Choose **Line chart**.
3. Drag `Year` then `Quarter` into the **Axis** well (hierarchy will order them).
4. **Values**: `Total Sales`.
5. If quarters sort incorrectly, use `Sort by Column` on the `Quarter` column with a numeric quarter field.
6. For continuous axis, use `dim_date[calendar_date]` and set X‑Axis → Type = **Continuous** in formatting.

> DAX helpers for this visual:
> ```DAX
> Year = YEAR(SELECTEDVALUE(dim_date[calendar_date]))
> Quarter = "Q" & FORMAT(SELECTEDVALUE(dim_date[calendar_date]), "Q")
> ```

### 4. Customer Segment Analysis (Pie Chart)

1. Add a **Pie chart** visual.
2. **Legend**: `dim_customer[segment]`.
3. **Values**: `Total Sales`.
4. Adjust the `Detail` or `Tooltip` with `Order Count` or `Total Profit`.

> Useful measure: `Order Count = COUNT(fact_orders[order_id])`.

### 5. Shipping Mode Preferences (Horizontal Bar Chart)

1. Insert a **Stacked bar chart** and set orientation to horizontal.
2. **Axis**: `dim_shipmode[ship_mode]`.
3. **Values**: `Order Count` (included above) or `COUNTROWS(fact_orders)`.
4. Add filter on `fact_orders` or `fact_sales` if you want only delivered orders, etc.

### 6. Top Products by Profit (Treemap)

1. Pick the **Treemap** visual.
2. **Group**: `dim_product[product_name]`.
3. **Values**: `Total Profit`.
4. Apply a **Top N filter** to the visual:
   - In the Filters pane, expand the field `dim_product[product_name]`.
   - Choose **Top N** from the filter type dropdown.
   - Enter `20` in the “Show items” box and drag the measure `Total Profit` into the *By value* area.
   - Click **Apply filter**.

> Alternatively you can create a ranking measure and filter manually:
>
> ```DAX
> Product Profit Rank =
>     RANKX(
>         ALL(dim_product[product_name]),
>         [Total Profit],
>         ,
>         DESC,
>         Dense
>     )
> ```
>
> Then add a visual-level filter on `Product Profit Rank` where `<= 20`.

### 7. Monthly Sales Heatmap (Matrix)

1. Choose the **Matrix** visual.
2. **Rows**: `dim_date[month]` (or a custom month name column).
3. **Columns**: `dim_date[weekday]`.
4. **Values**: `Total Sales`.
5. Turn on **Conditional formatting** (Color scale) to create the heatmap appearance.

> You may need calculated columns in `dim_date` for month name and weekday name.

### 8. Discount Impact Analysis (Scatter Chart)

1. Add a **Scatter chart**.
2. **X‑axis**: `fact_sales[discount]`.
3. **Y‑axis**: `fact_sales[profit]`.
4. **Size**: `fact_sales[quantity]`.
5. Use `dim_product[category]` or `dim_customer[segment]` as the **Legend** to colour points.

### 9. Customer Geographic Distribution (Filled Map)

1. Place a **Filled map** visual (new one or duplicate the first).
2. **Location**: `dim_customer[state]` (set Data category to **State or Province**).
3. **Values**: `Customer Count` (distinct count of customer_key from dim_customer).

> Measure:
> ```DAX
> Customer Count = DISTINCTCOUNT(dim_customer[customer_key])
> ```

### 10. Year‑over‑Year Comparison (Waterfall Chart)

1. Insert a **Waterfall chart**.
2. **Category**: `Year` (from dim_date, as a column or measure).
3. **Values**: `Total Sales`.
4. Format the visual to show the difference between years automatically.
5. For more control, build a measure such as:
   ```DAX
   YoY Change = [Total Sales] - CALCULATE([Total Sales], SAMEPERIODLASTYEAR(dim_date[calendar_date]))
   ```
   and display it as the breakdown in the waterfall.

---

### DAX Summary

```DAX
Total Sales = SUM(fact_sales[sales])
Total Profit = SUM(fact_sales[profit])
Average Order Value = AVERAGE(fact_orders[total_sales])
Profit Margin = DIVIDE([Total Profit], [Total Sales])
Order Count = COUNT(fact_orders[order_id])
Customer Count = DISTINCTCOUNT(dim_customer[customer_key])

Sales by Region =
    CALCULATE([Total Sales], ALLEXCEPT(dim_customer, dim_customer[region]))

Sales by Category =
    CALCULATE([Total Sales], ALLEXCEPT(dim_product, dim_product[category]))

Year = YEAR(SELECTEDVALUE(dim_date[calendar_date]))
Quarter = "Q" & FORMAT(SELECTEDVALUE(dim_date[calendar_date]), "Q")
YoY Sales =
    CALCULATE([Total Sales], SAMEPERIODLASTYEAR(dim_date[calendar_date]))

YoY Change =
    [Total Sales] - CALCULATE([Total Sales], SAMEPERIODLASTYEAR(dim_date[calendar_date]))
```

> With these measures and the step-by-step build instructions above you can construct every visual in the list.

---

---

## Sample DAX Measures

Create these measures in Power BI (right‑click a table in the Model view → **New measure**):

```DAX
Total Sales = SUM(fact_sales[sales])
Total Profit = SUM(fact_sales[profit])
Average Order Value = AVERAGE(fact_orders[total_sales])
Profit Margin = DIVIDE([Total Profit], [Total Sales])
Order Count = COUNT(fact_orders[order_id])
```

### Visual-specific DAX helpers

Below are a few additional formulas you can drop into visuals or use for calculated columns/filters:

```DAX
Sales by Region =
    CALCULATE([Total Sales], ALLEXCEPT(dim_customer, dim_customer[region]))

Sales by Category =
    CALCULATE([Total Sales], ALLEXCEPT(dim_product, dim_product[category]))

Quarter ="Q" & FORMAT(dim_date[calendar_date], "Q")

Year = YEAR(dim_date[calendar_date])

Year = YEAR(SELECTEDVALUE(dim_date[calendar_date]))

Quarter = "Q" & FORMAT(SELECTEDVALUE(dim_date[calendar_date]), "Q")

YoY Sales =
    CALCULATE([Total Sales], SAMEPERIODLASTYEAR(dim_date[calendar_date]))

Customer Count = DISTINCTCOUNT(dim_customer[customer_key])

```

> You can reference these measures directly in the **Values** field of any visual.  For example, use `Sales by Region` with a filled map or `Order Count` for shipping‑mode preferences.

---

---

## Export Complete Files

All 7 CSV files are ready in:
```
D:\DW\cw\powerbi_exports\
```

Total data: ~70,000 rows ready for analysis!



## next
Would you like me to help you create specific visualizations or export any additional data?