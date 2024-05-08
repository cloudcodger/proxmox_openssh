The `proxmox_datacenter` role
=============================

Configure a Proxmox Datacenter by doing the following tasks.

Because the `community.general.proxmox` and `community.general.proxmox_kvm` modules either require figuring out a secure way of dealing with an `api_password` or creating an `api_token_id` and associated `api_token_secret`. The need exists for a set of modules that can create these tokens and secrets. Each token is associated with a user and following the best practice of putting users in groups and placing ACLs on the groups, this role attempts to provide the group(s), user(s) and token(s) for use by those other modules.

- Change the `local` storage to allow `images` content.
  Facilitates use for uploading customized cloud-init images to be used with `proxmox_kvm`.
  Needed by `proxmox_ve`.
- Create a `configs` storage for `snippets` content under Corosync file system.
  Facilitates use for custom cloud-init user config files.
  Caution: There is a size limitation here. This is NOT intended for large files or a large number of files.
- Create all Permissions Groups provided by `datacenter_groups` and ACLs for the Administrator role.
- Create all Permissions Users provided by `datacenter_users` and placed inside all the `datacenter_users_groups`.
  The users get ACL permissions from their groups.
  Must exist in order to create API tokens on them.
- Create User API tokens and ACLs for the Administrator role.
  A local secrets directory is created to hold any newly created token values.
  Tokens names are `<prefix>user-realm-token?-apihost?<suffix>.token`.
  For multiple API hosts, the `-apihost` section is added to prevent naming conflicts, as each API host would use the same token name.

Every installation of Proxmox defines a Datacenter. When multiple hosts are joined together in a Cluster, many configuration items defined at the Datacenter level are syncronized across all host systems and only need to be set on one of the clustered hosts to be usable on all of them.

This role is designed to be run inside a play with `hosts: localhost` as it will create a secrets directory and store generated API tokens inside for local use outside this collection. See the collection README.md file for additional details.

When a list is provided for `proxmox_api_host`, each will be configured the same way. This facilitates the creation of multiple non-clustered Proxmox VE Datacenters in one call of the role. In this case, each API host name will be added to the token file names to differentiate between the same API tokens created on each host. For a cluster of Proxmox hosts, any host joined to the cluster can be used.

Requirements
------------

- Proxmox_VE installed on hosts.
- Python `proxmoxer` module.
- Python `openssh_wrapper` module.

Role Variables
--------------

- `proxmox_api_host`
  - MUST be set via parameters. The default will not work and only configured as an example.
  - Potential values:
    - a resolvable hostname
    - an IP address
    - a list of a mixture of the above two values
- `proxmox_api_port` - (default: `22`)
  - What SSH port will be used in the case that `proxmox_api_host` is not using default ports.
- `proxmox_api_user` - (default: `root`)
  - The user for `proxmoxer` connection to each API host.
  - Ansible must have passwordless SSH connectivity to each API host or tasks will fail.
- `proxmox_api_sudo` - (default: `false`)
  - Whether `proxmoxer` connection will use sudo. Possibly needed when `proxmox_api_user` is not root.
- `datacenter_groups` - (default: value of `datacenter_users_groups`)
  - A list of group to create and given permissions to the `Administrator` role.
  - Do not use this to create groups for which you do not want these permissions added.
- `datacenter_users` - (default: `['devops@pve']`)
  - A list of users in `user@realm` to create and added to the `datacenter_users_groups`.
- `datacenter_users_groups` - (default: `['Admin']`)
  - A list of all groups membership for the above user creation.
  - Make sure to include any of these in `datacenter_groups` as well to make sure they are created and have the permissions.
- `datacenter_tokens` - (default: `['devops@pve!ansible']`)
  - A list of all user API tokens to create in the format of `user@realm!token` and given permissions to the `Administrator` role.
  - Each specified user must already exist. Use the above variable to make sure they are created.
  - Do not use this to create API tokens for which you do not want these permissions added.
- `local_token_secrets_dir` - (default: `~/.pve_tokens`)
  - Directory created and used to hold API tokens that are created.
- `local_token_secret_name_prefix` - (default: `""`)
  - A prefix appended to each API token file created.
- `local_token_secret_name_suffix` - (default: `""`)
  - A suffix appended to each API token file created.

Example Playbook
----------------

An example of how to use the role.

```yaml
---
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
