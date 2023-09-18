#!/usr/bin/python

# Copyright: (c) 2018, Cloud Codger <cloud@codger.site>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: proxmox_group

short_description:
  - Proxmox Group management for Proxmox VE Datacenter

version_added: "1.0.0"

description:
  - Create or delete a group for Proxmox VE Datacenter.
  - Uses the proxmoxer openssh backend.
  - Deletes group even if users are assigned to the group.

options:
    group:
        aliases: [ 'name', 'groupid' ]
        description: The group name or groupid.
        required: true
        type: str
    comment:
        description: A description text for the group.
        required: false
        type: str
    state:
        description: The desired state of the group.
        choices: [ 'present', 'absent' ]
        default: present
        type: str

extends_documentation_fragment:
    - cloudcodger.proxmox_openssh.proxmox.documentation

author:
    - Cloud Codger (@cloudcodger) <cloud@codger.site>
'''

EXAMPLES = r'''
- name: "Create Admin group."
  cloudcodger.proxmox_openssh.proxmox_group:
    api_host: "pve1"
    api_user: "root"
    group: "Admin"
    state: present

- name: "Create Admin group with a comment."
  cloudcodger.proxmox_openssh.proxmox_group:
    api_host: "192.168.1.21"
    api_user: "root"
    group: "Admin"
    comment: "Administrator users group"
    state: present

- name: "Delete Admin group."
  cloudcodger.proxmox_openssh.proxmox_group:
    api_host: "pve1"
    api_user: "root"
    group: "Admin"
    state: absent
'''

RETURN = r'''
group_id:
    description: The group ID.
    returned: success
    type: str
    sample: 'Admin'
msg:
    description: A short message on what the module did.
    returned: always
    type: str
    sample: "Group Admin successfully created"
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cloudcodger.proxmox_openssh.plugins.module_utils.proxmox_openssh import (ProxmoxOpenSSHAnsible, proxmox_openssh_argument_spec)

class ProxmoxOpenSSHGroupAnsible(ProxmoxOpenSSHAnsible):

    def get(self, groupid):
        """
        Get group info

        :param groupid: str - name of the group
        :return: dict - group info
        """
        try:
            return self.proxmox_api.access.groups.get(groupid)
        except Exception as e:
            self.module.fail_json(msg="Failed to get group with ID {0}: {1}".format(groupid, e))

    def exists(self, groupid):
        """
        Check if the group exists

        :param groupid: str - name of the group
        :return: bool - if the group exists
        """
        for group in self.get_groups():
            if group['groupid'] == groupid:
                return True
        return False

    def is_empty(self, groupid):
        """
        Check whether group has users

        :param groupid: str - name of the group
        :return: bool - if the group is empty
        """
        return True if not self.get(groupid)['members'] else False

    def create(self, groupid, comment=None):
        """
        Create group

        :param groupid: str - name of the group
        :param comment: str
        :return: None
        """
        if self.exists(groupid):
            self.module.exit_json(changed=False, groupid=groupid, msg="Group {0} exists".format(groupid))

        if self.module.check_mode:
            return

        try:
            self.proxmox_api.access.groups.create(groupid=groupid, comment=comment)
        except Exception as e:
            self.module.fail_json(msg="Failed to create group with ID {0}: {1}".format(groupid, e))

    def delete(self, groupid):
        """
        Delete group

        :param groupid: str - name of the group
        :return: None
        """
        if not self.exists(groupid):
            self.module.exit_json(changed=False, groupid=groupid, msg="Group {0} doesn't exist".format(groupid))

        if self.module.check_mode:
            return

        try:
            self.proxmox_api.access.groups.delete(groupid)
        except Exception as e:
            self.module.fail_json(msg="Failed to delete group with ID {0}: {1}".format(groupid, e))

def main():

    module_args = proxmox_openssh_argument_spec()
    group_args = dict(
        groupid=dict(type='str', aliases=['group', 'name'], required=True),
        comment=dict(type="str"),
        state=dict(type='str', choices=['present', 'absent'], default='present'),
    )
    module_args.update(group_args)

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    proxmox_group = ProxmoxOpenSSHGroupAnsible(module)
    comment = module.params['comment']
    groupid = module.params['groupid']
    state = module.params['state']

    if state == 'present':
        proxmox_group.create(groupid, comment)
        module.exit_json(changed=True, groupid=groupid, msg="Group {0} successfully created".format(groupid))
    else:
        proxmox_group.delete(groupid)
        module.exit_json(changed=True, groupid=groupid, msg="Group {0} successfully deleted".format(groupid))

if __name__ == '__main__':

    main()
