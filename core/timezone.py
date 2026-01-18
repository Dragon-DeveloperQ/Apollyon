from timezonefinder import TimezoneFinder


tf = TimezoneFinder()


def find_time_zone(lat, lon):
    
    tz_name = tf.timezone_at(lng=lon, lat=lat)
    if tz_name is None:
        # Попробуем ближайшую точку
        tz_name = tf.closest_timezone_at(lng=lon, lat=lat)

    return tz_name