import sqlite3
import csv
import os

class PowerBIDataExporter:
    def __init__(self, db_path='superstore.db', output_dir='powerbi_data'):
        self.db_path = db_path
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def export_all_data(self):
        """Export all data warehouse tables for Power BI"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        tables = ['Customers', 'Products', 'SalesFact', 'DimDate', 'DimStore', 'DimShipMode']
        
        for table in tables:
            print(f"Exporting {table}...")
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            
            if rows:
                columns = rows[0].keys()
                filepath = os.path.join(self.output_dir, f"{table}.csv")
                
                with open(filepath, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=columns)
                    writer.writeheader()
                    for row in rows:
                        writer.writerow(dict(row))
                
                print(f"  Exported {len(rows)} records to {filepath}")
        
        conn.close()
        print(f"\nAll data exported to {self.output_dir}/")
    
    def export_analytics_views(self):
        """Export pre-aggregated views for Power BI analysis"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Sales by Region
        print("Creating Sales by Region view...")
        cursor.execute("""
            SELECT 
                c.Region,
                COUNT(DISTINCT s.OrderID) as TotalOrders,
                SUM(s.Sales) as TotalSales,
                SUM(s.Profit) as TotalProfit,
                AVG(s.Profit) as AvgProfit,
                SUM(s.Quantity) as TotalQuantity
            FROM SalesFact s
            JOIN Customers c ON s.CustomerID = c.CustomerID
            GROUP BY c.Region
        """)
        self._write_query_results(cursor, 'SalesByRegion.csv')
        
        # Sales by Category
        print("Creating Sales by Category view...")
        cursor.execute("""
            SELECT 
                p.Category,
                p.SubCategory,
                COUNT(DISTINCT s.OrderID) as TotalOrders,
                SUM(s.Sales) as TotalSales,
                SUM(s.Profit) as TotalProfit,
                AVG(s.Profit) as AvgProfit
            FROM SalesFact s
            JOIN Products p ON s.ProductID = p.ProductID
            GROUP BY p.Category, p.SubCategory
        """)
        self._write_query_results(cursor, 'SalesByCategory.csv')
        
        # Sales by Time
        print("Creating Sales by Time view...")
        cursor.execute("""
            SELECT 
                d.Year,
                d.Quarter,
                d.Month,
                d.CalendarDate,
                COUNT(DISTINCT s.OrderID) as TotalOrders,
                SUM(s.Sales) as TotalSales,
                SUM(s.Profit) as TotalProfit
            FROM SalesFact s
            JOIN DimDate d ON s.OrderDate LIKE d.CalendarDate || '%'
            GROUP BY d.Year, d.Quarter, d.Month
            ORDER BY d.Year, d.Month
        """)
        self._write_query_results(cursor, 'SalesByTime.csv')
        
        # Sales by Customer Segment
        print("Creating Sales by Customer Segment view...")
        cursor.execute("""
            SELECT 
                c.Segment,
                c.Region,
                COUNT(DISTINCT s.OrderID) as TotalOrders,
                SUM(s.Sales) as TotalSales,
                SUM(s.Profit) as TotalProfit,
                AVG(s.Sales) as AvgOrderValue
            FROM SalesFact s
            JOIN Customers c ON s.CustomerID = c.CustomerID
            GROUP BY c.Segment, c.Region
        """)
        self._write_query_results(cursor, 'SalesBySegment.csv')
        
        # Sales by Ship Mode
        print("Creating Sales by Ship Mode view...")
        cursor.execute("""
            SELECT 
                s.ShipMode,
                COUNT(DISTINCT s.OrderID) as TotalOrders,
                SUM(s.Sales) as TotalSales,
                SUM(s.Profit) as TotalProfit
            FROM SalesFact s
            GROUP BY s.ShipMode
        """)
        self._write_query_results(cursor, 'SalesByShipMode.csv')
        
        # Top Products
        print("Creating Top Products view...")
        cursor.execute("""
            SELECT 
                p.ProductID,
                p.ProductName,
                p.Category,
                p.SubCategory,
                SUM(s.Sales) as TotalSales,
                SUM(s.Profit) as TotalProfit,
                SUM(s.Quantity) as TotalQuantity,
                COUNT(DISTINCT s.OrderID) as OrderCount
            FROM SalesFact s
            JOIN Products p ON s.ProductID = p.ProductID
            GROUP BY p.ProductID
            ORDER BY TotalSales DESC
            LIMIT 50
        """)
        self._write_query_results(cursor, 'TopProducts.csv')
        
        # Top Customers
        print("Creating Top Customers view...")
        cursor.execute("""
            SELECT 
                c.CustomerID,
                c.CustomerName,
                c.Segment,
                c.Region,
                SUM(s.Sales) as TotalSales,
                SUM(s.Profit) as TotalProfit,
                COUNT(DISTINCT s.OrderID) as OrderCount
            FROM SalesFact s
            JOIN Customers c ON s.CustomerID = c.CustomerID
            GROUP BY c.CustomerID
            ORDER BY TotalSales DESC
            LIMIT 50
        """)
        self._write_query_results(cursor, 'TopCustomers.csv')
        
        # Regional Performance
        print("Creating Regional Performance view...")
        cursor.execute("""
            SELECT 
                c.State,
                c.Region,
                SUM(s.Sales) as TotalSales,
                SUM(s.Profit) as TotalProfit,
                COUNT(DISTINCT s.OrderID) as TotalOrders,
                AVG(s.Profit) as AvgProfitMargin
            FROM SalesFact s
            JOIN Customers c ON s.CustomerID = c.CustomerID
            GROUP BY c.State
            ORDER BY TotalSales DESC
        """)
        self._write_query_results(cursor, 'RegionalPerformance.csv')
        
        # Monthly Trend Analysis
        print("Creating Monthly Trend view...")
        cursor.execute("""
            SELECT 
                strftime('%Y', OrderDate) as Year,
                strftime('%m', OrderDate) as Month,
                COUNT(DISTINCT OrderID) as OrderCount,
                SUM(Sales) as TotalSales,
                SUM(Profit) as TotalProfit,
                AVG(Discount) as AvgDiscount
            FROM SalesFact
            GROUP BY strftime('%Y-%m', OrderDate)
            ORDER BY Year, Month
        """)
        self._write_query_results(cursor, 'MonthlyTrend.csv')
        
        # Profitability Analysis
        print("Creating Profitability Analysis view...")
        cursor.execute("""
            SELECT 
                p.Category,
                p.SubCategory,
                s.Discount,
                CASE 
                    WHEN s.Discount = 0 THEN 'No Discount'
                    WHEN s.Discount <= 0.1 THEN 'Low Discount'
                    WHEN s.Discount <= 0.2 THEN 'Medium Discount'
                    ELSE 'High Discount'
                END as DiscountTier,
                COUNT(DISTINCT s.OrderID) as OrderCount,
                SUM(s.Sales) as TotalSales,
                SUM(s.Profit) as TotalProfit
            FROM SalesFact s
            JOIN Products p ON s.ProductID = p.ProductID
            GROUP BY p.Category, s.Discount
        """)
        self._write_query_results(cursor, 'ProfitabilityAnalysis.csv')
        
        conn.close()
        print("\nAll analytics views exported!")
    
    def _write_query_results(self, cursor, filename):
        rows = cursor.fetchall()
        if rows:
            columns = [description[0] for description in cursor.description]
            filepath = os.path.join(self.output_dir, filename)
            
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(columns)
                writer.writerows(rows)
            
            print(f"  Created {filename} with {len(rows)} rows")


if __name__ == "__main__":
    exporter = PowerBIDataExporter()
    exporter.export_all_data()
    exporter.export_analytics_views()
    print("\nData export complete! Files are ready for Power BI import.")
