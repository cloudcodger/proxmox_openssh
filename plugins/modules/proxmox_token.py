#!/usr/bin/python

# Copyright: (c) 2018, Cloud Codger <cloud@codger.site>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: proxmox_token

short_description:
  - Proxmox User specific API Token management for Proxmox VE Datacenter

version_added: "1.0.0"

description:
  - Create or delete a user-specific API token for Proxmox VE Datacenter.
  - Uses the proxmoxer openssh backend.

options:
    user:
        aliases: [ 'userid' ]
        description: Full User ID, in the `name@realm` format.
        required: true
        type: str
    token:
        aliases: [ 'name', 'tokenid' ]
        description: User-specific token ID.
        required: true
        type: str
    comment:
        description: A description text for the user.
        type: str
    expire:
        description: API token expiration date (seconds since epoch). '0' means no expiration date.
        default: 0
        type: int
    privsep:
        description: Restrict API token privileges with separate ACLs (default), or give full privileges of corresponding user.
        default: true
        type: bool
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
- name: "Create devops user-specific token."
  cloudcodger.proxmox_openssh.proxmox_token:
    api_host: "pve1"
    api_user: "root"
    token: "ansible"
    user: "devops@pve"
    state: present

- name: "Create devops user-specific token with a comment."
  cloudcodger.proxmox_openssh.proxmox_token:
    api_host: "192.168.1.21"
    api_user: "root"
    token: "ansible"
    user: "devops@pve"
    comment: "Administive API token for devops user."
    state: present

- name: "Delete devops user-specific token."
  cloudcodger.proxmox_openssh.proxmox_token:
    api_host: "pve1"
    api_user: "root"
    token: "ansible"
    user: "devops@pve"
    state: absent
'''

RETURN = r'''
tokenid:
    description: The token ID.
    returned: success
    type: str
    sample: 'ansible'
token:
    description: The token value.
    returned: changed i(state=present)
    type: str
    sample: '20a357ce-9a49-4c17-96ab-7afb7cd81b21'
userid:
    desctiption: The user in `user@realm` format.
    returned: success
    type: str
    sample: 'devops@pve'
msg:
    description: A short message on what the module did.
    returned: always
    type: str
    sample: "Token ansible!devops@pve successfully created"
'''

# from ansible_collections.community.general.plugins.module_utils.proxmox import (ansible_to_proxmox_bool, proxmox_to_ansible_bool)
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cloudcodger.proxmox_openssh.plugins.module_utils.proxmox_openssh import (ProxmoxOpenSSHAnsible, proxmox_openssh_argument_spec)

class ProxmoxOpenSSHTokenAnsible(ProxmoxOpenSSHAnsible):
    def get(self, tokenid, userid):
        """
        Get user-specific token info

        :param tokenid: str - the Token ID
        :param userid: str - full User ID, in the `name@realm` format
        :return: dict - token info
        """
        try:
            return self.proxmox_api.access.users(userid).get_token(tokenid)
        except Exception as e:
            self.module.fail_json(msg="Failed to get token ID {0} for user ID {1}: {2}".format(tokenid, userid, e))

    def exists(self, tokenid, userid):
        """
        Check if the user-specific token exists

        :param tokenid: str - the Token ID
        :param userid: str - full User ID, in the `name@realm` format
        :return: bool - if the user-specific token exists
        """
        for user in self.get_users():
            if user['userid'] == userid:
              for token in self.proxmox_api.access.users(userid).token.get():
                  if token['tokenid'] == tokenid:
                      # self.module.exit_json(changed=False, token=token['tokenid'])
                      return True
        return False

    def create(self, tokenid, userid, comment=None, privsep=True, expire=0):
        """
        Create user-specific token

        :param tokenid: str - the Token ID
        :param userid: str - full User ID, in the `name@realm` format
        :param comment: str
        :param privsep: bool
        :param expire: int - seconds since epoch
        :return: None
        """
        if self.exists(tokenid, userid):
            self.module.exit_json(changed=False, tokenid=tokenid, userid=userid, msg="Token {0} for user {1} exists".format(tokenid, userid))

        if self.module.check_mode:
            return

        try:
            return self.proxmox_api.access.users(userid).token(tokenid).create(
                comment=comment,
                privsep=privsep,
                expire=expire,
                )
        except Exception as e:
            self.module.fail_json(msg="Failed to create token with ID {0} for user with ID {1}: {2}".format(tokenid, userid, e))

    def delete(self, tokenid, userid):
        """
        Delete user-specific token

        :param tokenid: str - the Token ID
        :param userid: str - full User ID, in the `name@realm` format
        :return: None
        """
        if not self.exists(tokenid, userid):
            self.module.exit_json(changed=False, tokenid=tokenid, userid=userid, msg="Token {0} for user {1} doesn't exist".format(tokenid, userid))

        if self.module.check_mode:
            return

        try:
            self.proxmox_api.access.users(userid).token(tokenid).delete()
        except Exception as e:
            self.module.fail_json(msg="Failed to delete token {0} for user with ID {1}: {1}".format(tokenid, userid, e))

def main():
    module_args = proxmox_openssh_argument_spec()
    token_args = dict(
        tokenid=dict(type='str', aliases=['token', 'name'], required=True),
        userid=dict(type='str', aliases=['user'], required=True),
        comment=dict(type="str"),
        privsep=dict(type="bool", default=True),
        expire=dict(type="int", default=0),
        state=dict(type='str', choices=['present', 'absent'], default='present'),
    )
    module_args.update(token_args)

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    proxmox_token = ProxmoxOpenSSHTokenAnsible(module)
    tokenid = module.params['tokenid']
    userid = module.params['userid']
    comment = module.params['comment']
    privsep = module.params['privsep']
    expire = module.params['expire']
    state = module.params['state']

    if state == 'present':
        new_token = proxmox_token.create(tokenid, userid, comment=comment, privsep=privsep, expire=expire)
        module.exit_json(changed=True, tokenid=tokenid, token=new_token['value'], userid=userid, msg="Token {0} for User {1} successfully created".format(tokenid, userid))
    else:
        proxmox_token.delete(tokenid, userid)
        module.exit_json(changed=True, tokenid=tokenid, userid=userid, msg="Token {0} for User {1} successfully deleted".format(tokenid, userid))

if __name__ == '__main__':
    main()
