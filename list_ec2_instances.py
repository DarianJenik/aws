# lists EC2 instances with public IPs and their tags

import boto3

boto3.setup_default_session(profile_name='cloud-tool-default')
session = boto3.session.Session(profile_name='cloud-tool-default')

client = session.client('ec2')
regions = [region['RegionName'] for region in client.describe_regions()['Regions']]

# main loop through each region and each ec2 instance
counter = 0

for region in regions:
    ec2_client = session.client('ec2', region_name=region)
    ec2_resource = boto3.resource('ec2', region_name=region)


    # table of all security groups in region and identify the ones that are 0.0.0.0/0 inbound with ports
    # each region groups are unique
    security_groups = {}
    groups = ec2_client.describe_security_groups()
    for ec2_security_groups in groups["SecurityGroups"]:

        #print(ec2_security_groups)
        ip_ranges = []
        security_group_details = {}
        for security_group in ec2_security_groups["IpPermissions"]:

            # find the any IP rules - this could be better and does not address IP6
            for ip_range in security_group["IpRanges"]:
                #if ip_range["CidrIp"] == "0.0.0.0/0":

                    # sometimes there isn't a destination port.
                    try:
                        ip_ranges_text = str(ip_range["CidrIp"]) + ' : ' + str(security_group["ToPort"])
                    except:
                        ip_ranges_text = str(ip_range["CidrIp"]) + " : -"
                    ip_ranges.append(ip_ranges_text)

        # add it to the table.  If no 0.0.0.0/0 then put some text in there so that the report reads ok.
        security_group_details["GroupName"] = ec2_security_groups["GroupName"]
        if ip_ranges == []:
            security_group_details["Rules"] = "NOEXTERNALRULES"
        else:
            security_group_details["Rules"] = ip_ranges

        # was being paranoid, never seen this happen yet.
        if ec2_security_groups["GroupId"] in security_groups.keys():
            print("ERROR !!! - ", ec2_security_groups["GroupId"], " ALREADY EXISTS!!")
        else:
            security_groups[ec2_security_groups["GroupId"]] = security_group_details

    # main loop looking through the ec2 instances
    # remember this is done for each region

    ec2_response = ec2_client.describe_instances()

    for reservations in ec2_response["Reservations"]:
        for instance in reservations["Instances"]:

            # this bit can fail - can't remember why.
            try:
                if instance["PublicIpAddress"]:
                    counter += 1
                    print(region, " ", end="")
                    print(instance["InstanceId"], " ", end="")
                    try:
                        print(instance["KeyName"], " ", end="")
                    except:
                        print("NOKEYNAME", " ", end="")
                    try:
                        print(instance["PublicIpAddress"])
                    except:
                        print("NOPUBLICIP")

                    # Pull out status for the instance.  Sometimes a status is not available.   May mean terminated.
                    print("\tSTATUS: ", end="")
                    if ec2_client.describe_instance_status(InstanceIds=[str(instance["InstanceId"])])['InstanceStatuses']:
                        status = ec2_client.describe_instance_status(InstanceIds=[str(instance["InstanceId"])])\
                            ['InstanceStatuses']\
                            [0]\
                            ['InstanceState']\
                            ['Name']
                        print(status)
                    else:
                        print("No Status Available")

                    # Pull out the tags for the instance
                    ec2_instance = ec2_resource.Instance(instance["InstanceId"])
                    print("\tTAGS:")
                    for tags in ec2_instance.tags:
                        print("\t\t", tags["Key"], " : ", tags["Value"])

                    # Sometimes there are more than one interface.  (In the sand box... whyyyyy?  IAS much?)
                    # fine..
                    interfaces = instance["NetworkInterfaces"]
                    interface_counter = 0
                    for interface in interfaces:
                        interface_counter +=1
                    print("\tNo INTERFACES: ", interface_counter)
                    for interface in interfaces:
                        print("\t\t", interface["Association"]["PublicIp"])
                        for interface_group in interface["Groups"]:
                            interface_group_id = interface_group["GroupId"]
                            print("\t\t\t", interface_group_id, " - ", security_groups[interface_group_id]["GroupName"])
                            print("\t\t\t+++", security_groups[interface_group_id])
                            print("\t\t\t---", security_groups[interface_group_id]["Rules"])
                            if security_groups[interface_group_id]["Rules"] == "NOEXTERNALRULES":
                                print("\t\t\t\tNOEXTERNALRULES")
                            """
                            if security_groups[interface_group_id]["Rules"] == "NOEXTERNALRULES":
                                print("\t\t\t\tNOEXTERNALRULES")
                                security_groups = {}
                                groups = ec2_client.describe_security_groups()
                                for ec2_security_groups in groups["SecurityGroups"]:
                                    if ec2_security_groups["GroupId"] == interface_group_id:
                                        print(ec2_security_groups)

                            else:
                                for rules in security_groups[interface_group_id]["Rules"]:
                                    print("\t\t\t\t", rules)
                                    """
            except:
                pass

print("\n\nNumber of instances: ", counter)


