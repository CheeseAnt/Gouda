import os
import json
import boto3
import dataclasses
from boto3.dynamodb import conditions

class DynamoDBWrapper:
  def __init__(self, table_name):
    self.table_name = f"gt_{table_name}"  # Apply table name prefix
    aws_access_key_id = os.environ.get("aws_key")
    aws_secret_access_key = os.environ.get("aws_secret")
    region_name = "eu-west-1"

    dynamodb = boto3.resource(
        'dynamodb',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region_name
    )
    self.table = dynamodb.Table(self.table_name)

  def put_item(self, item):
    try:
      self.table.put_item(Item=item)
    except Exception as e:
      # Handle potential conflicts (e.g., duplicate entries)
      print(f"Put item failed: {e}")

  def get_item(self, key):
    response = self.table.get_item(Key=key)
    if "Item" in response:
        return response['Item']
    else:
        return None

  def update_item(self, key, update_expr, expression_attribute_values=None):
    try:
      self.table.update_item(
          Key=key,
          UpdateExpression=update_expr,
          ExpressionAttributeValues=expression_attribute_values
      )
    except Exception as e:
      print(f"Update item failed: {e}")

  def query(self, index_name=None, key_condition_expr=None, expression_attribute_values=None):
    kwargs = {}
    if index_name:
      kwargs["IndexName"] = index_name
    if key_condition_expr:
      kwargs["KeyConditionExpression"] = key_condition_expr
    if expression_attribute_values:
      kwargs["ExpressionAttributeValues"] = expression_attribute_values
    response = self.table.query(**kwargs)
    return response["Items"]

# Example usage
db = DynamoDBWrapper("user")
user_data = {"id": "user123", "email": "test2", 'read': False}
db.put_item(user_data)
# print(db.get_item({'id': 'user123', 'email':'test', 'read': False}))

print(db.table.query(KeyConditionExpression=conditions.Key('read').eq(False)))
