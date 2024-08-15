from flask import Flask, jsonify, request
from flask_cors import CORS
import pyodbc

app = Flask(__name__)
CORS(app)

# SQL Server connection settings
conn_str = (
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=(localdb)\\localDB1;'
    'DATABASE=master;'
    'Trusted_Connection=yes;'
)

# Function to fetch data
def fetch_data(query):
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    cursor.execute(query)
    columns = [column[0] for column in cursor.description]
    results = []
    for row in cursor.fetchall():
        results.append(dict(zip(columns, row)))
    cursor.close()
    conn.close()
    return results

# Endpoint to fetch products
@app.route('/products', methods=['GET'])
def get_products():
    query = "SELECT ProductID, ProductName, Price, Inventory, Barcode FROM Products"
    data = fetch_data(query)
    return jsonify(data)

# Endpoint to update a product
@app.route('/products/<int:id>/buy', methods=['POST'])
def buy_product(id):
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    # Check inventory
    cursor.execute("SELECT Inventory FROM Products WHERE ProductID = ?", id)
    inventory = cursor.fetchone()[0]

    if inventory > 0:
        # Reduce inventory by 1
        cursor.execute("UPDATE Products SET Inventory = Inventory - 1 WHERE ProductID = ?", id)
        conn.commit()
        message = "Purchase successful!"
    else:
        message = "Sorry, this product is out of stock."

    cursor.close()
    conn.close()
    return jsonify({"message": message}), 200

if __name__ == '__main__':
    app.run(debug=True)
