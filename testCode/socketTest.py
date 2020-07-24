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
    print("No wired ethernet at eth0")

modacServerIPAddr = '192.168.0.10'

import platform  # For getting the operating system name
import subprocess  # For executing a shell command

def ping(host):
    """
    Returns True if host (str) responds to a ping request.
    Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
    """

    # Option for the number of packets as a function of
    param = '-n' if platform.system().lower() == 'windows' else '-c'

    # Building the command. Ex: "ping -c 1 google.com"
    command = ['ping', param, '1', host]

    return subprocess.call(command) == 0

value = ping(modacServerIPAddr)
print("Ping = ", value)

noNetAddress = '127.0.0.1'
value = ping(noNetAddress)
print("Ping = ", value)