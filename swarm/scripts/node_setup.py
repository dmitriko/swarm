#! /usr/bin/python

""" Install depenencies and perform initial setup for VGD Cloud """

from subprocess import call, Popen, PIPE
import os
import sys


USER = 'vgdcloud'
PYTHON_DEPS = ['tornado', 'pika' 'ipython'] 
YUM_DEPS = ['emacs-nox', 'sudo', 'python-setuptools', 'kvm',
            'virt-manager', 'libvrit', 'bridge-utils',
            'qemu-kvm', 'wget', 'avahi']
PKLA_FILE = \
'/etc/polkit-1/localauthority/50-local.d/50-libvirt-remote-access.pkla'
DEFAULT_PKLA_CONTENT = """[libvirt Management Access]
Identity=unix-user:%s
Action=org.libvirt.unix.manage
ResultAny=yes
ResultInactive=yes
ResultActive=yes
""" % USER

LOG_DIR = '/var/log/vgdcloud'
CONFIG_DIR = '/etc/vgdcloud'
CONFIG_FILE = 'vgdcloud.conf'

DEFAULT_CONFIG = """# config variable for node daemon
# see manager config for RabbitMQ connection data
amqp_user = "guest" 
amqp_password = "guest" 
amqp_host = "localhost"
amqp_vhost = "/"

# storages - comma separated list of pathes on local FS
# (could be mount points or plain directory) to store
# virtual machine disks

storage = '/home/vgdcloud' # most probably U need to change this!

"""


def check_is_root():
    "This should be run with sudo"
    if os.getuid() != 0:
        sys.stderr.write('Run it with sudo.')
        sys.exit(1)


def yum_install():
    """YUM install deps"

    """
    if call(['yum', '-y', 'install'] + YUM_DEPS):
        sys.exit(1)
        

def fix_libvirt():
    "Remove default network, fix avahi"
    call(['/etc/init.d/libvritd', 'restart'])
    call(['/etc/init.d/messagebus', 'restart'])
    call(['/etc/init.d/avahi-daemon', 'restart'])
    call(['/sbin/chkconfig', 'messagebus', 'on'])
    call(['/sbin/chkconfig', 'avahi-daemon', 'on'])
    call(['virsh', 'net-destroy', 'default'])
    call(['virsh', 'net-undefine', 'default'])
    call(['/etc/init.d/libvritd', 'restart'])


def easy_install():
    "Setup required Python modules"
    if call(['easy_install'] + PYTHON_DEPS):
        sys.stderr.write('Could not install deps.')
        sys.exit(1)


def add_user():
    "Add user vgdcloud user to OS"
    proc = Popen(['/usr/sbin/useradd', '-m', USER], stderr=PIPE, stdout=PIPE)
    if proc.wait():
        err = proc.communicate()[1]
        if 'exists' not in err:
            sys.stderr.write('Could not create user %s' % USER)
            sys.exit(1)
    

def create_dirs():
    "Create dir for logs and conf, put default config file"
    for dir_path in [LOG_DIR, CONFIG_DIR]:
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
            if call(['chown', USER, dir_path]):
                raise RuntimeError("Could not chown %s" % LOG_DIR)
    config_path = os.path.join(CONFIG_DIR, CONFIG_FILE)
    if not os.path.exists(config_path):
        open(config_path, 'w').write(DEFAULT_CONFIG)
    

def make_pkla_file():
    "Make PolicyKit file to allow non root user manage libvirt"
    if os.path.exists(PKLA_FILE):
        print 'Warning: %s already exists' % PKLA_FILE
        return

    dir_name = os.path.dirname(PKLA_FILE)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    open(PKLA_FILE, 'w').write(DEFAULT_PKLA_CONTENT)


def main():
    "Install deps, create user and dirs, fix libvirt"
    check_is_root()
    yum_install()
    add_user()
    create_dirs()
    fix_libvirt()
    easy_install()
    print 'Done'


if __name__ == '__main__':
    main()
