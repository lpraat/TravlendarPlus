import datetime

from dateutil.rrule import DAILY, WEEKLY, MONTHLY, YEARLY
from dateutil.rrule import rrule

from src.utils import strptime, generate_occurrences

# mapping between the recurrence rules and the event maximum accepted duration
RRULE = {
    'DAILY': {
        'name': DAILY,
        'max_duration': datetime.timedelta(seconds=86400).total_seconds()
    },
    'WEEKLY': {
        'name': WEEKLY,
        'max_duration': datetime.timedelta(seconds=86400 * 6).total_seconds()
    },
    'MONTHLY': {
        'name': MONTHLY,
        'max_duration': datetime.timedelta(seconds=86400 * 6 * 20).total_seconds(),
    },
    'YEARLY': {
        'name': YEARLY,
        'max_duration': datetime.timedelta(seconds=86400 * 6 * 20 * 11).total_seconds()
    }
}


def is_valid_time(t):
    try:
        return strptime(t)
    except:
        return None


def are_valid_times(t_start, t_end):
    t1 = is_valid_time(t_start)
    t2 = is_valid_time(t_end)

    if t1 and t2:
        return t1 < t2


def is_rrule_valid(recurrence_rule):
    return recurrence_rule in ('NORMAL', 'DAILY', 'WEEKLY', 'MONTHLY', 'YEARLY')


def is_rrule_compatible(event):
    """
    :param event: the event.
    :return: true if the recurrence rule is compatible with respect to the event duration false otherwise.
    """
    recurrence_rule = event['recurrence_rule']
    if recurrence_rule == 'NORMAL':
        return True

    if 'until' not in event or not is_valid_time(event['until']):
        return False

    start_time = strptime(event['start_time'])
    end_time = strptime(event['end_time'])
    until = strptime(event['until'])
    return (abs(start_time - end_time).total_seconds() < RRULE[recurrence_rule]['max_duration']) and \
           len([rrule(RRULE[recurrence_rule]['name'], dtstart=end_time, until=until, count=1)]) > 0


def validate_location(location):
    if (isinstance(location, tuple) or isinstance(location, list)) and len(location) == 2:
        latitude = location[0]
        longitude = location[1]
        return (-90 <= latitude <= 90) and (-180 <= longitude <= 180)
    return False


def validate_flex(event):
    """
    Checks if the event has the flex flag, if so checks if the flex duration is compatible with the event duration.
    :return: true if the event is valid according to the flex field false otherwise.
    """
    if 'flex' in event and event['flex'] is True:

        if 'flex_duration' not in event or not event['flex_duration']:
            return False

        flex_duration = datetime.timedelta(seconds=event['flex_duration']).total_seconds()

        return flex_duration < abs(strptime(event['start_time']) - strptime(event['end_time'])).total_seconds()
    return True


def validate_structure(event):
    """
    :param event: the event.
    :return: true if the event data structure is formed correctly false otherwise.
    """
    keys = ('name', 'location', 'start_time', 'end_time', 'next_is_base', 'recurrence_rule')
    for key in keys:
        if key not in set(event):
            return False
    return True


def validate_event(event):
    """
    :param event: the event.
    :return: if the event payload is formed correctly false otherwise.
    """
    return set(event) <= {'name', 'location', 'start_time', 'end_time', 'next_is_base', 'recurrence_rule', 'until',
                          'flex',
                          'flex_duration'} and \
           validate_structure(event) and are_valid_times(event['start_time'], event['end_time']) and validate_location(
        event['location']) and \
           is_rrule_valid(event['recurrence_rule']) and is_rrule_compatible(event) and validate_flex(event)


def event_can_be_inserted(event_to_check, user_schedule):
    """
    Checks if the event can be inserted in the user schedule by trying to generate all the event recurrences
    according to its recurrence rule and fitting them in the user schedule without any overlappings.
    :param event_to_check: the event.
    :param user_schedule: the user schedule.
    :return: true if the event fits in the user schedule false otherwise.
    """
    user_recurrences = []

    for calendar in user_schedule.values():
        for event in calendar['events'].values():
            for recurrence in event['recurrences'].values():
                start_time = recurrence['start_time']
                end_time = recurrence['end_time']

                user_recurrences.append((start_time, end_time))

    if event_to_check['recurrence_rule'] == 'NORMAL':
        user_recurrences.append((strptime(event_to_check['start_time']), strptime(event_to_check['end_time'])))
    else:

        rec_rule = RRULE[event_to_check['recurrence_rule']]['name']
        start_occurrences, end_occurrences = generate_occurrences(rec_rule, strptime(event_to_check['start_time']),
                                                                  strptime(event_to_check['end_time']),
                                                                  strptime(event_to_check['until']))
        for s_time, e_time in zip(start_occurrences, end_occurrences):
            user_recurrences.append((s_time, e_time))

    user_recurrences = sorted(user_recurrences)

    for i in range(1, len(user_recurrences)):
        if user_recurrences[i - 1][1] > user_recurrences[i][0]:
            return False

    return True
