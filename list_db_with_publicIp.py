import boto3

boto3.setup_default_session(profile_name='cloud-tool-default')
session = boto3.session.Session(profile_name='cloud-tool-default')

client = session.client('ec2')
regions = [region['RegionName'] for region in client.describe_regions()['Regions']]

counter = 0

for region in regions:
    rds_client = session.client('rds', region_name=region)
    rds_response = rds_client.describe_db_instances()


    for db_instance in rds_response["DBInstances"]:

        if db_instance["PubliclyAccessible"] == True:
            print(region, " ", end="")
            print(db_instance["DBInstanceIdentifier"]," ",end="")
            print(db_instance["Engine"])
            counter += 1

            db_tag_instance = rds_client.list_tags_for_resource(ResourceName=db_instance["DBInstanceArn"])
            for tags in db_tag_instance["TagList"]:
                print("\t", tags["Key"], " : ", tags["Value"])
            print("")

print("There are ", counter, "Databases that have \"PubliclyAvailable\" configurations.")
