import pandas as pd
from sqlalchemy import create_engine

# read excel files
sales = pd.read_excel(r'd:\DW\cw\sales_generated.xlsx', dtype={
    "RowID": int, "OrderID": str, "ShipMode": str,
    "CustomerID": str, "ProductID": str
})

# convert dates if necessary
sales["OrderDate"] = pd.to_datetime(sales["OrderDate"], errors='coerce')
sales["ShipDate"] = pd.to_datetime(sales["ShipDate"], errors='coerce')

# create sqlite database
engine = create_engine('sqlite:///d:/DW/cw/superstore.db')

# write tables
sales.to_sql('Sales', con=engine, if_exists='replace', index=False)
print('Sales table loaded, rows=', len(sales))

# optionally load customers and products too
for fname, tbl in [('customers_generated.xlsx','Customers'), ('products_generated.xlsx','Products')]:
    df = pd.read_excel(f'd:/DW/cw/{fname}')
    df.to_sql(tbl, con=engine, if_exists='replace', index=False)
    print(f'{tbl} loaded, rows=', len(df))
