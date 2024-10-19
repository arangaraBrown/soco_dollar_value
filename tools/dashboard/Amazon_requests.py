import pandas as pd
import os, sys, importlib
from pathlib import Path

def import_parents(level=1):
    global __package__
    file = Path(os.path.abspath('')).resolve()
    parent, top = file.parent, file.parents[level - 1]

    sys.path.append(str(top))
    try:
        sys.path.remove(str(parent))
    except ValueError: # already removed
        pass

    __package__ = '.'.join(parent.parts[len(top.parts):])
    importlib.import_module(__package__) # won't be needed after that

import_parents(level=2)

import boto3

id_column = 'profile_id' # Unique ID column for each profile
table_name = 'bace-db' # Update this if the name of the database TableName in template.yaml is changed
# Update `table_region` below to the region created with `sam deploy --guided`, saved in the SAM configuration file (samconfig.toml by default)
#   if different from the default region in ~/.aws/config (or C:\Users\USERNAME\.aws\config)
table_region = boto3.Session().region_name # example if different from default: table_region = 'us-east-2'
# os.environ['AWS_PROFILE'] = "YOUR_AWS_PROFILE_NAME" # Set this if your current AWS login profile is not the default one -- see profiles in ~/.aws/config (or C:\Users\USERNAME\.aws\config)

############################

def get_dynamo_data():
    import boto3

    # Start database connection
    ddb = boto3.resource('dynamodb', region_name = table_region)
    table = ddb.Table(table_name)

    # Scan all data from DynamoDB table
    response = table.scan()
    db_items = response['Items']

    # Go beyond the 1mb limit: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Scan.html
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        db_items.extend(response['Items'])

    return db_items


