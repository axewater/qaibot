# bot/manage_db.py
import sys
from sqlalchemy import create_engine, text
from sqlalchemy_utils import database_exists, drop_database, create_database
from sqlalchemy.exc import SQLAlchemyError
from config import SQLALCHEMY_DATABASE_URI

def main():
    engine = create_engine(SQLALCHEMY_DATABASE_URI)

    # Try to connect to the database
    try:
        if not database_exists(engine.url):
            print("Database does not exist.")
            sys.exit(1)
        print("Connected to the database successfully.")
    except SQLAlchemyError as e:
        print(f"Failed to connect to the database: {str(e)}")
        sys.exit(1)

    # Ask user if they want to delete and recreate the database
    response = input("Do you want to delete and recreate the database? (yes/no): ")
    if response.lower() == 'yes':
        try:
            # Forcibly close any open connections to the database
            with engine.begin() as conn:
                # Terminate all other connections to the database
                terminate_sql = text(
                    "SELECT pg_terminate_backend(pg_stat_activity.pid) "
                    "FROM pg_stat_activity "
                    "WHERE pg_stat_activity.datname = current_database() AND pid <> pg_backend_pid();"
                )
                conn.execute(terminate_sql)

            # Drop the database
            drop_database(engine.url)
            print("Database dropped successfully.")

            # Create a new, empty database
            create_database(engine.url)
            print("New database created successfully.")
        except Exception as e:
            print(f"Error during dropping and recreating the database: {str(e)}")
            sys.exit(1)
    else:
        print("Operation cancelled by the user.")

if __name__ == "__main__":
    main()
