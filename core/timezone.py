from timezonefinder import TimezoneFinder
from datetime import datetime, timezone, timedelta, date
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

tf = TimezoneFinder()


def find_time_zone(lat, lon):
    '''
    Находит IANA имя часового пояса по координатам.
    Или ближайший, если точный не найден.
    '''
    tz_name = tf.timezone_at(lng=lon, lat=lat)
    if tz_name is None:
        # Попробуем ближайшую точку
        tz_name = tf.closest_timezone_at(lng=lon, lat=lat)

    return tz_name

def tz_from_string(string: str) -> timezone:
    """
    Преобразует сохранённую строку в tzinfo.
    Поддерживает:
      - IANA имена, например "Europe/Chisinau"
      - смещения вида "+03:00" или "-04:30"
    При ошибке возвращает timezone.utc (fallback).
    """
    if not string:
        return timezone.utc

    s = string.strip()
    # Относительное время
    if (len(s) == 6 and (s[0] == '+' or s[0] == '-') and s[3] == ':' and s[1:3].isdigit() and s[4:6].isdigit()):
        try:
            sign = 1 if s[0] == '+' else -1
            hh = int(s[1:3])
            mm = int(s[4:6])
            return timezone(timedelta(hours=sign*hh, minutes=sign*mm))
        except Exception:
            return timezone.utc

    # Временные области IANA
    try:
        return ZoneInfo(s)
    except ZoneInfoNotFoundError:
        # fallback
        return timezone.utc
    except Exception:
        return timezone.utc