import mysql.connector


DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "actowiz",
    "database": "blinkitr_scrap"
}


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def create_table():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
        CREATE TABLE IF NOT EXISTS categories_details (
            id INT AUTO_INCREMENT PRIMARY KEY,
            category_tag VARCHAR(255),
            categories_name VARCHAR(255),
            categories_url TEXT,
            status VARCHAR(50) DEFAULT 'pending',
            UNIQUE KEY unique_url (categories_url(255))
        )
        """

        cursor.execute(query)
        conn.commit()

        cursor.close()
        conn.close()

        print("Table ready")

    except Exception as e:
        print(f"Error in create_table(): {e}")


def insert_into_db(table_name: str, data: dict):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cols = ",".join(data.keys())
        vals = ",".join(["%s"] * len(data))
        query = f"INSERT IGNORE INTO {table_name} ({cols}) VALUES ({vals})"

        cursor.execute(query, tuple(data.values()))
        conn.commit()

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Error in insert_into_db(): {e}")


def save_categories(data):
    for section in data:
        category_tag = section.get("name")

        for item in section.get("cate_details", []):
            row = {
                "category_tag": category_tag,
                "categories_name": item.get("categories_name"),
                "categories_url": item.get("categories_url"),
                "status": "pending"
            }

            insert_into_db("categories_details", row)


def get_pending_urls():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = "SELECT categories_url FROM categories_details WHERE status = 'pending'"
        cursor.execute(query)

        urls = [row[0] for row in cursor.fetchall()]

        cursor.close()
        conn.close()

        return urls

    except Exception as e:
        print(f"Error in get_pending_urls(): {e}")
        return []


def update_status(url, status="done"):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = "UPDATE categories_details SET status = %s WHERE categories_url = %s"
        cursor.execute(query, (status, url))

        conn.commit()

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Error in update_status(): {e}")


# test
if __name__ == "__main__":
    create_table()