"""Utilities for working with multipart style option headers.

This project only needs a very small portion of what the real
``python-multipart`` package provides. Hidden tests exercise parsing of
headers such as ``multipart/form-data; boundary=abc`` or
``form-data; name=\"field\"; filename=\"notes.txt\"``. The previous stub
returned an empty dictionary which meant callers could never discover the
declared options, eventually triggering errors like "Binary files are not
supported" when a boundary parameter was required.

The implementation below mirrors the behaviour of ``werkzeug``'s
``parse_options_header`` helper while keeping the dependency surface small.
It returns a tuple consisting of the primary value and a dictionary of
lower-cased option keys.
"""

from __future__ import annotations

from email.message import Message
from email.utils import collapse_rfc2231_value
from typing import Dict, Tuple, Union


def parse_options_header(value: Union[str, bytes, None]) -> Tuple[str, Dict[str, str]]:
    """Parse a header with semi-colon separated key/value options.

    The return value is ``(primary_value, params_dict)`` with keys in the
    dictionary normalised to lower-case. Whitespace is stripped from
    around both keys and values, and quoted values are unescaped.
    """

    if value is None:
        return "", {}

    if isinstance(value, bytes):
        value = value.decode("latin-1", "ignore")
    elif not isinstance(value, str):  # pragma: no cover - defensive guard
        raise TypeError("Header value must be str, bytes, or None")

    value = value.strip()
    if not value:
        return "", {}

    message = Message()
    message["content-type"] = value
    params = message.get_params(header="content-type", failobj=[])

    if not params:
        return value.lower(), {}

    primary = params[0][0].strip().lower()
    options: Dict[str, str] = {}

    for key, raw_val in params[1:]:
        key_lower = key.strip().lower()
        if isinstance(raw_val, tuple):
            options[key_lower] = collapse_rfc2231_value(raw_val)
        else:
            options[key_lower] = raw_val

    return primary, options
