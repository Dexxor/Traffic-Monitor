  # Traffic-Monitor

  Traffic Monitor is a basic python script that monitors incoming packets and incoming traffic all together and once the threshold has been passed for example there are 8 Mbit/s or 8000pps (Depending on if pps is true or not in the config )    incoming but the threshold is 5 Mbit/s or 500pps it will trigger the script and alert you over discord aswell as save a pcap for you to view the attack later.

  # Requirements
  * tcpdump
  * datetime
  * discord_webhook

  # Installation

    #Ubuntu and Debian based distribution
    apt install tcpdump python3 python3-pip screen -y
    #Centos/Rhel based distributions
    yum install tcpdump python3 python3-pip screen -y
  
    git clone https://github.com/Dexxor/Traffic-Monitor.git
    cd Traffic-Monitor
    pip3 install -r requirements.txt
    #Edit config.json to your liking
    screen python3 trafficmonitor.py
