#! /usr/bin/env python

import update_redmine
import os, sys

if __name__ == "__main__":
    args = [
        'dummy',
        "--db_password=" + os.environ['DB_PASSWORD'] + "",
        "--redmine_host=" + os.environ['REDMINE_HOST'] + "",
        "--release_tag=" + os.environ['RELEASE_TAG'] + "",
    ]
    if os.environ['INVALIDATE_SESSIONS'] == "yes":
        args.append("--invalidate_sessions")
    sys.exit(update_redmine.main(args))

# --size=$CM_SIZE --image=$CM_IMAGE --enable_apache=$CM_ENABLE_APACHE --enable_mysql=$CM_ENABLE_MYSQL --enable_jenkins=$CM_ENABLE_JENKINS --enable_memcache=$CM_ENABLE_MEMCACHE --enable_tomcat=$CM_ENABLE_TOMCAT
