#! /usr/bin/env python

import aegir_slave
import os, sys



if __name__ == "__main__":
    args = [
        'dummy',
        "--master=" + os.environ['CM_MASTER_FQDN'] + "",
        "--friendly_name=" + os.environ['CM_FRIENDLY_NAME'] + "",
        "--apache_port=" + os.environ['CM_APACHE_PORT'] + "",
        "--mysql_port=" + os.environ['CM_MYSQL_PORT'] + "",
    ]

    # Read the IP address from the file.
    output_ip = os.environ['WORKSPACE'] + "/node_ip.output"
    if output_ip is not None:
            with open(output_ip, 'r') as f:
                ip = f.read
                args.append("--ip=" + ip)

    sys.exit(aegir_slave.main(args))

# ./cm_build_scripts/aegir_slave --ip='$CM_SLAVE_IP' --master='$CM_MASTER_FQDN' --friendly_name='$CM_FRIENDLY_NAME' --apache_port=$CM_APACHE_PORT  --apache_port=$CM_MYSQL_PORT
