---
name: ansible-playbook
description: "Ansible playbooks and roles: ansible-playbook, undefined variable, variable precedence, idempotency, changed tasks, shell task, FQCN, handlers, vault, ansible-lint. Not generic CI/CD rollout. Triggers: ansible-playbook, playbook, inventory, vault, handler, ansible.builtin, ansible-galaxy, плейбук, инвентарь, роль, ансибл."
---

# Ansible Playbook

Write idempotent playbooks and roles. `--check --diff` first, then apply.

Do not replace this skill with Docker-only or GitLab YAML work. For containers inside
the task use `community.docker` here; for `.gitlab-ci.yml` use `gitlab-ci`.

## When to use

- Write/review a playbook, role, inventory, group_vars.
- Task failed, undefined var, wrong host, module missing.
- Vault, secrets, `no_log`.
- Turn manual shell commands into modules.

## Workflow

1. Find the existing inventory and roles. Do not introduce a second style into one repo.
2. State the goal as a state: package present, unit enabled, file 0644.
3. FQCN is mandatory: `ansible.builtin.copy`, not `copy`.
4. Secrets only in vault. `no_log: true` on tasks with passwords.
5. Verify: `ansible-lint`, then
   `ansible-playbook -i inventory play.yml --check --diff`.
6. Apply narrowly: `--limit`, `--tags`. Do not run all of prod "just in case".

## Skeleton

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

## Rules

- Every task has a `name:`.
- Do not use `shell`/`command` when a module exists.
- `changed_when`/`failed_when` for command wrappers.
- No `latest` for packages in prod — pin the version if the environment supports it.
- `serial:` and `max_fail_percentage` for rolling updates.
- Never log vault values.

## Companion skills

- Unit/journal on a single host without automation → `administering-linux`.
- Compose file as an artifact → `docker-ops`.
- Running a playbook from a GitLab job → `gitlab-ci`.
- General delivery/rollback framing → `agency-devops-automator`.

## References

- `references/playbooks.md` — inventory, vars, roles, vault, docker.
- `references/debug.md` — check/diff, lint, failed task, precedence.

<!-- A-EVOLVE-ROUTING-SIGNALS:START -->
## Routing signals: ansible ansible-playbook playbook inventory vault ansible-lint fqcn handler role become community.docker
<!-- A-EVOLVE-ROUTING-SIGNALS:END -->

Russian version: [`references/README.ru.md`](references/README.ru.md).
