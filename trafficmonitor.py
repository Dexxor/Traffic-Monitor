import time, sys, os, subprocess, datetime, json, threading
from discord_webhook import DiscordWebhook, DiscordEmbed
data = json.load(open('config.json'))

webhook_url = data['webhook_url']
threshold = data['threshold']
cooldown = data['cooldown']
server = data['servername']
pps = data['pps']
interface = data['interface']


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

def send_webhook_attack(attacksize, pps, pcapname):
        try:
            webhook = DiscordWebhook(url=webhook_url)
            embed = DiscordEmbed(title='Attack Detected', description='Method has been Dumped!', color=242424)
            embed.add_embed_field(name="Server", value=server, inline=False)
            embed.add_embed_field(name="Dump Name", value=pcapname, inline=False)
            embed.add_embed_field(name='Size', value=attacksize, inline=False)
            embed.add_embed_field(name="Peak Packets Per Second", value=pps, inline=False)
            webhook.add_embed(embed)
            webhook.execute()
        except:
            print("Looks like they downed us")
            
def send_webhook_attack_over():
        try:
            webhook = DiscordWebhook(url=webhook_url)
            embed = DiscordEmbed(title='Attack no longer detected', color=242424)
            embed.add_embed_field(name="Server", value=server, inline=False)
            webhook.add_embed(embed)
            webhook.execute() 
        except:
            print("Unable to send end notification for some reason ?!?")

def pcap():
    os.system("tcpdump -i {} -n -s0 -c 5000 -w '{}.pcap'".format(interface,datetime.datetime.now()))

def pullincoming(request):
    if request == 'mbits':
        old = subprocess.getoutput("cat /sys/class/net/%s/statistics/rx_bytes"%interface)
        time.sleep(0.25)
        new = subprocess.getoutput("cat /sys/class/net/%s/statistics/rx_bytes"%interface)
        current_incoming_bytes = (int(new) - int(old)) * 4
        current_incoming_mbits = current_incoming_bytes / int(125000)
        return current_incoming_mbits
    elif request == 'fulloutput':
        old = subprocess.getoutput("cat /sys/class/net/%s/statistics/rx_bytes"%interface)
        time.sleep(0.25)
        new = subprocess.getoutput("cat /sys/class/net/%s/statistics/rx_bytes"%interface)
        current_incoming_bytes = (int(new) - int(old)) * 4
        current_incoming_data = getsizeint(current_incoming_bytes)
        return current_incoming_data
        
def pullincomingpackets():
    oldpkt = subprocess.getoutput("cat /sys/class/net/%s/statistics/rx_packets"%interface)
    time.sleep(0.25)
    newpkt = subprocess.getoutput("cat /sys/class/net/%s/statistics/rx_packets"%interface)
    current_incoming_packets = (int(newpkt) - int(oldpkt)) * 4
    return current_incoming_packets

underattack = False

while True:            
    os.system("clear")
    print("Packets: %s" % pullincomingpackets())
    print("Incoming: %s" % pullincoming('fulloutput'))
    if underattack == False and (((int(pullincoming('mbits')) > int(threshold)) and not pps) or ((int(pullincomingpackets()) > int(threshold)) and pps)):
        print("Under Attack!")
        underattack = True
        time.sleep(1)

        if ((int(pullincoming('mbits')) > int(threshold)) and not pps) or ((int(pullincomingpackets()) > int(threshold)) and pps):
            send = threading.Thread(target=send_webhook_attack(pullincoming('fulloutput'), f"{pullincomingpackets()}", f"{datetime.datetime.now()}.pcap"))
            send.start()
            pcap()
            time.sleep(int(cooldown))
        else:
            print('False positive.')
            underattack = False
        
    if underattack == True and (((int(pullincoming('mbits')) > int(threshold)) and not pps) or ((int(pullincomingpackets()) > int(threshold)) and pps)):
        print("Attack not over yet!")
        time.sleep(int(cooldown))
        continue
    elif underattack == True:
        print('Attack Over!')
        underattack = False
        send_webhook_attack_over()
            
