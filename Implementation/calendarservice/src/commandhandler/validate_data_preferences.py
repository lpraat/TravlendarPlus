# default available vehicles
available_vehicles = ['bus', 'subway', 'train', 'tram', 'car', 'walking', 'bike', 'taxi', 'enjoy', 'mobike']


def validate_type(type):
    """
    :param type: the personal vehicle type.
    :return: if the personal vehicle type is valid.
    """
    return type in ('car', 'bike', 'motorbike')


def validate_location(location):
    """
    :param location: the pair to be checked.
    :return: true if the lat/long pair of coordinates are valid.
    """
    if (isinstance(location, tuple) or isinstance(location, list)) and len(location) == 2:
        latitude = location[0]
        longitude = location[1]
        return (-90 <= latitude <= 90) and (-180 <= longitude <= 180)
    return False


def validate_personal_vehicle(global_preferences):
    """
    :param global_preferences: the global preferences
    :return: true if the personal vehicles in the global preferences are formed correctly false otherwise
    """
    if 'personal_vehicles' in global_preferences:
        personal_vehicles = global_preferences['personal_vehicles']

        names = []

        for personal_vehicle in personal_vehicles:
            if not set(personal_vehicle) == {'name', 'type', 'location', 'active'} or \
                    not validate_type(personal_vehicle['type']) or \
                    not validate_location(personal_vehicle['location']) or \
                    not isinstance(personal_vehicle['active'], bool):
                return False

            name = personal_vehicle['name']
            if name in names:
                return False
            names.append(name)

    return True


def validate_vehicles(global_preferences):
    """
    :return: true if the vehicles in global preferences are in the available ones false otherwise
    """
    if 'vehicles' in global_preferences:
        vehicles = global_preferences['vehicles']
        for vehicle in vehicles:
            if vehicle not in available_vehicles:
                return False
    return True


def validate_structure(global_preferences):
    return 'vehicles' in global_preferences or 'personal_vehicles' in global_preferences


def validate_global_preferences(global_preferences):
    """
    :param global_preferences: the global preferences.
    :return: true if the global preferences are valid.
    """
    return set(global_preferences) <= {'vehicles', 'personal_vehicles'} and \
           validate_structure(global_preferences) and \
           validate_vehicles(global_preferences) and \
           validate_personal_vehicle(global_preferences)
