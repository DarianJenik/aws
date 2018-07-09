import boto3
import sys

f = open('output.txt','w')

boto3.setup_default_session(profile_name='cloud-tool-default')
session = boto3.session.Session(profile_name='cloud-tool-default')

client = session.client('ec2')
regions = [region['RegionName'] for region in client.describe_regions()['Regions']]

# table of all security groups and identify the ones that are 0.0.0.0/0 inbound with ports

#print(client.describe_security_groups())
print(regions)
for region in regions:

    ec2_client = session.client('ec2', region_name=region)
    ec2_resource = boto3.resource('ec2', region_name=region)

    ec2_response = ec2_client.describe_instances()

    f.write(str(ec2_client.describe_security_groups()))


exit()

groups = client.describe_security_groups()
print(groups)
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

#for value, key in security_groups.items():
#    print(value, key)
