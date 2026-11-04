"""Template rendering helper ensuring cross-version Starlette compatibility."""

from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


def render_template(
    templates: Jinja2Templates,
    request: Request,
    name: str,
    context: dict,
    status_code: int = 200,
) -> HTMLResponse:
    """Render a Jinja2 template compatibly across Starlette <0.28 and >=0.28 / 1.x."""
    try:
        # Starlette >= 0.28 and 1.x (supports request keyword argument)
        return templates.TemplateResponse(
            request=request,
            name=name,
            context=context,
            status_code=status_code,
        )
    except TypeError:
        # Starlette < 0.28 (name first, context second)
        return templates.TemplateResponse(
            name,
            context,
            status_code=status_code,
        )
