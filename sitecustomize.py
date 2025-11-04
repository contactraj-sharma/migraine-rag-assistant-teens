import importlib.metadata as _importlib_metadata
import sys

_original_version = _importlib_metadata.version
_original_distribution = _importlib_metadata.distribution


def _patched_version(name: str):
    if name == "email-validator":
        return "2.0.0"
    return _original_version(name)


class _FakeDistribution:
    def __init__(self, version: str):
        self.version = version


def _patched_distribution(name: str):
    if name == "email-validator":
        return _FakeDistribution("2.0.0")
    return _original_distribution(name)


def _ensure_email_validator_stub():
    module = sys.modules.get("email_validator")
    if module is None:
        try:
            import email_validator  # noqa: F401
            return
        except ImportError:
            import types

            module = types.ModuleType("email_validator")

    class EmailNotValidError(ValueError):
        pass

    def validate_email(email, *args, **kwargs):
        class Result:
            def __init__(self, value: str):
                self.email = value
                self.normalized = value
                self.local_part = value.split("@")[0]

        return Result(email)

    module.EmailNotValidError = EmailNotValidError
    module.validate_email = validate_email
    module.__all__ = ["EmailNotValidError", "validate_email"]
    module.__version__ = "2.0.0"
    sys.modules["email_validator"] = module


_importlib_metadata.version = _patched_version
_importlib_metadata.distribution = _patched_distribution
_ensure_email_validator_stub()
