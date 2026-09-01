# Playbooks, inventory, vault

## Inventory

INI:

```ini
[app]
app-01 ansible_host=10.20.0.11
app-02 ansible_host=10.20.0.12

[app:vars]
ansible_user=deploy
ansible_become=true
```

YAML:

```yaml
all:
  children:
    app:
      hosts:
        app-01:
          ansible_host: 10.20.0.11
      vars:
        ansible_user: deploy
```

Группы отражают роль, не DC. DC — в `group_vars/dc_spb.yml` через child group.

Проверка:

```bash
ansible-inventory -i inventory.yml --graph
ansible-inventory -i inventory.yml --host app-01
ansible app -i inventory.yml -m ansible.builtin.ping
```

## Variable precedence (коротко)

От низкого к высокому: role defaults → inventory/group_vars → host_vars →
play vars → task vars → extra-vars (`-e`) побеждает всех.

Если var «не та» — печатай происхождение:

```bash
ansible app-01 -i inventory.yml -m ansible.builtin.debug -a 'var=app_package'
ansible-playbook -i inventory.yml site.yml --list-hosts
```

`group_vars/all.yml` не место для секретов.

## Role layout

```text
roles/app/
  defaults/main.yml
  handlers/main.yml
  tasks/main.yml
  templates/app.conf.j2
  files/
  meta/main.yml
```

Вызов:

```yaml
roles:
  - role: app
    tags: [app]
```

Или `ansible.builtin.import_role` / `include_role` для условных ролей.

## Vault

```bash
ansible-vault encrypt group_vars/prod/vault.yml
ansible-vault edit group_vars/prod/vault.yml
ansible-vault view group_vars/prod/vault.yml
```

В CI — `ANSIBLE_VAULT_PASSWORD_FILE` или file-type CI variable.
Не `--ask-vault-pass` в pipeline.

```yaml
- name: Write TLS key
  ansible.builtin.copy:
    dest: /etc/ssl/private/app.key
    content: "{{ vault_tls_key }}"
    owner: root
    group: root
    mode: "0600"
  no_log: true
```

## Docker через Ansible

```yaml
- name: Ensure compose stack
  community.docker.docker_compose_v2:
    project_src: /opt/app
    state: present
    pull: missing
```

Collection:

```bash
ansible-galaxy collection install community.docker
```

`requirements.yml`:

```yaml
collections:
  - name: community.docker
    version: ">=4.0.0"
```

Не копируй `docker-compose` binary-вызов, если модуль работает.

## systemd из Ansible

```yaml
- name: Install unit
  ansible.builtin.copy:
    src: app.service
    dest: /etc/systemd/system/app.service
    mode: "0644"
  notify: Reload systemd

- name: Enable app
  ansible.builtin.systemd:
    name: app
    enabled: true
    state: started
    daemon_reload: true
```

Handler:

```yaml
- name: Reload systemd
  ansible.builtin.systemd:
    daemon_reload: true
```
