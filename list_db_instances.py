#List all RDS instances with public IPs and their tags

import boto3

boto3.setup_default_session(profile_name='cloud-tool-default')
session = boto3.session.Session(profile_name='cloud-tool-default')

# list of current regions
client = session.client('ec2')
regions = [region['RegionName'] for region in client.describe_regions()['Regions']]

# table of all security groups and identify the ones that are 0.0.0.0/0 inbound with ports
security_groups = {}
groups = client.describe_security_groups()
for ec2_security_groups in groups["SecurityGroups"]:
    ip_ranges = []
    security_group_details = {}
    for security_group in ec2_security_groups["IpPermissions"]:

        for ip_range in security_group["IpRanges"]:
            if ip_range["CidrIp"] == "0.0.0.0/0":
                try:
                    ip_ranges_text = str(ip_range["CidrIp"]) + ' : ' + str(security_group["ToPort"])
                except:
                    ip_ranges_text = str(ip_range["CidrIp"]) + " : -"
                ip_ranges.append(ip_ranges_text)
    security_group_details["GroupName"] = ec2_security_groups["GroupName"]
    if ip_ranges == []:
        security_group_details["Rules"] = "NOEXTERNALRULES"
    else:
        security_group_details["Rules"] = ip_ranges
    if ec2_security_groups["GroupId"] in security_groups.keys():
        print("ERROR !!! - ", ec2_security_groups["GroupId"], " ALREADY EXISTS!!")
    else:
        security_groups[ec2_security_groups["GroupId"]] = security_group_details

    #print(ec2_security_groups["GroupId"], " ", end="")
    #print(ec2_security_groups["GroupName"])
    #if ip_ranges == []:
    #    print("\t -")
    #else:
    #    for rules in ip_ranges:
    #        print("\t", rules)

for region in regions:
    rds_client = session.client('rds', region_name=region)
    rds_response = rds_client.describe_db_instances()

    for db_instance in rds_response["DBInstances"]:
        #print(db_instance)

        if db_instance["PubliclyAccessible"] == True:
            print(region, " ", end="")
            print(db_instance["DBInstanceIdentifier"]," ",end="")
            print(db_instance["Engine"])

            db_tag_instance = rds_client.list_tags_for_resource(ResourceName=db_instance["DBInstanceArn"])
            for tags in db_tag_instance["TagList"]:
                print("\t", tags["Key"], " : ", tags["Value"])
            print("")
            db_securitygroups = db_instance["VpcSecurityGroups"]
            print("*****************")
            print(db_securitygroups)
            print("-----------------")
            for group_id in db_securitygroups["VpcSecurityGroupId"]:
                print(security_groups[group_id])


