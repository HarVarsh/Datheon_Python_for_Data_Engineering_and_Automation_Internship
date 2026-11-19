from sqlalchemy import (
    MetaData, Table, Column, String,
    Integer, Text, DateTime, Numeric, ForeignKey
)

from database import engine

metadata = MetaData()

# Customer table
customers = Table( "customers",metadata,
    Column("customer_id", String(20), primary_key=True))

# Product table
products = Table("products",metadata,
    Column("stock_code", String(30), primary_key=True),
    Column("description", Text)
)

# Sales transaction table
sales_transactions = Table("sales_transactions",metadata,

    Column("source_row_id", Integer, primary_key=True),
    Column("invoice_no", String(30), nullable=False),
    Column("stock_code",String(30),ForeignKey("products.stock_code"),nullable=False),
    Column("customer_id",String(20),ForeignKey("customers.customer_id"),nullable=True),
    Column("quantity", Integer, nullable=False),
    Column("invoice_date", DateTime, nullable=False),
    Column("unit_price", Numeric(12, 2), nullable=False),
    Column("country", String(100))
)


def create_schema():
    metadata.create_all(engine)
    print("Database schema created successfully.")


if __name__ == "__main__":
    create_schema()