#!/usr/bin/python
"""Query class for vctools.  All methods that obtain info should go here."""
from __future__ import division
from __future__ import print_function

class Query(object):
    """
    Class handles queries for information regarding for vms, datastores
    and networks.
    """
    def __init__(self):
        self.datastore_info = None


    @classmethod
    def disk_size_format(cls, num):
        """Method converts datastore size in bytes to human readable format."""

        for attr in ['bytes', 'KB', 'MB', 'GB', 'TB']:
            if num < 1024.0:
                return '%3.2f %s' % (num, attr)
            num /= 1024.0


    @classmethod
    def create_container(cls, s_instance, *args):
        """
        Wrapper method for creating managed objects inside vim.view.ViewManager.

        """
        if hasattr(s_instance, 'content'):
            if hasattr(s_instance.content, 'viewManager'):
                return s_instance.content.viewManager.CreateContainerView(*args)
            else:
                raise Exception
        else:
            raise Exception


    @classmethod
    def get_obj(cls, container, name):
        """
        Returns an object inside of ContainerView if it matches name.

        """

        for obj in container:
            if obj.name == name:
                return obj


    @classmethod
    def list_obj_attrs(cls, container, attr, view=True):
        """
        Returns a list of attributes inside of container.

        """
        if view:
            return [getattr(obj, attr) for obj in container.view]
        else:
            return [getattr(obj, attr) for obj in container]


    def folders_lookup(self, container, datacenter, name):
        """
        Returns the object for a folder name.  Currently, it only searches for
        the folder through one level of subfolders. This method is needed for
        building new virtual machines.

        """
        obj = self.get_obj(container, datacenter)

        if hasattr(obj, 'vmFolder'):
            for folder in obj.vmFolder.childEntity:
                if hasattr(folder, 'childType'):
                    if folder.name == name:
                        return folder
                if hasattr(folder, 'childEntity'):
                    for item in folder.childEntity:
                        if hasattr(item, 'childType'):
                            if item.name == name:
                                return item

    def list_vm_folders(self, container, datacenter):
        """
        Returns a list of Virtual Machine folders.  Sub folders will be listed
        with its parent -> subfolder. Currently it only searches for one
        level of subfolders.

        """
        obj = self.get_obj(container, datacenter)
        folders = []

        if hasattr(obj, 'vmFolder'):
            for folder in obj.vmFolder.childEntity:
                if hasattr(folder, 'childType'):
                    folders.append(folder.name)
                if hasattr(folder, 'childEntity'):
                    for item in folder.childEntity:
                        if hasattr(item, 'childType'):
                            folders.append(item.parent.name+' -> '+item.name)
        return folders


    def datastore_most_space(self, container, cluster):
        """Attempts to find the datastore with the most free space."""
        obj = self.get_obj(container, cluster)
        datastores = {}
        for datastore in obj.datastore:
            # if datastore is a VMware File System
            if datastore.summary.type == 'VMFS':
                free = int(datastore.summary.freeSpace)
                datastores.update({datastore.name:free})


        most = max(datastores.itervalues())
        for key, value in datastores.iteritems():
            if value == most:
                print(key)


    # pylint: disable=too-many-locals
    def return_datastores(self, container, cluster, header=True):
        """
        Returns a summary of disk space for datastores listed inside a
        cluster. Identical to list_datastore_info, but returns the datastores
        as an list object instead of printing them to stdout.
        """

        obj = self.get_obj(container, cluster)

        self.datastore_info = []

        if header:
            header = [
            'Datastore', 'Capacity', 'Provisioned', 'Pct', 'Free Space', 'Pct'
            ]
            self.datastore_info.append(header)

        for datastore in obj.datastore:
            info = []
            # type is long(bytes)
            free = int(datastore.summary.freeSpace)
            capacity = int(datastore.summary.capacity)

            # uncommitted is sometimes None, so we'll convert that to 0.
            if not datastore.summary.uncommitted:
                uncommitted = int(0)
            else:
                uncommitted = int(datastore.summary.uncommitted)

            provisioned = int((capacity - free) + uncommitted)

            provisioned_pct = '{0:.2%}'.format((provisioned / capacity))
            free_pct = '{0:.2%}'.format((free / capacity))

            info.append(datastore.name)
            info.append(self.disk_size_format(capacity))
            info.append(self.disk_size_format(provisioned))
            info.append(provisioned_pct)
            info.append(self.disk_size_format(free))
            info.append(free_pct)

            self.datastore_info.append(info)


        # sort by datastore name
        self.datastore_info.sort(key=lambda x: x[0])

        return self.datastore_info


    def list_vm_info(self, container, datacenter):
        """
        Returns a list of names for VMs located inside a datacenter.

        """

        obj = self.get_obj(container, datacenter)

        vms = {}

        # recurse through datacenter object attributes looking for vms.
        if hasattr(obj, 'vmFolder'):
            for virtmachine in obj.vmFolder.childEntity:
                # pylint: disable=protected-access
                if hasattr(virtmachine, 'childEntity'):
                    for virt in virtmachine.childEntity:
                        vms.update({virt.name:virt._moId})
                else:
                    vms.update({virtmachine.name:virt._moId})

        return vms


    def get_vmid_by_name(self, container, datacenter, name):
        """
        Returns the moId of matched name

        """

        obj = self.get_obj(container, datacenter)

        # recurse through datacenter object attributes looking for vm that
        # matches hostname.
        if hasattr(obj, 'vmFolder'):
            for virtmachine in obj.vmFolder.childEntity:
                # pylint: disable=protected-access
                if hasattr(virtmachine, 'childEntity'):
                    for virt in virtmachine.childEntity:
                        if virt.name == name:
                            return virt._moId
                else:
                    if virt.name == name:
                        return virt._moId

