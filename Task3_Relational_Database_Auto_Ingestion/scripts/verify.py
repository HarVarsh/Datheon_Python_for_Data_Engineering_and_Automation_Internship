from sqlalchemy import text

from database import engine


queries = {

    "Total Customers":
    "SELECT COUNT(*) FROM customers",

    "Total Products":
    "SELECT COUNT(*) FROM products",

    "Total Sales Records":
    "SELECT COUNT(*) FROM sales_transactions",

    "Unique Invoices":
    "SELECT COUNT(DISTINCT invoice_no) FROM sales_transactions",

    "Missing Customer IDs":
    """
    SELECT COUNT(*)
    FROM sales_transactions
    WHERE customer_id IS NULL
    """,

    "Negative Quantity Records":
    """
    SELECT COUNT(*)
    FROM sales_transactions
    WHERE quantity < 0
    """
}


with engine.connect() as connection:

    print("\nDATABASE VERIFICATION REPORT")
    print("=" * 40)

    for title, query in queries.items():

        result = connection.execute(
            text(query)
        ).scalar()

        print(f"{title}: {result}")

    print("=" * 40)