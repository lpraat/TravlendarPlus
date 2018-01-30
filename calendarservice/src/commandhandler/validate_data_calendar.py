import datetime

from src.commandhandler.validate_data_preferences import validate_location


def validate_color(color):
    """
    Checks the list color is a valid rgb triple.
    :param color: the triple, like [0, 245, 255]
    :return: true if the color is valid false otherwise.
    """
    if isinstance(color, list):
        for c in color:
            if not (0 <= c <= 255):
                return False
        return True
    return False


def is_boolean(v):
    return isinstance(v, bool)


def only_half(t):
    return t.minute == 0 or t.minute == 30


def validate_time(t):
    """
    Checks the time constraint tuple is valid.
    :param t: the tuple to be checked.
    :return: true if the tuple is valid false otherwise.
    """
    if t is None:
        return True

    if isinstance(t, list) and len(t) == 2:
        try:

            t1 = datetime.datetime.strptime(t[0], '%H:%M').time()
            t2 = datetime.datetime.strptime(t[1], '%H:%M').time()
            return t1 < t2 and only_half(t1) and only_half(t2)

        except ValueError:
            return False

    return False


def validate_mileage(m):
    return m is None or m > 0


def validate_vehicle_preference(v):
    return validate_time(v['time']) and validate_mileage(v['mileage'])


def validate_preferences(p):
    """
    :param p: the calendar preferences
    :return: true if the calendar preferences are valid false otherwise.
    """
    for vehicle in p:
        if not (set(vehicle) == {'name', 'time', 'mileage'}) or not (
        validate_mileage(vehicle['mileage'])) or not validate_time(
                vehicle['time']):
            return False
    return True


def validate_calendar_data(d):
    """
    Validate calendar data coming from a request payload.
    :param d: the data payload.
    :return: true if the data is formed correctly false otherwise.
    """
    return {'name', 'description', 'base', 'color', 'active', 'carbon', 'preferences'} == set(d) and \
           validate_location(d['base']) and validate_color(d['color']) and is_boolean(d['active']) and \
           is_boolean(d['carbon']) and validate_preferences(d['preferences'])


def validate_calendar_preferences(p, gp):
    """
    :param p: the calendar preferences.
    :param gp: the global preferences.
    :return: true if the calendar preferences are valid with respect to the global one, false otherwise.
    """
    if 'personal_vehicles' not in gp:
        gp['personal_vehicles'] = []

    vehicles = gp['vehicles']
    personal_vehicles = gp['personal_vehicles']

    personal_vehicles_names = list(p_vehicle['name'] for p_vehicle in personal_vehicles)

    for vehicle in p:
        if vehicle['name'] not in (vehicles + personal_vehicles_names) or \
                (vehicle['name'] in personal_vehicles_names and is_personal_vehicle_inactive(vehicle['name'],
                                                                                             personal_vehicles)):
            return False
    return True


def is_personal_vehicle_inactive(vehicle_name, personal_vehicles):
    for p_vehicle in personal_vehicles:
        if p_vehicle['name'] == vehicle_name:
            if p_vehicle['active']:
                return False
            else:
                return True
