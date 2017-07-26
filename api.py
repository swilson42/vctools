#!/usr/bin/python
# vim: et ts=4 sw=4
""" An API for curl enthusiasts."""
from __future__ import print_function
import os
import subprocess
import textwrap
from flask import Flask, request
#
from vctools.query import Query

api = Flask(__name__)
# allow trailing slash or not
api.url_map.strict_slashes = False

@api.route('/')
def root():
    """
    vctools API

    GET /api/<command> Returns information on how to use command.

    command:
        create        Create a new virtual machine
        mkbootiso     Create a boot.iso on a per server basis.
        mount         Mount an iso on a virtual machine.
        power         Configure power state for virtual machine.
        reconfig      Reconfigure attributes on an existing virtual machine.
        umount        Unmount an iso on a virtual machine.
        upload        Upload a boot.iso to a remote datastore.

    """
    return textwrap.dedent(root.__doc__)

@api.route('/mkbootiso', methods=['GET', 'POST'])
def mkbootiso():
    """
    POST /api/mkbootiso <json>

    Create ISOs on remote server.

    This route supports basic Anaconda configuration options to create an ISO with specific network
    information. This information can be used for automating server installations with static IPs.

    Dependencies:

        python 2.7+
        genisoimage

    Preparation:

        Download an ISO from a vendor that supports Anaconda.

        Mount it using the loop option:

            mount -o loop rhel-server-7.2-x86_64-boot.iso /mnt/tmp/rhel7/

        Copy necessary contents to a folder. In this example, only isolinux/ is needed. Copying only
        mandatory files will keep the size down to save bandwidth and disk space.

            cp -a /mnt/tmp/rhel7/isolinux/ /opt/isos/rhel7/

    Permissions:

        The Apache user should have write permissions to files inside isolinux/, and write
        permissions to the output directories.

    Example:

        curl -i -k -H "Content-Type: application/json" -X POST \\
        https://hostname.domain.com/api/mkbootiso \\
        -d @- << EOF
            {
                "source" : "/opt/isos/rhel7",
                "ks" : "http://ks.domain.com/rhel7-ks.cfg",
                "options" : {
                    "biosdevname" : "0",
                    "gateway" : "10.10.10.1",
                    "hostname" : "hostname.domain.com",
                    "ip" : "10.10.10.10",
                    "nameserver" : "4.2.2.2",
                    "net.ifnames" : "0",
                    "netmask" : "255.255.255.0"
                },
                "output": "/tmp"
            }
        EOF
    """

    if request.method == 'GET':
        return textwrap.dedent(mkbootiso.__doc__)

    if request.method == 'POST':
        data = request.get_json()

        label = """
            default vesamenu.c32
            display boot.msg
            timeout 5
            label iso created by {0}
            menu default
            kernel vmlinuz
            append initrd=initrd.img {1} {2}

            """.format(__name__, 'ks=' + data['ks'],
                   ' '.join("%s=%s" % (key, val) for (key, val) in data['options'].iteritems()))

        # update the iso
        with open(data['source'] + '/isolinux/isolinux.cfg', 'w') as iso_cfg:
            iso_cfg.write(textwrap.dedent(label))

        cmd = """
              /usr/bin/genisoimage -quiet -J -T -o {0} -b isolinux/isolinux.bin
              -c isolinux/boot.cat -no-emul-boot -boot-load-size 4 -boot-info-table -R
              -m TRANS.TBL -graft-points {1}""".format(
                  data['output'] + '/' + data['options']['hostname'] + '.iso', data['source']
        )

        # create the iso
        create_iso = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, shell=False)
        stdout, stderr = create_iso.communicate()

        if stdout:
            api.logger.info(stdout)

        if stderr:
            api.logger.error(stderr)

        if create_iso.returncode == 0:
            iso_size = Query.disk_size_format(
                os.stat(data['output'] + '/' + data['options']['hostname'] + '.iso').st_size
            )

            return '{0} {1}\n'.format(
                data['output'] + '/' + data['options']['hostname'] + '.iso', iso_size
            )


if __name__ == '__main__':
    api.run(threaded=True)
