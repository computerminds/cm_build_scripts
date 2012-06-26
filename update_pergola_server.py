#! /usr/bin/env python

"""Create server script

Valid options:
  --size - The size of the machine to create (required)
  --image - The image to use for the machine (required)
  --branch
  --update_branch
  --output_ip
  --help - Print this help
"""

import sys, getopt, socket, os, time
from helpers import cm_libcloud
import fabric.api as fabric
from libcloud.compute.types import NodeState

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "h", ["help", "size=", "image=", "output_ip=", 'branch=', 'update_branch='])
        except getopt.error, msg:
             raise Usage(msg)
        # process options
        size = None
        image = None
        branch = 'stable'
        update_branch = 'master'
        output_ip = None

        for o, a in opts:
            if o in ("-h", "--help"):
                print __doc__
                return 0;
            if o in ("--size"):
                size = a
            if o in ("--image"):
                image = a
            if o in ("--output_ip"):
                output_ip = a
            if o in ("--branch"):
                branch = a
            if o in ("--update_branch"):
                update_branch = a


        # Check the command line options
        if size is None:
            raise Usage, "the --size option must be specified"
        if image is None:
            raise Usage, "the --image option must be specified"
        
        try:
            # Create a server with the specified image and size
            print '===> Creating the server. This may take a minute or two...'
            print ""
            node = cm_libcloud.create_server(image, size)
            
            print_node_details(node)
    
            # Use Fabric to install pergola
            install_pergola(node, branch)
            
            # Use Fabric to update pergola
            update_pergola(node, update_branch)
    
            # Finally, reboot the node
            print '===> Rebooting the node...'
            cm_libcloud.reboot_node(node)
            print '===> done'
            
            print_node_details(node)
    
            if output_ip is not None:
                with open(output_ip, 'w') as f:
                    f.write(node.public_ip[0])
            
        except:
            print "===> Test failure"
            raise
        finally:
            print "===> Destroying this node"
            cm_libcloud.destroy_node(node)

        return 0

    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2

def print_node_details(node):
    print ""
    print "-----------------------------------------------------------"
    print ""
    print "Server details:"
    print ""
    print "Public IP: %s" % node.public_ip[0]
    print ""
    if node.extra.get('password'):
        print "Root user password: %s" % node.extra.get('password')
        print ""
    print "SSH connection string:"
    print "ssh root@%s" % node.public_ip[0]
    print ""
    print "-----------------------------------------------------------"
    print ""
    

def install_pergola(node, branch):
    cm_libcloud.fabric_setup(node)

    fabric.run("apt-get update", pty=True)
    
    print '===> Installing git'
    fabric.run("apt-get install git-core -y", pty=True)

    print '===> Installing Pergola'
    fabric.run("apt-get install git-core -y", pty=True)
    fabric.run("git clone git://github.com/computerminds/pergola.git -b %s /opt/pergola" % (branch), pty=True)

    # Need to preseed some options for postfix
    fabric.run("echo 'postfix postfix/main_mailer_type select Internet Site' | debconf-set-selections", pty=True)
    fabric.run("echo 'postfix postfix/mailname string $HOSTNAME' | debconf-set-selections", pty=True)
    fabric.run("echo 'postfix postfix/destinations string localhost.localdomain, localhost' | debconf-set-selections", pty=True)


    with fabric.cd('/opt/pergola'):
        fabric.run("python setup.py", pty=True)

def update_pergola(node, branch):
    print '===> Updating Pergola to branch %s' % (branch)
    
    with fabric.cd('/opt/pergola'):
        fabric.run("git checkout -f %s" % (branch), pty=True)
        fabric.run("python update.py")

def disable_apache(node):
    _disable_initd(node, ["apache2"])

def disable_mysql(node):
    _disable_upstart(node, ["mysql"])

def disable_jenkins(node):
    _disable_initd(node, ["jenkins"])

def disable_memcache(node):
    _disable_initd(node, ["memcached"])

def disable_tomcat(node):
    _disable_initd(node, ["tomcat6"])

def disable_mercury(node):
    _disable_initd(node, ["bcfg2", "pound"])

def _disable_initd(node, scripts):
    cm_libcloud.fabric_setup(node)
    for script in scripts:
        fabric.run("update-rc.d " + script + " disable", pty=True)

def _disable_upstart(node, scripts):
    cm_libcloud.fabric_setup(node)
    for script in scripts:
        with fabric.cd('/etc/init'):
            fabric.run("mv " + script + ".conf " + script + ".conf.disabled", pty=True)


if __name__ == "__main__":
    sys.exit(main())
