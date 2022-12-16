from datetime import datetime, tzinfo
from typing import Optional, cast

import pytz
from decouple import config

_timezone: Optional[tzinfo] = None


def get_timezone() -> tzinfo:
    global _timezone

    if _timezone is None:
        timezone_name = config(
            'TIMEZONE',
            default='system'
        )

        # If configured to use system timezone, use system timezone
        if timezone_name != 'system':
            _timezone = pytz.timezone(timezone_name)
        else:
            _timezone = datetime.now().astimezone().tzinfo

    return _timezone


def time_now(string: bool = False) -> datetime:
    time = datetime.now(tz=get_timezone())

    return time if not string else format_time(time)


def time_now_str() -> str:
    return cast(str, time_now(string=True))


def format_time(time: datetime) -> str:
    return time.isoformat()
