# lists EC2 instances with public IPs and their tags

import boto3
import sys

f = open('output.txt','w')
sys.stdout = f

boto3.setup_default_session(profile_name='cloud-tool-default')
session = boto3.session.Session(profile_name='cloud-tool-default')

#build the list of regions
client = session.client('ec2')
regions = [region['RegionName'] for region in client.describe_regions()['Regions']]

# main loop through each region and each ec2 instance
for region in regions:
    print("REGION +++++", region)
    client = session.client('ec2', region_name=region)
    resource = boto3.resource('ec2', region_name=region)

    security_groups = {}

    for security_group in client.describe_security_groups()["SecurityGroups"]:
        print("******", security_group)
        print(security_group["GroupId"], " : ", security_group["GroupName"])

