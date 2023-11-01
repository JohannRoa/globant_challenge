import json
import psycopg2
import os
from datetime import datetime
import re

DB =os.getenv("RDS_DBNAME")
USER =os.getenv("RDS_USER")
PASSWORD =os.getenv("RDS_PASSWORD")
HOST =os.getenv("RDS_HOST")
PORT =os.getenv("RDS_PORT")



def lambda_handler(event, context):
    # Access the event body, which should contain the batch of records
    try:
        batch_records = json.loads(event['body'])
        print(batch_records)
    except:
        # Handle the absence of 'body' or other event structures as needed
        return {
            "statusCode": 400,
            "body": json.dumps({"message":"Invalid request format"})
        }

    # Initialize the PostgreSQL database connection parameters
    db_params = {
        'dbname': DB,
        'user': USER,
        'password': PASSWORD,
        'host': HOST,
        'port': PORT
    }

    # Initialize an empty list to store failed transactions
    failed_transactions = []
    
    # Initialize an empty list to store valid transactions
    valid_transactions = []

    # Establish a connection to the PostgreSQL database
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()
    
    if not isinstance(batch_records, list):
        batch_records=[batch_records]
    # Process each record in the batch
    for record_data in batch_records:
        try:
            # Validate the transaction data to ensure it conforms to the rules
            if validate_transaction(record_data):
                # Perform the database insert operation
                print("Validation ok")
                valid_transactions.append(record_data)
            else:
                # Log the failed transaction
                failed_transactions.append(record_data)
        except Exception as e:
            # Log any exceptions or errors during processing
            print(f"Error processing record: {str(e)}")
            
    # Perform the database insert operation for all valid transactions
    if valid_transactions:
        try:
            insert_transactions(cursor, valid_transactions)
            conn.commit()
        except Exception as e:
           return {
            "statusCode": 400,
            "body": json.dumps({"message":f"Error while inserting valid format transactions {e}"})
        }

    # Close the database connection
    cursor.close()
    conn.close()

    # Optionally, you can log the failed transactions
    if failed_transactions:
        print(f"Failed transactions: {json.dumps(failed_transactions)}")

    # Return a response indicating the successful processing of the batch
    return {
        "statusCode": 200,
        "body": json.dumps({"message":"Batch processed successfully","failed_transactions":failed_transactions})
    }

def is_valid_iso_datetime(datetime_str):
    expected_datetime_format = "%Y-%m-%dT%H:%M:%SZ"
    try:
        datetime.strptime(datetime_str, expected_datetime_format)
        return True
    except ValueError:
        return False
def validate_transaction(transaction_data):
    # Define the expected data types for each field
    expected_data_types = {
        'id': int,
        'department': str
    }

    # Define a function to check if a string represents a valid ISO datetime
    

    for field, expected_type in expected_data_types.items():
        if field not in transaction_data:
            transaction_data["error"]="Missing field or fields incorrect"
            return False  # Field is missing

       
        if not isinstance(transaction_data[field], expected_type):
                transaction_data["error"]="Problem with data type"
                return False

    # All checks passed; the record is valid
    return True

def insert_transactions(cursor, transactions):
    # Execute the INSERT query with proper error handling
    insert_query = "INSERT INTO departments (id, department) VALUES (%s, %s);"
    values = [(record['id'], record['department']) for record in transactions]
    cursor.executemany(insert_query, values)
    