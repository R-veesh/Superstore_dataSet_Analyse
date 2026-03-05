import pandas as pd

path = r'd:\DW\cw\bin\Sample - Superstore.csv'
# load with proper encoding and parse dates optionally
df = pd.read_csv(path, encoding='latin1', parse_dates=["Order Date","Ship Date"])

# customers
customers = (
    df[[
        "Customer ID", "Customer Name", "Segment",
        "Country", "City", "State", "Postal Code", "Region"
    ]]
    .drop_duplicates()
    .rename(columns={
        "Customer ID": "CustomerID",
        "Customer Name": "CustomerName",
        "Postal Code": "PostalCode"
    })
    .reset_index(drop=True)
)

# products
products = (
    df[[
        "Product ID", "Category", "Sub-Category", "Product Name"
    ]]
    .drop_duplicates()
    .rename(columns={
        "Product ID": "ProductID",
        "Sub-Category": "SubCategory",
        "Product Name": "ProductName"
    })
    .reset_index(drop=True)
)

# sales
sales = (
    df[[
        "Row ID", "Order ID", "Order Date", "Ship Date", "Ship Mode",
        "Customer ID", "Product ID", "Sales", "Quantity", "Discount",
        "Profit"
    ]]
    .rename(columns={
        "Row ID": "RowID",
        "Order ID": "OrderID",
        "Order Date": "OrderDate",
        "Ship Date": "ShipDate",
        "Ship Mode": "ShipMode",
        "Customer ID": "CustomerID",
        "Product ID": "ProductID"
    })
)

# write to excel (use new names to avoid locks)
customers.to_excel("customers_generated.xlsx", index=False)
products.to_excel("products_generated.xlsx", index=False)
sales.to_excel("sales_generated.xlsx", index=False)

print("Exported: customers.xlsx, products.xlsx, sales.xlsx")
