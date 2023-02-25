import psycopg2
from psycopg2.extras import RealDictCursor
from .config import settings

try:
    password = settings.database_password
    conn = psycopg2.connect(host=settings.database_hostname,
    database=settings.database_name, user=settings.database_username, 
    password=password,
    cursor_factory=RealDictCursor)
    cursor = conn.cursor()
    print("Database connection was succesfull!")
except Exception as error:
    print("Connecting to database failed")
    print("Error was ", error)
    