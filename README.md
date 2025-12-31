# Ansible Collection `cloudcodger.proxmox_openssh`

[Proxmox Virtual Environment (PVE)](https://proxmox.com/en/products/proxmox-virtual-environment/overview) Ansible Collection.

Provides a role and modules for managing a PVE Datacenter using the Python `proxmoxer` module with the `openssh` backend.

The;

- [Proxmox Inventory Source](https://docs.ansible.com/projects/ansible/latest/collections/community/general/proxmox_inventory.html)
- [`community.general.proxmox_kvm`](https://docs.ansible.com/ansible/latest/collections/community/general/proxmox_kvm_module.html) module
- [`community.general.proxmox`](https://docs.ansible.com/ansible/latest/collections/community/general/proxmox_module.html) module

all use the Python `proxmoxer` module with the `HTTPS` backend, this requires, either figuring out a secure way of dealing with an `api_password`, or creating an `api_token_id` and associated `api_token_secret`. The need exists for a set of modules that can create these tokens and secrets. Each token is associated with a user and following the best practice of putting users in groups and placing ACLs on the groups, the `datacenter` role creates the group(s), user(s) and token(s) for use by those other modules.

# Requirements

The roles in this collection have the following requirements.

- Proxmox_VE installed on hosts.
- Python `openssh_wrapper` module.
- Python `proxmoxer` module.
- Python `requests` module.

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

# Role

- [cloudcodger.proxmox_openssh.datacenter](./roles/datacenter/README.md)

# Proxmox Virtualization and Cloud-Init

Items in this collection are designed to make it easier to use the Cloud-Init capability built into Proxmox.

When starting with Proxmox, a common approach is to start something like this in the UI.

- Find an ISO image for the desired OS and download it
- Upload that ISO to a storage location in Proxmox
- Create a VM and attach the ISO as a virtual CD/DVD
- Boot the VM (from the ISO as the disk is empty at this point)
- Connect to the Console
- Go through the normal installation process as you would with a physical system

This quickly becomes tedeous, repetative and time consuming. Next common approach, cloning.

Learning how to `clone` VMs leads to learning how to turn a VM into a template and create clones from templates. Using a template with the "Linked Clone" may be the fastest way to create a virtual machine but introduces some restrictions and you will not be able to remove the template until all linked clones have been removed first. This is a fantastic way to quickly create a VM for a short test that will be destroyed right afterwards, however, working with clones also requires changing a lot of values inside the OS of the new VM after it has been cloned and it is easy to overlook updating one that will later causes problems.

Next is learning how to create VMs using a [Cloud-Init](https://cloudinit.readthedocs.io/en/latest/) image that was specifically created to allow cloud providers to configure virtual machines using multiple init scripts.

This collection helps set up a Proxmox datacent with items for Cloud-Init by changing the `local` storage to include the `images` content type and optionally creating a new `configs` storage allowing `snippets` content type that can be used for `user_data` configuration files. See the [cloudcodger.proxmox_ve](https://github.com/cloudcodger/proxmox_ve) collection for additional roles related to Cloud-Init usage.

**CAUTION:** The `configs` storage is type `Directory` at `/etc/pve/configs` synced to all cluster nodes via Corosync. Do to limitations in Corosync on the number of files and their sizes, only use this for small snippet files. Like the Cloud-Init user data configuration files (`snippets`). This provides a nice place to put any custom Cloud-Init User Config YAML files.
