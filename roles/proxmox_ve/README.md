`proxmox_ve`
=========

Proxmox virtual environment host configurator.

Configure one or more Proxmox host systems by doing the following.

- optionally configure all hosts into a cluster (default configures each host individually).
  Setting `cluster_name` to a non-empty string will create a cluster and will join all playbook `hosts` as nodes in the cluster.
  Uses the `pvecm` command in order to join nodes via passwordless SSH and avoid having to use the `root` password.
- Update the APT repositories to the "no-subscription" URLs.
  Set `enterprise_license` to true to disable this change.
  Optionally, set `pve_apt_enterprise_url` and `pve_apt_ceph_enterprise_url` if they have changed since PVE version 8.x.
- Add and Remove SSH authorized keys for the `root` user.
  Two lists provide the keys to authorize or de-authorize.
  At least one public key must already have been added in order to execute this role.
- Create a `images/00` directory under the `local` storage on each host and upload cloud-init image files there.
  The `images` content must be configured in order to use any uploaded images. See `proxmox_datacenter` README.md.
- Perform `apt dist-upgrade`, `reboot` and `apt autoremove` on the very first role execution.
  Using a marker file protects this from executing on subsequent executions.
  Assumption here is that the first execution of this role is performed on new installations and NOT on systems that have been operating for some time.
  The marker can be created by executing `touch /root/.ansible/proxmox_ve.first.run` on each host and will prevent unwanted automated reboots via this role.

Requirements
------------

- Proxmox_VE installed on hosts.
- Python `proxmoxer` module.
- Python `openssh_wrapper` module.
- Any image files to be uploaded must exist a `files` directory at the same level as the playbook calling this role.

Role Variables
--------------

- `cloud_init_image_files` - (default: `[]`, empty list)
  - A list of file names to upload to `local` storage under `images/00`.
- `cluster_name` - (default: `""` empty string)
  - Name of the Proxmox cluster.
  - The default empty string will cause each host to be configured individually and no cluster will be created.
- `enterprise_license` - (default: `false`)
  - Which APT repository URLs to configure. See below.
- `proxmox_host_authorized_keys` - (default: `[]`, empty list)
  - List of public SSH keys for inclusion in the `root` user `authorized_keys` file.
- `proxmox_host_deauthorized_keys` - (default: `[]`, empty list)
  - List of public SSH keys for removal from the `root` user `authorized_keys` file.
- `pve_apt_enterprise_url` - (default: `'https://enterprise.proxmox.com/debian/pve'`)
- `pve_apt_no_sub_url` - (default: `'http://download.proxmox.com/debian/pve'`)
- `pve_apt_ceph_enterprise_url` - (default: `'https://enterprise.proxmox.com/debian/ceph-quincy'`)
- `pve_apt_ceph_no_sub_url` - (default: `'http://download.proxmox.com/debian/ceph-quincy'`)

Above URLs are those from Proxmox VE version 8 at the time of role creation. They will need to be overridden when using a different version of Proxmox and only those needed according to the value of `enterprise_license` will need to be set.

Example Playbook
----------------

An example of how to use the role.

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
```
