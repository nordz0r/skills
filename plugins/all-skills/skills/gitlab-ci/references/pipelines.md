# GitLab CI YAML

## rules, не only/except

```yaml
build:
  stage: build
  image: python:3.12-bookworm
  script:
    - pip install -r requirements.txt
    - pytest -q
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
  cache:
    key:
      files:
        - requirements.txt
    paths:
      - .cache/pip
  artifacts:
    when: on_failure
    expire_in: 3 days
    paths:
      - junit.xml
    reports:
      junit: junit.xml
```

`workflow:rules` режет весь pipeline. `rules` на job режет конкретный job.

MR + branch pipeline одновременно не гоняй: в `workflow` отфильтруй branch,
если открыт MR.

## needs (DAG)

```yaml
test:
  stage: test
  needs: ["build"]

deploy:
  stage: deploy
  needs:
    - job: build
      artifacts: true
    - job: test
  environment:
    name: production
    url: https://app.example.com
  resource_group: production
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
      when: manual
      allow_failure: false
```

`resource_group` не даёт двум prod-деплоям ехать параллельно.

## Docker build + GitLab Registry

Предпочитай BuildKit kaniko/buildah на unprivileged runner.
dind — только если без него нельзя.

```yaml
build-image:
  stage: build
  image:
    name: gcr.io/kaniko-project/executor:v1.23.2-debug
    entrypoint: [""]
  script:
    - mkdir -p /kaniko/.docker
    - echo "{\"auths\":{\"$CI_REGISTRY\":{\"username\":\"$CI_REGISTRY_USER\",\"password\":\"$CI_REGISTRY_PASSWORD\"}}}" > /kaniko/.docker/config.json
    - /kaniko/executor
        --context "$CI_PROJECT_DIR"
        --dockerfile "$CI_PROJECT_DIR/Dockerfile"
        --destination "$CI_REGISTRY_IMAGE:$CI_COMMIT_SHA"
        --destination "$CI_REGISTRY_IMAGE:$CI_COMMIT_REF_SLUG"
  rules:
    - if: $CI_COMMIT_BRANCH
```

Если всё же dind:

```yaml
variables:
  DOCKER_HOST: tcp://docker:2376
  DOCKER_TLS_CERTDIR: "/certs"
  DOCKER_TLS_VERIFY: "1"
  DOCKER_CERT_PATH: "/certs/client"

build-dind:
  image: docker:27.4
  services:
    - name: docker:27.4-dind
      alias: docker
      command: ["--tls=true"]
  before_script:
    - docker login -u "$CI_REGISTRY_USER" -p "$CI_REGISTRY_PASSWORD" "$CI_REGISTRY"
  script:
    - docker build -t "$CI_REGISTRY_IMAGE:$CI_COMMIT_SHA" .
    - docker push "$CI_REGISTRY_IMAGE:$CI_COMMIT_SHA"
```

`docker.sock` bind в job — это root на runner host. Не делай на shared runner.

## include и компоненты

```yaml
include:
  - local: /ci/build.yml
  - project: ops/ci-templates
    file: /docker.yml
    ref: v3.2.0
  - component: $CI_SERVER_FQDN/to-be-continuous/docker/gitlab-ci-docker@5.0.0
    inputs:
      image: $CI_REGISTRY_IMAGE
```

Всегда пинь `ref` / версию компонента. `latest` в include = сюрприз в понедельник.

## Переменные и секреты

| Тип | Куда |
|-----|------|
| Masked + protected | токены, пароли |
| File variable | kubeconfig, SSH key, vault role |
| CI_JOB_TOKEN | доступ к registry/репо этой job |

Не логируй `env` целиком. Masked переменная всё равно утечёт, если её
напечатать кусками.

Проверка YAML:

```bash
glab ci lint
# или
curl --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  --data-binary @.gitlab-ci.yml \
  "$CI_API_V4_URL/projects/$PROJECT_ID/ci/lint"
```

## Частые поломки YAML

- `script` строка с `: ` без кавычек → YAML mapping.
- `rules:when:always` на job с ручным prod.
- Cache key слишком общий → чужие артефакты.
- `artifacts:paths` относительные, а job пишет в `/tmp`.
- `GIT_STRATEGY: none` на deploy, а манифесты в репо.
