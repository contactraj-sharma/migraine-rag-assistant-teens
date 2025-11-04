class EmailNotValidError(ValueError):
    pass


def validate_email(email, *args, **kwargs):
    class Result:
        def __init__(self, value: str):
            self.email = value
            self.normalized = value
            self.local_part = value.split("@")[0]

    return Result(email)
