from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from libcloud.compute.deployment import MultiStepDeployment, ScriptDeployment, SSHKeyDeployment
import os, sys, random, string, ConfigParser, time

import libcloud.security
libcloud.security.VERIFY_SSL_CERT = True


# Fetch some values from the config file
config = ConfigParser.RawConfigParser()
config.read(os.path.expanduser('~/config/cm_build_scripts.ini'))

# Try to abstract the provider here, as we may end up supporting others
# Theoretically since we are using libcloud, it should support any
# provider that supports the deploy_node function (Amazon EC2 doesn't)
provider = config.get('CM_server', 'provider')
provider_driver = config.get(provider, 'driver')

# API credentials
user = config.get(provider, 'user')
key = config.get(provider, 'key')

# A quick dependency check.
def dependency_check():
    try:
        open(os.path.expanduser("~/.ssh/id_rsa.pub")).read()
    except IOError:
        print "You need at least a public key called id_rsa.pub in your .ssh directory"
        sys.exit(1)

# Helper script to generate a random password
def gen_passwd():
    N=8
    return ''.join(random.choice(string.ascii_letters + string.digits) for x in range(N))
    
# Return a connection to our chosen Provider.
def get_connection():
    Driver = get_driver(getattr(Provider, provider_driver))
    conn = Driver(user, key)
    return conn
  
def get_images():
    conn = get_connection()
    return conn.list_images()
    
def get_sizes():
    conn = get_connection()
    return conn.list_sizes()
    
def create_server(selected_image, selected_size, node_name=None):
    if node_name is None:
        node_name = 'CM Mercury ' + str(time.time())
    images = get_images();
    sizes = get_sizes();
    
    # We'll use the distro and size from the config ini
    preferred_image = [image for image in images if selected_image in image.name]
    assert len(preferred_image) == 1, "We found more than one image for %s, will be assuming the first one" % selected_image

    preferred_size = [size for size in sizes if selected_size in size.name]
    
    dispatch = [
        SSHKeyDeployment(open(os.path.expanduser("~/.ssh/id_rsa.pub")).read()),
    ]
    msd = MultiStepDeployment(dispatch)
    
    conn = get_connection()
    node = conn.deploy_node(name=node_name,image=preferred_image[0], size=preferred_size[0], deploy=msd)
    
    return node

