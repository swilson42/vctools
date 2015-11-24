#!/usr/bin/python
# vim: expandtab shiftwidth=4 tabstop=4
"""Prompts for User Inputs"""
from __future__ import print_function
from pyVmomi import vim # pylint: disable=no-name-in-module
from vctools.query import Query
import os
import sys

class Prompts(object):
    """
    User prompts for selection configuration values.  It's best if these
    methods are configured as class methods
    """
    def __init__(self):
        pass

    @classmethod
    def name(cls):
        """ Returns string name. """
        return raw_input('Name: ')

    @classmethod
    def networks(cls, session, cluster):
        """
        Method will prompt user to select a networks. Since multiple networks
        can be added to a VM, it will prompt the user to exit or add more.
        The networks should be selected in the order of which they want the
        interfaces set on the VM. For example, the first network selected will
        be configured on eth0 on the VM.

        Args:
            session (obj): Auth session object
            cluster (str): Name of cluster

        Returns:
            selected_networks (list): A list of selected networks
        """
        clusters = Query.create_container(
            session, session.content.rootFolder, [vim.ComputeResource], True
        )
        cluster = Query.get_obj(clusters.view, cluster)
        networks = Query.list_obj_attrs(cluster.network, 'name', view=False)
        networks.sort()

        print('\n')
        print('%s Networks Found.\n' % (len(networks)))

        for num, opt in enumerate(networks, start=1):
            print('%s: %s' % (num, opt))

        selected_networks = []

        while True:
            if selected_networks:
                print('selected: ' + ','.join(selected_networks))

            val = raw_input(
                '\nPlease select number:\n(Q)uit (S)how Networks\n'
                ).strip()

            # need to test whether selection is an integer or not.
            try:
                if int(val) <= len(networks):
                    # need to substract 1 since we start enumeration at 1.
                    val = int(val) - 1
                    selected_networks.append(networks[val])
                    continue
                else:
                    print('Invalid number.')
                    continue
            except ValueError:
                if val == 'Q':
                    break
                elif val == 'S':
                    for num, opt in enumerate(networks, start=1):
                        print('%s: %s' % (num, opt))
                else:
                    print('Invalid option.')
                    continue

        return selected_networks


    @classmethod
    def datastores(cls, session, cluster):
        """
        Method will prompt user to select a datastore from a cluster

        Args:
            session (obj): Auth session object
            cluster (str): Name of cluster

        Returns:
            datastore (str): Name of selected datastore
        """
        clusters = Query.create_container(
            session, session.content.rootFolder, [vim.ComputeResource], True
        )
        datastores = Query.return_datastores(clusters.view, cluster)

        print('\n')
        if (len(datastores) -1) == 0:
            print('No Datastores Found.')
            sys.exit(1)
        else:
            print('%s Datastores Found.\n' % (len(datastores) - 1))

        for num, opt in enumerate(datastores):
            # the first item is the header information, so we will
            # not allow it as an option.
            if num == 0:
                print('\t%s' % (
                    # pylint: disable=star-args
                    '{0:30}\t{1:10}\t{2:10}\t{3:6}\t{4:10}\t{5:6}'.\
                        format(*opt)
                    )
                )
            else:
                print('%s: %s' % (
                    num,
                    # pylint: disable=star-args
                    '{0:30}\t{1:10}\t{2:10}\t{3:6}\t{4:10}\t{5:6}'.\
                        format(*opt)
                    )
                )

        while True:
            val = int(raw_input('\nPlease select number: ').strip())
            if val > 0 and val <= (len(datastores) - 1):
                break
            else:
                print('Invalid number')
                continue

        datastore = datastores[val][0]

        return datastore


    @classmethod
    def folders(cls, session, datacenter):
        """
        Method will prompt user to select a folder from a datacenter

        Args:
            session (obj):    Auth session object
            datacenter (str): Name of datacenter
        Returns:
            folder (str): Name of selected folder
        """
        datacenters = Query.create_container(
            session, session.content.rootFolder,
            [vim.Datacenter], True
        )
        folders = Query.list_vm_folders(
            datacenters.view, datacenter
        )
        folders.sort()

        for num, opt in enumerate(folders, start=1):
            print('%s: %s' % (num, opt))

        while True:
            val = int(raw_input('\nPlease select number: ').strip())
            if int(val) <= len(folders):
                # need to substract 1 since we start enumeration at 1.
                val = int(val) - 1
                selected_folder = folders[val]
                break
            else:
                print('Invalid number.')
                continue

        return selected_folder


    @classmethod
    def datacenters(cls, session):
        """
        Method will prompt user to select a datacenter

        Args:
            session (obj): Auth session object

        Returns:
            datacenter (str): Name of selected datacenter
        """
        datacenters_choices = Query.create_container(
            session, session.content.rootFolder,
            [vim.Datacenter], True
        )
        datacenters = Query.list_obj_attrs(datacenters_choices, 'name')
        datacenters.sort()

        for num, opt in enumerate(datacenters, start=1):
            print('%s: %s' % (num, opt))

        while True:
            val = int(raw_input('\nPlease select number: ').strip())
            if int(val) <= len(datacenters):
                # need to substract 1 since we start enumeration at 1.
                val = int(val) - 1
                selected_datacenter = datacenters[val]
                break
            else:
                print('Invalid number.')
                continue

        return selected_datacenter


    @classmethod
    def clusters(cls, session):
        """
        Method will prompt user to select a cluster

        Args:
            session (obj): Auth session object

        Returns:
            cluster (str): Name of selected cluster
        """
        clusters_choices = Query.create_container(
            session, session.content.rootFolder,
            [vim.ComputeResource], True
        )
        clusters = Query.list_obj_attrs(clusters_choices, 'name')
        clusters.sort()

        for num, opt in enumerate(clusters, start=1):
            print('%s: %s' % (num, opt))

        while True:
            val = int(raw_input('\nPlease select number: ').strip())
            if int(val) <= len(clusters):
                # need to substract 1 since we start enumeration at 1.
                val = int(val) - 1
                selected_cluster = clusters[val]
                break
            else:
                print('Invalid number.')
                continue

        return selected_cluster

