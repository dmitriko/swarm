
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


LIBVIRT_XML = """<domain type='kvm' id='1'>
  <name>usbvm</name>
  <uuid>c2127a40-eb4c-4e3c-af5b-ab455fd8bb40</uuid>
  <memory unit='KiB'>2048000</memory>
  <currentMemory unit='KiB'>2048000</currentMemory>
  <vcpu placement='static'>4</vcpu>
  <os>
    <type arch='x86_64' machine='rhel6.3.0'>hvm</type>
    <boot dev='hd'/>
  </os>
  <features>
    <acpi/>
    <apic/>
    <pae/>
  </features>
  <clock offset='utc'/>
  <on_poweroff>destroy</on_poweroff>
  <on_reboot>restart</on_reboot>
  <on_crash>restart</on_crash>
  <devices>
    <emulator>/usr/libexec/qemu-kvm</emulator>
    <disk type='file' device='disk'>
      <driver name='qemu' type='qcow2'/>
      <source file='/home/vgd/storage2/usbvm_d0.qcow2'/>
      <target dev='hda' bus='ide'/>
      <alias name='ide0-0-0'/>
      <address type='drive' controller='0' bus='0' target='0' unit='0'/>
    </disk>
    <disk type='file' device='cdrom'>
      <driver name='qemu' type='raw'/>
      <source file='/home/vgd/storage2/debian-6.0.6-amd64-DVD-1.iso'/>
      <target dev='hdc' bus='ide'/>
      <readonly/>
      <alias name='ide0-1-0'/>
      <address type='drive' controller='0' bus='1' target='0' unit='0'/>
    </disk>
    <controller type='usb' index='0'>
      <alias name='usb0'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x01' function='0x2'/>
    </controller>
    <controller type='ide' index='0'>
      <alias name='ide0'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x01' function='0x1'/>
    </controller>
    <interface type='bridge'>
      <mac address='52:54:00:fe:49:df'/>
      <source bridge='virbr2'/>
      <target dev='vnet0'/>
      <alias name='net0'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x03' function='0x0'/>
    </interface>
    <serial type='pty'>
      <source path='/dev/pts/1'/>
      <target port='0'/>
      <alias name='serial0'/>
    </serial>
    <console type='pty' tty='/dev/pts/1'>
      <source path='/dev/pts/1'/>
      <target type='serial' port='0'/>
      <alias name='serial0'/>
    </console>
    <input type='tablet' bus='usb'>
      <alias name='input0'/>
    </input>
    <input type='mouse' bus='ps2'/>
    <graphics type='vnc' port='5900' autoport='yes' listen='127.0.0.1'>
      <listen type='address' address='127.0.0.1'/>
    </graphics>
    <video>
      <model type='cirrus' vram='9216' heads='1'/>
      <alias name='video0'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x02' function='0x0'/>
    </video>
    <hostdev mode='subsystem' type='usb' managed='yes'>
      <source>
        <address bus='1' device='1'/>
      </source>
      <alias name='hostdev0'/>
    </hostdev>
    <memballoon model='virtio'>
      <alias name='balloon0'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x04' function='0x0'/>
    </memballoon>
  </devices>
  <seclabel type='dynamic' model='selinux' relabel='yes'>
    <label>system_u:system_r:svirt_t:s0:c321,c392</label>
    <imagelabel>system_u:object_r:svirt_image_t:s0:c321,c392</imagelabel>
  </seclabel>
</domain>"""


VIRSH_LIST = ' Id    Name                           State\n----------------------------------------------------\n 1     usbvm                          running\n 2     hydravm                        running\n 4     testvm                         running\n'

DF_RAW = 'Filesystem            Size  Used Avail Use% Mounted on\n/dev/mapper/vg_bart-lv_root\n                       50G  9.4G   38G  21% /\ntmpfs                  24G     0   24G   0% /dev/shm\n/dev/sda1             485M   40M  420M   9% /boot\n/dev/mapper/vg_bart-lv_home\n                      753G   13G  702G   2% /home'
