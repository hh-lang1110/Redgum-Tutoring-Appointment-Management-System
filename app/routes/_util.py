"""Small helpers shared by the route modules."""
from urllib.parse import urljoin, urlparse

from flask import request


def safe_redirect_target(target, fallback):
    """Return ``target`` when it points back at this site, else ``fallback``.

    Used where a form hands control back to whatever page submitted it. The
    Referer header is attacker-controlled, so redirecting to it unchecked
    turns the endpoint into an open redirect: a link to this site can bounce
    the visitor on to somewhere else, which is what makes a phishing URL look
    trustworthy. Anything not resolving to this host is discarded.
    """
    if not target:
        return fallback
    host = urlparse(request.host_url)
    candidate = urlparse(urljoin(request.host_url, target))
    if candidate.scheme in ("http", "https") and candidate.netloc == host.netloc:
        return target
    return fallback
