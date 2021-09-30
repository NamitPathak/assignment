import troposphere.elasticloadbalancingv2 as elb
from troposphere import Ref, Template, Tags, Parameter


def create_load_balancer(template, public_subnet, public_subnet_2, security_group):
    load_balancer = template.add_resource(elb.LoadBalancer(
        "ApplicationElasticLoadBalancer",
        Name="ApplicationELB",
        Subnets=[Ref(public_subnet), Ref(public_subnet_2)],
        Scheme="internet-facing",
        SecurityGroups=[Ref(security_group)]
    ))
    return load_balancer


def create_target_group(template, vpc, server_port):
    target_group = template.add_resource(elb.TargetGroup(
        "TargetGroupForELB",
        VpcId=Ref(vpc),
        HealthCheckIntervalSeconds="20",
        HealthCheckProtocol="HTTP",
        HealthCheckTimeoutSeconds="10",
        HealthyThresholdCount="3",
        Matcher=elb.Matcher(
            HttpCode="200"),
        Name="TargetGroup",
        Port=Ref(server_port),
        Protocol="HTTP",
        UnhealthyThresholdCount="3"
    ))
    return target_group


def create_elb_listener(template, load_balancer, target_group, server_port):
    elb_listener = template.add_resource(elb.Listener(
        "ELBListener",
        LoadBalancerArn=Ref(load_balancer),
        Port=Ref(server_port),
        Protocol="HTTP",
        DefaultActions=[elb.Action(
            Type="forward",
            TargetGroupArn=Ref(target_group)
        )]
    ))


