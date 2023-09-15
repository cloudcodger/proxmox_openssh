# -*- coding: utf-8 -*-
#
# Copyright (c) 2020, Cloud Codger <cloud at codger.site>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import traceback

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.proxmox import (ProxmoxAnsible, ansible_to_proxmox_bool, proxmox_to_ansible_bool)

PROXMOXER_IMP_ERR = None
try:
    from proxmoxer import ProxmoxAPI
    HAS_PROXMOXER = True
except ImportError:
    HAS_PROXMOXER = False
    PROXMOXER_IMP_ERR = traceback.format_exc()

def proxmox_openssh_argument_spec():
    return dict(
        api_host=dict(type='str',
                      required=True
                      ),
        api_user=dict(type='str',
                      required=True
                      ),
    )

# Extending the ProxmoxAnsible class and override _connect so that proxmoxer uses openssh backend
# instead of the default, https backend
class ProxmoxOpenSSHAnsible(ProxmoxAnsible):
    def _connect(self):
        api_host = self.module.params['api_host']
        api_user = self.module.params['api_user']

        auth_args = {'user': api_user, 'backend': 'openssh'}

        try:
            return ProxmoxAPI(api_host, **auth_args)
        except Exception as e:
            self.module.fail_json(msg='%s' % e, exception=traceback.format_exc())

    def get_groups(self):
        """Retrieve groups information

        :return: dict - groups information
        """
        try:
            return self.proxmox_api.access.groups.get()
        except Exception as e:
            self.module.fail_json(msg="Unable to retrieve groups: {0}".format(e))

    def get_users(self):
        """Retrieve users information

        :return: dict - users information
        """
        try:
            return self.proxmox_api.access.users.get()
        except Exception as e:
            self.module.fail_json(msg="Unable to retrieve users: {0}".format(e))
