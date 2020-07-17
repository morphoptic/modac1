import socket

hostname = socket.gethostname()
print ("hostname: " + hostname)

IPAddr = socket.gethostbyname(hostname)
print ("ipaddr: " + IPAddr)

import ifaddr

adapters = ifaddr.get_adapters()
eth0Available = False
for adapter in adapters:
    if 'eth0' == adapter.nice_name:
        eth0Available = True
    print("IPs for network adapter "+ adapter.nice_name)
    for ip in adapter.ips:
        print("   %s/%s"%(ip.ip,ip.network_prefix))

if eth0Available:
    print("Wired ethernet eth0 is available")
else:
    print("No wired ethernet")