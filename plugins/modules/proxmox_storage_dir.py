#!/usr/bin/python

# Copyright: (c) 2018, Cloud Codger <cloud@codger.site>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: proxmox_storage_dir

short_description:
  - Proxmox VE Datacenter Storage management for directory type

version_added: "1.0.0"

description:
  - Manage directory type Storage for Proxmox VE Datacenter.
  - Uses proxmoxer openssh backend.

options:
    storage:
        aliases: [ 'name', 'storageid' ]
        description: The Storage ID (for example, local).
        required: true
        type: str
    content:
        description: Comma seperated list of content types.
        default: 'images'
        type: str
    path:
        description:
        - File system path.
        - Required if I(state=present).
        type: str
    shared:
        description: Mark storage as shared.
        default: False
        type: bool
    state:
        description: The desired state of the storage.
        choices: [ 'present', 'absent' ]
        default: present
        type: str

extends_documentation_fragment:
    - cloudcodger.proxmox_openssh.proxmox.documentation

author:
    - Cloud Codger (@cloudcodger) <cloud@codger.site>
'''

EXAMPLES = r'''
- name: "Create local-tst storage."
  cloudcodger.proxmox_openssh.proxmox_storage_dir:
    api_host: "pve1"
    api_user: "root"
    path: "/var/lib/tst"
    storage: "local-tst"
    state: present

- name: "Create local-ci storage with images,iso content."
  cloudcodger.proxmox_openssh.proxmox_storage_dir:
    api_host: "192.168.1.51"
    api_user: "root"
    content: "images,iso"
    path: "/var/lib/ci"
    storage: "local-ci"
    state: present

- name: "Create special shared configs storage for SMALL snippets content."
  cloudcodger.proxmox_openssh.proxmox_storage_dir:
    api_host: "pve1"
    api_user: "root"
    content: "snippets"
    path: "/etc/pve/configs"
    shared: true
    storage: "shared"
    state: present

- name: "Delete the test storage."
  cloudcodger.proxmox_openssh.proxmox_storage_dir:
    api_host: "pve1"
    api_user: "root"
    storage: "test"
    state: absent
'''

RETURN = r'''
storage_content:
    description: The storage content allowed.
    returned: success i(state=present)
    type: str
    sample: 'images,iso'
storage_id:
    description: The storage ID.
    returned: success
    type: str
    sample: 'local-ci'
msg:
    description: A short message on what the module did.
    returned: always
    type: str
    sample: "Storage {name} successfully created"
'''

import traceback

# from ansible_collections.community.general.plugins.module_utils.proxmox import (ansible_to_proxmox_bool, proxmox_to_ansible_bool)
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cloudcodger.proxmox_openssh.plugins.module_utils.proxmox_openssh import (ProxmoxOpenSSHAnsible, proxmox_openssh_argument_spec)

class ProxmoxOpenSSHStorageDirectoryAnsible(ProxmoxOpenSSHAnsible):
    def get(self, storageid):
        """
        Get directory type storage info

        :param storageid: str - name of the directory type storage
        :return: dict - storage info
        """
        try:
            return self.proxmox_api.storage.get(storageid)
        except Exception as e:
            self.module.fail_json(msg="Failed to get directory type storage with ID {0}: {1}".format(storageid, e))

    def exists(self, storageid):
        """
        Check if the storage exists

        :param storageid: str - name of the directory type storage
        :return: bool - if the storage exists
        """
        for storage in self.get_storages(type='dir'):
            if storage['storage'] == storageid:
                return True
        return False

    def create(self, storageid, path, content=None, shared=False):
        """
        Create a directory type storage

        :param storageid: str - name of the directory type storage
        :param path: str - file system path
        :param content: str - comma seperated list of allowed content types
        :param shared: bool - mark the storage as shared
        :return: None
        """
        if self.exists(storageid):
            storage_item = self.get(storageid)
            if content is not None and not set(storage_item['content']) == set(content):
                self.proxmox_api.storage(storageid).set(content=content)
                return
            if storage_item['shared'] | bool != shared:
                self.proxmox_api.storage(storageid).set(shared=shared)
                return
            self.module.exit_json(changed=False, storage_id=storageid, storage_content=content, msg="Storage {0} exists".format(storageid))

        if self.module.check_mode:
            return

        try:
            self.proxmox_api.storage.create(storage=storageid, type='dir', path=path, content=content, shared=shared)
        except Exception as e:
            self.module.fail_json(msg="Failed to create storage with ID {0} and path {1}: {2}".format(storageid, path, e))

    def delete(self, storageid):
        """
        Delete directory type storage

        :param storageid: str - name of the directory type storage
        :return: None
        """
        if not self.exists(storageid):
            self.module.exit_json(changed=False, storage_id=storageid, msg="storage {0} doesn't exist".format(storageid))

        if self.module.check_mode:
            return

        try:
            self.proxmox_api.storage.delete(storageid)
        except Exception as e:
            self.module.fail_json(msg="Failed to delete directory type storage with ID {0}: {1}".format(storageid, e))

def main():
    module_args = proxmox_openssh_argument_spec()
    storage_args = dict(
        storageid=dict(type='str', aliases=['storage', 'name'], required=True),
        content=dict(type='str', default='images'),
        path=dict(type='str'),
        shared=dict(type="bool", default=False),
        state=dict(type='str', choices=['present', 'absent'], default='present'),
    )
    module_args.update(storage_args)

    module = AnsibleModule(
        argument_spec=module_args,
        required_if=[
            ('state', 'present', ('path'))
        ]
        supports_check_mode=True
    )

    proxmox_storage = ProxmoxOpenSSHStorageDirectoryAnsible(module)
    content = module.params['content'].lower()
    path = module.params['path']
    shared = module.params['shared']
    storageid = module.params['storageid']
    state = module.params['state']

    if state == 'present':
        proxmox_storage.create(storageid, path, content, shared)
        module.exit_json(changed=True, storage_id=storageid, storage_content=content, msg="Storage {0} successfully created".format(storageid))
    else:
        proxmox_storage.delete(storageid)
        module.exit_json(changed=True, storage_id=storageid, msg="Storage {0} successfully deleted".format(storageid))

if __name__ == '__main__':
    main()
