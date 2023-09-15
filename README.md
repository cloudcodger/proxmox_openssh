# Ansible Collection - cloudcodger.proxmox_openssh

This collection contains a set of roles and modules for managing servers with [Proxmox Virtual Environment](https://www.proxmox.com/en/proxmox-virtual-environment/overview) installed that helps get them configured from initial install to a state for real world use.

Including:
- configured for no-subscription use (APT repository changes)
- installing the latest patches, and reboot if required
- clustering hosts together
- creating a group or groups and a user or users in that group
- creating API tokens on any of the users
- setting ACL permissions for the Administrator role and the recursive path `/` on the above group(s) and token(s)

As part of being idempotent, the default configuration uses a marker file to make sure the reboot only happens on the initial role execution. Done in order to prevent the potential situation where all the hosts in a cluster get rebooted at the same time in a live production environment. See the README.md for the `proxmox_ve` role for how to prevent the initial reboot when this is not desired.

When using either the [`community.general.proxmox_kvm`](https://docs.ansible.com/ansible/latest/collections/community/general/proxmox_kvm_module.html) or [`community.general.proxmox`](https://docs.ansible.com/ansible/latest/collections/community/general/proxmox_module.html) modules to create Proxmox VMs or Proxmox Containers, respectively, they require providing a password for an API user that has enough permissions to create those resources or creating a API token with the necessary permissions instead. Either way, the user and associated password or API token had to first be created manually. This collection not only provides initial setup but also the creation of a group, a user and an API Token that can be used for those modules in an automated way.

# Roles

Two roles are provided to configure the Proxmox VE host systems as described. Because some tasks are performed on the individual host systems and others are performed on `localhost` using the [Proxmox API](https://pve.proxmox.com/pve-docs/api-viewer/) via the `proxmoxer` Python module, a playbook for configuring Proxmox hosts needs to have two plays. The first runs on all hosts and the second runs on `localhost` (See the example playbook section).

## `proxmox_ve`

Called on all hosts that have Proxmox VE installed on them. Configures the clustering, APT repositories, directory for cloud-init images, uploads images, and reboots when appropriate.

## `proxmox_datacenter`

Called on `localhost` and users the `proxmoxer` Python module abd its `openssh` backend to connect to one or more hosts to configure the groups, users, API tokens and permissions ACLs.

This module makes use of the various Ansible modules in the collection to perform these tasks with the exception of clustering. The Proxmox CLI command `pvecm` supports the ability to join cluster nodes via SSH but this ability was not found in the Proxmox API calls. So this configuration is performed using the CLI commands to avoid having to deal with `root` user passwords in the calls.

# Modules

The modules included in this collection all use the Python [`proxmoxer`](https://proxmoxer.github.io/docs/2.0/) module and the `openssh` backend (connection method). This allows for use of passwordless SSH connections using preconfigured SSH key pairs. The same SSH keys used for Ansible to connect to hosts.

## Requirements for all modules

- Proxmox_VE installed on hosts.
- Python `proxmoxer` module.
- Python `openssh_wrapper` module.

## Included modules

- `cloudcodger.proxmox_openssh.proxmox_acl` - Access Control List (ACL) management
- `cloudcodger.proxmox_openssh.proxmox_group` - Group management
- `cloudcodger.proxmox_openssh.proxmox_storage_dir` - Storage management of directory (`dir`) storage type
- `cloudcodger.proxmox_openssh.proxmox_token` - User API Token management
- `cloudcodger.proxmox_openssh.proxmox_user` - User management

# Example Playbook

As shown here, the playbook needs two plays. One that runs on the inventory hosts (`hosts: proxmox_collection_hosts` in this example) and another that runs on the controller (`hosts: localhost`).

```
---
- name: Configure Proxmox on host systems.
  hosts: proxmox_collection_hosts
  roles:
    - role: cloudcodger.proxmox_openssh.proxmox_ve
      cloud_init_image_files:
        - 'ubuntu-22.04-server.qcow2'
      cluster_name: 'lab'
      proxmox_host_authorized_keys:
        - ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIN+K0KwgKOeeyW519YavKQodVgwWcRUIucZkOfplsKMl devops-guy-mbp
        - ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJk/hSmxsyznAhhsD5cO9wcTgOs+/xz09kZ5woSUUQAY devops-gal-mbp
      proxmox_host_deauthorized_keys:
        - ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIPMFTr31EjjWadkvE/H9zJm0xklizbAOAMjtVVGctDXr retired@computer.local

- name: Configure the Proxmox Datacenter.
  hosts: localhost
  roles:
    - role: cloudcodger.proxmox_openssh.proxmox_datacenter
      datacenter_users: ['s1m0ne@pve']
      proxmox_api_host: "{{ groups['proxmox_collection_hosts'] | first }}"
      datacenter_tokens: ['s1m0ne@pve!ansible']
      local_token_secret_name_prefix: "cluster-"
      local_token_secret_name_suffix: "-dev"
```
