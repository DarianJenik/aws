import boto3

boto3.setup_default_session(profile_name='cloud-tool-default')
session = boto3.session.Session(profile_name='cloud-tool-default')

client = session.client('ec2')
regions = [region['RegionName'] for region in client.describe_regions()['Regions']]

counter = 0

for region in regions:
    ec2_client = session.client('ec2', region_name=region)
    ec2 = boto3.resource('ec2', region_name=region)

    # Fetching all security groups in AWS account
    sgs = ec2.security_groups.all()

    # Creating a list of only security group names
    all_sgs = set([sg.group_name for sg in sgs])

    # Getting all instances in AWS account
    instances = ec2.instances.all()

    # Getting all security groups attached to any instances
    inssgs = set([sg['GroupName'] for ins in instances for sg in ins.security_groups])

    # Removing duplicate SGs
    unused_sgs = all_sgs - inssgs

    for sg in unused_sgs:
        counter += 1
        print(region, " - ", sg)

print("\n\tUnused security groups : ", counter)
