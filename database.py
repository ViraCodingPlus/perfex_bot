import os
import time
import subprocess
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
BACKUP_DIR = os.getenv('BACKUP_DIR', 'backups')

# Ensure backup directory exists
os.makedirs(BACKUP_DIR, exist_ok=True)

def get_connection():
    """Create a connection to the database"""
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        return connection
    except Error as e:
        raise Exception(f"Error connecting to MySQL database: {e}")

def backup_database():
    """Create a backup of the database"""
    timestamp = time.strftime('%Y%m%d-%H%M%S')
    backup_file = os.path.join(BACKUP_DIR, f"{DB_NAME}-{timestamp}.sql")
    
    # Check if we're on Windows
    if os.name == 'nt':
        # On Windows, use the mysqldump command in a slightly different way
        cmd = [
            'mysqldump',
            f'--host={DB_HOST}',
            f'--user={DB_USER}',
            f'--password={DB_PASSWORD}',
            DB_NAME,
            f'--result-file={backup_file}'
        ]
    else:
        # Unix-based systems
        cmd = [
            'mysqldump',
            f'--host={DB_HOST}',
            f'--user={DB_USER}',
            f'--password={DB_PASSWORD}',
            DB_NAME,
            '>', 
            backup_file
        ]
    
    try:
        # For Windows, we'll use subprocess directly
        if os.name == 'nt':
            subprocess.run(cmd, check=True)
        else:
            # For Unix, we'll use shell=True to properly handle the redirect
            subprocess.run(' '.join(cmd), shell=True, check=True)
            
        return backup_file
    except subprocess.CalledProcessError as e:
        raise Exception(f"Database backup failed: {e}")

def execute_query(query, params=None, fetch=True):
    """Execute a query and return results"""
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        cursor.execute(query, params or ())
        
        if fetch:
            result = cursor.fetchall()
            return result
        else:
            connection.commit()
            return cursor.rowcount
    except Error as e:
        raise Exception(f"Query execution failed: {e}")
    finally:
        cursor.close()
        connection.close()

# Alternatively, use pyMySQL with SQLAlchemy for more advanced database operations
def get_sqlalchemy_engine():
    """Get SQLAlchemy engine for the database"""
    try:
        from sqlalchemy import create_engine
        
        connection_string = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
        engine = create_engine(connection_string)
        return engine
    except ImportError:
        raise Exception("SQLAlchemy or PyMySQL not installed")
    except Exception as e:
        raise Exception(f"Error creating SQLAlchemy engine: {e}") 