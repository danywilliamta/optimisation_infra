import psycopg2
import os
from dotenv import load_dotenv
import logging
import time
load_dotenv()

logger = logging.getLogger(__name__)

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT", 5439)

#Here we define a class to handle database connections and operations

class DatabaseConnector:
    def __init__(
        self,
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT,
    ):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port
        self.connection = None

        logger.info("Attempting to connect to the database...")
        healthy_db = self.connect_to_db()
        # Retry logic for database connection otherwise we got issues when the DB is not ready yet
        for _attempt in range(5):
            if healthy_db:
                break
            logger.warning(f"Database connection failed. Retrying in 5 seconds... (Attempt {_attempt + 1}/5)")
            time.sleep(5)
            healthy_db = self.connect_to_db()


        if self.connection and not self.table_exist():
            self.initialize_db()

    def connect_to_db(self):
        """Establish a connection to the PostgreSQL database."""
        try:
            conn = psycopg2.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                port=self.port,
            )
            logger.info("Database connection established.")
            self.connection = conn
            return True
        except Exception as e:
            logger.error(f"An error occurred while connecting to the database: {e}")
            return None

    def initialize_db(self):
        """Initialize the database with necessary tables."""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                """
            CREATE TABLE system_metrics (
                id SERIAL PRIMARY KEY,
                metrics JSONB,   
                analysis JSONB,
            created_at TIMESTAMPTZ DEFAULT NOW()
            );
            """
            )
            self.connection.commit()
            cursor.close()
            logger.info("Database initialized with necessary tables.")
        except Exception as e:
            logger.error(f"An error occurred while initializing the database: {e}")

    def table_exist(self):
        cur = self.connection.cursor()

        cur.execute(
            """
            SELECT EXISTS (
                SELECT 1 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'system_metrics'
            );
        """
        )
        exists = cur.fetchone()[0]
        return exists

    def insert_data(self, metrics, analysis):
        """Insert data into the specified table."""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                """
                INSERT INTO system_metrics (metrics, analysis)
                VALUES (%s, %s)
                RETURNING id;
                """,
                (metrics, analysis),
            )

            self.connection.commit()
            cursor.close()
            logger.info("Data inserted successfully.")
        except Exception as e:
            logger.error(f"An error occurred while inserting data: {e}")
            self.connection.rollback()
