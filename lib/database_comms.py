import lib.db.cassandra_db as cassandra_db
import lib.db.redis_db as redis_db
import lib.db.defines as db_defines



STR_DATABASE_TYPE_REDIS = 'redis'
STR_DATABASE_TYPE_CASSANDRA = 'cassandra'


def init_database(database_type, host, port):
    
    if database_type == STR_DATABASE_TYPE_REDIS:
        return redis_db.redis.Redis(host=host, port=port, decode_responses=True)

    elif database_type == STR_DATABASE_TYPE_CASSANDRA:        
        # CONNECT TO THE DATABASE
        cluster = cassandra_db.Cluster(
            contact_points=[host], 
                        port=port, 
                        load_balancing_policy=cassandra_db.DCAwareRoundRobinPolicy(local_dc='datacenter1'),
                        protocol_version=5
        )
        session = cluster.connect()
        session.execute(f'DROP TABLE IF EXISTS {db_defines.NAMEOF_DATABASE_SWARM_KEYSPACE}.{db_defines.NAMEOF_DATABASE_SWARM_TABLE_ACTIVE_NODES}')
        # CREATE A NAME SPACE IN THE DATABSE FOR STORING SWARM INFO
        session.execute( cassandra_db.QUERY_DATABASE_CREATE_KEYSPACE )
        # CREATE A TABLE TO MANAGE ACTIVE SWARM NODES
        session.execute(cassandra_db.QUERY_DATABASE_CREATE_TABLE)
        return session
    
def connect_to_database(database_type, host, port):
    if database_type == STR_DATABASE_TYPE_REDIS:
        return redis_db.redis.Redis(host=host, port=port, decode_responses=True)

    elif database_type == STR_DATABASE_TYPE_CASSANDRA:        
        # CONNECT TO THE DATABASE
        cluster = cassandra_db.Cluster(
            contact_points=[host], 
                        port=port, 
                        load_balancing_policy=cassandra_db.DCAwareRoundRobinPolicy(local_dc='datacenter1'),
                        protocol_version=5
        )
        session = cluster.connect()
        return session


def get_node_swarm_mac_by_swarm_ip(database_type, session, node_swarm_ip):
    if database_type == STR_DATABASE_TYPE_CASSANDRA:
        query = f"""SELECT {db_defines.NAMEOF_DATABASE_FIELD_NODE_SWARM_MAC} from 
        {db_defines.NAMEOF_DATABASE_SWARM_KEYSPACE}.{db_defines.NAMEOF_DATABASE_SWARM_TABLE_ACTIVE_NODES}
        WHERE {db_defines.NAMEOF_DATABASE_FIELD_NODE_SWARM_IP} = '{node_swarm_ip}' ALLOW FILTERING; """
        result = session.execute(query)
        if (result.one() == None or len(result.one()) > 1 ):
            print(f'Node {node_swarm_ip} not found in database or is duplicate, Node rejected')
        return result.one()[0]


    
def update_db_with_left_node(database_type, session, node_swarm_id):
    if database_type == STR_DATABASE_TYPE_CASSANDRA:
        query = f"""UPDATE {db_defines.NAMEOF_DATABASE_SWARM_KEYSPACE}.{db_defines.NAMEOF_DATABASE_SWARM_TABLE_ACTIVE_NODES}
        SET {db_defines.NAMEOF_DATABASE_FIELD_NODE_SWARM_STATUS} = '{db_defines.SWARM_STATUS.LEFT.value}'
        WHERE {db_defines.NAMEOF_DATABASE_FIELD_NODE_SWARM_ID} = {node_swarm_id}  IF EXISTS;
        """
        return session.execute(query)
    
def insert_node_into_swarm_database(database_type, session, host_id, this_ap_id, node_vip, node_vmac, node_phy_mac):
    query = f"""
    INSERT INTO {db_defines.NAMEOF_DATABASE_SWARM_KEYSPACE}.{db_defines.NAMEOF_DATABASE_SWARM_TABLE_ACTIVE_NODES} (
    {db_defines.NAMEOF_DATABASE_FIELD_NODE_SWARM_ID}, {db_defines.NAMEOF_DATABASE_FIELD_NODE_CURRENT_AP},
    {db_defines.NAMEOF_DATABASE_FIELD_NODE_SWARM_STATUS}, {db_defines.NAMEOF_DATABASE_FIELD_LAST_UPDATE_TIMESTAMP}, 
    {db_defines.NAMEOF_DATABASE_FIELD_NODE_SWARM_IP}, {db_defines.NAMEOF_DATABASE_FIELD_NODE_SWARM_MAC},
    {db_defines.NAMEOF_DATABASE_FIELD_NODE_PHYSICAL_MAC})
    VALUES ({host_id}, '{this_ap_id}', '{db_defines.SWARM_STATUS.JOINED.value}', toTimeStamp(now() ),
    '{node_vip}', '{node_vmac}', '{node_phy_mac}');
    """
    session.execute(query)


def get_next_available_host_id_from_swarm_table(database_typ, session, first_host_id, max_host_id, node_physical_mac):
    if database_typ == STR_DATABASE_TYPE_CASSANDRA:
        query=  f""" SELECT {db_defines.NAMEOF_DATABASE_FIELD_NODE_SWARM_ID} FROM 
            {db_defines.NAMEOF_DATABASE_SWARM_KEYSPACE}.{db_defines.NAMEOF_DATABASE_SWARM_TABLE_ACTIVE_NODES}
            WHERE {db_defines.NAMEOF_DATABASE_FIELD_NODE_PHYSICAL_MAC} = '{node_physical_mac}' ALLOW FILTERING
            """
        result = session.execute(query)            
        print(result.one())
        if result.one() != None:
            print(result[0][0])
            return result[0][0]
        
        query = f""" SELECT {db_defines.NAMEOF_DATABASE_FIELD_NODE_SWARM_ID} FROM 
            {db_defines.NAMEOF_DATABASE_SWARM_KEYSPACE}.{db_defines.NAMEOF_DATABASE_SWARM_TABLE_ACTIVE_NODES}"""
        result = session.execute(query)
        id_list = []
        for row in result:
            id_list.append(row[0])
        print(id_list)
        if (id_list == []):
            return first_host_id
        return min(set(range(first_host_id, max_host_id + 1 )) - set(id_list))
    
def delete_node_from_swarm_database(database_type, session, node_swarm_id):
    if database_type == STR_DATABASE_TYPE_CASSANDRA:
        query = f"""
            DELETE FROM {db_defines.NAMEOF_DATABASE_SWARM_KEYSPACE}.{db_defines.NAMEOF_DATABASE_SWARM_TABLE_ACTIVE_NODES} 
            WHERE {db_defines.NAMEOF_DATABASE_FIELD_NODE_SWARM_ID} = {node_swarm_id};
            """
        session.execute(query)