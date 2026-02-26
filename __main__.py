import pulumi
import pulumi_aws as aws
import os

# Read the public key from the environment (set by GitHub Actions)
public_key = os.getenv("PUBLIC_KEY")

pulumi.export("public_key", public_key)

# create a key pair using the public key
key_pair = aws.ec2.KeyPair("my-key-pair",
  key_name = "my-key-pair",
  public_key = public_key                           
)


# define vpc and subnet configuration
vpc = aws.ec2.Vpc("my-vpc",
  cidr_block = "10.0.0.0/16",
  enable_dns_hostnames = True,
  enable_dns_support = True            
)

# create public subnet
public_subnet = aws.ec2.Subnet("public-subnet",
  vpc_id = vpc.id,
  cidr_block = "10.0.1.0/24",
  map_public_ip_on_launch = True,
  availability_zone = "ap-southeast-1a"
)

# create internet gateway
igw = aws.ec2.InternetGateway("igw",
  vpc_id = vpc.id,  
)

# create a public route table
public_route_table = aws.ec2.RouteTable("public-route-table",
  vpc_id = vpc.id,
  routes = [{
    "cidr_block": "0.0.0.0/0",
    "gateway_id": igw.id
  }]                                      
)

public_route_table_association = aws.ec2.RouteTableAssociation("public-route-table-association",
  subnet_id = public_subnet.id,
  route_table_id = public_route_table.id
)

# create a security group
public_sg = aws.ec2.SecurityGroup("public-sg", 
  description = "Enable SSH and K3s access",
  vpc_id = vpc.id,
  ingress = [
    {"protocol": "tcp", "from_port": 22, "to_port": 22, "cidr_blocks": ["0.0.0.0/0"]},
    {"protocol": "tcp", "from_port": 6443, "to_port": 6443, "cidr_blocks": ["0.0.0.0/0"]}
  ],
  egress = [
    {"protocol": "-1", "from_port": 0, "to_port": 0, "cidr_blocks": ["0.0.0.0/0"]}
  ]
)


# create instance in the vpc and subnet
ami_id = "ami-08d59269edddde222"
instance_type = "t3.small"


master_node = aws.ec2.Instance("master-node",
  instance_type = instance_type,
  ami = ami_id,
  subnet_id = public_subnet.id,
  key_name = key_pair.key_name,
  vpc_security_group_ids = [public_sg.id],
  tags = {
    "Name": "master-node"
  }
)

worker_node_1 = aws.ec2.Instance("worker-node-1",
  instance_type = instance_type,
  ami = ami_id,
  subnet_id = public_subnet.id,
  key_name = key_pair.key_name,
  vpc_security_group_ids = [public_sg.id],
  tags = {
    "Name": "worker-node-1"
  }
)

worker_node_2 = aws.ec2.Instance("worker-node-2",
  instance_type = instance_type,
  ami = ami_id,
  subnet_id = public_subnet.id,
  key_name = key_pair.key_name,
  vpc_security_group_ids = [public_sg.id],
  tags = {
    "Name": "worker-node-2"
  }
)

nginx_instance = aws.ec2.Instance("nginx-instance",
  instance_type = instance_type,
  ami = ami_id,
  subnet_id = public_subnet.id,
  key_name = key_pair.key_name,
  vpc_security_group_ids = [public_sg.id],
  tags = {
    "Name": "nginx-instance"
  }
)



pulumi.export("master_node_id", master_node.id)
pulumi.export("worker_node_1_id", worker_node_1.id)
pulumi.export("worker_node_2_id", worker_node_2.id)
pulumi.export("nginx_instance", nginx_instance.id)