"""
Generic HTML template rendering via Jinja2. Knows nothing about emails,
alerts, or auth — just "how to turn a .html file + some values into a
final string", same generic role core/email.py plays for SMTP.
"""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader

_templates_dir = Path(__file__).resolve().parent.parent / "templates" / "emails"
_env = Environment(loader=FileSystemLoader(_templates_dir), autoescape=True)


def render_template(template_name: str, **context) -> str:
    """Renders a file from templates/emails/ with the given values.
    Ex: render_template("alert_down.html", monitor_name="API", status_code=500)
    """
    template = _env.get_template(template_name)
    return template.render(**context)
