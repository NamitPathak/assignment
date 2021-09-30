This script will create a cli command to execute a python script which will create a CloudFormation template
using Troposphere and execute it.

The directory structure is as follows :

Template -
|--- main.py -- This is the main driver program which will run the whole script<br />
|--- vpc.py  -- This template consist of definitions to create all the vpc resources including vpc,subnets,nat gateway, route table, routes and all the subnet assocition with route table.<br />
|--- asg.py  -- This template consist of definitions to create all the autoscaling group resources.<br />
|--- alb.py  -- This template consist of definitions to create all the load balancers resources including target group and application load balancer.<br />
|--- alarms.py -- This template consist of definitions to sns topic notifications and cloud watch alarms resources.<br />
|--- s3bucket.py -- This template consist of definitions to create s3 bucket for ngnix logs.<br />

This script can be executed by running the main.py file and by passing all required cli parameters.

Here is the list of all parameters required to pass to the CLI.

--VpcCidrRange            -vcr          --> Cidr Range for VPC<br />
--PublicSubnetCidrRange   -psr          --> Cidr Range for Public Subnet 1<br />
--PublicSubnet2CidrRange  -psr2         --> Cidr Range for Public Subnet 2<br />
--PrivateSubnetCidrRange  -pr           --> Cidr Range for Private Subnet<br />
--SecurityGroupProtocol   -sgp          --> Protocol for the security group ex tcp<br />
--SecurityGroupPort       -sgt          --> Port Number for the security group ex - 80<br />
--SecurityGroupCidr       -sgc          --> Cidr Range for Security Group<br />
--LogsBucketName          -lbn          --> Bucket Name for ngnix logs<br />
--Email                   -e            --> Email for alarms notifications<br />

Here is the example to execute the main.py

python main.py -vcr 10.0.0.0/16 -psr 10.0.0.0/24 -psr2 10.0.1.0/24 -pr 10.0.2.0/24 -sgp tcp -sgt 80 -sgc 0.0.0.0/0 -lbn logsbuckettest2 -e namit125@gmail.com
