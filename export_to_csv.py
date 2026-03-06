import subprocess

mysql_path = r'C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe'

# Define queries without created_at for cleaner export
exports = [
    ('dim_customer', 'SELECT customer_key, customer_id, customer_name, segment, country, city, state, postal_code, region FROM dim_customer'),
    ('dim_product', 'SELECT product_key, product_id, category, subcategory, product_name FROM dim_product'),
    ('dim_store', 'SELECT store_key, store_id, store_name, region, city, state FROM dim_store'),
    ('dim_date', 'SELECT date_key, calendar_date, year, quarter, month, day, weekday, fiscal_year, fiscal_quarter FROM dim_date'),
    ('dim_shipmode', 'SELECT shipmode_key, ship_mode FROM dim_shipmode'),
    ('fact_sales', 'SELECT sales_key, row_id, order_id, order_date_key, ship_date_key, customer_key, product_key, store_key, shipmode_key, sales, quantity, discount, profit FROM fact_sales'),
    ('fact_orders', 'SELECT order_key, order_id, order_date_key, ship_date_key, customer_key, shipmode_key, store_key, total_sales, total_quantity, total_discount, total_profit, product_count FROM fact_orders')
]

for table_name, query in exports:
    print(f'Exporting {table_name}...')
    
    result = subprocess.run([
        mysql_path,
        '-u', 'root', '-p5533', 'superstore',
        '-e', query
    ], capture_output=True, text=True)
    
    lines = result.stdout.strip().split('\n')
    if not lines:
        continue
    
    # Get header
    header = lines[0].split('\t')
    
    # Write CSV manually (without csv module to avoid extra quotes)
    with open(f'D:/DW/cw/powerbi_exports/{table_name}.csv', 'w', encoding='utf-8') as f:
        # Write header
        f.write(','.join(header) + '\n')
        
        # Write data rows
        for line in lines[1:]:
            if line.strip():  # Skip empty lines
                # Handle values with commas/quotes
                values = line.split('\t')
                escaped = []
                for v in values:
                    v = v.strip()
                    if ',' in v or '"' in v or '\n' in v:
                        v = '"' + v.replace('"', '""') + '"'
                    escaped.append(v)
                f.write(','.join(escaped) + '\n')
    
    print(f'Exported {table_name}: {len(lines)-1} rows')

print('\nAll tables exported successfully!')
print('Files saved to: D:/DW/cw/powerbi_exports/')
