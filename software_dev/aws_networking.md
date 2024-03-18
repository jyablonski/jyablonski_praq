# AWS Networking

## VPCs
A Virtual Private Cloud (VPC) is a logically isolated section of the AWS cloud where you can launch AWS resources. It allows you to define your own private network in the AWS cloud, complete with IP address ranges, subnets, and routing tables. Each AWS account can have multiple VPCs, and you can configure the networking environment within each VPC according to your needs.

Example VPC CIDR: `10.0.0.0/16`
- Represents the range of IP Addresses assigned to this vpc
- Multiple different AWS Accounts can specify this same CIDR Range
- AWS will only allow 1 IP Address to be used at 1 time


## Subnets
Subnets are subdivisions of a VPC's IP address range. They allow you to segment your VPC into smaller, more manageable portions. Each subnet is associated with an Availability Zone (AZ), which is a distinct geographic location within an AWS region. Subnets can be public or private, depending on whether they have direct internet access.

Public Subnets: These are connected to the internet through a Network Address Translation (NAT) gateway or instance. Resources in a public subnet can communicate directly with the internet and can be accessed from outside the VPC.

Private Subnets: These are not directly accessible from the internet. Resources in a private subnet can communicate with the internet through a NAT gateway or instance in a public subnet.

A VPC contains one or more subnets. Subnets help you divide the IP address space of your VPC and deploy resources in different segments. By creating both public and private subnets, you can control how your resources interact with the internet.

Each Subnet in a VPC is associated with a route table that contains a list of routes that determine how traffic should be directed.

Example Subnets that go into the VPC CIDR `10.0.0.0/16`: 
- Public Subnet 1 `10.0.1.0/24` US East 1 Availability Zone 2 - 249 Available IP Addresses remaining (some are in use, and the network/broadcast address aren't available)
- Public Subnet 2 `10.0.3.0/24` US East 1 Availability Zone 4 - 249 Available IP Addresses remaining
- These are smaller subdivisions of the VPC CIDR Range
- Resources in these subnets can communicate to other subnets in the same VPC, as well as the Internet because they're public.

## Security Groups
Security Groups are virtual firewalls that control inbound and outbound traffic for AWS resources. They act as stateful firewalls, which means if you allow inbound traffic, the corresponding outbound response is automatically allowed. Security Groups are associated with EC2 instances, RDS instances, and other resources. They help control network traffic to and from resources and ensure a secure environment.

Subnets and Security Groups work together to control network traffic. EC2 instances (or other resources) in a subnet use the associated Security Group's rules to determine which traffic is allowed in and out. You can define security group rules to control traffic between instances in different subnets, or between instances in a subnet and the internet.

VPCs provide the overall networking environment, while Security Groups control traffic within that environment. Security Groups are associated with specific resources in a VPC, helping you define fine-grained rules for each resource's inbound and outbound traffic.

## Route Tables
Amazon Web Services (AWS) route tables are networking constructs that control the traffic flow between subnets in a Virtual Private Cloud (VPC) and the destinations outside the VPC, including the internet and other VPCs. Route tables determine how traffic is directed within a VPC by specifying the routes that traffic should take.

Here are the key aspects of AWS route tables:

- Association with Subnets: Each subnet in a VPC is associated with a specific route table. This association dictates how traffic is routed in and out of the subnet. A subnet can be associated with only one route table at a time.

- Default Route Table: When you create a VPC, AWS automatically creates a default route table for that VPC. This default route table is initially associated with all the subnets in the VPC. It defines how traffic should be routed within the VPC.

- Custom Route Tables: You can create custom route tables to customize the routing behavior of specific subnets. For example, you might create a custom route table to route traffic through a virtual private gateway for a VPN connection.

- Routes: A route table contains routes that define where network traffic should be directed. Each route in the table consists of a destination CIDR block and a target. The target can be an internet gateway, a virtual private gateway, a network interface, a VPC peering connection, or a transit gateway, among other options.

- Main Routes and Additional Routes: Route tables contain both main routes (directly connected routes to the VPC's CIDR block) and additional routes (custom routes defined by you). The order of routes matters: traffic is routed based on the most specific matching route.

- Route Propagation: For VPN and Direct Connect connections, you can propagate routes from a VPN or Direct Connect attachment to a custom route table, making it easier to manage routing for on-premises networks.

- Route Priority: In case of multiple routes with overlapping CIDR blocks, the most specific route takes precedence. If no matching route is found, the traffic is routed based on the default route.

- Internet Access: To enable internet access for instances in a subnet, you associate the subnet with a route table that has a route to an Internet Gateway. This is typically the default route table for public subnets.

- Private Access: For private subnets, you might associate the subnet with a route table that routes traffic through a Network Address Translation (NAT) gateway or instance for internet-bound traffic.

- VPC Peering and Transit Gateway Routes: For communicating with resources in other VPCs or transit gateways, you create specific routes in your route tables.

## Internet & NAT Gateways
Amazon Web Services (AWS) provides two key networking components for enabling internet connectivity from within Virtual Private Clouds (VPCs): Internet Gateways and Network Address Translation (NAT) Gateways. These gateways play different roles in facilitating communication between resources in your VPC and the public internet.

1. Internet Gateway:
- An Internet Gateway (IGW) is a component that attaches to a VPC that allows resources within your VPC to access the internet and be accessed from the internet. An IGW is a logical connection point and operates at the network layer to provide a path for internet-bound traffic.

Key features of an Internet Gateway:

- Enables instances in public subnets to communicate directly with the internet.
- Allows resources with public IP addresses to be accessible from the internet.
- Requires associated route entries in the VPC's route tables directing internet-bound traffic through the IGW.
  - Add a route in the public route table with a destination of `0.0.0.0/0` (which represents all IP addresses) and a target of your Internet Gateway.
  - ![image](https://github.com/jyablonski/jyablonski_praq/assets/16946556/6af91d2d-2502-4ee8-8138-e7936ef62744)
- Suitable for scenarios where you need to run public-facing applications.
- Internet Gateways are provided free by AWS

1. Network Address Translation (NAT) Gateway:
- A Network Address Translation (NAT) Gateway is a managed service that enables instances in private subnets to initiate outbound connections to the internet, while preventing unsolicited inbound traffic from reaching those instances. It's used to provide internet access to instances that don't have public IP addresses.

Key features of a NAT Gateway:

- Helps instances in private subnets access the internet for updates, patches, and other outbound communication.
- Provides a public IP address for instances to use for outbound traffic.
- Translates private IP addresses to its own public IP address when instances initiate internet-bound connections.
- Offers greater availability, scalability, and easier management compared to a NAT instance.
- A common use case for a NAT Gateway is enabling instances in private subnets to access software repositories, update servers, or interact with external APIs, while maintaining a higher level of security.
- NAT Gateways have an hourly charge associated with them ($0.045 / hr)


## Transit Gateways
An Amazon Web Services (AWS) Transit Gateway is a networking service that simplifies and centralizes the management of network connectivity between Amazon Virtual Private Clouds (VPCs), on-premises networks, and other Amazon Web Services accounts. It acts as a hub that facilitates interconnecting multiple VPCs and on-premises networks in a scalable and efficient manner.

Here are the key features and benefits of AWS Transit Gateway:

Centralized Hub: AWS Transit Gateway provides a central hub for connecting multiple VPCs and on-premises networks. Instead of creating individual peering connections between each VPC pair, you can connect all VPCs and on-premises networks to the Transit Gateway.

Simplified Network Architecture: With Transit Gateway, you can create a fully meshed network topology with a single connection to the hub, reducing the complexity of managing numerous peering connections.

Scalability: Transit Gateway supports the connection of thousands of VPCs and on-premises networks, making it suitable for large-scale environments.

Transitive Routing: Transit Gateway supports transitive routing, meaning traffic can flow from one VPC to another through the Transit Gateway even if there is no direct peering connection between the two VPCs.

Global Scope: Transit Gateway can span multiple AWS regions, enabling inter-region connectivity without the need for complex VPN or Direct Connect configurations.

Network Policies: You can attach route tables to Transit Gateway attachments to control the routing of traffic between different VPCs and networks. This provides fine-grained control over communication paths.

VPN and Direct Connect Integration: You can connect on-premises networks to Transit Gateway using VPN and AWS Direct Connect. This simplifies the management of hybrid network configurations.

Resource Sharing: Transit Gateway allows for the sharing of resources, such as Network Load Balancers, across multiple VPCs attached to the same Transit Gateway.

Route Propagation: Route propagation enables automatic route table updates for the attached VPCs, simplifying the routing configuration.


### CIDR Blocks
CIDR blocks, also known as CIDR notation or CIDR prefixes, are a way of representing IP address ranges using a combination of an IP address and a prefix length. CIDR stands for Classless Inter-Domain Routing, and it allows for more efficient allocation and routing of IP addresses on the internet.

In CIDR notation, an IP address range is represented by the combination of an IP address and a prefix length separated by a forward slash (/). Here's how it works:

1. **IP Address**: The IP address specifies the starting address of the range. It can be any valid IPv4 or IPv6 address.

2. **Prefix Length**: The prefix length specifies the number of bits in the network portion of the address. It determines the size of the address range and how many addresses are included in it. A larger prefix length corresponds to a smaller address range with fewer addresses, while a smaller prefix length corresponds to a larger address range with more addresses.

For example, in IPv4 CIDR notation:

- `192.168.1.0/24` represents the range of IP addresses from `192.168.1.0` to `192.168.1.255`, with the first 24 bits (or the first three octets) representing the network portion and the last 8 bits representing the host portion.

- `10.0.0.0/8` represents the range of IP addresses from `10.0.0.0` to `10.255.255.255`, with the first 8 bits representing the network portion and the remaining bits representing the host portion.

CIDR blocks are commonly used in networking for purposes such as IP address allocation, subnetting, routing, and firewall configuration. They provide a flexible and efficient way of representing IP address ranges and are widely used in internet routing protocols such as BGP (Border Gateway Protocol).

Here are examples of some of the most common sets of bits typically used in subnet masks, along with the corresponding CIDR notation and number of possible IP addresses:

1. **/24 (255.255.255.0)**:
   - This is a common subnet mask used for small to medium-sized networks.
   - Number of possible IP addresses: 256 (2^8)

2. **/16 (255.255.0.0)**:
   - This is a common subnet mask used for large networks or organizations.
   - Number of possible IP addresses: 65,536 (2^16)

3. **/8 (255.0.0.0)**:
   - This is a common subnet mask used for very large networks or Internet Service Providers (ISPs).
   - Number of possible IP addresses: 16,777,216 (2^24)

These are some of the most commonly used subnet masks, representing different sizes of networks. The larger the subnet mask (the fewer bits available for host addresses), the fewer possible IP addresses within the network. Conversely, smaller subnet masks allow for more host addresses but cover smaller ranges of IP addresses.

VPC CIDR Block `10.0.0.0/16`
- IP Address: 10.0.0.0
  - This is the starting IP address of the range.
  - In binary, it is `00001010.00000000.00000000.00000000`.
- Subnet Mask: /16
  - The /16 indicates the subnet mask's prefix length. It specifies the number of bits in the subnet mask that are set to 1, starting from the left. In this case, the first 16 bits are set to 1.
- Binary Subnet Mask: `11111111.11111111.00000000.00000000`
  - The binary subnet mask has the first 16 bits set to 1 and the remaining 16 bits set to 0.
  - This range spans 65,536 individual IP addresses.


Subnet CIDR Block `10.0.1.0/24`
- Network Address `10.0.1.0`
- Usable IP Addresses: `10.0.1.1` to `10.0.1.254`
- Broadcast Address: `10.0.1.255`