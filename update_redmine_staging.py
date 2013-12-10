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
import datetime
from time import sleep

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

    logger('Downloading Redmine')
    fabric.run("cd /var/www && git clone git@github.com:computerminds/redmine.git redmine-staging-%s && cd redmine-staging-%s && git checkout %s && cd .." % (release_tag, release_tag, release_tag), pty=True)

    #logger('Stopping nginx server')
    #fabric.run("service nginx stop", pty=True)
    
    logger('Stopping thin')
    fabric.run("service thin-staging stop", pty=True)

    logger('Backing up MySQL')
    today = datetime.date.today()
    fabric.run("mysqldump -u root -p%s redmine_staging | gzip > /tmp/redmine_staging_%s.gz" % (db_password, today.strftime('%Y-%m-%d')), pty=True)

    logger('Copying files')
    fabric.run("rm -f /var/www/redmine-staging-%s/files/delete.me" % (release_tag), pty=True)
    fabric.run("cp -al /var/www/redmine-staging/files /var/www/redmine-staging-%s/" % (release_tag), pty=True)

    logger('Copying configuration')
    fabric.run("cp -f /var/www/redmine-staging/config/database.yml /var/www/redmine-staging-%s/config/" % (release_tag), pty=True)
    fabric.run("cp -f /var/www/redmine-staging/config/configuration.yml /var/www/redmine-staging-%s/config/" % (release_tag), pty=True)

    with fabric.cd("/var/www/redmine-staging-%s" % (release_tag)):
        logger('Running Redmine bundler')
        fabric.run("bundle install --without development test rmagick postgresql sqlite", pty=True)

        logger('Running Redmine migration')
        fabric.run("rake generate_secret_token", pty=True)

        fabric.run("rake db:migrate RAILS_ENV=production", pty=True)

        fabric.run("rake redmine:plugins:migrate RAILS_ENV=production", pty=True)

        logger('Cleaning up')
        fabric.run("rake tmp:cache:clear", pty=True)
        fabric.run("rake tmp:sessions:clear", pty=True)

    logger('Setting the new version of Redmine')
    with fabric.cd("/var/www"):
        fabric.run("rm redmine-staging", pty=True)
        fabric.run("ln -s redmine-staging-%s/ redmine-staging" % (release_tag), pty=True)


    logger('Starting thin')
    fabric.run("service thin-staging start", pty=True)
    
    logger('Waiting for thin to bootstrap Redmine...')
    sleep(15)

    logger('Restarting nginx server')
    fabric.run("service nginx restart", pty=True)


if __name__ == "__main__":
    sys.exit(main())
