import boto3
import os
from botocore.exceptions import ClientError

def create_dynamodb_client():
    # Prompt for AWS credentials
    aws_access_key_id = os.environ.get("aws_key")
    aws_secret_access_key = os.environ.get("aws_secret")
    region_name = "eu-west-1"

    # Create a DynamoDB client
    try:
        dynamodb = boto3.client(
            'dynamodb',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )
        return dynamodb
    except Exception as e:
        print(f"Error creating DynamoDB client: {e}")
        return None

def list_tables(dynamodb):
    try:
        response = dynamodb.list_tables()
        tables = response.get('TableNames', [])
        print("DynamoDB tables:")
        for table in tables:
            print(f"- {table}")
    except ClientError as e:
        print(f"Error listing tables: {e}")

def put_item(dynamodb, table_name, item):
    try:
        response = dynamodb.put_item(
            TableName=table_name,
            Item=item
        )
        print(f"Item added successfully to table '{table_name}'")
    except ClientError as e:
        print(f"Error adding item to table '{table_name}': {e}")

def get_item(dynamodb, table_name, key):
    try:
        response = dynamodb.get_item(
            TableName=table_name,
            Key=key
        )
        item = response.get('Item')
        if item:
            print(f"Item retrieved from table '{table_name}':")
            print(item)
        else:
            print(f"Item not found in table '{table_name}'")
    except ClientError as e:
        print(f"Error retrieving item from table '{table_name}': {e}")

def main():
    dynamodb = create_dynamodb_client()
    if dynamodb:
        list_tables(dynamodb)

        # Example: Put an item into a table
        table_name = input("Enter the name of the table to add an item: ")
        item = {
            'id': {'S': 'example_id'},
            'email': {'S': 'John Doe'},
            'age': {'N': '30'}
        }
        put_item(dynamodb, table_name, item)

        # Example: Get an item from a table
        key = {'id': {'S': 'example_id'}, 'email': {'S': 'John Doe'}}
        get_item(dynamodb, table_name, key)

if __name__ == "__main__":
    main()