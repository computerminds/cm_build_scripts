#! /usr/bin/env python

"""Update Redmine script

Updates the Computerminds instance of Redmine

Valid options:
  --db_password - The database password to use.
  --redmine_host - The Redmine server to connect to.
  --release_tag - The redmine version to checkout.
"""

import sys, getopt
import fabric.api as fabric

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "h", ["help", "db_password=", "redmine_host=", "release_tag="])
        except getopt.error, msg:
             raise Usage(msg)
        # process options
        db_password = None
        redmine_host = None
        release_tag = None

        for o, a in opts:
            if o in ("-h", "--help"):
                print __doc__
                return 0;
            if o in ("--db_password"):
                db_password = a
            if o in ("--redmine_host"):
                redmine_host = a
            if o in ("--release_tag"):
                release_tag = a

        if db_password is None:
            raise Usage, "the --db_password option must be specified"
        if redmine_host is None:
            raise Usage, "the --redmine_host option must be specified"
        if release_tag is None:
            raise Usage, "the --release_tag option must be specified"

        update_redmine(db_password, redmine_host, release_tag)

        return 0

    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2

def logger(message):
    print ("===> %s" % message)

def update_redmine(db_password = None, redmine_host = None, release_tag = None):

    # Connect to the aegir host.
    fabric.env.host_string = redmine_host
    fabric.env.user = 'root'

    logger('Stopping apache server')
    fabric.run("/etc/init.d/apache2 stop", pty=True)

    logger('Backing up MySQL')
    fabric.run("mysql -u root -p%s redmine | gzip > /tmp/redmine_`date +%y_%m_%d`.gz" % (), pty=True)

    logger('Downloading Redmine')
    fabric.run("cd /var/www/support && git clone https://github.com/redmine/redmine.git redmine-%s && cd redmine-%s && git checkout %s" % (release_tag, release_tag, release_tag), pty=True)

    logger('Restarting thin')
    fabric.run("/etc/init.d/thin restart", pty=True)

    logger('Starting apache server')
    fabric.run("/etc/init.d/apache2 start", pty=True)


if __name__ == "__main__":
    sys.exit(main())
