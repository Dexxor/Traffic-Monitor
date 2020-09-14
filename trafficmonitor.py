import time, sys, os, subprocess, datetime, json
from discord_webhook import DiscordWebhook, DiscordEmbed
with open('config.json') as config_file:
    data = json.load(config_file)
webhook_url = data['webhook_url']
mbit_threshold = data['mbit_threshold']
cooldown = data['cooldown']
server = data['servername']
interface = data['interface']

while True:

    def getsizeint(B):
         B = float(B)
         KB = float(125)
         MB = float(125000)
         GB = float(1.25e+8) 
         TB = float(KB ** 4) 
         
         if B < KB:
            return '{0} {1}'.format(B,'Bytes' if 0 == B > 1 else 'Byte')
         elif KB <= B < MB:
            return '{0:.2f} Kb/s'.format(B/KB)
         elif MB <= B < GB:
            return '{0:.2f} Mb/s'.format(B/MB)
         elif GB <= B < TB:
            return '{0:.2f} GB'.format(B/GB)
         elif TB <= B:
               return '{0:.2f} TB'.format(B/TB)
            
    def send_webhook(attacksize, pps, pcapname):
            webhook = DiscordWebhook(url=webhook_url)
            embed = DiscordEmbed(title='Attack Detected', description='Method has been Dumped!', color=242424)
            embed.add_embed_field(name="Server", value=server, inline=False)
            embed.add_embed_field(name="Dump Name", value=pcapname, inline=False)
            embed.add_embed_field(name='Size', value=attacksize, inline=False)
            embed.add_embed_field(name="Peak Packets Per Second", value=pps, inline=False)
            webhook.add_embed(embed)
            response = webhook.execute() 
            
    
    def pullincoming(request):
        if request == 'mbits':
            old = subprocess.getoutput("grep %s: /proc/net/dev | cut -d : -f2 | awk '{print $1}'"%interface)
            time.sleep(1)
            new = subprocess.getoutput("grep %s: /proc/net/dev | cut -d : -f2 | awk '{print $1}'"%interface)
            current_incoming_bytes = int(new) - int(old)
            current_incoming_mbits = current_incoming_bytes / int(125000)
            return current_incoming_mbits
        elif request == 'fulloutput':
            old = subprocess.getoutput("grep %s: /proc/net/dev | cut -d : -f2 | awk '{print $1}'"%interface)
            time.sleep(1)
            new = subprocess.getoutput("grep %s: /proc/net/dev | cut -d : -f2 | awk '{print $1}'"%interface)
            current_incoming_bytes = int(new) - int(old)
            current_incoming_data = getsizeint(current_incoming_bytes)
            return current_incoming_data
            
    def pullincomingpackets():
        oldpkt = subprocess.getoutput("grep %s: /proc/net/dev | cut -d : -f2 | awk '{print $2}'"%interface)
        time.sleep(1)
        newpkt = subprocess.getoutput("grep %s: /proc/net/dev | cut -d : -f2 | awk '{print $2}'"%interface)
        current_incoming_packets = int(newpkt) - int(oldpkt)
        return current_incoming_packets

    os.system("clear")

    print("Packets: %s" % pullincomingpackets())
    print("Incoming: %s" % pullincoming('fulloutput'))
    
    if int(pullincoming('mbits')) > int(mbit_threshold):
        print("Under Attack!")
        time.sleep(2)
        send_webhook(pullincoming('fulloutput'), f"{pullincomingpackets()}", f"{datetime.datetime.now()}.pcap")
        os.system("tcpdump -n -s0 -c 5000 -w '%s.pcap'"%(datetime.datetime.now()))
        time.sleep(int(cooldown))
        if int(pullincoming('mbits')) > int(mbit_threshold):
            print("Attack not over yet!")
            time.sleep(150)
        else:
            print('Attack Over!')
        
time.sleep(1)