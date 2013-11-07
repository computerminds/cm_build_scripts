#!/bin/sh -ex

# curl -L https://raw.github.com/computerminds/cm_build_scripts/master/install-puppet.sh | sh

# Add the puppet repo.

wget http://apt.puppetlabs.com/puppetlabs-release-precise.deb
dpkg -i puppetlabs-release-precise.deb
rm puppetlabs-release-precise.deb
apt-get update

# Install puppet
apt-get install puppet

# Configure puppet
echo "" > /etc/puppet/puppet.conf
echo "[main]" >> /etc/puppet/puppet.conf
echo "    logdir=/var/log/puppet" >> /etc/puppet/puppet.conf
echo "    vardir=/var/lib/puppet" >> /etc/puppet/puppet.conf
echo "    ssldir=/var/lib/puppet/ssl" >> /etc/puppet/puppet.conf
echo "    rundir=/var/run/puppet" >> /etc/puppet/puppet.conf
echo "    factpath=$vardir/lib/facter" >> /etc/puppet/puppet.conf
echo "    templatedir=$confdir/templates" >> /etc/puppet/puppet.conf
echo "" >> /etc/puppet/puppet.conf
echo "    [master]" >> /etc/puppet/puppet.conf
echo "    # These are needed when the puppetmaster is run by passenger" >> /etc/puppet/puppet.conf
echo "    # and can safely be removed if webrick is used." >> /etc/puppet/puppet.conf
echo "    ssl_client_header = SSL_CLIENT_S_DN" >> /etc/puppet/puppet.conf
echo "    ssl_client_verify_header = SSL_CLIENT_VERIFY" >> /etc/puppet/puppet.conf
echo "" >> /etc/puppet/puppet.conf
echo "    [agent]" >> /etc/puppet/puppet.conf
echo "    server = puppetmaster.computerminds.co.uk" >> /etc/puppet/puppet.conf
echo "    report = true" >> /etc/puppet/puppet.conf
echo "    pluginsync = true" >> /etc/puppet/puppet.conf
echo "" >> /etc/puppet/puppet.conf

# Enable puppet
echo 'START=yes' >> /etc/default/puppet

# Start puppet
service puppet start
