"""Confluence space management tools.

Tools:
    - confluence_get_spaces: Get all spaces the user has access to
    - confluence_get_space: Get a specific space by key
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from typing import Any, Dict, List, Optional

from _common import (
    AtlassianCredentials,
    get_confluence_client,
    format_json_response,
    format_error_response,
    ConfigurationError,
    AuthenticationError,
    ValidationError,
    NotFoundError,
    APIError,
    NetworkError,
)


def _simplify_space(space_data: Dict[str, Any]) -> Dict[str, Any]:
    """Simplify space data to essential fields."""
    return {
        'id': space_data.get('id', ''),
        'key': space_data.get('key', ''),
        'name': space_data.get('name', ''),
        'type': space_data.get('type', ''),
        'description': space_data.get('description', {}).get('plain', {}).get('value', ''),
        'status': space_data.get('status', ''),
        'url': space_data.get('_links', {}).get('webui', '')
    }


def confluence_get_spaces(
    space_type: Optional[str] = None,
    limit: int = 100,
    credentials: Optional[AtlassianCredentials] = None
) -> str:
    """Get all Confluence spaces the user has access to.

    Args:
        space_type: Filter by space type ('global', 'personal', 'collaboration'). Optional.
        limit: Maximum number of spaces to return (default: 100)
        credentials: Optional AtlassianCredentials object

    Returns:
        JSON string with list of spaces or error information
    """
    try:
        client = get_confluence_client(credentials)

        params = {
            'limit': limit,
            'expand': 'description.plain'
        }

        if space_type:
            params['type'] = space_type

        response = client.get('/rest/api/space', params=params)
        results = response.get('results', [])

        spaces = [_simplify_space(s) for s in results]

        return format_json_response({
            'total': len(spaces),
            'spaces': spaces
        })

    except ConfigurationError as e:
        return format_error_response('ConfigurationError', str(e))
    except AuthenticationError as e:
        return format_error_response('AuthenticationError', str(e))
    except ValidationError as e:
        return format_error_response('ValidationError', str(e))
    except NotFoundError as e:
        return format_error_response('NotFoundError', str(e))
    except (APIError, NetworkError) as e:
        return format_error_response(type(e).__name__, str(e))
    except Exception as e:
        return format_error_response('UnexpectedError', f'Unexpected error: {str(e)}')


def confluence_get_space(
    space_key: str,
    credentials: Optional[AtlassianCredentials] = None
) -> str:
    """Get a specific Confluence space by key.

    Args:
        space_key: The space key (e.g., 'DS', 'KB')
        credentials: Optional AtlassianCredentials object

    Returns:
        JSON string with space data or error information
    """
    try:
        client = get_confluence_client(credentials)

        if not space_key:
            raise ValidationError('space_key is required')

        params = {'expand': 'description.plain,permissions'}
        space_data = client.get(f'/rest/api/space/{space_key}', params=params)

        simplified = _simplify_space(space_data)

        # Add permissions info if available
        permissions = space_data.get('permissions', [])
        if permissions:
            simplified['permissions_count'] = len(permissions)

        return format_json_response(simplified)

    except ConfigurationError as e:
        return format_error_response('ConfigurationError', str(e))
    except AuthenticationError as e:
        return format_error_response('AuthenticationError', str(e))
    except ValidationError as e:
        return format_error_response('ValidationError', str(e))
    except NotFoundError as e:
        return format_error_response('NotFoundError', str(e))
    except (APIError, NetworkError) as e:
        return format_error_response(type(e).__name__, str(e))
    except Exception as e:
        return format_error_response('UnexpectedError', f'Unexpected error: {str(e)}')


def confluence_get_space_content(
    space_key: str,
    content_type: str = 'page',
    limit: int = 50,
    credentials: Optional[AtlassianCredentials] = None
) -> str:
    """Get content (pages, blogposts) from a Confluence space.

    Args:
        space_key: The space key (e.g., 'DS', 'KB')
        content_type: Type of content ('page' or 'blogpost'). Default: 'page'
        limit: Maximum number of items to return (default: 50)
        credentials: Optional AtlassianCredentials object

    Returns:
        JSON string with list of content or error information
    """
    try:
        client = get_confluence_client(credentials)

        if not space_key:
            raise ValidationError('space_key is required')

        params = {
            'spaceKey': space_key,
            'type': content_type,
            'limit': limit,
            'expand': 'version'
        }

        response = client.get('/rest/api/content', params=params)
        results = response.get('results', [])

        contents = []
        for item in results:
            contents.append({
                'id': item.get('id', ''),
                'title': item.get('title', ''),
                'type': item.get('type', ''),
                'version': item.get('version', {}).get('number', 1),
                'updated': item.get('version', {}).get('when', ''),
                'url': item.get('_links', {}).get('webui', '')
            })

        return format_json_response({
            'space_key': space_key,
            'content_type': content_type,
            'total': len(contents),
            'contents': contents
        })

    except ConfigurationError as e:
        return format_error_response('ConfigurationError', str(e))
    except AuthenticationError as e:
        return format_error_response('AuthenticationError', str(e))
    except ValidationError as e:
        return format_error_response('ValidationError', str(e))
    except NotFoundError as e:
        return format_error_response('NotFoundError', str(e))
    except (APIError, NetworkError) as e:
        return format_error_response(type(e).__name__, str(e))
    except Exception as e:
        return format_error_response('UnexpectedError', f'Unexpected error: {str(e)}')


