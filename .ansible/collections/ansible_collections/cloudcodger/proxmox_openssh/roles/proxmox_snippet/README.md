The `proxmox_snippet` role
==========================

Create a snippet file on a Proxmox host.

Initially created for use with the `cloudcodger.proxmox_client.cloud_init` role for creating a snippet file on a Proxmox host that can be used with `cicustom` when creating a VM. Because of this, the defaults for the role create a snippet in the `configs` storage pool as created when using the `cloudcodger.proxmox_openssh.proxmox_ve` role, named `vendor-data.yml`. Because the `configs` storage pool is a shared pool, the snippet only needs to be created on one host. Corosync will then make it available on all the hosts in the cluster.

Requirements
------------

- Proxmox_VE installed on hosts.
- Python `openssh_wrapper` module.
- The storage pool must already exist on the Proxmox host and be configured for snippets content.

Role Variables
--------------

- `proxmox_snippet_contents` - A multi-line string containing the full text to be placed inside the snippet file (see `""` file).
- `proxmox_snippet_name` - The name of the snippet file (default `vendor-data.yml`).
- `proxmox_snippet_path` - The directory path in which to place the snippet (default `/etc/pve/configs/snippets`).

The `proxmox_snippet_contents` is considered to be a multi-line string that will get added to the file as is. Setting this to YAML or JSON will produce unpredictable results.

Example Playbook
----------------

```yaml
---
- name: Configure the Proxmox Datacenter.
  hosts: "{{ groups['proxmox_hosts'] | first }}"
  roles:
    - role: cloudcodger.proxmox_openssh.proxmox_snippet
      proxmox_snippet_name: user-data-101.yml
      proxmox_snippet_contents: |-
        #cloud-config
        apt:
          primary:
            - arches: [default]
              uri: "http://mirror.local/ubuntu/"
        chpasswd:
          expire: False
        fqdn: name1
        hostname: name1
        manage_etc_hosts: true
        ssh_authorized_keys:
          - ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIN+K0KwgKOeeyW519YavKQodVgwWcRUIucZkOfplsKMl devops-guy-mbp
          - ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJk/hSmxsyznAhhsD5cO9wcTgOs+/xz09kZ5woSUUQAY devops-gal-mbp
        users:
          - default
```
