import mysql.connector
global cnx

# Connect the MySQL database with the FastAPI backend.
cnx = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="pandeyji_eatery"
)

def get_next_order_id():
    # Create a cursor object
    cursor = cnx.cursor()

    # Write an SQL query to get the next available order_id
    query = ("SELECT MAX(order_id) FROM orders")

    # Execute the query
    cursor.execute(query)

    # Fetch the result
    result = cursor.fetchone()[0]

    # Close the cursor and connection
    cursor.close()


    if result is None:
        # If there is no available order_id
        return 1
    else:
        # Return the order_id
        return result + 1

def get_order_status(order_id : int):
    # Create a cursor object
    cursor = cnx.cursor()

    # Write an SQL query
    query = ("SELECT status FROM order_tracking WHERE order_id = %s")

    # Execute the query
    cursor.execute(query, (order_id,))

    # Fetch the result
    result = cursor.fetchone()

    # Close the cursor and connection
    cursor.close()

    if result is not None:
        # If the query returned a valid value
        return result[0]
    else:
        return None
    
def insert_order_item(food_item, quantity, order_id):
    try:
        # Create a cursor object
        cursor = cnx.cursor()

        # Call the stored procedure
        cursor.callproc("insert_order_item", (food_item, quantity, order_id))

        # Commit the changes
        cnx.commit()

        # Close the cursor
        cursor.close()

        print("Order item inserted successfully!")

        return 1
    except mysql.connector.Error as err:
        print("Error inserting order item:", err)

        # Rollback the changes
        cnx.rollback()

        return -1
    
def get_total_order_price(order_id):
    # Create a cursor object
    cursor = cnx.cursor()

    # Write an SQL query to get the total order price of a particular order
    query = f"SELECT get_total_order_price({order_id})"

    # Execute the query
    cursor.execute(query)

    # Fetch the result
    result = cursor.fetchone()[0]

    # Close the cursor and connection
    cursor.close()

    return result

def insert_order_tracking(order_id, status):
    # Create a cursor object
    cursor = cnx.cursor()

    # Write an SQL query to insert the status of the order into the database.
    query = "INSERT INTO order_tracking (order_id, status) VALUES (%s, %s)"

    # Execute the query
    cursor.execute(query, (order_id, status))

    # Commit the changes
    cnx.commit()

    # Close the cursor
    cursor.close()