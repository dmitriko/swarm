"Various config options common for Node and Manager"


from tornado.options import define


def define_common_options():

    define('log_file', default='',  help = 'File path to log file')

    define('config', help = 'File path to config file')

    define('debug', default=False, type=bool)

    define('amqp_host', help='AMQP server host', default='localhost')

    define('amqp_port', help='AMQP server port', type=int, default=5672)

    define('amqp_vhost', help='AMQP virtual host', default='/')

    define('amqp_user', help='User name for connect to AMQP server', 
           default='guest'),
    
    define('amqp_password', help='Password to connect to AMQP server',
           default='guest')

    define('updates_exchange', help="Name for AMQP exchange for updates",
           default="updates_ex")

    define('reports_exchange', help='Name for AMQP exchage for events',
           default='reports_ex')

    define('rpc_exchange', help='Name for AMQP exchange used for RPC',
           default='rpc_ex')

    define('reports_queue', default='events_q',
           help='Name for AMQP Queue for Manager listen Events')

           
def define_node_options():
    define('oid', help='UUID of current node')
    define('storages', help='Comma separated list of paths to storages')
