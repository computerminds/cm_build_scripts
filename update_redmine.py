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
    fabric.local("rm -rf redmine && git clone git://github.com/redmine/redmine.git redmine && cd redmine && git checkout %s && cd .." % (release_tag), True)
    fabric.local("rsync -Pvr redmine root@%s:/var/www/support/redmine-%s" % (redmine_host, release_tag), True)

    logger('Stopping apache server')
    fabric.run("/etc/init.d/apache2 stop", pty=True)

    logger('Backing up MySQL')
    today = datetime.date.today()
    fabric.run("mysqldump -u redmine -p%s redmine | gzip > /tmp/redmine_%s.gz" % (db_password, today.strftime('%Y-%m-%d')), pty=True)


    logger('Copying config')
    fabric.run("cp /var/www/support/redmine/config/database.yml /var/www/support/redmine-%s/config/database.yml" % (release_tag), pty=True)
    fabric.run("cp /var/www/support/redmine/config/configuration.yml /var/www/support/redmine-%s/config/configuration.yml" % (release_tag), pty=True)
    fabric.run("cp /var/www/support/redmine/config/environments/production_sync.rb /var/www/support/redmine-%s/config/environments/production_sync.rb" % (release_tag), pty=True)

    logger('Copying files')
    fabric.run("rsync -aH /var/www/support/redmine/files /var/www/support/redmine-%s/" % (release_tag), pty=True)

    logger('Copying custom plugins')
    fabric.run("rsync -aH /var/www/support/redmine/vendor/plugins/action_mailer_optional_tls /var/www/support/redmine-%s/vendor/plugins/" % (release_tag), pty=True)

    logger('Copying custom themes')
    fabric.run("rsync -aH /var/www/support/redmine/public/themes/modula-mojito /var/www/support/redmine-%s/public/themes/" % (release_tag), pty=True)

    with fabric.cd("/var/www/support/redmine-%s" % (release_tag)):
        logger('Running Redmine bundler')
        fabric.run("bundle install --without development test rmagick postgresql", pty=True)

        logger('Running Redmine migration')
        fabric.run("rake generate_session_store", pty=True)

        fabric.run("rake db:migrate RAILS_ENV=production", pty=True)

        fabric.run("rake db:migrate_plugins RAILS_ENV=production", pty=True)

        logger('Cleaning up')
        fabric.run("rake tmp:cache:clear", pty=True)
        fabric.run("rake tmp:sessions:clear", pty=True)

    logger('Setting the new version of Redmine')
    with fabric.cd("/var/www/support"):
        fabric.run("ln -sf redmine-%s/ redmine" % (release_tag), pty=True)


    logger('Restarting thin')
    fabric.run("/etc/init.d/thin restart", pty=True)

    logger('Starting apache server')
    fabric.run("/etc/init.d/apache2 start", pty=True)


if __name__ == "__main__":
    sys.exit(main())
