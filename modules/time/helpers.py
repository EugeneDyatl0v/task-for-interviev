import datetime


def get_utc_now() -> datetime.datetime:
    return datetime.datetime.now(datetime.UTC).replace(tzinfo=None)


def get_from_utc_now_on_delta(**kwargs) -> datetime.datetime:
    return (
        datetime.datetime.now(datetime.UTC).replace(tzinfo=None)
        + datetime.timedelta(**kwargs)
    )
