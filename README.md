
# Requirements
1. in the RPi5 devices that are meant to work as Access Points:
   - Install the bmv2 docker image p4jet.tar.gz by running `docker load -i p4jet.tar.gz`

2. In the RPi5 devices that are meant to work as swarm nodes:
   -  download and install the NIKSS switch, follow instructions on the link: https://github.com/NIKSS-vSwitch/nikss
  
# Configuring the Network
All required config is moved to the  /lib/global_config file


# Starting the Network
1. Clone the Repo to the devices meant to work as Access Points and set the config as in the section Congifuring the Network
2. Run the file ./ap_manager/run_ap_container.sh
3. Start a single instance only on one of the APs of cassandra database `./start_cassandra_docker.sh`
4. Start the ap_manager by source the file ./run.sh providing two arguments first one is the role which can be {ap: for access point, sn: for smart node} for example:
   ```
   cd ./ap_manager/client_monitor
   . ./run.sh  ap 1
   ```
this script should handle the configuration of the smartedge-bb vxlan tunnel, the virtual environment creation and installation of python packages, and the creation and starting of the hotspot connection
5. Start the node_manager by source the file ./run.sh for example `. ./run.sh sn 1`
6. Connect the swarm node to one of the APs by using the command `nmcli dev wifi connect R1AP password 123456123 ifname wlan0`
