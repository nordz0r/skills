# Отладка Ansible

## Перед apply

```bash
ansible-playbook --syntax-check -i inventory.yml site.yml
ansible-lint site.yml
ansible-playbook -i inventory.yml site.yml --list-tasks --list-hosts
ansible-playbook -i inventory.yml site.yml --check --diff --limit app-01
```

`--check` врёт, если модуль не поддерживает check mode (`shell` почти всегда).
Смотри warning `module does not support check mode`.

## Failed task

Типичный вывод: `fatal: [app-01]: FAILED! => ...`.

1. Модуль и аргументы — в `invocation`.
2. `msg` / `stderr`.
3. Хост тот? `--limit` vs inventory hostname vs `ansible_host`.
4. Become: `Missing sudo password`, `become_method`.
5. Python interpreter: `/usr/bin/python` vs python3.

```bash
ansible app-01 -i inventory.yml -m ansible.builtin.setup
ansible app-01 -i inventory.yml -b -m ansible.builtin.command -a 'id'
ANSIBLE_DEBUG=1 ansible-playbook -i inventory.yml site.yml --limit app-01 -vvv
```

`-vvv` печатает секреты. Не кидай полный лог в чат.

## Undefined variable

```yaml
- name: Fail fast if required vars missing
  ansible.builtin.assert:
    that:
      - app_package is defined
      - vault_db_password is defined
```

Jinja `{{ var }}` в `when:` не нужна:

```yaml
when: app_enabled | bool
```

не `when: "{{ app_enabled }}"`.

## Идемпотентность сломана

Симптом: каждый прогон `changed=N`.

- `shell` без `creates=`/`changed_when: false`.
- `copy` с разным содержимым из-за неотсортированного dict.
- `template` с `ansible_date_time` внутри.
- `file: owner=` на bind-mount, который Docker тут же перезаписывает.

Проверка:

```bash
ansible-playbook -i inventory.yml site.yml --limit app-01
ansible-playbook -i inventory.yml site.yml --limit app-01
# второй прогон: changed=0
```

## Connection

```bash
ansible app-01 -i inventory.yml -m ansible.builtin.ping -vv
ssh -o BatchMode=yes deploy@10.20.0.11 true
```

`ansible_host` vs inventory name путают лимиты. `--limit app-01` не матчит IP.

Для jump host:

```ini
ansible_ssh_common_args=-o ProxyJump=bastion.example.com
```

## Galaxy / collections

```bash
ansible-galaxy collection list
ansible-galaxy collection install -r requirements.yml
ansible-doc community.docker.docker_compose_v2
```

`couldn't resolve module/action` — collection не установлена на controller,
не на target.

## ansible.cfg минимум

```ini
[defaults]
inventory = inventory.yml
roles_path = roles
collections_path = ~/.ansible/collections:/usr/share/ansible/collections
retry_files_enabled = False
stdout_callback = yaml
host_key_checking = True
interpreter_python = auto_silent

[privilege_escalation]
become = True
become_method = sudo
```
