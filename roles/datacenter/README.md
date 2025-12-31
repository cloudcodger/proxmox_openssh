# The `datacenter` role

Configure a Proxmox Datacenter. The datacenter is cluster wide and not unique to each PVE node in a cluster.

Objective:

- Create a `pve_secrets` directory on the control node.
- Update the `local` storage allowed content to include `images`.
- Create a `configs` storage for `snippets` content (optional).
- Create `Administrator` and `Auditor` groups, users, tokens, and permission ACLs.

This role uses the modules within this collection that use the `proxmoxer` modules `openssh` backend (where the collection gets it's name) to make modifications to the PVE Datacenter. It is run on `localhost` and not the PVE nodes.

By default, this role creates an API token (`devops@pve!ansible`) that will have the Administrator role so it can create CTs and VMs and such. It will also create two API tokens (`devops@pve!inventory` and `exporter@pve!prometheus`) that will have the Auditor role. One for use with the Proxmox Inventory source and the other for use with the `prometheus_pve_exporter` utility.

# Requirements

- Proxmox_VE installed on hosts.
- Python `proxmoxer` module.
- Python `openssh_wrapper` module.

# Role Variables

- `datacenter_add_configs_storage`
  - When true, adds the `configs` shared storage that allows `snippets` content.
  - Default: `true`
  - Created under `/etc/pve` which has Corosyn size restrictions.
  - NOT intended for large files or a large number of files.
  - Facilitates use for custom cloud-init user config files.

- `datacenter_administrator_groups`
  - A list of groups to create that will be given the `Administrator` role.
  - Default: `[Admin]`

- `datacenter_administrator_tokens`
  - A list of API tokens to create that will be given the `Administrator` role.
  - Default: `['devops@pve!ansible']`
  - For each token, the associated user (`devops@pve` for the default) will be created and assigned to the fist group in the `datacenter_administrator_groups` list.

- `datacenter_auditor_groups`
  - A list of groups to create that will be given the `PVEAuditor` role.
  - Default: `[Auditor]`

- `datacenter_auditor_tokens`
  - A list of API tokens to create that will be given the `PVEAuditor` role.
  - Default: `['devops@pve!inventory', 'exporter@pve!prometheus']`
  - Must be in the format of `user@realm!token`.
  - For each token, the associated user (`devops@pve` and `exporter@pve` for the default) will be created and assigned to the fist group in the `datacenter_auditor_groups` list.

- `datacenter_local_storage_content`
  - String assigned to the `local` storage for allowed content.
  - Default: `images,iso,vztmpl,backup`
  - Needed in order to use this storage for clound-init images that can be used with `import-from` when creating a VM.
  - A new Proxmox datacenter will have `iso,vztmpl,backup` for the allowed content. Override the default value if desired.

- `datacenter_pm_api_host`
  - The host for all Proxmox API calls.
  - Default: `pve`
  - The default value is almost always going to be wrong. Either a resolvable name or IP address must be provided.

- `datacenter_pm_api_user`
  - The user for `proxmoxer` connection to each API host.
  - Default: `root`
  - Ansible must have passwordless SSH connectivity to each API host or tasks will fail.

- `datacenter_token_secrets_dir`
  - Directory created on the control host and used to hold API tokens that are created.
  - Default: `~/.pve_tokens`
  - Tokens are stored in files named using the template of `<prefix><user>-<realm>-<token_id><suffix>.token`.

- `datacenter_token_secret_name_prefix`
  - A prefix prepended to each API token file created.
  - Default: `""`
  - This allows for managing multiple PVE clusters on the same control node and avoid naming conflicts.

- `datacenter_token_secret_name_suffix`
  - A suffix appended to each API token file created.
  - Default: `""`
  - This allows for managing multiple PVE clusters on the same control node and avoid naming conflicts.

# Example Playbook

An example of how to use the role.

```yaml
---
- name: Configure the Proxmox Datacenter cluster using all defaults.
  hosts: localhost

  roles:
    - role: cloudcodger.proxmox_openssh.datacenter
      datacenter_pm_api_host: "{{ groups['proxmox_collection_hosts'] | first }}"
```

```yaml
---
- name: Configure the Proxmox Datacenter with a unique administrator token.
  hosts: localhost

  roles:
    - role: cloudcodger.proxmox_openssh.datacenter
      datacenter_pm_api_host: "{{ proxmox_collection_host }}"
      datacenter_administrator_tokens: ['s1m0ne@pve!ansible']
```

```yaml
---
- name: Configure the Proxmox Datacenter with the local token copy having a prefix and suffix.
  hosts: localhost

  roles:
    - role: cloudcodger.proxmox_openssh.datacenter
      datacenter_pm_api_host: "{{ proxmox_collection_host }}"
      local_token_secret_name_prefix: "lab-"
      local_token_secret_name_suffix: "-dev"
```
