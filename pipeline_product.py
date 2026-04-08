import mysql.connector


DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "actowiz",
    "database": "blinkitr_scrap"
}


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def create_product_table():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
        CREATE TABLE IF NOT EXISTS GetProductPages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            category_id VARCHAR(50),
            category_name VARCHAR(255),
            product_id VARCHAR(50),
            product_name TEXT,
            product_url TEXT,
            status VARCHAR(50) DEFAULT 'pending',
            UNIQUE KEY unique_product (product_id)
        )
        """

        cursor.execute(query)
        conn.commit()

        cursor.close()
        conn.close()

        print("Product Table Ready")

    except Exception as e:
        print("Error:", e)


def insert_product(data):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cols = ",".join(data.keys())
        vals = ",".join(["%s"] * len(data))

        query = f"INSERT IGNORE INTO GetProductPages ({cols}) VALUES ({vals})"

        cursor.execute(query, tuple(data.values()))
        conn.commit()

        cursor.close()
        conn.close()

    except Exception as e:
        print("Insert Error:", e)