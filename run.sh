# Set the working directory to where the script path is stored
# This makes the script executable from anywhere
SCRIPT_PATH="${BASH_SOURCE[0]:-$0}";
cd "$( dirname -- "$SCRIPT_PATH"; )";


# IP Configurations
BACKBONE_SUBNET=192.168.100.0
BACKBONE_MASK=/24

SWARM_SUBNET=192.168.10.0
SWARM_SUBNET_MASK=/24

# This function prints the next IP
nextip(){
    IP=$1
    IP_HEX=$(printf '%.2X%.2X%.2X%.2X\n' `echo $IP | sed -e 's/\./ /g'`)
    NEXT_IP_HEX=$(printf %.8X `echo $(( 0x$IP_HEX + $2 ))`)
    NEXT_IP=$(printf '%d.%d.%d.%d\n' `echo $NEXT_IP_HEX | sed -r 's/(..)/0x\1 /g'`)
    echo "$NEXT_IP"
}




# Check if number of parameters passed to the script is equal to 2
if [ "$#" != '2' ] || [[ "${BASH_SOURCE[0]}" == "${0}" ]] ; then
    echo -e "\e[32mError:\e[0m"
    echo -e "Script must be sourced with parameters: \nparam1 Script Type: [ap, co, nd] \nparam2 a numeric id\n"
    echo -e "for example:\nsource ./run ap 1\n"
    return
fi

# read the script Role from first parameters and the numeric ID of the node from the second parameter
export ROLE=$1
export NUMID=$2


# generate the IP addresses for the node

BACKBONE_IP=$(nextip $BACKBONE_SUBNET $NUMID)
SWARM_IP=$(nextip $SWARM_SUBNET $NUMID)
l0_ip=$(nextip 127.1.0.0 $NUMID)

# Genereate the MAC address for the node
oldMAC=00:00:00:00:00:00
mac=$(echo $oldMAC | tr -d ':')
macadd=$(( 0x$mac + $NUMID ))
macnew=$(printf "%012x" $macadd | sed 's/../&:/g;s/:$//')

echo $macnew


[[ "$VIRTUAL_ENV" == "" ]]; INVENV=$?

if [ $INVENV -eq "0" ]; then
    if [ -d ".venv"  ]; then
        echo "sourcing from .venv"

        . ./.venv/bin/activate
        
    else 
        python -m venv .venv
        . ./.venv/bin/activate
        pip install aenum cassandra-driver psutil
    fi
    source ~/.bashrc
    alias python='$VIRTUAL_ENV/bin/python'
    alias sudo='sudo '
else
    alias python='$VIRTUAL_ENV/bin/python'
    alias sudo='sudo '
fi 


case $ROLE in
# Coordinator:
    co)
    echo "Role is set to Coordinator"
    sudo ip link add smartedge-bb type vxlan id 1000 dev eth0 group 239.255.1.1 dstport 4789
    sudo ip link set dev smartedge-bb address $macnew
    sudo ip address add ${BACKBONE_IP}${BACKBONE_MASK} dev smartedge-bb
    sudo ip address add ${SWARM_IP}${SWARM_SUBNET_MASK} dev smartedge-bb
    sudo ip link set dev smartedge-bb up
    sudo python ./coordinator/coordinator.py
    ;;
# Access Point: 
    ap)
    echo "Role is set as Access Point"
    sudo ifconfig lo:0 $l0_ip netmask 255.255.255.255 up
    if  nmcli connection show | grep -q 'SmartEdgeHotspot'; then
        echo -e "Connection SmartEdgeHotspot exists: starting wifi hotspot"
        sudo nmcli con up SmartEdgeHotspot
    else
        echo -e "Connection SmartEdgeHotspot does not exists: \n\tcreating connection and starting wifi hotspot"
        sudo nmcli con add type wifi ifname wlan0 con-name SmartEdgeHotspot autoconnect yes ssid R${NUMID}AP
        sudo nmcli con modify SmartEdgeHotspot 802-11-wireless.mode ap 802-11-wireless.band bg ipv4.method shared
        sudo nmcli con modify SmartEdgeHotspot wifi-sec.key-mgmt wpa-psk
        sudo nmcli con modify SmartEdgeHotspot wifi-sec.psk "123456123"
        sudo nmcli con up SmartEdgeHotspot
    fi
    sudo ip link add smartedge-bb type vxlan id 1000 dev eth0 group 239.255.1.1 dstport 4789
    sudo ip link set dev smartedge-bb address $macnew
    sudo ip address add $BACKBONE_IP dev smartedge-bb
    sudo ip link set dev smartedge-bb up
    sudo python ./ap_manager/ap_manager.py
    ;;
# Smart Node
    sn)
    sudo ifconfig lo:0 $l0_ip netmask 255.255.255.255 up
    sudo python ./node_manager/node_manager.py
    ;;



    *)
    echo "unkown"
    ;;
esac









