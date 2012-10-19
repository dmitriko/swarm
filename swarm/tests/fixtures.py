
IFCONFIG_DATA = """eth0      Link encap:Ethernet  HWaddr 34:40:B5:E1:96:88  
          inet addr:10.0.0.1  Bcast:10.0.0.255  Mask:255.255.255.0
          UP BROADCAST MULTICAST  MTU:1500  Metric:1
          RX packets:7989434 errors:0 dropped:0 overruns:0 frame:0
          TX packets:0 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:1000 
          RX bytes:556075873 (530.3 MiB)  TX bytes:0 (0.0 b)

eth1      Link encap:Ethernet  HWaddr 34:40:B5:E1:96:8C  
          inet addr:10.0.1.1  Bcast:10.0.1.255  Mask:255.255.255.0
          UP BROADCAST MULTICAST  MTU:1500  Metric:1
          RX packets:10 errors:0 dropped:0 overruns:0 frame:0
          TX packets:0 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:1000 
          RX bytes:600 (600.0 b)  TX bytes:0 (0.0 b)

eth2      Link encap:Ethernet  HWaddr 34:40:B5:E1:96:8A  
          inet6 addr: fe80::3640:b5ff:fee1:968a/64 Scope:Link
          UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
          RX packets:19735154 errors:35 dropped:105 overruns:0 frame:0
          TX packets:4613398 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:1000 
          RX bytes:12836793539 (11.9 GiB)  TX bytes:339347134 (323.6 MiB)

eth3      Link encap:Ethernet  HWaddr 34:40:B5:E1:96:8E  
          inet addr:10.0.2.1  Bcast:10.0.2.255  Mask:255.255.255.0
          inet6 addr: fe80::3640:b5ff:fee1:968e/64 Scope:Link
          UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
          RX packets:5730 errors:0 dropped:0 overruns:0 frame:0
          TX packets:3297 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:1000 
          RX bytes:518280 (506.1 KiB)  TX bytes:636629 (621.7 KiB)

lo        Link encap:Local Loopback  
          inet addr:127.0.0.1  Mask:255.0.0.0
          inet6 addr: ::1/128 Scope:Host
          UP LOOPBACK RUNNING  MTU:16436  Metric:1
          RX packets:39174 errors:0 dropped:0 overruns:0 frame:0
          TX packets:39174 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:0 
          RX bytes:15051134 (14.3 MiB)  TX bytes:15051134 (14.3 MiB)

virbr2    Link encap:Ethernet  HWaddr 34:40:B5:E1:96:8A  
          inet addr:91.218.108.170  Bcast:91.218.108.175  Mask:255.255.255.248
          inet6 addr: fe80::3640:b5ff:fee1:968a/64 Scope:Link
          UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
          RX packets:11530363 errors:0 dropped:0 overruns:0 frame:0
          TX packets:1744551 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:0 
          RX bytes:5339790098 (4.9 GiB)  TX bytes:132645902 (126.5 MiB)

vnet0     Link encap:Ethernet  HWaddr FE:54:00:46:82:15  
          inet6 addr: fe80::fc54:ff:fe46:8215/64 Scope:Link
          UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
          RX packets:100541 errors:0 dropped:0 overruns:0 frame:0
          TX packets:3214154 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:500 
          RX bytes:11546476 (11.0 MiB)  TX bytes:348405586 (332.2 MiB)

vnet1     Link encap:Ethernet  HWaddr FE:54:00:FE:49:DF  
          inet6 addr: fe80::fc54:ff:fefe:49df/64 Scope:Link
          UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
          RX packets:1205 errors:0 dropped:0 overruns:0 frame:0
          TX packets:3158908 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:500 
          RX bytes:105305 (102.8 KiB)  TX bytes:247523347 (236.0 MiB)"""


BRCTL_SHOW_DATA = 'bridge name\tbridge id\t\tSTP enabled\tinterfaces\nvirbr2\t\t8000.3440b5e1968a\tno\t\teth2\n\t\t\t\t\t\t\tvnet0\n\t\t\t\t\t\t\tvnet1'
