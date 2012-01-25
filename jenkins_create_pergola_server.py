#! /usr/bin/env python

import create_pergola_server
import os, sys



if __name__ == "__main__":
    args = [
        'dummy',
        "--size=" + os.environ['CM_SIZE'] + "",
        "--image=" + os.environ['CM_IMAGE'] + "",
        "--branch=" + os.environ['PERGOLA_BRANCH'] + "",
        "--output_ip=" + os.environ['WORKSPACE'] + "/node_ip.output",
    ]
    sys.exit(create_pergola_server.main(args))

# --size=$CM_SIZE --image=$CM_IMAGE --enable_apache=$CM_ENABLE_APACHE --enable_mysql=$CM_ENABLE_MYSQL --enable_jenkins=$CM_ENABLE_JENKINS --enable_memcache=$CM_ENABLE_MEMCACHE --enable_tomcat=$CM_ENABLE_TOMCAT
