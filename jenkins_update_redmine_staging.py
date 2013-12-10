#! /usr/bin/env python

import update_redmine_staging
import os, sys

if __name__ == "__main__":
    args = [
        'dummy',
        "--db_password=" + os.environ['DB_PASSWORD'] + "",
        "--redmine_host=" + os.environ['REDMINE_HOST'] + "",
        "--release_tag=" + os.environ['RELEASE_TAG'] + "",
    ]
    sys.exit(update_redmine_staging.main(args))

