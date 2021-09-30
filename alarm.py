from troposphere import Ref, Template
from troposphere.sns import Subscription, Topic
from troposphere.cloudwatch import Alarm, MetricDimension


def create_sns_topic(template, email):
    sns_topic = template.add_resource(Topic(
        "CpuAlarm",
        Subscription=[Subscription(
            Protocol="email",
            Endpoint=Ref(email)
        )]
    ))
    return sns_topic


def create_cloudwatch_alarm(template, sns_topic, asg_group_name):
    cpu_alarm = template.add_resource(Alarm(
        "InstanceCPUUsageAlarm",
        AlarmDescription="Alarm if ec2 instance cpu utilization go beyond 50 percent",
        Namespace="AWS/EC2",
        MetricName="CPUUtilization",
        Dimensions=[
            MetricDimension(
                Name="AutoScalingGroupName",
                Value=Ref(asg_group_name)
            ),
        ],
        Statistic="Average",
        Period="300",
        EvaluationPeriods="1",
        Threshold="50",
        ComparisonOperator="GreaterThanThreshold",
        AlarmActions=[Ref(sns_topic), ],
        InsufficientDataActions=[
            Ref(sns_topic), ]
    ))
