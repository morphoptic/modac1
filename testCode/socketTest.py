import socket

hostname = socket.gethostname()
print ("hostname: " + hostname)

IPAddr = socket.gethostbyname(hostname)
print ("ipaddr: " + IPAddr)

import ifaddr

adapters = ifaddr.get_adapters()
for adapter in adapters:
    print("IPs for network adapter "+ adapter.nice_name)
    for ip in adapter.ips:
        print("   %s/%s"%(ip.ip,ip.network_prefix))
                