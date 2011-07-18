#! /usr/bin/env python

import aegir_slave
import os, sys



if __name__ == "__main__":
    args = [
        'dummy',
        "--ip=" + os.environ['CM_SLAVE_IP'] + "",
        "--master=" + os.environ['CM_MASTER_FQDN'] + "",
        "--friendly_name=" + os.environ['CM_FRIENDLY_NAME'] + "",
        "--apache_port=" + os.environ['CM_APACHE_PORT'] + "",
        "--mysql_port=" + os.environ['CM_MYSQL_PORT'] + "",
    ]
    sys.exit(aegir_slave.main(args))

# ./cm_build_scripts/aegir_slave --ip='$CM_SLAVE_IP' --master='$CM_MASTER_FQDN' --friendly_name='$CM_FRIENDLY_NAME' --apache_port=$CM_APACHE_PORT  --apache_port=$CM_MYSQL_PORT
