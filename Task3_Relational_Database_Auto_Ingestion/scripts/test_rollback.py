
from sqlalchemy import select, func

from database import engine
from schema import sales_transactions


TEST_SOURCE_ROW_ID = -999999999


def test_transaction_rollback():

    # Check whether the test ID already exists
    with engine.connect() as connection:

        existing_count = connection.execute(
            select(func.count())
            .select_from(sales_transactions)
            .where(
                sales_transactions.c.source_row_id
                == TEST_SOURCE_ROW_ID
            )
        ).scalar_one()

    if existing_count:
        raise RuntimeError(
            "Test ID already exists. Choose another ID."
        )

    print("Starting rollback test...")

    try:

        with engine.begin() as connection:

            # Copy an existing valid transaction
            original = connection.execute(
                select(sales_transactions).limit(1)
            ).mappings().first()

            if original is None:
                raise RuntimeError(
                    "No existing transaction found."
                )

            test_record = dict(original)
            test_record["source_row_id"] = TEST_SOURCE_ROW_ID

            connection.execute(
                sales_transactions.insert().values(test_record)
            )

            print("Temporary record inserted inside transaction.")

            # Deliberately trigger a failure
            raise RuntimeError(
                "Intentional error for rollback testing."
            )

    except RuntimeError as error:

        print("Expected test exception:", error)
        print("Transaction should have been rolled back.")

    # Confirm that the temporary record does not exist
    with engine.connect() as connection:

        final_count = connection.execute(
            select(func.count())
            .select_from(sales_transactions)
            .where(
                sales_transactions.c.source_row_id
                == TEST_SOURCE_ROW_ID
            )
        ).scalar_one()

    if final_count == 0:
        print("PASS: Temporary record was rolled back.")
    else:
        raise AssertionError(
            "FAIL: Temporary record still exists."
        )

    engine.dispose()


if __name__ == "__main__":
    test_transaction_rollback()
