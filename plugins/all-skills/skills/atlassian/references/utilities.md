# Atlassian utilities: functions, signatures, response shapes

Moved out of `SKILL.md` to keep it under 500 lines. Import paths are relative to the skill root (`scripts.*`).

## Available Utilities

### Jira Issue Management (`scripts.jira_issues`)

```python
from scripts.jira_issues import (
    jira_get_issue,      # Get issue by key
    jira_create_issue,   # Create new issue
    jira_update_issue,   # Update existing issue
    jira_delete_issue,   # Delete issue
    jira_add_comment     # Add comment to issue
)

# Create issue with full options
jira_create_issue(
    project_key="PROJ",
    summary="Bug fix",
    issue_type="Bug",
    description="Description",
    assignee="user@company.com",
    priority="High",
    labels=["urgent", "backend"],
    custom_fields={
        "customfield_10001": "Custom value",
        "customfield_10002": 123
    }
)
```

### Jira Search (`scripts.jira_search`)

```python
from scripts.jira_search import jira_search, jira_search_fields

# Search with JQL
jira_search(
    jql="project = PROJ AND status = 'In Progress'",
    fields="summary,status,assignee",
    limit=50
)

# Find field definitions
jira_search_fields(keyword="custom")
```

### Jira Workflow (`scripts.jira_workflow`)

```python
from scripts.jira_workflow import jira_get_transitions, jira_transition_issue

# Get available transitions
jira_get_transitions(issue_key="PROJ-123")

# Transition issue to new status
jira_transition_issue(
    issue_key="PROJ-123",
    transition_id="31",
    comment="Moving to review"
)
```

### Jira Agile (`scripts.jira_agile`)

```python
from scripts.jira_agile import (
    jira_get_agile_boards,
    jira_get_sprints_from_board,
    jira_get_sprint_issues,
    jira_create_sprint,
    jira_update_sprint
)

# Get boards
jira_get_agile_boards(project_key="PROJ")

# Get active sprints
jira_get_sprints_from_board(board_id=1, state="active")

# Create new sprint
jira_create_sprint(
    board_id=1,
    sprint_name="Sprint 5",
    start_date="2024-01-15",
    end_date="2024-01-29",
    goal="Complete feature X"
)
```

### Jira Links (`scripts.jira_links`)

```python
from scripts.jira_links import (
    jira_get_link_types,
    jira_create_issue_link,
    jira_link_to_epic,
    jira_remove_issue_link
)

# Link issues
jira_create_issue_link(
    link_type="Blocks",
    inward_issue_key="PROJ-123",
    outward_issue_key="PROJ-456"
)

# Link to epic
jira_link_to_epic(issue_key="PROJ-123", epic_key="PROJ-100")
```

### Jira Worklog (`scripts.jira_worklog`)

```python
from scripts.jira_worklog import jira_get_worklog, jira_add_worklog

# Add time spent
jira_add_worklog(
    issue_key="PROJ-123",
    time_spent="2h 30m",
    comment="Code review"
)
```

### Jira Projects (`scripts.jira_projects`)

```python
from scripts.jira_projects import (
    jira_get_all_projects,
    jira_get_project_issues,
    jira_get_project_versions,
    jira_create_version
)

# Get all projects
jira_get_all_projects()

# Create version
jira_create_version(
    project_key="PROJ",
    name="v2.0.0",
    release_date="2024-03-01"
)
```

### Confluence Pages (`scripts.confluence_pages`)

```python
from scripts.confluence_pages import (
    confluence_get_page,
    confluence_create_page,
    confluence_update_page,
    confluence_delete_page
)

# Get page by title
confluence_get_page(title="Meeting Notes", space_key="TEAM")

# Create page with parent
confluence_create_page(
    space_key="DEV",
    title="API Documentation",
    content="<h1>API Docs</h1><p>Content here</p>",
    parent_id="12345"
)

# Update page
confluence_update_page(
    page_id="67890",
    title="Updated Title",
    content="<p>New content</p>"
)
```

### Confluence Search (`scripts.confluence_search`)

```python
from scripts.confluence_search import confluence_search

# Search with CQL
confluence_search(
    query="space = DEV AND type = page AND text ~ 'API'",
    limit=25
)
```

### Confluence Comments (`scripts.confluence_comments`)

```python
from scripts.confluence_comments import confluence_get_comments, confluence_add_comment

# Add comment
confluence_add_comment(
    page_id="12345",
    content="Great documentation!"
)
```

### Confluence Labels (`scripts.confluence_labels`)

```python
from scripts.confluence_labels import (
    confluence_get_labels,
    confluence_add_label,
    confluence_remove_label
)

# Manage labels
confluence_add_label(page_id="12345", name="reviewed")
confluence_remove_label(page_id="12345", name="draft")
```

### Bitbucket Projects (`scripts.bitbucket_projects`)

```python
from scripts.bitbucket_projects import (
    bitbucket_list_projects,
    bitbucket_list_repositories
)

# List all projects
bitbucket_list_projects(limit=25)

# List repositories in a project
bitbucket_list_repositories(project_key="PROJ", limit=50)
```

### Bitbucket Pull Requests (`scripts.bitbucket_pull_requests`)

```python
from scripts.bitbucket_pull_requests import (
    bitbucket_create_pull_request,
    bitbucket_get_pull_request,
    bitbucket_merge_pull_request,
    bitbucket_decline_pull_request,
    bitbucket_add_pr_comment,
    bitbucket_get_pr_diff
)

# Create a pull request
bitbucket_create_pull_request(
    project_key="PROJ",
    repository_slug="my-repo",
    title="Feature: Add new API",
    source_branch="feature/new-api",
    target_branch="master",
    description="Implements the new API endpoint",
    reviewers=["john.doe", "jane.smith"]
)

# Get PR details
bitbucket_get_pull_request(
    project_key="PROJ",
    repository_slug="my-repo",
    pr_id=123
)

# Merge PR (version from get_pull_request)
bitbucket_merge_pull_request(
    project_key="PROJ",
    repository_slug="my-repo",
    pr_id=123,
    version=5,
    strategy="squash"
)

# Add comment to PR
bitbucket_add_pr_comment(
    project_key="PROJ",
    repository_slug="my-repo",
    pr_id=123,
    text="LGTM!"
)
```

### Bitbucket Files & Search (`scripts.bitbucket_files`)

```python
from scripts.bitbucket_files import (
    bitbucket_get_file_content,
    bitbucket_search
)

# Get file content
bitbucket_get_file_content(
    project_key="PROJ",
    repository_slug="my-repo",
    file_path="src/main.py",
    branch="develop"
)

# Search code
bitbucket_search(
    query="def authenticate",
    project_key="PROJ",
    search_type="code",
    limit=25
)
```

### Bitbucket Commits (`scripts.bitbucket_commits`)

```python
from scripts.bitbucket_commits import (
    bitbucket_get_commits,
    bitbucket_get_commit
)

# Get recent commits from a branch
bitbucket_get_commits(
    project_key="PROJ",
    repository_slug="my-repo",
    branch="master",
    limit=10
)

# Get details of a specific commit
bitbucket_get_commit(
    project_key="PROJ",
    repository_slug="my-repo",
    commit_id="1da11eaec25aed8b251de24841885c91493b3173"
)
```

### Jira Users (`scripts.jira_users`)

```python
from scripts.jira_users import jira_get_user_profile

# Get Jira user profile
jira_get_user_profile(
    user_identifier="user@company.com",
    credentials=credentials  # Optional
)
```

## Function Signature Pattern

All skill functions follow this signature pattern:

```python
def skill_function(
    required_param1: str,
    required_param2: str,
    optional_param: Optional[str] = None,
    credentials: Optional[AtlassianCredentials] = None  # Always last parameter
) -> str:
    """Function description.
    
    Args:
        required_param1: Description
        required_param2: Description
        optional_param: Description (optional)
        credentials: Optional AtlassianCredentials for Agent environments.
                    If not provided, uses environment variables.
    
    Returns:
        JSON string with result or error information
    """
```

The `credentials` parameter is:
- **Optional**: If not provided, configuration loads from environment variables
- **Always the last parameter**: Maintains consistent function signatures
- **Backward compatible**: Existing code without credentials parameter continues to work

## Response Data Structures

All functions return JSON strings with **flattened** data structures (not nested API responses).

### Jira Issue Structure

```json
{
  "key": "PROJ-123",
  "id": "10001",
  "summary": "Issue title",
  "description": "Issue description",
  "status": "In Progress",
  "issue_type": "Task",
  "priority": "High",
  "assignee": "user@company.com",
  "reporter": "reporter@company.com",
  "created": "2024-01-15T10:30:00.000+0000",
  "updated": "2024-01-16T14:20:00.000+0000",
  "labels": ["backend", "urgent"],
  "components": ["API", "Auth"],
  "custom_fields": {}
}
```

### Confluence Page Structure

```json
{
  "id": "12345",
  "title": "Page Title",
  "space_key": "DEV",
  "status": "current",
  "created": "2024-01-15T10:30:00.000Z",
  "updated": "2024-01-16T14:20:00.000Z",
  "author": "user@company.com",
  "version": 3,
  "url": "https://company.atlassian.net/wiki/spaces/DEV/pages/12345"
}
```

> **Note**: These are simplified structures. The original Jira API returns nested data like `{"key": "...", "fields": {"summary": "...", "status": {"name": "..."}}}`, but this skill flattens it for easier use.
