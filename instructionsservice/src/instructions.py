import datetime
import json
import logging
from collections import defaultdict
from os import environ as env

import requests
from dateutil import parser, rrule
from dateutil.rrule import DAILY, WEEKLY, MONTHLY, YEARLY
from flask import Blueprint, jsonify, abort

from models import Overview, Step
from models import db
from queries import get_overviews_by_date, get_incoming_daily, get_all_daily, get_previous_daily

logger = logging.getLogger(__name__)
instructions = Blueprint('instructions', __name__)

COMPUTE_SERVICE_IP = env['COMPUTE_SERVICE_IP'] if 'COMPUTE_SERVICE_IP' in env else 'localhost'
COMPUTE_SERVICE_PORT = int(env['COMPUTE_SERVICE_PORT']) if 'COMPUTE_SERVICE_PORT' in env else 5000
COMPUTE_SERVICE_URL = f"http://{COMPUTE_SERVICE_IP}:{COMPUTE_SERVICE_PORT}/compute"
COMPUTE_SERVICE_DURATION_URL = f"http://{COMPUTE_SERVICE_IP}:{COMPUTE_SERVICE_PORT}/duration"

TRANSIT_VEHICLES = frozenset(['bus', 'subway', 'train', 'tram', 'walking'])
DRIVING_VEHICLES = frozenset(['car', 'taxi', 'enjoy', 'motorbike'])
CYCLING_VEHICLES = frozenset(['bike', 'mobike'])
VEHICLES = TRANSIT_VEHICLES | DRIVING_VEHICLES | CYCLING_VEHICLES
VEHICLES_MAPPING = {
    'transit': TRANSIT_VEHICLES,
    'driving': DRIVING_VEHICLES,
    'bicycling': CYCLING_VEHICLES
}
FREQUENCIES_MAPPING = {
    'DAILY': DAILY,
    'WEEKLY': WEEKLY,
    'MONTHLY': MONTHLY,
    'YEARLY': YEARLY
}


def pick_instruction(ls):
    """
    Choose an instruction from the ones given.
    Picks the one that leads to the goal in less time.
    """
    try:
        return min(ls, key=lambda x: x['duration'])
    except ValueError:  # min is empty sequence:
        return None


def satisfies_preferences(instruction, calendar_preferences, date):
    """
    Whether this instruction satisfies global and calendar preferences or not
    """
    constraints = {'TRANSIT': defaultdict(lambda: {'mileage': None, 'time': (None, None)}),
                   'DRIVING': {'mileage': None, 'time': (None, None)},
                   'CYCLING': {'mileage': None, 'time': (None, None)},
                   'WALKING': {'mileage': None, 'time': (None, None)}}
    for preference in calendar_preferences:
        if preference['time']:
            constraint_start = datetime.datetime.strptime(preference['time'][0], "%H:%M").replace(
                day=date.day,
                month=date.month,
                year=date.year
            )
            constraint_end = datetime.datetime.strptime(preference['time'][1], "%H:%M").replace(
                day=date.day,
                month=date.month,
                year=date.year
            )
        else:
            constraint_start = constraint_end = None
        for mode, vehicles in VEHICLES_MAPPING.items():
            if preference['name'] in vehicles:
                constraint = {'time': (constraint_start, constraint_end), 'mileage': preference['mileage']}
                if mode == 'transit':
                    constraints['TRANSIT'][preference['name']] = constraint
                else:
                    constraints[mode.upper()] = constraint
    for step in instruction['steps']:
        if step['travel_mode'] == 'TRANSIT':
            constraint = constraints['TRANSIT'][step.get('type', 'walking').lower()]
            try:
                step_start = parser.parse(step['departure_time'])
                step_end = parser.parse(step['arrival_time'])
                # noinspection PyTypeChecker
                # if a constraint time is specified and the instructions fall into the constraint window return False
                if constraint['time'][0] and not (step_start < constraint['time'][0] or step_end > constraint['time'][1]):
                    logger.info(f"Time constraint violated. Invalidating solution")
                    return False
            except KeyError:
                pass
        else:
            constraint = constraints[step['travel_mode']]
        if constraint['mileage']:
            constraint['mileage'] -= step['distance']
            if constraint['mileage'] <= 0:
                logger.warning("Mileage constraint violated. Invalidating solution.")
                return False
    return True


def yield_recurrences(event):
    start_time, end_time = (parser.parse(event[t]) for t in ('start_time', 'end_time'))
    try:
        freq = FREQUENCIES_MAPPING[event['recurrence_rule']]
        start_times = list(
            rrule.rrule(freq=freq, until=parser.parse(event.get('until', start_time)), dtstart=start_time))
        end_times = list(rrule.rrule(freq=freq, count=len(start_times), dtstart=end_time))
        for s, e in zip(start_times, end_times):
            yield {**event, **{'start_time': s, 'end_time': e}}
    except KeyError:  # recurrence is normal, but still need to modify event start and end time
        yield {**event, **{'start_time': start_time, 'end_time': end_time}}


def fix_arrival_time(event, data):
    """Returns a new arrival time for this event by performing calculations on the flex option"""
    flex = event['flex_duration']
    logger.info(f"Flex duration: {flex}")
    if flex is None:
        return event['start_time']  # flex disabled, arrival time remains the same
    # time in seconds needed to reach the event just in time
    try:
        time_to = requests.get(COMPUTE_SERVICE_DURATION_URL, params=data).json()
        next_overview = list(get_incoming_daily(event['user_id'], event['start_time']))[0]
        new_data = {
            'origin': ','.join(str(x) for x in event['location']),
            'destination': ','.join(str(x) for x in (next_overview.end_lat, next_overview.end_lng)),
            'mode': data['mode'],
            'arrival_time': int(next_overview.start_date.timestamp())
        }
        # time in seconds needed to reach the event AFTER the flex one just in time
        time_from = requests.get(COMPUTE_SERVICE_DURATION_URL, params=new_data).json()
        # Calculate if this event can be reached in time by putting it at the end of the flex window
        previous_overviews = list(get_previous_daily(event['user_id'], event['start_time']))
        previous_date = previous_overviews[-1].end_date if previous_overviews else \
            event['start_time'].replace(hour=0, minute=0, second=0)
        perfect_arrival_date = max(previous_date + datetime.timedelta(seconds=time_to), event['start_time'])
        # I can't reach it if I cannot consume the flex duration entirely by arriving as soon as I can
        can_reach = perfect_arrival_date + datetime.timedelta(seconds=flex) <= event['end_time']
        # Calculate if user can departure in time from this event without arriving late to the next one
        perfect_departure_date = min(next_overview.start_date - datetime.timedelta(seconds=time_from),
                                     event['start_time'] + datetime.timedelta(seconds=flex))
        # I can't leave it in time if by departuring as late as I can I still cannot consume the flex duration
        can_leave = event['start_time'] + datetime.timedelta(seconds=flex) <= perfect_departure_date
        if can_reach or not can_leave:
            # if this event can be reached in time, set the arrival time accordingly (regardless of can_leave).
            # By default, this option is returned if the event cannot be left in time as well
            return perfect_arrival_date
        else:
            # Otherwise, at least try to not raise a warning for the next event
            return perfect_departure_date - datetime.timedelta(seconds=flex)
    except (IndexError, json.decoder.JSONDecodeError):
        # no incoming overviews, event can be allocated freely inside the flex window
        # leaving it at the end of the window is the most reasonable option if it's unreachable (JSONDecodeError)
        return event['end_time'] - datetime.timedelta(seconds=flex)


def get_trip_origin(calendar, event):
    event_start = event['start_time']
    day_start = event_start.replace(hour=0, minute=0, second=0, year=1995)
    # gets overviews in the same day but that happen before the event passed as parameter
    overviews = get_overviews_by_date(event['user_id'], day_start, event_start)
    logger.info(f"Overviews found previously on the same day for this event: {overviews}")
    if not overviews:  # no overviews found on the same day for this user
        return calendar.base
    else:
        previous = max(overviews, key=lambda o: o.start_date)  # picks latest event
        logger.info(f"Latest event found: {previous}")
        return previous.end_lat, previous.end_lng


def fix_next_trip(global_preferences, calendar, event, id):
    logger.info("Fixing overviews for the very next event..")
    event_end = event['end_time']
    overviews = get_incoming_daily(event['user_id'], event_end)
    if not overviews:  # there isn't any event after this one in the given day
        logger.info("No trip found after the inserted one.")
        # insert a new return instruction only if user wants to go back to base
        fix_return_instruction(global_preferences, calendar, event_end, event['id'], id,
                               insert_new=event['next_is_base'])
    else:
        earliest = min(overviews, key=lambda o: o.start_date)
        update_event_instructions(global_preferences, calendar, earliest)


def update_event_instructions(global_preferences, calendar, event, **kwargs):
    new_event = {
        'location': kwargs.get('location', (event.end_lat, event.end_lng)),
        'start_time': kwargs.get('start_time', event.start_date),
        'end_time': kwargs.get('end_time', event.end_date),
        'id': kwargs.get('id', event.event_id),
        'user_id': kwargs.get('user_id', event.user_id),
        'calendar_id': kwargs.get('calendar_id', event.calendar_id),
        'flex_duration': kwargs.get('flex_duration', event.flex_duration),
        'next_is_base': kwargs.get('next_is_base', event.next_is_base)
    }
    db.session.delete(event)
    db.session.commit()
    logger.info(f"Updating travel instructions for event: {event}. Deleted old instance..")
    logger.info(f"eventid: {event.event_id}")
    logger.info(Overview.query.get((1, 1, 1, 2, True)))
    calculate_instruction(global_preferences, calendar, new_event, event.id, fix_next=False)


def fix_return_instruction(global_preferences, calendar, new_start, event_id, id, insert_new=True):
    logger.info(f"Fixing return instruction.")
    base_instructions = get_all_daily(global_preferences.user_id, new_start, return_only=True)
    if base_instructions:  # instruction that brings back to base is already calculated, need to delete it
        db.session.delete(base_instructions[0])
        db.session.commit()
        logger.info("Deleted old base instruction.")
    if insert_new:
        logger.info("Inserting new base instruction")
        return_event = {
            'name': "Return event",
            'location': calendar.base,
            'start_time': new_start,
            'end_time': new_start.replace(hour=23, minute=59, second=59),
            'user_id': global_preferences.user_id,
            'calendar_id': calendar.id,
            'id': event_id,
            'flex_duration': None,
            'next_is_base': False
        }
        calculate_instruction(global_preferences, calendar, return_event, id, departure=False, fix_next=False)


def calculate_instruction(global_preferences, calendar, event, id, departure=True, fix_next=True):
    logger.info(f"eventid: {id}")
    logger.info(f"Calculating instruction for event {event}")
    db.session.commit()
    logger.info(f"Global: {global_preferences}, Calendar: {calendar.preferences}")
    personal_vehicles = {pv['name']: {'type': pv['type']} for pv in global_preferences.personal_vehicles}
    active_vehicles = set(vehicle_info['name'] if vehicle_info['name'] in VEHICLES else
                          personal_vehicles[vehicle_info['name']]['type'] for vehicle_info in calendar.preferences)
    overviews = []
    for mode, vehicles in VEHICLES_MAPPING.items():
        if active_vehicles & vehicles:  # if at least one travel mean is in the intersection, ask for directions
            event['start_time'] += datetime.timedelta(milliseconds=1)
            data = {
                'origin': ','.join(str(x) for x in get_trip_origin(calendar, event)),
                'destination': ','.join(str(x) for x in event['location']),
                'mode': mode,
                # if this trip is the one that goes back to base, departure time is set instead
                'arrival_time' if departure else 'departure_time': int(event['start_time'].timestamp())
            }
            if departure:
                data['arrival_time'] = int(fix_arrival_time(event, data).timestamp())
            # travel compute service returns a list of overviews
            response = requests.get(COMPUTE_SERVICE_URL, params=data).json()
            response = [{**r, **{'true_start': datetime.datetime.fromtimestamp(data['arrival_time' if departure else 'departure_time'])}}
                        for r in response]
            # keep only the instructions that satisfy the preferences
            overviews.extend([overview for overview in response
                              if satisfies_preferences(overview, calendar.preferences, event['start_time'])])
    instruction = pick_instruction(overviews)
    logger.info(event)
    add_instruction(instruction, id=id, user_id=event['user_id'], calendar_id=event['calendar_id'],
                    event_id=event['id'], start_date=event['start_time'], end_date=event['end_time'],
                    departure=departure, reachable=True, next_is_base = event['next_is_base'],
                    location=event['location'], flex_duration=event['flex_duration'])
    if fix_next:
        fix_next_trip(global_preferences, calendar, event, id)


def add_instruction(instruction, **kwargs):
    """
    Adds a travel instruction to the database.
    """
    logger.info(f"Adding instruction to database: {kwargs}")
    end_lat, end_lng = kwargs.pop('location')
    if not instruction:  # inserts an empty instruction in the db with the reachable flag set to false
        warning_overview = Overview(**{**kwargs, **{'reachable': False, 'end_lat': end_lat, 'end_lng': end_lng}})
        db.session.add(warning_overview)
        db.session.commit()
        logger.info(f"Added unreachable instruction: {warning_overview}")
        return
    previous_overviews = list(get_overviews_by_date(kwargs['user_id'], kwargs['start_date'].replace(year=1995),instruction['true_start'] - datetime.timedelta(seconds=1)))
    logger.info(previous_overviews)
    previous_date = previous_overviews[-1].end_date if previous_overviews else datetime.datetime.now()
    # If the event is not a return instruction and cannot be reached in time from the previous event mark unreachable
    if previous_date + datetime.timedelta(seconds=instruction['duration']) > instruction['true_start'] and kwargs['departure']:
        kwargs['reachable'] = False
        logger.warning(f"Instruction has been marked as unreachable.")
    steps = instruction.pop('steps')
    instruction.pop('true_start')
    overview = Overview(**{**instruction, **kwargs})
    del kwargs['start_date'], kwargs['end_date'], kwargs['departure'], kwargs['flex_duration'], kwargs['reachable'], kwargs['next_is_base']
    for i, step in enumerate(steps):
        if step['travel_mode'] == 'TRANSIT':  # gets datetime objects from strings, only present in transit
            try:
                step['departure_time'] = parser.parse(step['departure_time'])
                step['arrival_time'] = parser.parse(step['arrival_time'])
            except KeyError:
                pass
        step['event_id'] = kwargs['id']
        step['id'] = i
        step = Step(**{**kwargs, **step}, overview=overview)
        db.session.add(step)
    db.session.add(overview)
    db.session.commit()
    logger.info(f"Stored instruction {overview}: {overview.start_address} -> {overview.end_address}")


@instructions.route(
    '/users/<int:user_id>/calendars/<int:calendar_id>/events/<int:event_id>/recurrence/<int:recurrence_id>/instruction',
    methods=['GET'])
def get_instruction(user_id, calendar_id, event_id, recurrence_id):
    """
    Retrieves a saved travel instruction that matches the combinations of id given.
    """
    result = Overview.query.get((recurrence_id, user_id, calendar_id, event_id, True))
    if not result:
        abort(404)
    overview = result.as_dict()
    steps = sorted(Step.query.filter_by(user_id=user_id,
                                        calendar_id=calendar_id,
                                        event_id=event_id,
                                        overview_id=recurrence_id,
                                        departure=True).all(), key=lambda step: step.id)
    output = {'overview': overview, 'steps': []}
    for step in steps:
        s = step.as_dict()
        s['travel_mode'] = str(s['travel_mode'])
        s['type'] = str(s.get('type', ''))
        output['steps'].append(s)
    return jsonify(output)


@instructions.route(
    '/users/<int:user_id>/calendars/<int:calendar_id>/events/<int:event_id>/recurrence/<int:recurrence_id>/return', methods=['GET'])
def get_recurrence(user_id, calendar_id, event_id, recurrence_id):
    """
    Retrieves a saved travel instruction that matches the combinations of id given.
    """
    result = Overview.query.get((recurrence_id, user_id, calendar_id, event_id, False))
    if not result:
        abort(404)
    overview = result.as_dict()
    steps = sorted(Step.query.filter_by(user_id=user_id,
                                        calendar_id=calendar_id,
                                        event_id=event_id,
                                        overview_id=recurrence_id,
                                        departure=False).all(), key=lambda step: step.id)
    output = {'overview': overview, 'steps': []}
    for step in steps:
        s = step.as_dict()
        s['travel_mode'] = str(s['travel_mode'])
        s['type'] = str(s.get('type', ''))
        output['steps'].append(s)
    return jsonify(output)