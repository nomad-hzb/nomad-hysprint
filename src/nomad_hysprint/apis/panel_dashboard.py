from urllib.parse import unquote

import panel as pn
from bokeh.settings import settings
from fastapi import FastAPI
from nomad.auth.tokens import get_user_from_keycloak_token
from nomad.config import config
from panel.io.fastapi import add_application

from .app import build_dashboard

settings.resources = 'inline'

panel_dashboard_api_entry_point = config.get_plugin_entry_point(
    'nomad_hysprint.apis:panel_dashboard_api_entry_point'
)

app = FastAPI(
    root_path=f'{config.services.api_base_path}/{panel_dashboard_api_entry_point.prefix}',
)


def _get_token() -> str | None:
    """Pull the access token from the session cookies (or query args)."""
    # 1. cookie "Authorization" -> "Bearer%20ey..."
    raw = pn.state.cookies.get('Authorization')
    if raw:
        return unquote(raw).removeprefix('Bearer ').strip()

    # 2. fallback: ?token=... on the initial request
    args = pn.state.session_args or {}
    if 'token' in args:
        value = args['token'][0]
        return value.decode() if isinstance(value, bytes) else value

    return None


@add_application('/', app=app)
def panel_app():
    token = _get_token()
    if not token:
        return pn.pane.Alert('Not authenticated', alert_type='danger')

    try:
        auth_res = get_user_from_keycloak_token(token)
        user = auth_res.user
    except Exception:
        return pn.pane.Alert('Invalid or expired token', alert_type='danger')
    return build_dashboard(user.user_id)
