from troposphere.autoscaling import AutoScalingGroup, LaunchConfiguration, Tag
from troposphere.policies import (
    AutoScalingReplacingUpdate,
    AutoScalingRollingUpdate,
    UpdatePolicy,
)
from troposphere import Ref, Join, FindInMap, Base64
from troposphere.iam import Role, InstanceProfile, PolicyType
from awacs.aws import Allow, Statement, Principal, PolicyDocument
from awacs.sts import AssumeRole


def create_instance_role(template):
    instance_role = template.add_resource(Role(
        "InstanceRole",
        AssumeRolePolicyDocument=PolicyDocument(
            Statement=[
                Statement(
                    Effect=Allow,
                    Action=[AssumeRole],
                    Principal=Principal("Service", ["ec2.amazonaws.com"])
                )
            ]
        )
    ))
    return instance_role


def create_instance_role_policy(template, instance_role, bucket_name):
    instance_role_policy = template.add_resource(PolicyType(
        "InstanceRolePolicy",
        PolicyName="instance_policy",
        Roles=[Ref(instance_role)],
        PolicyDocument={
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Action": [
                    "s3:PutObject"
                ],
                "Resource": Join("", ["arn:aws:s3:::", Ref(bucket_name), "/*"])
            }],
        }
    ))


def create_instance_profile(template, instance_role):
    instance_profile = template.add_resource(InstanceProfile(
            "InstanceProfile",
            Roles=[Ref(instance_role)]
    ))


def create_launch_config(template, security_group, bucket_name):

    template.add_mapping('RegionMap', {
        "us-east-1": {"64": "ami-087c17d1fe0178315"},
        "us-east-2": {"64": "ami-00dfe2c7ce89a450b"},
    })

    launch_config = template.add_resource(LaunchConfiguration(
        "LaunchConfiguration",
        ImageId=FindInMap("RegionMap", Ref("AWS::Region"), "64"),
        InstanceType="t2.micro",
        SecurityGroups=[Ref(security_group)],
        UserData=Base64(Join("", [
            "#!/bin/bash", "\n",
            "amazon-linux-extras install nginx1 -y\n",
            "rpm -Uvh https://s3.amazonaws.com/amazoncloudwatch-agent/amazon_linux/amd64/latest/amazon-cloudwatch-agent.rpm\n",
            "service nginx start\n",
            "echo '0 /5 * * * aws s3 cp /var/log/nginx/ s3://", Ref(bucket_name), "/ --recursive' > /tmp/serverlogs.txt\n"
            "bash -c 'crontab /tmp/serverlogs.txt'\n"]
        ))
    ))
    return launch_config


def create_auto_scaling(template, security_group, private_subnet, launch_config, target_group):
    autoscaling_group = template.add_resource(AutoScalingGroup(
        "AutoScalingGroups",
        LaunchConfigurationName=Ref(launch_config),
        VPCZoneIdentifier=[Ref(private_subnet)],
        MinSize="1",
        MaxSize="5",
        DesiredCapacity="1",
        TargetGroupARNs=[Ref(target_group)]
    ))
    return autoscaling_group

