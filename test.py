import psycopg2
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

def connect_to_db():
    connection = None
    cursor = None

    try:
        # Set up the connection parameters. Replace these with your own settings.
        connection = psycopg2.connect(
            host=settings.db_host,
            port=settings.db_port,
            dbname=settings.db_name,
            user=settings.db_user,
            password=settings.db_password
        )

        # Create a cursor object
        cursor = connection.cursor()

        # Execute a simple SQL query
        # cursor.execute("SELECT * FROM scryfall;")

        # Fetch the result
        # record = cursor.fetchone()
        # print(f"You are connected to - {record}")

    except Exception as error:
        print(f"Error while connecting to PostgreSQL: {error}")

    finally:
        # Close the cursor and the connection
        if cursor:
            cursor.close()
        if connection:
            connection.close()
        print("Connection closed.")

if __name__ == "__main__":
    # load_dotenv('.env')
    load_dotenv('.env.local')

    class Settings(BaseSettings):
        db_host: str = ""
        db_port: int = 5432
        db_name: str = ""
        db_user: str = ""
        db_password: str = ""

    class Config:
        env_prefix = ''
        case_sensitive = False

    settings = Settings()

    connect_to_db()
