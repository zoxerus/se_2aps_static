
# Requirements
1. in the RPi5 devices that are meant to work as Access Points:
   - start a wifi hotspot. for example using nmcli:
     ```
       nmcli con add type wifi ifname wlan0 con-name Hotspot autoconnect yes ssid R1AP
       nmcli con modify Hotspot 802-11-wireless.mode ap 802-11-wireless.band bg ipv4.method shared
       nmcli con modify Hotspot wifi-sec.key-mgmt wpa-psk
       nmcli con modify Hotspot wifi-sec.psk "123456123"
       nmcli con up Hotspot
     ```
   - Install the bmv2 docker image `docker pull p4lang/pi`
   - create a virtual python environment inside the folder ./ap_manager/client_monitor `python3 -m venv .venv`
   - source the new environment `source ./.venv/bin/activate`
   - Install the required python modules: `pip install psutil aenum cassandra-driver`
2. In the RPi5 devices that are meant to work as swarm nodes:
   -  download and install the NIKSS switch, follow instructions on the link: https://github.com/NIKSS-vSwitch/nikss
  
# Configuring the Network
All required config is moved to the  /lib/global_config file


# Starting the Network
1. Clone the Repo to the devices meant to work as Access Points and set the config as in the section Congifuring the Network
2. Run the file ./ap_manager/run_ap_container.sh
3. Start the ap_manager by source the file ./ap_manager/client_monitor/run.sh for example:
   ```
   cd ./ap_manager/client_monitor
   . ./run.sh
   ```
4. Start a cassandra database 

5. Start the node_manager by source the file ./node_manager/run.sh for example `. ./run.sh`
6. Connect the swarm node to one of the APs by using the command `nmcli dev wifi connect R1AP password 123456123 ifname wlan0`
