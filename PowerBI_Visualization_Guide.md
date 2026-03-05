# Power BI Visualization Guide
## Superstore Sales Data Warehouse - 10 Visualizations

### Getting Started

1. Open Power BI Desktop
2. Click "Get Data" and select "Folder"
3. Browse to `D:\DW\cw\powerbi_data`
4. Select all CSV files and click "Combine & Transform"
5. Create the following 10 visualizations

---

## Visualization 1: Total Sales by Region (Donut Chart)

**Purpose:** Show sales distribution across geographic regions

**Data Source:** `SalesByRegion.csv`

**Configuration:**
- **Visualization Type:** Donut Chart
- **Legend:** Region
- **Values:** TotalSales (Sum)
- **Title:** "Sales Distribution by Region"

**Insights:**
- West region typically leads in sales
- South and Central regions show strong performance
- East region may have growth potential

---

## Visualization 2: Monthly Sales Trend (Line Chart)

**Purpose:** Track sales performance over time

**Data Source:** `MonthlyTrend.csv`

**Configuration:**
- **Visualization Type:** Line Chart
- **X-Axis:** Month (MMM-YYYY format)
- **Y-Axis:** TotalSales (Sum)
- **Secondary Y-Axis:** TotalProfit (Sum)
- **Title:** "Monthly Sales and Profit Trend"

**Insights:**
- Identify seasonal peaks (November/December holiday season)
- Track year-over-year growth
- Detect profit margin trends

---

## Visualization 3: Sales by Category (Bar Chart)

**Purpose:** Compare performance across product categories

**Data Source:** `SalesByCategory.csv`

**Configuration:**
- **Visualization Type:** Stacked Bar Chart
- **Y-Axis:** SubCategory
- **X-Axis:** TotalSales (Sum)
- **Legend:** Category
- **Title:** "Sales by Product Category"

**Insights:**
- Office Supplies usually dominate volume
- Furniture shows higher ticket sizes
- Technology category growth potential

---

## Visualization 4: Top 10 Products by Sales (Horizontal Bar)

**Purpose:** Identify best-selling products

**Data Source:** `TopProducts.csv`

**Configuration:**
- **Visualization Type:** Horizontal Bar Chart
- **Y-Axis:** ProductName (Top 10 filter)
- **X-Axis:** TotalSales (Sum)
- **Title:** "Top 10 Products by Sales"
- **Filter:** Top N = 10 by TotalSales

**Insights:**
- Focus inventory on top performers
- Analyze pricing of high-volume items
- Identify product bundling opportunities

---

## Visualization 5: Customer Segment Performance (Pie Chart)

**Purpose:** Analyze sales by customer segment

**Data Source:** `SalesBySegment.csv`

**Configuration:**
- **Visualization Type:** Pie Chart
- **Legend:** Segment
- **Values:** TotalSales (Sum)
- **Title:** "Sales by Customer Segment"

**Insights:**
- Consumer segment typically largest
- Corporate segment shows consistent growth
- Home Office segment opportunities

---

## Visualization 6: Profit Margin by Region (Stacked Column)

**Purpose:** Analyze profitability across regions

**Data Source:** `SalesByRegion.csv`

**Configuration:**
- **Visualization Type:** Stacked Column Chart
- **X-Axis:** Region
- **Y-Axis:** TotalProfit (Sum)
- **Title:** "Total Profit by Region"
- **Secondary:** Add TotalSales for margin calculation

**Insights:**
- Identify most profitable regions
- Investigate negative profit areas
- Regional pricing strategy implications

---

## Visualization 7: Sales by Ship Mode (Funnel Chart)

**Purpose:** Analyze shipping preferences and costs

**Data Source:** `SalesByShipMode.csv`

**Configuration:**
- **Visualization Type:** Funnel Chart
- **Group:** ShipMode
- **Values:** TotalOrders (Count)
- **Title:** "Orders by Ship Mode"

**Insights:**
- Standard Class typically most popular
- Same-day shipping growth opportunity
- Shipping cost optimization

---

## Visualization 8: Regional Performance Map (Map Visual)

**Purpose:** Geographic sales visualization

**Data Source:** `RegionalPerformance.csv`

**Configuration:**
- **Visualization Type:** Map
- **Location:** State
- **Bubble Size:** TotalSales
- **Color:** AvgProfitMargin
- **Title:** "Geographic Sales Performance"

**Insights:**
- State-level performance gaps
- Density of sales in metropolitan areas
- Regional expansion opportunities

---

## Visualization 9: Discount Impact on Profitability (Scatter Chart)

**Purpose:** Analyze relationship between discounts and profit

**Data Source:** `ProfitabilityAnalysis.csv`

**Configuration:**
- **Visualization Type:** Scatter Chart
- **X-Axis:** DiscountTier
- **Y-Axis:** TotalProfit
- **Size:** OrderCount
- **Color:** Category
- **Title:** "Discount Impact on Profitability"

**Insights:**
- High discounts erode profit margins
- Optimal discount levels by category
- Promotional strategy optimization

---

## Visualization 10: KPI Dashboard Cards

**Purpose:** Key performance indicators at a glance

**Data Source:** `SalesByRegion.csv` or `SalesFact.csv`

**Configuration:**
- **Visualization Type:** Card (multiple)
- **Card 1:** Total Sales = SUM(TotalSales)
- **Card 2:** Total Profit = SUM(TotalProfit)
- **Card 3:** Total Orders = SUM(TotalOrders)
- **Card 4:** Avg Order Value = AVG(AvgOrderValue)
- **Title:** "KPI Dashboard"

**Calculated Measures to Create:**
```
Total Sales = SUM(SalesFact[Sales])
Total Profit = SUM(SalesFact[Profit])
Total Orders = DISTINCTCOUNT(SalesFact[OrderID])
Profit Margin = DIVIDE([Total Profit], [Total Sales])
```

---

## Creating Data Relationships

In Power BI, go to "Model" view and create:

1. **SalesFact** → **Customers** (CustomerID)
2. **SalesFact** → **Products** (ProductID)
3. **SalesFact** → **DimDate** (OrderDate)
4. **SalesFact** → **DimShipMode** (ShipMode)

---

## Report Layout Recommendation

| Row | Visualization | Size |
|-----|---------------|------|
| 1 | KPI Cards (4 cards) | Full width |
| 2 | Monthly Trend Line | 1/2 width |
| 2 | Sales by Region Donut | 1/2 width |
| 3 | Sales by Category Bar | 1/3 width |
| 3 | Customer Segment Pie | 1/3 width |
| 3 | Ship Mode Funnel | 1/3 width |
| 4 | Top Products Horizontal Bar | 1/2 width |
| 4 | Profitability Scatter | 1/2 width |
| 5 | Regional Map | Full width |

---

## Export Instructions

After creating visualizations:
1. File → Export → Export to PDF
2. Or publish to Power BI Service
3. Share with stakeholders

---

## Sample DAX Measures

```DAX
Total Sales = SUM(SalesFact[Sales])

Total Profit = SUM(SalesFact[Profit])

Profit Margin = 
    DIVIDE([Total Profit], [Total Sales], 0)

YTD Sales = 
    TOTALYTD([Total Sales], SalesFact[OrderDate])

YoY Growth = 
    VAR CurrentYear = [Total SalesYear = CALCUL]
    VAR LastATE([Total Sales], SAMEPERIODLASTYEAR('DimDate'[DateKey]))
    RETURN DIVIDE(CurrentYear - LastYear, LastYear)

Top Products = 
    TOPN(10, Products, [Total Sales], DESC)
```

---

## Color Palette Recommendations

- **Primary:** #1F77B4 (Blue)
- **Secondary:** #FF7F0E (Orange)
- **Tertiary:** #2CA02C (Green)
- **Accent:** #D62728 (Red)
- **Neutral:** #9467BD (Purple)

Apply consistent formatting across all visualizations for professional appearance.
