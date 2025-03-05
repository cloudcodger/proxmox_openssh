#!/usr/bin/python

# Copyright: (c) 2018, Cloud Codger <cloud@codger.site>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: proxmox_user

short_description:
  - Proxmox User management for Proxmox VE Datacenter

version_added: "1.0.0"

description:
  - Create or delete a user for Proxmox VE Datacenter.
  - Uses the proxmoxer openssh backend.

options:
    user:
        aliases: [ 'name', 'userid' ]
        description: Full User ID, in the `name@realm` format.
        required: true
        type: str
    comment:
        description: A description text for the user.
        type: str
    email:
        description: The email address for the user.
        type: str
    firstname:
        description: The first name for the user.
        type: str
    groups:
        description: A comma seperated list of groups for the user.
        type: str
    lastname:
        description: The last name for the user.
        type: str
    state:
        description: The desired state of the user.
        choices: [ 'present', 'absent' ]
        default: present
        type: str

extends_documentation_fragment:
    - cloudcodger.proxmox_openssh.proxmox.documentation

author:
    - Cloud Codger (@cloudcodger) <cloud@codger.site>
'''

EXAMPLES = r'''
# Create a Proxmox VE Datacenter Permissions User
- name: "Create devops user."
  cloudcodger.proxmox_openssh.proxmox_user:
    api_host: "pve1"
    api_user: "root"
    user: "devops@pve"
    state: present

- name: "Create devops user with a comment."
  cloudcodger.proxmox_openssh.proxmox_user:
    api_host: "192.168.1.21"
    api_user: "root"
    user: "devops@pve"
    comment: "Administive user for API access."
    state: present

- name: "Delete devops user."
  cloudcodger.proxmox_openssh.proxmox_user:
    api_host: "pve1"
    api_user: "root"
    user: "devops@pve"
    state: absent
'''

RETURN = r'''
user_id:
    description: The user ID.
    returned: success
    type: str
    sample: 'devops@pve'
msg:
    description: A short message on what the module did.
    returned: always
    type: str
    sample: "User devops@pve successfully created"
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cloudcodger.proxmox_openssh.plugins.module_utils.proxmox_openssh import (ProxmoxOpenSSHAnsible, proxmox_openssh_argument_spec)

class ProxmoxOpenSSHUserAnsible(ProxmoxOpenSSHAnsible):

    def get(self, userid):
        """
        Get user info

        :param userid: str - full User ID, in the `name@realm` format
        :return: dict - user info
        """
        try:
            return self.proxmox_api.access.users.get(userid)
        except Exception as e:
            self.module.fail_json(msg="Failed to get user with ID {0}: {1}".format(userid, e))

    def exists(self, userid):
        """
        Check if the user exists

        :param userid: str - full User ID, in the `name@realm` format
        :return: bool - if the user exists
        """
        for user in self.get_users():
            if user['userid'] == userid:
                return True
        return False

    def create(self, userid, comment=None, email=None, groups=None, firstname=None, lastname=None):
        """
        Create user

        :param userid: str - full User ID, in the `name@realm` format
        :param comment: str
        :param email: str
        :param groups: str
        :param firstname: str
        :param lastname: str
        :return: None
        """
        if self.exists(userid):
            self.module.exit_json(changed=False, userid=userid, msg="User {0} exists".format(userid))

        if self.module.check_mode:
            return

        try:
            self.proxmox_api.access.users.create(
                userid=userid,
                comment=comment,
                email=email,
                groups=groups,
                firstname=firstname,
                lastname=lastname,
                )
        except Exception as e:
            self.module.fail_json(msg="Failed to create user with ID {0}: {1}".format(userid, e))

    def delete(self, userid):
        """
        Delete user

        :param userid: str - full User ID, in the `name@realm` format
        :return: None
        """
        if not self.exists(userid):
            self.module.exit_json(changed=False, userid=userid, msg="User {0} doesn't exist".format(userid))

        if self.module.check_mode:
            return

        try:
            self.proxmox_api.access.users.delete(userid)
        except Exception as e:
            self.module.fail_json(msg="Failed to delete user with ID {0}: {1}".format(userid, e))

def main():

    module_args = proxmox_openssh_argument_spec()
    user_args = dict(
        userid=dict(type='str', aliases=['user', 'name'], required=True),
        comment=dict(type="str"),
        email=dict(type="str"),
        groups=dict(type="str"),
        firstname=dict(type="str"),
        lastname=dict(type="str"),
        state=dict(type='str', choices=['present', 'absent'], default='present'),
    )
    module_args.update(user_args)

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    proxmox_user = ProxmoxOpenSSHUserAnsible(module)
    userid = module.params['userid']
    comment = module.params['comment']
    email = module.params['email']
    groups = module.params['groups']
    firstname = module.params['firstname']
    lastname = module.params['lastname']
    state = module.params['state']

    if state == 'present':
        proxmox_user.create(userid, comment=comment, email=email, groups=groups, firstname=firstname, lastname=lastname)
        module.exit_json(changed=True, userid=userid, msg="User {0} successfully created".format(userid))
    else:
        proxmox_user.delete(userid)
        module.exit_json(changed=True, userid=userid, msg="User {0} successfully deleted".format(userid))

if __name__ == '__main__':

    main()
