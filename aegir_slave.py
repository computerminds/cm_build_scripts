#! /usr/bin/env python

"""Aegir slave script

Valid options:
  --ip - The ip address of the Aegir slave (required)
  --master - The FQDN of the Aegir master server (required)
  --friendy_name - The friendly name of the Aegir slave (required)
  --apache_port - The apache port for the webserver
  --mysql_port - The apache port for the webserver
  --help - Print this help
"""

import sys, getopt, socket
from helpers import cm_libcloud
import fabric.api as fabric

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "h", ["help", "ip=", "master=", "friendly_name=", "apache_port=", "mysql_port="])
        except getopt.error, msg:
             raise Usage(msg)
        # process options
        ip = None
        master = None
        friendly_name = None
        apache_port = None
        mysql_port = None
        mysql_pass = None
        
        for o, a in opts:
            if o in ("-h", "--help"):
                print __doc__
                return 0;
            if o in ("--ip"):
                ip = a
            if o in ("--master"):
                master = a
            if o in ("--friendly_name"):
                friendly_name = a
            if o in ("--apache_port"):
                apache_port = a
            if o in ("--mysql_port"):
                mysql_port = a
        
        
        # Check the command line options
        if ip is None:
            raise Usage, "the --ip option must be specified"
        if master is None:
            raise Usage, "the --master option must be specified"
        if friendly_name is None:
            raise Usage, "the --friendly_name option must be specified"
        
        # Set up the Mercury server as an Aegir slave
        
        setup_base_slave(ip)
        
        if apache_port != None:
            setup_apache_slave(ip, apache_port)
            
        if mysql_port != None:
            mysql_pass = setup_mysql_slave(ip, master, mysql_port)
            
        add_aegir_slave(master, ip, apache_port, mysql_port, mysql_pass)
        
        
        return 0
        
    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2

def setup_base_slave(ip):
    print 'Setting up the base Aegir system.'
    fab_slave(ip)
    result = fabric.run("adduser --system --group --home /var/aegir aegir", pty=True)
    if 'already exists' in result:
        # If we've already created the user, then it's an early exit for us.
        return
    fabric.run("adduser aegir www-data    #make aegir a user of group www-data", pty=True)
    fabric.run("chsh -s /bin/sh aegir", pty=True)
    
    #fabric.run("", pty=True)
    fabric.run("mkdir /var/aegir/.ssh", pty=True)
    fabric.run("touch /var/aegir/.ssh/authorized_keys", pty=True)
    fabric.run("echo 'ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAy+rElNLeCyJ9qW1eKqgpIN+N09MYOUiGIPIyrC/qvCIDIZwbFGDxVe7D4x71HGu3tMYzp1jk69Iiqy7z/DjTb6ep0iXp8zwmrfgVf7n2XsnVIT57GZsb0JYJ3bO8UJZghLPTe1f05WjSvWNoL1N6pdtt2NHuLEC5FNZm4eo/xiYueAVM8wTalQnD0PTSpH03b0Wr+VcHJt+Chlf2BfU/CTn87q3yErotBOmgVJjo9t3Y+dZW1tISC/b1aFqRccYcQCc4sK6l98j9WE19xMT0wMKeRB4B37oZ+igOPBcY1K7AZ/8BSIUSP/YgJZYhYbsFW9zgDgv2qVcX5OwWRdh0YQ== aegir@li184-53' >> /var/aegir/.ssh/authorized_keys", pty=True)
    fabric.run("chown -R aegir:aegir /var/aegir/.ssh", pty=True)
    fabric.run("chmod 644 /var/aegir/.ssh/authorized_keys", pty=True)
    fabric.run("chmod 700 /var/aegir/.ssh", pty=True)
    
    
def fab_slave(ip, user='root'):
    cm_libcloud.fabric_setup_ip(ip, user)
    
def fab_master(fqdn, user='root'):
    fabric.env.host_string = fqdn
    fabric.env.user = user
        
def setup_apache_slave(ip, port):
    print 'Setting up the apache Aegir slave.'
    fab_slave(ip)
    if 'aegir ALL=NOPASSWD: /usr/sbin/apache2ctl' not in fabric.run("cat /etc/sudoers", pty=True):
        fabric.run("echo 'aegir ALL=NOPASSWD: /usr/sbin/apache2ctl' >> /etc/sudoers", pty=True)
    
    if 'aegir.conf' not in fabric.run("ls /etc/apache2/conf.d/", pty=True):
        fabric.run("ln -s /var/aegir/config/apache.conf /etc/apache2/conf.d/aegir.conf", pty=True)
    
    fabric.run("echo 'Listen 8080' > /etc/apache2/ports.conf", pty=True)
    

def setup_mysql_slave(ip, master, port):
    print 'Setting up the MySQL Aegir slave.'
    fab_slave(ip)
    
    master_ip = socket.gethostbyname(master)
    
    root_password = cm_libcloud.gen_passwd(16)
    
    if 'root' not in fabric.run("echo \"SELECT User FROM mysql.user WHERE User = \'root\' AND Host = \'" + master_ip + "\';\" > /tmp/cmd && mysql -u root < /tmp/cmd", pty=True):
        fabric.run("echo \"CREATE USER \'root\'@\'" + master_ip + "\' IDENTIFIED BY \'" + root_password + "\';\" > /tmp/cmd && mysql -u root < /tmp/cmd", pty=True)
        fabric.run("echo \"GRANT ALL PRIVILEGES ON *.* TO \'root\'@\'" + master_ip + "\' WITH GRANT OPTION;\" > /tmp/cmd && mysql -u root < /tmp/cmd", pty=True)
    
    # Need some magic to get through iptables
    with fabric.settings(
        warn_only=True
    ):
        if 'tcp dpt:' + port not in fabric.run("iptables -L -n | grep '" + master_ip + "'", pty=True):
            fabric.run("iptables -I INPUT 8 -p tcp --dport " + port + " -s " + master_ip + " -j ACCEPT", pty=True)
            fabric.run("iptables-save > /etc/iptables.rules ", pty=True)
    
    if 'bind-address = ' + ip not in fabric.run("cat /etc/mysql/my.cnf", pty=True):
        fabric.run("echo '[mysqld]' >> /etc/mysql/my.cnf", pty=True)
        fabric.run("echo 'bind-address = " + ip + "' >> /etc/mysql/my.cnf", pty=True)
    
    print 'Restarting MySQL'
    fabric.run("service mysql restart", pty=True)
    
    return root_password
    
def add_aegir_slave(master_fqdn, slave_ip, apache_port=None, mysql_port=None, mysql_pass=None):

    fab_master(master_fqdn)
    with fabric.cd('/var/aegir/'):
        # We can't use fabric.sudo here unfortunately.
        fabric.run("su - -s /bin/sh aegir -c 'ssh -o StrictHostKeyChecking=no aegir@%s exit'" % (slave_ip), pty=True)
        # server_name is slave_ip without dots
        server_name = slave_ip.replace('.', '')
        fabric.run("su - -s /bin/sh aegir -c 'drush --remote_host=\'%s\' provision-save \'@server_%s\' --context_type=\'server\' --master_url=\'http://%s/\' --ip_addresses=%s'" % (slave_ip, server_name, master_fqdn, slave_ip), pty=True)
        if apache_port is not None:    
            fabric.run("su - -s /bin/sh aegir -c 'drush provision-save \'@server_%s\' --http_port=\'%s\' --http_service_type=\'apache\''" % (server_name, apache_port), pty=True)
        if mysql_port is not None:    
            fabric.run("su - -s /bin/sh aegir -c 'drush provision-save \'@server_%s\' --db_port=\'%s\' --db_service_type=\'mysql\' --master_db=\'mysql://root:%s@%s\''" % (server_name, mysql_port, mysql_pass, slave_ip), pty=True)
            
        fabric.run("su - -s /bin/sh aegir -c 'drush @hostmaster hosting-import \'@server_%s\''" % (server_name), pty=True)
        
    # TODO
    # Set the 'Friendly name' in Aegir somehow.
    print 'At the moment I can\'t set the friendly name of the Aegir server, so you will need to do it manually.'

if __name__ == "__main__":
    sys.exit(main())