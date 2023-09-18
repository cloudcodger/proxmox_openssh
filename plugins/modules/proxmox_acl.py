#!/usr/bin/python

# Copyright: (c) 2018, Cloud Codger <cloud@codger.site>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: proxmox_acl

short_description:
  - Proxmox Access Control List (ACL) management for Proxmox VE Datacenter

version_added: "1.0.0"

description:
  - Create or delete ACL (permissions) for Proxmox VE Datacenter.
  - Uses the proxmoxer openssh backend.
  - Requires one of groups, tokens, and/or users.

options:
    path:
        description: The access control path.
        required: true
        type: str
    roleid:
        description: The permissions role.
        required: true
        type: str
    groups:
        description: Comma separated list of groups.
        required: false
        type: str
    tokens:
        description: Comma separated list of API tokens.
        required: false
        type: str
    users:
        description: Comma separated list of users.
        required: false
        type: str
    propagate:
        description: Allow to propagate (inherit) permissions.
        required: false
        type: bool
        default: True
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
# Create a Proxmox VE Datacenter Permissions Access Control List (ACL)
- name: "Create ACL for Administrator role with path / for the Admin group."
  cloudcodger.proxmox_openssh.proxmox_acl:
    api_host: "pve1"
    api_user: "root"
    path: "/"
    roles: ["Administrator"]
    groups: ["Admin"]
    state: present

- name: "Create ACL for Administrator role with path / for the Admin group and the devops@pve user."
  cloudcodger.proxmox_openssh.proxmox_acl:
    api_host: "192.168.1.21"
    api_user: "root"
    path: "/"
    roles: ["Administrator"]
    groups: ["Admin"]
    users: ["devops@pve"]
    state: present

- name: "Delete ACL for Administrator role with path / for the Admin group."
  cloudcodger.proxmox_openssh.proxmox_acl:
    api_host: "pve1"
    api_user: "root"
    path: "/"
    roles: ["Administrator"]
    groups: ["Admin"]
    state: absent
'''

RETURN = r'''
acl_path:
    description: The path for the ACL.
    returned: success i(state=present)
    type: str
    sample: '/'
roleid:
    description: The role for the ACL.
    returned: success i(state=present)
    type: str
    sample: 'Administrator'
removed_acls:
    description: A list of dicts for the ACLs removed.
    returned: success i(state=absent)
    type: list
    sample: '[{"path": "/", "propagate": 1, "roleid": "Administrator", "type": "user", "ugid": "devops@pve"}]'
msg:
    description: A short message on what the module did.
    returned: always
    type: str
    sample: "Group Admin successfully created"
'''

import re
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cloudcodger.proxmox_openssh.plugins.module_utils.proxmox_openssh import (ProxmoxOpenSSHAnsible, proxmox_openssh_argument_spec)

class ProxmoxOpenSSHACLAnsible(ProxmoxOpenSSHAnsible):

    def all_exist(self, path, roleid, **kwargs):
        """
        Check if all the ACLs for a path and roleid for specified groups, tokens, and users exist

        :param path: str - the access control path
        :param roleid: str - name of the role
        :param propagate: bool - allow to propagate (inherit) permissions
        :param groups: str - comman seperated list of group names
        :param tokens: str - comman seperated list of tokens as user@real!token
        :param users: str - comman seperated list of users as user@real
        :return: bool - if the ACLs exist for all groups, tokens and users
        """
        current_acls = self.proxmox_api.access.acl.get()
        if not current_acls:
            return False

        matching_groups = []
        matching_tokens = []
        matching_users = []

        for acl in current_acls:
            if acl['path'] != path:
                continue
            if acl['propagate'] != kwargs['propagate']:
                continue
            if acl['roleid'] != roleid:
                continue
            if acl['type'] == 'group':
                matching_groups.append(acl['ugid'])
            if acl['type'] == 'token':
                matching_tokens.append(acl['ugid'])
            if acl['type'] == 'user':
                matching_users.append(acl['ugid'])

        if 'groups' in kwargs and kwargs['groups']:
            if not matching_groups:
                return False
            for ugid in re.split(r'[, ]+', kwargs['groups']):
                if ugid not in matching_groups:
                    return False

        if 'tokens' in kwargs and kwargs['tokens']:
            if not matching_tokens:
                return False
            for ugid in re.split(r'[, ]+', kwargs['tokens']):
                if ugid not in matching_tokens:
                    return False

        if 'users' in kwargs and kwargs['users']:
            if not matching_users:
                return False
            for ugid in re.split(r'[, ]+', kwargs['users']):
                if ugid not in matching_users:
                    return False

        return True

    def matching_acls(self, path, roleid, **kwargs):
        """
        Check if all the ACLs for a path and roleid for specified groups, tokens, and users exist

        :param path: str - the access control path
        :param roleid: str - name of the role
        :param groups: str - comman seperated list of group names
        :param tokens: str - comman seperated list of tokens as user@real!token
        :param users: str - comman seperated list of users as user@real
        :return: list - a list of matching ACLs
        """
        matched_acls = []

        current_acls = self.proxmox_api.access.acl.get()
        if not current_acls:
            self.module.exit_json(changed=False, msg="No ACLs exist.")

        for acl in current_acls:
            if acl['path'] != path or acl['roleid'] != roleid:
                continue
            if acl['type'] == 'group' and 'groups' in kwargs and kwargs['groups']:
                for ugid in re.split(r'[, ]+', kwargs['groups']):
                    if acl['ugid'] == ugid:
                        matched_acls.append({'path': path, 'roleid': roleid, 'propagate': acl['propagate'], 'type': 'group', 'ugid': ugid})
            if acl['type'] == 'token' and 'tokens' in kwargs and kwargs['tokens']:
                for ugid in re.split(r'[, ]+', kwargs['tokens']):
                    if acl['ugid'] == ugid:
                        matched_acls.append({'path': path, 'roleid': roleid, 'propagate': acl['propagate'], 'type': 'token', 'ugid': ugid})
            if acl['type'] == 'user' and 'users' in kwargs and kwargs['users']:
                for ugid in re.split(r'[, ]+', kwargs['users']):
                    if acl['ugid'] == ugid:
                        matched_acls.append({'path': path, 'roleid': roleid, 'propagate': acl['propagate'], 'type': 'user', 'ugid': ugid})

        return matched_acls

    def group_acl_exists(self, path, roleid, groupid):
        """
        Check if the ACL for a group exists

        :param path: str - the access control path
        :param roleid: str - name of the role
        :param groupid: str - name of the group
        :return: bool - if the acl exists
        """
        for item in self.proxmox_api.access.acl.get():
            if item['path'] == path and item['roleid'] == roleid and item['type'] == "group" and item['ugid'] == groupid:
                return True
        return False

    def token_acl_exists(self, path, roleid, tokenid):
        """
        Check if the ACL for a token exists

        :param path: str - the access control path
        :param roleid: str - name of the role
        :param tokenid: str - name of the token
        :return: bool - if the acl exists
        """
        for item in self.proxmox_api.access.acl.get():
            if item['path'] == path and item['roleid'] == roleid and item['type'] == "token" and item['ugid'] == tokenid:
                return True
        return False

    def user_acl_exists(self, path, roleid, userid):
        """
        Check if the ACL for a user exists

        :param path: str - the access control path
        :param roleid: str - name of the role
        :param userid: str - name of the user
        :return: bool - if the acl exists
        """
        for item in self.proxmox_api.access.acl.get():
            if item['path'] == path and item['roleid'] == roleid and item['type'] == "user" and item['ugid'] == userid:
                return True
        return False

    def create(self, path, roleid, **kwargs):
        """
        Create permissions ACLs

        :param path: str - the access control path
        :param roleid: str - name of the role
        :param groups: str - list of the group names
        :param tokens: str - list of the tokens as user@realm!token
        :param users: str - list of the users as user@realm
        :param propagate: bool
        :return: None
        """
        if self.all_exist(path, roleid, **kwargs):
            self.module.exit_json(changed=False, roleid=roleid, msg="All requested ACLs for path '{0}' and roleid '{1}' exist".format(path, roleid))

        if self.module.check_mode:
            return

        try:
            self.proxmox_api.access.acl.set(path=path, roles=roleid, **kwargs)
        except Exception as e:
            self.module.fail_json(msg="Failed to create ACL for {0}: {1}".format(kwargs, e))

    def delete(self, path, roleid, **kwargs):
        """
        Delete permissions ACLs

        :param path: str - the access control path
        :param roleid: str - name of the role
        :param propagate: bool - allow to propagate (inherit) permissions
        :param groups: str - list of the group names
        :param tokens: str - list of the tokens as user@realm!token
        :param users: str - list of the users as user@realm
        :return: list - list of ACL dicts removed
        """

        removing = self.matching_acls(path, roleid, **kwargs)

        if not removing:
            self.module.exit_json(changed=False, msg="No requested ACLs for path '{0}' and roleid '{1}' exist".format(path, roleid))

        if self.module.check_mode:
            return removing

        try:
            self.proxmox_api.access.acl.set(path=path, roles=roleid, delete=True, **kwargs)
            return removing
        except Exception as e:
            self.module.fail_json(msg="Failed to delete ACLs for {0}: {1}".format(removing, e))

def main():

    module_args = proxmox_openssh_argument_spec()
    acl_args = dict(
        path=dict(type="str", required=True),
        roleid=dict(type="str", required=True),
        groups=dict(type='str'),
        tokens=dict(type="str"),
        users=dict(type="str"),
        propagate=dict(type="bool", default=True),
        state=dict(type='str', choices=['present', 'absent'], default='present'),
    )
    module_args.update(acl_args)

    module = AnsibleModule(
        argument_spec=module_args,
        required_one_of=[
            ('groups', 'tokens', 'users')
        ],
        supports_check_mode=True
    )

    proxmox_acl = ProxmoxOpenSSHACLAnsible(module)
    path = module.params['path']
    roleid = module.params['roleid']
    state = module.params['state']

    if state == 'present':
        proxmox_acl.create(path, roleid,
                           groups=module.params['groups'],
                           tokens=module.params['tokens'],
                           users=module.params['users'],
                           propagate=module.params['propagate'])
        module.exit_json(changed=True, acl_path=path, roleid=roleid, msg="ACLs for path {0} and roleid {1} successfully created".format(path, roleid))
    else:
        # TBD: see if 'propagate' can be added. It is currently ignored when checking for ACLs to be removed.
        removed_acls = proxmox_acl.delete(path, roleid,
                           groups=module.params['groups'],
                           tokens=module.params['tokens'],
                           users=module.params['users'])
        module.exit_json(changed=True, removed_acls=removed_acls, msg="ACLs for path {0} and roleid {1} successfully deleted".format(path, roleid))

if __name__ == '__main__':

    main()
