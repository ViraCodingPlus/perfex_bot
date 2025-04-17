import os
import time
import io
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
    """Create a backup of the database in memory"""
    try:
        connection = get_connection()
        cursor = connection.cursor()
        
        # Get all tables
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        
        # Create a string buffer to store the backup
        backup_buffer = io.StringIO()
        
        # Write header
        backup_buffer.write(f"-- Database backup of {DB_NAME}\n")
        backup_buffer.write(f"-- Generated on {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Backup each table
        for table in tables:
            # Get table structure
            cursor.execute(f"SHOW CREATE TABLE {table}")
            create_table = cursor.fetchone()[1]
            backup_buffer.write(f"{create_table};\n\n")
            
            # Get table data
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            
            if rows:
                # Get column names
                cursor.execute(f"SHOW COLUMNS FROM {table}")
                columns = [column[0] for column in cursor.fetchall()]
                
                # Write INSERT statements
                for row in rows:
                    values = []
                    for value in row:
                        if value is None:
                            values.append("NULL")
                        elif isinstance(value, (int, float)):
                            values.append(str(value))
                        else:
                            values.append(f"'{str(value).replace("'", "''")}'")
                    
                    insert = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(values)});\n"
                    backup_buffer.write(insert)
                
                backup_buffer.write("\n")
        
        # Close connections
        cursor.close()
        connection.close()
        
        # Convert string buffer to bytes
        backup_data = backup_buffer.getvalue().encode('utf-8')
        backup_buffer.close()
        
        return backup_data
    except Exception as e:
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