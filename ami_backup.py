# Automated AMI Backups
#
# @author Robert Kozora <bobby@kozora.me>
#
# This script will search for all instances having a tag with "Backup" or "backup"
# on it. As soon as we have the instances list, we loop through each instance
# and create an AMI of it. Also, it will look for a "Retention" tag key which
# will be used as a retention policy number in days. If there is no tag with
# that name, it will use a 14 days default value for each AMI.
#
# After creating the AMI it creates a "DeleteOn" tag on the AMI indicating when
# it will be deleted using the Retention value and another Lambda function 

import boto3
import collections
import datetime
import sys
import pprint
import os

ec = boto3.client('ec2')
ec2_instance_id = os.environ['instance_id']


def lambda_handler(event, context):
    try:
        retention_days = os.environ['retention']
    except:
        retention_days = 13
    create_time = datetime.datetime.now()
    create_fmt = create_time.strftime('%Y-%m-%d')

    AMIid = ec.create_image(InstanceId=ec2_instance_id,
                            Name="Lambda - " + os.environ['instance_id'] + " from " + create_fmt,
                            Description="Lambda created AMI of instance " + ec2_instance_id + " from " + create_fmt,
                            NoReboot=True, DryRun=False)

    print "Retaining AMI %s of instance %s for %d days" % (
        AMIid['ImageId'],
        os.environ['instance_id'],
        retention_days,
    )

    delete_date = datetime.date.today() + datetime.timedelta(days=retention_days)
    delete_fmt = delete_date.strftime('%m-%d-%Y')

    ec.create_tags(
        Resources=[os.environ['instance_id']],
        Tags=[
            {'Key': 'ami_delete_on', 'Value': delete_fmt},
        ]
    )
