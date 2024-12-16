import psutil 
import lib.global_config as global_config

# Configuring a unique IP on the loopback interface to be used
# as an ID for nodes and Access Points.
# Currently only using last byte of lo:0 as an ID
# This can be configured for example using:
# ifconfig lo:0 127.0.1.1 netmask 255.255.255.255 up

loopback_if = 'lo:0'
loopback_id = psutil.net_if_addrs()[loopback_if][0][1].split('.')
this_ap_id = f'AP:{int(loopback_id[3]):03}'

# this_ap_id = global_config.this_ap_id

# This a P4 switch port number for forwardign packets to other APs
# over the backbone network
ap_communication_switch_port = global_config.swarm_backbone_switch_port

# This is the switch port number that goes to the coordinator
swarm_coordinator_switch_port = global_config.swarm_backbone_switch_port

# name of the default wlan interface to use
default_wlan_interface = global_config.default_wlan_interface
default_ethernet_device = global_config.default_ethernet_device


# currently assuming a /24 mask
this_swarm_subnet= global_config.this_swarm_subnet
this_swarm_dhcp_start = global_config.this_swarm_dhcp_start
this_swarm_dhcp_end = global_config.this_swarm_dhcp_end


# Hostname and Port numbers to connect to the database
database_hostname = global_config.database_hostname
database_port = global_config.database_port

# Coordinator TCP port for the node manager to communicate with the coordinator
# this info is sent by the AP to the swarm node.
coordinator_tcp_port = global_config.coordinator_tcp_port

# a TCP port number for the AP Manager to commmunicate with the node manager
node_manager_tcp_port = global_config.node_manager_tcp_port

