# Confluence Formatting Cookbook: красивые статьи в storage format

`confluence_create_page` и `confluence_update_page` принимают тело страницы в
**storage format** (XHTML-подобный XML Confluence). Этот референс — готовые
куски разметки для статей «как в хорошем wiki»: заголовки, панели, макросы,
таблицы, задачи, оглавление, layout.

## Базовая структура статьи

```xml
<p><em>Автор: @ivanov · Обновлено: 2026-09-02 · Статус: актуально</em></p>
<ac:structured-macro ac:name="toc" ac:schema-version="1">
  <ac:parameter ac:name="minLevel">2</ac:parameter>
  <ac:parameter ac:name="maxLevel">3</ac:parameter>
</ac:structured-macro>
<h2>Цель</h2>
<p>Коротко: зачем существует эта страница.</p>
```

- `toc` — автооглавление по заголовкам (min/maxLevel ограничивают глубину).
- `<h1>` оставляйте для названия страницы; в теле начинайте с `<h2>`.

## Инфо-панели (info / note / warning / tip)

```xml
<ac:structured-macro ac:name="info" ac:schema-version="1">
  <ac:parameter ac:name="title">Полезно знать</ac:parameter>
  <ac:rich-text-body>
    <p>Текст подсказки.</p>
  </ac:rich-text-body>
</ac:structured-macro>

<ac:structured-macro ac:name="warning" ac:schema-version="1">
  <ac:parameter ac:name="title">Осторожно</ac:parameter>
  <ac:rich-text-body>
    <p>Опасная операция: удаляет данные.</p>
  </ac:rich-text-body>
</ac:structured-macro>
```

Имена макросов: `info`, `note`, `warning`, `tip` (в DC также `panel` с
параметрами `title`, `bgColor`, `borderColor`, `titleBGColor`).

## Блок кода с подсветкой

```xml
<ac:structured-macro ac:name="code" ac:schema-version="1">
  <ac:parameter ac:name="language">bash</ac:parameter>
  <ac:parameter ac:name="title">Развёртывание</ac:parameter>
  <ac:plain-text-body><![CDATA[systemctl restart myapp]]></ac:plain-text-body>
</ac:structured-macro>
```

Тело кода — строго `ac:plain-text-body` + `CDATA` (иначе Confluence
проэкранирует HTML-символы). Языки: `bash`, `python`, `sql`, `yaml`, `json`,
`java`, `javascript`, `xml`, `html/css`, `none`.

## Таблицы

```xml
<table>
  <tbody>
    <tr>
      <th>Сервис</th><th>Владелец</th><th>SLA</th>
    </tr>
    <tr>
      <td>api-gateway</td><td><ac:link><ri:user ri:userkey="4028..."/></ac:link></td>
      <td><ac:structured-macro ac:name="status" ac:schema-version="1">
            <ac:parameter ac:name="colour">Green</ac:parameter>
            <ac:parameter ac:name="title">99.9%</ac:parameter>
          </ac:structured-macro></td>
    </tr>
  </tbody>
</table>
```

Шапка таблицы — `<th>`; макрос `status` рисует цветной бейдж
(`Green`, `Yellow`, `Red`, `Grey` / `Blue`, `Purple` в новых версиях).

## Чек-листы (task list)

```xml
<ac:task-list>
  <ac:task>
    <ac:task-status>complete</ac:task-status>
    <ac:task-body>Подготовить стенд</ac:task-body>
  </ac:task>
  <ac:task>
    <ac:task-status>incomplete</ac:task-status>
    <ac:task-body><ac:link><ri:user ri:username="ivanov"/></ac:link> прогнать тесты</ac:task-body>
  </ac:task>
</ac:task-list>
```

## Ссылки

```xml
<!-- Внутренняя страница -->
<ac:link>
  <ri:page ri:content-title="Runbook: Payments" ri:space-key="OPS"/>
  <ac:plain-text-link-body><![CDATA[Runbook платежей]]></ac:plain-text-link-body>
</ac:link>

<!-- Внешняя ссылка -->
<a href="https://example.com/docs">Документация API</a>

<!-- Задача Jira через ярлык -->
<ac:link>
  <ri:shortcut ri:key="jira" ri:parameter="PROJ-123"/>
  <ac:plain-text-link-body><![CDATA[PROJ-123]]></ac:plain-text-link-body>
</ac:link>

<!-- Вложение -->
<ac:link>
  <ri:attachment ri:filename="architecture.png"/>
  <ac:plain-text-link-body><![CDATA[Схема архитектуры]]></ac:plain-text-link-body>
</ac:link>
```

`ri:space-key` опционален (тогда поиск по всем пространствам). Заголовок
зависит от точного имени страницы — берите его из `confluence_get_page`.

## Изображения

```xml
<!-- Прикреплённый файл (загружен заранее в страницу) -->
<ac:image ac:align="center" ac:width="600">
  <ri:attachment ri:filename="diagram.png"/>
</ac:image>

<!-- Внешняя картинка -->
<ac:image>
  <ri:url ri:value="https://example.com/img/logo.png"/>
</ac:image>
```

Атрибуты: `ac:align`, `ac:width`, `ac:height`, `ac:border="true"`,
`ac:thumbnail="true"`, `ac:alt`.

## Сворачиваемые секции (expand)

```xml
<ac:structured-macro ac:name="expand" ac:schema-version="1">
  <ac:parameter ac:name="title">Полный лог деплоя</ac:parameter>
  <ac:rich-text-body>
    <ac:structured-macro ac:name="noformat"><ac:plain-text-body>
      <![CDATA[... длинный вывод ...]]>
    </ac:plain-text-body></ac:structured-macro>
  </ac:rich-text-body>
</ac:structured-macro>
```

## Двухколоночный layout

```xml
<ac:layout>
  <ac:layout-section ac:type="two_equal">
    <ac:layout-cell><h3>Проблема</h3><p>...</p></ac:layout-cell>
    <ac:layout-cell><h3>Решение</h3><p>...</p></ac:layout-cell>
  </ac:layout-section>
</ac:layout>
```

Типы секций: `single`, `two_equal`, `two_left_sidebar`, `two_right_sidebar`,
`three_equal`, `three_with_sidebars`.

## Эмодзи и текстовые эффекты

```xml
<ac:emoticon ac:name="check" />   <!-- галочка -->
<ac:emoticon ac:name="warning" /> <!-- ⚠ -->
<strong>жирный</strong>, <em>курсив</em>,
<span style="text-decoration: underline;">подчёркнутый</span>,
<span style="color: #ff0000;">красный текст</span>, <code>inline-код</code>
<hr /> <!-- разделитель -->
```

## Готовый шаблон: Meeting Notes

```xml
<ac:structured-macro ac:name="info" ac:schema-version="1">
  <ac:parameter ac:name="title">Встреча</ac:parameter>
  <ac:rich-text-body><p>Дата: 2026-09-02 · Участники: ... · Протоколирует: ...</p></ac:rich-text-body>
</ac:structured-macro>
<h2>Agenda</h2>
<ul><li>Тема 1</li><li>Тема 2</li></ul>
<h2>Решения</h2>
<ac:structured-macro ac:name="panel" ac:schema-version="1">
  <ac:parameter ac:name="title">Ключевые решения</ac:parameter>
  <ac:rich-text-body><ul><li>Решение 1 — потому что ...</li></ul></ac:rich-text-body>
</ac:structured-macro>
<h2>Action Items</h2>
<ac:task-list>
  <ac:task><ac:task-status>incomplete</ac:task-status>
    <ac:task-body>@ivanov — сделать X к пятнице</ac:task-body></ac:task>
</ac:task-list>
```

## Как применять через скилл

```python
from scripts.confluence_pages import confluence_create_page, confluence_update_page

body = '''<h2>Цель</h2><p>...</p>
<ac:structured-macro ac:name="info"><ac:rich-text-body><p>...</p></ac:rich-text-body></ac:structured-macro>'''

confluence_create_page(space_key="DEV", title="Runbook: Checkout",
                       content=body, parent_id="12345")

# Обновление: сначала прочитать текущую версию
# page = json.loads(confluence_get_page(title="Runbook: Checkout", space_key="DEV"))
# confluence_update_page(page_id=page["id"], title=page["title"],
#                        content=новый_body)  # версия инкрементится автоматически
```

Ограничения: страница — единый документ; вложения загружаются отдельно
(через UI или REST `/rest/api/content/{id}/child/attachment`); в
`confluence_update_page` передавайте полный новый body, а не дифф.
