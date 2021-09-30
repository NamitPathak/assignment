# Create VPC Resource
from troposphere.ec2 import (
    VPC,
    InternetGateway,
    VPCGatewayAttachment,
    Subnet,
    RouteTable,
    Route,
    SubnetRouteTableAssociation
)
from troposphere import ec2
from troposphere import Tags, Ref, GetAtt, Join


# Create VPC
def create_vpc(template, vpc_cidr):
    vpc = template.add_resource(VPC(
        "VPC",
        CidrBlock=Ref(vpc_cidr),
        Tags=Tags(ResourceName="VPC")
    ))
    return vpc


# Create Internet Gateway
def create_internet_gateway(template):
    internet_gateway = template.add_resource(InternetGateway(
        "InternetGateway",
        Tags=Tags(ResourceName="InternetGateway")
    ))
    return internet_gateway


# Attach internet gateway to VPC
def attach_internet_gateway_with_vpc(template, internet_gateway, vpc):
    internet_gateway_attachment = template.add_resource(VPCGatewayAttachment(
        "InternetGatewayAttachment",
        InternetGatewayId=Ref(internet_gateway),
        VpcId=Ref(vpc)
    ))
    return internet_gateway_attachment


# Create public subnet
def create_public_subnet(template, vpc, public_subnet_cidr, subnet_name, subnet_az):
    public_subnet = template.add_resource(
        Subnet(
            subnet_name,
            CidrBlock=Ref(public_subnet_cidr),
            VpcId=Ref(vpc),
            Tags=Tags(ResourceName="public subnet"),
            MapPublicIpOnLaunch=True,
            AvailabilityZone=Join("", [Ref("AWS::Region"), subnet_az])
        )
    )
    return public_subnet


# Create private subnet
def create_private_subnet(template, vpc, private_subnet_cidr):
    private_subnet = template.add_resource(
        Subnet(
            "PrivateSubnet",
            CidrBlock=Ref(private_subnet_cidr),
            VpcId=Ref(vpc),
            Tags=Tags(ResourceName="private subnet")
        )
    )
    return private_subnet


# Create elastic ip address
def create_elastic_ip_for_natgateway(template):
    elastic_ip = template.add_resource(ec2.EIP(
        "ElasticIP",
        Domain="vpc"
    ))
    return elastic_ip


# Create NAT Gateway
def create_nat_gateway(template, elastic_ip, public_subnet):
    nat_gateway = template.add_resource(ec2.NatGateway(
        "NatGateway",
        AllocationId=GetAtt(elastic_ip, "AllocationId"),
        SubnetId=Ref(public_subnet)
    ))
    return nat_gateway


# Create public route table for subnet
def create_public_route_table(template, vpc):
    public_route_table = template.add_resource(RouteTable(
        "PublicRouteTable",
        VpcId=Ref(vpc),
        Tags=Tags(Name="public route table")
    ))
    return public_route_table


# Create Default Route for public route table
def create_public_route(template, internet_gateway_attachment, public_route_table, internet_gateway):
    template.add_resource(Route(
        "PublicRoute",
        DependsOn=internet_gateway_attachment.title,
        RouteTableId=Ref(public_route_table),
        DestinationCidrBlock='0.0.0.0/0',
        GatewayId=Ref(internet_gateway)
    ))


# Create route table association for public subnet
def public_subnet_route_table_association(template, public_route_table, public_subnet, public_assoc_name):
    template.add_resource(SubnetRouteTableAssociation(
        public_assoc_name,
        RouteTableId=Ref(public_route_table),
        SubnetId=Ref(public_subnet)
    ))


# Create private route table for subnet
def create_private_route_table(template, vpc):
    private_route_table = template.add_resource(RouteTable(
        "PrivateRouteTable",
        VpcId=Ref(vpc),
        Tags=Tags(Name="private route table")
    ))
    return private_route_table


# Create Default Route for public route table
def create_private_route(template, private_route_table, nat_gateway):
    template.add_resource(Route(
        "PrivateRoute",
        RouteTableId=Ref(private_route_table),
        DestinationCidrBlock='0.0.0.0/0',
        NatGatewayId=Ref(nat_gateway)
    ))


# Create route table association for private subnet
def private_subnet_route_table_association(template, private_route_table, private_subnet):
    template.add_resource(SubnetRouteTableAssociation(
        "PrivateSubnetRouteTableAssociation",
        RouteTableId=Ref(private_route_table),
        SubnetId=Ref(private_subnet)
    ))


# Create Security Group
def create_security_group(template, vpc, sg_protocol, sg_port, sg_cidr_ip):
    security_group = template.add_resource(ec2.SecurityGroup(
        "SecurityGroup",
        GroupDescription="SG Rule to allow http on host machine",
        VpcId=Ref(vpc),
        SecurityGroupIngress=[
            ec2.SecurityGroupRule(
                IpProtocol=Ref(sg_protocol),
                FromPort=Ref(sg_port),
                ToPort=Ref(sg_port),
                CidrIp=Ref(sg_cidr_ip)
            )]
    ))
    return security_group






