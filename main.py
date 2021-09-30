import boto3
import json
import argparse
import alb
import vpc

from troposphere import Template
from troposphere.ec2 import VPC

from vpc import *
from alb import *
from asg import *
from s3bucket import *
from alarm import *


# Set template for cloud formation
template = Template()
template.set_version("2010-09-09")
template.set_description(
    """\
AWS cloud formation template to create all the resources """
)


# Parameters for VPC Resources
vpc_cidr = template.add_parameter(Parameter(
        "VpcCidrRange",
        Type="String",
        Default="10.0.0.0/8",
        Description="Cidr Range for VPC",
    ))

public_subnet_cidr = template.add_parameter(Parameter(
        "PublicSubnetCidrRange",
        Type="String",
        Description="Cidr Range for public subnet",
    ))

public_subnet_2_cidr = template.add_parameter(Parameter(
        "PublicSubnet2CidrRange",
        Type="String",
        Description="Cidr Range for public subnet 2",
    ))

private_subnet_cidr = template.add_parameter(Parameter(
        "PrivateSubnetCidrRange",
        Type="String",
        Description="Cidr Range for private subnet",
    ))

sg_protocol = template.add_parameter(Parameter(
        "SecurityGroupProtocol",
        Type="String",
        Description="Security Group Protocol Ex- TCP/HTTP",
    ))

sg_port = template.add_parameter(Parameter(
        "SecurityGroupPort",
        Type="String",
        Description="Security Group Port",
    ))

sg_cidr_ip = template.add_parameter(Parameter(
        "SecurityGroupCidr",
        Type="String",
        Description="Security Group Cidr for inbound rules",
    ))

# Logs Bucket Name Parameter

logs_bucket_name = template.add_parameter(Parameter(
        "LogsBucketName",
        Description="Bucket Name for logging of Nginx Logs",
        Type="String"
    ))

# SNS Topic Email
sns_topic_email = template.add_parameter(Parameter(
        "Email",
        Description="Email for sns topic",
        Type="String"
    ))


def create_cloud_formation_stack():
    client = boto3.client('cloudformation')
    resource = client.create_stack(
        StackName="SimplAssignment",
        TemplateBody=template.to_yaml(),
        Capabilities=[
            "CAPABILITY_IAM"
        ],
        EnableTerminationProtection=False,
        Parameters=[
            {
                'ParameterKey': 'VpcCidrRange',
                'ParameterValue': args["VpcCidrRange"]
            },
            {
                'ParameterKey': 'PublicSubnetCidrRange',
                'ParameterValue': args["PublicSubnetCidrRange"]
            },
            {
                'ParameterKey': 'PublicSubnet2CidrRange',
                'ParameterValue': args["PublicSubnet2CidrRange"]
            },
            {
                'ParameterKey': 'PrivateSubnetCidrRange',
                'ParameterValue': args["PrivateSubnetCidrRange"]
            },
            {
                'ParameterKey': 'SecurityGroupProtocol',
                'ParameterValue': args["SecurityGroupProtocol"]
            },
            {
                'ParameterKey': 'SecurityGroupPort',
                'ParameterValue': args["SecurityGroupPort"]
            },
            {
                'ParameterKey': 'SecurityGroupCidr',
                'ParameterValue': args["SecurityGroupCidr"]
            },
            {
                'ParameterKey': 'LogsBucketName',
                'ParameterValue': args["LogsBucketName"]
            },
            {
                'ParameterKey': 'Email',
                'ParameterValue': args["Email"]
            }
        ]
    )


# Create VPC
create_vpc = vpc.create_vpc(template, vpc_cidr)

# Create Security Groups
security_group = vpc.create_security_group(template, create_vpc, sg_protocol, sg_port, sg_cidr_ip)

# Create Subnets public and private
public_subnet = create_public_subnet(template, create_vpc, public_subnet_cidr, "PublicSubnet", "a")
public_subnet_2 = create_public_subnet(template, create_vpc, public_subnet_2_cidr, "PublicSubnet2", "b")
private_subnet = create_private_subnet(template, create_vpc, private_subnet_cidr)

# Create Internet gateway and its attachment with VPC
internet_gateway = create_internet_gateway(template)
internet_gateway_attachment = attach_internet_gateway_with_vpc(template, internet_gateway, create_vpc)

# Create public route for public subnet
public_route_table = create_public_route_table(template, create_vpc)
create_public_route(template, internet_gateway_attachment, public_route_table, internet_gateway)
public_subnet_route_table_association(template, public_route_table, public_subnet, "PublicSubnetRouteTableAssoc")
public_subnet_route_table_association(template, public_route_table, public_subnet_2, "PublicSubnetRouteTableAssoc2")

# Create EIP and Nat gateway.
elastic_ip = create_elastic_ip_for_natgateway(template)
nat_gateway = create_nat_gateway(template, elastic_ip, public_subnet)

# Create private route for private subnet.
private_route_table = create_private_route_table(template, create_vpc)
create_private_route(template, private_route_table, nat_gateway)
private_subnet_route_table_association(template, private_route_table, private_subnet)

# Create Load Balancer , Target Groups and Listener
load_balancer = create_load_balancer(template, public_subnet, public_subnet_2, security_group)
target_groups = create_target_group(template, create_vpc, sg_port)
create_elb_listener(template, load_balancer, target_groups, sg_port)

# Create S3 Bucket for Nginx Logs
create_s3_bucket(template, logs_bucket_name)

# Create Autoscaling group and Launch Template for EC2 and role for it.
instance_role = create_instance_role(template)
create_instance_role_policy(template, instance_role, logs_bucket_name)
create_instance_profile(template, instance_role)
launch_config = create_launch_config(template, security_group, logs_bucket_name)
asg_group = create_auto_scaling(template, security_group, private_subnet, launch_config, target_groups)

# Create SNS Topic to send alarm
sns_topic = create_sns_topic(template, sns_topic_email)

# Cloud watch alarm to check cpu utilization
create_cloudwatch_alarm(template, sns_topic, asg_group)


if __name__ == "__main__":
    # Create CLI Parser to pass the argument from the CLI command.
    parser = argparse.ArgumentParser(description='Parse all the variables passed From CLI Command.')

    parser.add_argument("-vcr", "--VpcCidrRange", required=True,
                        help="vpc cidr range")
    parser.add_argument("-psr", "--PublicSubnetCidrRange", required=True,
                        help="public subnet cidr range")
    parser.add_argument("-psr2", "--PublicSubnet2CidrRange", required=True,
                        help="public subnet 2 cidr range")
    parser.add_argument("-pr", "--PrivateSubnetCidrRange", required=True,
                        help="private subnet cidr range")
    parser.add_argument("-sgp", "--SecurityGroupProtocol", required=True,
                        help="Security Group protocol")
    parser.add_argument("-sgt", "--SecurityGroupPort", required=True,
                        help="Security Group port")
    parser.add_argument("-sgc", "--SecurityGroupCidr", required=True,
                        help="Security Group cidr range")
    parser.add_argument("-lbn", "--LogsBucketName", required=True,
                        help="Logs Bucket Name")
    parser.add_argument("-e", "--Email", required=True,
                        help="Email for SNS Topic")

    args = vars(parser.parse_args())

    print(template.to_yaml())

    # Call the boto3 code to create the stack from the yaml template generated by troposphere
    create_cloud_formation_stack()



