# the ID of the current Access Point

this_swarm_id = '1000'
swarm_backbone_switch_port = 510

default_wlan_interface = 'wlan0'
default_ethernet_device = 'eth0'

this_ap_id = 'AP:004'

REDIS_PORT = 6379
CASSANDRA_PORT = 9402

'''
In the new documentation, I have replaced the name vxlan1000 with the name smartedge-bb, but the functionality remains the same.
In this file I am using two networks:
the 192.168.10.0/24 is the swarm subnet
the 192.168.100.0/24 is the smartedge backbone and it is a vxlan overlay network used to connect the coordinator with the APs
The IP of the coordinator is on the backbone network is 192.168.100.6 and on the swarm subnet it takes the IP 192.168.10.1
and the access points have the IPs 192.168.100.3, 192.168.100.4, and 192.168.10.5.
currently the Access Points don't take swarm IP (e.g on the subnet 192.168.10.0/24) as it is not needed. 
'''


# here configure the subnet range that need to be allocated to the swarm
# here we assume a /24 subnet mask
this_swarm_subnet='192.168.10.0'  ## this is the subnet to use for the swarm
this_swarm_dhcp_start = 2         # this is the first IP to be assigned to the swarm node e.g: 192.168.10.2
this_swarm_dhcp_end  = 200        # last IP to be assigned e.g: 192.168.10.200  so it supports 199 nodes (arbitrary number can be changed to any)


# This is the ip and port number of the database
database_hostname = '0.0.0.0'
database_port = 9042

# this is a tcp port number used to reach the coordinator from the swarm nodes
coordinator_tcp_port = 29997

# this is a tcp port number used to reach the swarm node manager from the access points
# in order to send the swarm config
node_manager_tcp_port = 29997

# this is the default thrift port used for configuring the P4 switches in the network
default_thrift_port = 9090

# list of access points in the network, used to propagate configuration changes
# this list of IPs and MACs are the ones configured on the smartedge-bb on each access point

the_other_ap = '10.30.2.189'