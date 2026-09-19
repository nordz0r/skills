---
name: ansible-playbook
description: "Ansible playbooks и roles: ansible-playbook, undefined variable, variable precedence, idempotency, changed tasks, shell task, FQCN, handlers, vault, ansible-lint. Не общий CI/CD rollout. Триггеры: ansible-playbook, playbook, inventory, vault, handler, ansible.builtin, ansible-galaxy."
---

# Ansible Playbook

Пиши идемпотентные playbooks и roles. Сначала `--check --diff`, потом apply.

Не подменяй этот skill Docker-only или GitLab YAML. Для контейнеров внутри
задачи используй `community.docker` здесь; для `.gitlab-ci.yml` — `gitlab-ci`.

## Когда использовать

- Написать/ревью playbook, role, inventory, group_vars.
- Task failed, undefined var, wrong host, module missing.
- Vault, секреты, `no_log`.
- Перевести ручные shell-команды в модули.

## Workflow

1. Найди существующий inventory и роли. Не плоди второй стиль в одном репо.
2. Цель сформулируй как состояние: пакет present, unit enabled, файл 0644.
3. FQCN обязателен: `ansible.builtin.copy`, не `copy`.
4. Секреты только в vault. `no_log: true` на задачах с паролями.
5. Проверка: `ansible-lint`, затем
   `ansible-playbook -i inventory play.yml --check --diff`.
6. Apply узко: `--limit`, `--tags`. Не гоняй весь prod «на всякий случай».

## Каркас

```yaml
---
- name: Configure app hosts
  hosts: app
  become: true
  gather_facts: true
  vars_files:
    - vars/app.yml
  handlers:
    - name: Restart app
      ansible.builtin.service:
        name: app
        state: restarted
  tasks:
    - name: Install app package
      ansible.builtin.package:
        name: "{{ app_package }}"
        state: present
      tags: [packages]

    - name: Deploy app config
      ansible.builtin.template:
        src: app.conf.j2
        dest: /etc/app/app.conf
        owner: root
        group: app
        mode: "0640"
        validate: "/usr/sbin/app -t -c %s"
      notify: Restart app
      tags: [config]
```

## Правила

- Каждая задача с `name:`.
- Не используй `shell`/`command`, если есть модуль.
- `changed_when`/`failed_when` для command-обёрток.
- Не `latest` для пакетов на проде — фиксируй версию, если среда это умеет.
- `serial:` и `max_fail_percentage` для rolling.
- Не логируй vault-значения.

## Companion skills

- Unit/journal на одном хосте без автоматизации → `administering-linux`.
- Compose-файл как артефакт → `docker-ops`.
- Запуск playbook из GitLab job → `gitlab-ci`.
- Общий delivery/rollback framing → `agency-devops-automator`.

## References

- `references/playbooks.md` — inventory, vars, roles, vault, docker.
- `references/debug.md` — check/diff, lint, failed task, precedence.

<!-- A-EVOLVE-ROUTING-SIGNALS:START -->
## Routing signals: ansible ansible-playbook playbook inventory vault ansible-lint fqcn handler role become community.docker
<!-- A-EVOLVE-ROUTING-SIGNALS:END -->
