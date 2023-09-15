# -*- coding: utf-8 -*-
# Copyright (c) 2020, Cloud Codger <cloud at codger.site>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later


from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment(object):
    # Common parameters for Proxmox VE modules
    DOCUMENTATION = r'''
options:
  api_host:
    description:
      - Specify the target host of the Proxmox VE cluster.
    type: str
    required: true
  api_user:
    description:
      - Specify the user to authenticate with.
    type: str
    required: true
requirements: [ "openssh-wrapper", "proxmoxer", "requests" ]
'''
