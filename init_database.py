#!/usr/bin/env python

from aenum import Enum

try:
    from cassandra.cluster import Cluster
    from cassandra.policies import DCAwareRoundRobinPolicy
except:
    print('Cassandra python module not installed')


CASSANDRA_DEFAULT_PORT = 9042
CASSANDRA_HOST = '0.0.0.0'

# CONSTANTS WITH DESCRIPTIVE NAMES
NAMEOF_DATABASE_SWARM_KEYSPACE = 'KS_SWARM'
NAMEOF_DATABASE_REPLICATION_STRATEGY = 'SimpleStrategy'
NAMEOF_DATABASE_SWARM_TABLE_ACTIVE_NODES = 'Active_Nodes'
NUMBEROF_DATABASE_REPLICATION_FACTOR = '1'

NAMEOF_DATABASE_FIELD_NODE_UUID = 'Node_UUID'
TYPEOF_DATABASE_FIELD_NODE_UUID = 'text'

NAMEOF_DATABASE_FIELD_NODE_SWARM_ID = 'Node_Swarm_ID'
TYPEOF_DATABASE_FIELD_NODE_SWARM_ID = 'int'


NAMEOF_DATABASE_FIELD_NODE_SWARM_IP = 'Swarm_IP'
TYPEOF_DATABASE_FIELD_NODE_SWARM_IP = 'text'

NAMEOF_DATABASE_FIELD_NODE_SWARM_MAC = 'Swarm_MAC'
TYPEOF_DATABASE_FIELD_NODE_SWARM_MAC = 'text'

NAMEOF_DATABASE_FIELD_NODE_PHYSICAL_MAC = 'Physical_MAC'
TYPEOF_DATABASE_FIELD_NODE_PHYSICAL_MAC = 'text'

NAMEOF_DATABASE_FIELD_NODE_CURRENT_AP = 'Node_Current_AP'
TYPEOF_DATABASE_FIELD_NODE_CURRENT_AP = 'text'

NAMEOF_DATABASE_FIELD_NODE_CURRENT_SWARM = 'Node_Current_SWARM'
TYPEOF_DATABASE_FIELD_NODE_CURRENT_SWARM = 'text'

NAMEOF_DATABASE_FIELD_NODE_SWARM_STATUS = 'Node_Swarm_Status'
TYPEOF_DATABASE_FIELD_NODE_SWARM_STATUS = 'text'

NAMEOF_DATABASE_FIELD_LAST_UPDATE_TIMESTAMP = 'Last_Update_Timestamp'
TYPEOF_DATABASE_FIELD_LAST_UPDATE_TIMESTAMP = 'timestamp'

# DATABASE QUERIES
QUERY_DATABASE_CREATE_KEYSPACE = f"""\
CREATE KEYSPACE IF NOT EXISTS {NAMEOF_DATABASE_SWARM_KEYSPACE} \
WITH REPLICATION = {{ \
'class' : '{NAMEOF_DATABASE_REPLICATION_STRATEGY}', \
'replication_factor' : '{NUMBEROF_DATABASE_REPLICATION_FACTOR}' }}; \
                                """
                                
QUERY_DATABASE_CREATE_TABLE =  f"""
CREATE TABLE IF NOT EXISTS {NAMEOF_DATABASE_SWARM_KEYSPACE}.{NAMEOF_DATABASE_SWARM_TABLE_ACTIVE_NODES}
(
{NAMEOF_DATABASE_FIELD_NODE_SWARM_ID} {TYPEOF_DATABASE_FIELD_NODE_SWARM_ID} PRIMARY KEY,
{NAMEOF_DATABASE_FIELD_NODE_UUID} {TYPEOF_DATABASE_FIELD_NODE_UUID},
{NAMEOF_DATABASE_FIELD_NODE_CURRENT_AP} {TYPEOF_DATABASE_FIELD_NODE_CURRENT_AP},
{NAMEOF_DATABASE_FIELD_NODE_SWARM_STATUS} {TYPEOF_DATABASE_FIELD_NODE_SWARM_STATUS},
{NAMEOF_DATABASE_FIELD_NODE_SWARM_IP} {TYPEOF_DATABASE_FIELD_NODE_SWARM_IP},
{NAMEOF_DATABASE_FIELD_NODE_SWARM_MAC} {TYPEOF_DATABASE_FIELD_NODE_SWARM_MAC},
{NAMEOF_DATABASE_FIELD_NODE_PHYSICAL_MAC} {TYPEOF_DATABASE_FIELD_NODE_PHYSICAL_MAC},
{NAMEOF_DATABASE_FIELD_LAST_UPDATE_TIMESTAMP} {TYPEOF_DATABASE_FIELD_LAST_UPDATE_TIMESTAMP}
);
"""


class SWARM_STATUS(Enum):
    JOINED  = 'Joined'
    PENDING = 'Pending'
    LEFT    = 'Left'

def init_database(host, port):
    # CONNECT TO THE DATABASE
    cluster = Cluster(
        contact_points=[host], 
                    port=port, 
                    load_balancing_policy=DCAwareRoundRobinPolicy(local_dc='datacenter1'),
                    protocol_version=5
    )
    session = cluster.connect()
    session.execute(f'DROP TABLE IF EXISTS {NAMEOF_DATABASE_SWARM_KEYSPACE}.{NAMEOF_DATABASE_SWARM_TABLE_ACTIVE_NODES}')
    # CREATE A NAME SPACE IN THE DATABSE FOR STORING SWARM INFO
    session.execute( QUERY_DATABASE_CREATE_KEYSPACE )
    # CREATE A TABLE TO MANAGE ACTIVE SWARM NODES
    session.execute(QUERY_DATABASE_CREATE_TABLE)
    


def main():
    init_database(CASSANDRA_HOST, CASSANDRA_DEFAULT_PORT)
