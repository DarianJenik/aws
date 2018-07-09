# this is setup for boto2

import boto.s3.connection
import boto3

# Don't do this.. really just don't.
access_key = 'XXXXX'
secret_key = 'XXXXX'

conn = boto.connect_s3(
    aws_access_key_id = access_key,
    aws_secret_access_key = secret_key,
    host = 's3.amazonaws.com',
    # is_secure=False,               # uncomment if you are not using ssl
    calling_format = boto.s3.connection.OrdinaryCallingFormat(),
    )

print("\nHere is a list of the S3 buckets:\n")

for bucket in conn.get_all_buckets():
    print("{name}\t{created}".format(
        name = bucket.name,
        created = bucket.creation_date,)
        )
