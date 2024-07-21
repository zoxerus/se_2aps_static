import sys
# setting path
sys.path.append('..')

import lib.config as config
import json
import subprocess
import time
import socket
import re
import threading
import lib.bmv2_thrift_lib as bmv2_thrift
import lib.database_comms as db_comms

COORDINATOR_MAX_TCP_CONNNECTIONS = 5


SWARM_NODE_TCP_SERVER = ('', 29997) 


DEFAULT_THRIFT_PORT = 9090

db_in_use = db_comms.STR_DATABASE_TYPE_CASSANDRA

database_session = db_comms.init_database(db_in_use, '0.0.0.0', config.database_port)

lock = threading.Lock()

swarm_access_points = set()


def extract_numbers(lst):
    """
    Extracts numbers from a list of strings using regular expressions.
    """
    # Compile a regular expression pattern to match digits
    pattern = re.compile(r'\d+')
     
    # Use the pattern to extract all digits from each string in the list
    extracted_numbers = [pattern.findall(s) for s in lst]
     
    # Convert the extracted numbers from strings to integers
    return [int(x) for sublist in extracted_numbers for x in sublist]

def add_bmv2_swarm_broadcast_port_to_ap(ap_ip,thrift_port, switch_port ):
        res = bmv2_thrift.send_cli_command_to_bmv2(cli_command='mc_dump', thrift_ip=ap_ip, thrift_port=thrift_port)
        res_lines = res.splitlines()
        i = 0
        
        for line in res_lines:
            if 'mgrp(' in line:
                port_list = set(extract_numbers([ res_lines[i+1].split('ports=[')[1].split(']')[0] ]))
                port_list.add(switch_port)
                broadcast_ports =  ' '.join( str(port) for port in port_list)
                bmv2_thrift.send_cli_command_to_bmv2(f"mc_node_update 0 {broadcast_ports} ", ap_ip, thrift_port )  
            i = i + 1


def get_ap_ip_from_ap_id(ap_id):
    try:
        return config.ap_list[ap_id][1]
    except:
        return None
        
class Swarm_Node_Handler:
    def __init__(self, message, node_socket: socket.socket):
        self.message_as_word_array = message.split()
        self.node_socket = node_socket
        
    def handle_message(self):
        match self.message_as_word_array[0]:
            case 'Join_Request':
                self.handle_new_station_message()
                
            case 'node_left_ap':
                pass
            case _:
                pass    
            
    def handle_new_station_message(self):
        with lock:
            print('\nNew Join Request from: ', end='')
            req_id = self.message_as_word_array[1]
            node_uuid = self.message_as_word_array[2]
            node_swarm_id = self.message_as_word_array[3]
            node_swarm_ip = self.message_as_word_array[4]
            node_swarm_mac = self.message_as_word_array[5]
            node_swarm_ap = self.message_as_word_array[6]
            print(node_uuid + ' on ' + node_swarm_ap)        
        
            ap_ip = get_ap_ip_from_ap_id(node_swarm_ap)
            if (ap_ip == None):
                print(f'Error: could not find IP of access point {node_swarm_ap}')
                return
      
            db_comms.update_db_with_joined_node(db_in_use, database_session, node_uuid, node_swarm_id)
                        
            add_bmv2_swarm_broadcast_port_to_ap(ap_ip= ap_ip, thrift_port=DEFAULT_THRIFT_PORT, switch_port= node_swarm_id)

            entry_handle = bmv2_thrift.add_entry_to_bmv2(communication_protocol= bmv2_thrift.P4_CONTROL_METHOD_THRIFT_CLI,
                                                        table_name='MyIngress.tb_ipv4_lpm',
                action_name='MyIngress.ac_ipv4_forward_mac', match_keys=f'{node_swarm_ip}/32' , 
                action_params= f'{str(node_swarm_id)} {node_swarm_mac}', thrift_ip= ap_ip, thrift_port= DEFAULT_THRIFT_PORT )
        
            entry_handle = bmv2_thrift.add_entry_to_bmv2(communication_protocol= bmv2_thrift.P4_CONTROL_METHOD_THRIFT_CLI, 
                                                        table_name='MyIngress.tb_l2_forward', action_name= 'ac_l2_forward', 
                                                        match_keys= f'{node_swarm_mac}', action_params= str(node_swarm_id),
                                                        thrift_ip= ap_ip, thrift_port= DEFAULT_THRIFT_PORT)
            
            bmv2_thrift.delete_forwarding_entry_from_bmv2(
                communication_protocol= bmv2_thrift.P4_CONTROL_METHOD_THRIFT_CLI, table_name='MyIngress.tb_swarm_control', key= f'{node_swarm_id} {config.this_ap_vip}',
                thrift_ip= ap_ip, thrift_port= DEFAULT_THRIFT_PORT)

            bmv2_thrift.delete_forwarding_entry_from_bmv2(
                communication_protocol= bmv2_thrift.P4_CONTROL_METHOD_THRIFT_CLI, table_name= 'MyIngress.tb_swarm_control', 
                key= f'{config.swarm_backbone_switch_port} {node_swarm_ip }', thrift_ip= ap_ip, thrift_port=DEFAULT_THRIFT_PORT)
            
            for key in config.ap_list.keys():
                if key != node_swarm_ap:
                    entry_handle = bmv2_thrift.add_entry_to_bmv2(communication_protocol= bmv2_thrift.P4_CONTROL_METHOD_THRIFT_CLI,
                                                        table_name='MyIngress.tb_ipv4_lpm',
                            action_name='MyIngress.ac_ipv4_forward_mac', match_keys=f'{node_swarm_ip}/32' , 
                            action_params= f'{config.swarm_backbone_switch_port} {config.ap_list[node_swarm_ap][0]}', thrift_ip= config.ap_list[key][1], thrift_port= DEFAULT_THRIFT_PORT )
                    
                    entry_handle = bmv2_thrift.add_entry_to_bmv2(communication_protocol= bmv2_thrift.P4_CONTROL_METHOD_THRIFT_CLI, 
                                            table_name='MyIngress.tb_l2_forward', action_name= 'ac_l2_forward', 
                                            match_keys= f'{node_swarm_mac}', action_params= str(config.swarm_backbone_switch_port),
                                            thrift_ip= config.ap_list[key][1], thrift_port= DEFAULT_THRIFT_PORT)
                    
                                
        self.node_socket.send( bytes( f'{req_id} accepted'.encode() ) )


def set_keepalive_linux(sock, after_idle_sec=1, interval_sec=3, max_fails=5):
    """Set TCP keepalive on an open socket.

    It activates after 1 second (after_idle_sec) of idleness,
    then sends a keepalive ping once every 3 seconds (interval_sec),
    and closes the connection after 5 failed ping (max_fails), or 15 seconds
    """
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, after_idle_sec)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, interval_sec)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, max_fails)

def handle_swarm_node(node_socket, address):
    try:
        message = node_socket.recv(1024).decode()
        print(f'received: {message} from {address}')    
        
        message_handler = Swarm_Node_Handler(message= message, node_socket=node_socket)
        message_handler.handle_message()
    except Exception as e:
        print(e)


# receives TCP connections from swarm nodes
def swarm_coordinator():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as serversocket:
        serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serversocket.bind(SWARM_NODE_TCP_SERVER)
        set_keepalive_linux(sock= serversocket, after_idle_sec=1, interval_sec=3, max_fails= 5)
        serversocket.listen(COORDINATOR_MAX_TCP_CONNNECTIONS)
        # swarm_access_points.add(serversocket)
        while True:
            (node_socket, address) = serversocket.accept()
            print(f'received connection request from {address}')
            threading.Thread(target=handle_swarm_node, args=(node_socket, address, ), daemon= True ).start()



def main():
    swarm_coordinator()
    # threading.Thread(target=ap_server).start()
    threading.Thread(target=swarm_coordinator, daemon= True).start()
    return 0 

if __name__ == "__main__":
    main()