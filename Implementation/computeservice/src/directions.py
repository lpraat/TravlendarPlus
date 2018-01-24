import json
import logging
from itertools import chain, combinations_with_replacement
import googlemaps
from datetime import datetime
from flask import jsonify, request, abort
from src import compute, r
import pytz

logger = logging.getLogger(__name__)

DECIMAL_PRECISION = 4  # 3 ~ 111m, 4 ~ 11m
GOOGLE_API_KEY = 'AIzaSyDD-9297jX-PYLwVzuXtS00aVcabQFTZC0'
COORD_KEY_FORMAT = "origin_lat:{}:origin_lng:{}dest_lat:{}:dest_lng:{}:mode:{}"
STEP_KEY_FORMAT = "step:{}"

if r.dbsize() is 0:
    r.set('counter', 0)


def cache_steps(steps, ids):
    for (i, origin), (j, destination) in combinations_with_replacement(list(enumerate(steps)), 2):
        if i > j:  # can't cache direction for inverse trips
            continue
        key = COORD_KEY_FORMAT.format(
            origin['start_lat'], origin['start_lng'],
            destination['end_lat'], destination['end_lng'],
            # If a single step in the trip uses a public transportation system, this solution is cached as transit
            'transit' if any(step['travel_mode'] == 'TRANSIT' for step in steps[i:j + 1]) else origin[
                'travel_mode'].lower())
        if key[-7:] == 'transit':  # solutions that use public transportation are not cached
            continue
        value = json.dumps(ids[i:j + 1])  # list of step ids that connect the saved path
        r.set(key, value)


def fix_cycling_duration(overview):
    """
    Since cycling is treated as walking, the overall duration and for each step should be set as 1/3 of the walking one
    """
    overview['duration'] /= 3
    for step in overview['steps']:
        step['duration'] /= 3


def parse_time(d):
    """
    Calculates a datetime object given the dictionary with the time info returned by Google API
    """
    return str(datetime.fromtimestamp(d['value'], tz=pytz.timezone(d['time_zone'])))


def parse_details(d):
    """
    Returns a dictionary with selected information from the info returned by Google API
    """
    return {
        'start_lat': round(d['start_location']['lat'], DECIMAL_PRECISION),
        'start_lng': round(d['start_location']['lng'], DECIMAL_PRECISION),
        'end_lat': round(d['end_location']['lat'], DECIMAL_PRECISION),
        'end_lng': round(d['end_location']['lng'], DECIMAL_PRECISION),
        'distance': d['distance']['value'],
        'duration': d['duration']['value'],
    }


def parse_step_details(d):
    """
    Retrieves further information from each step in the trip. If this step is a 'transit' type, more information is
    acquired about the public transportation used, otherwise just text instructions are retrieved.
    """
    base_info = {
        'travel_mode': d['travel_mode'],
        'instructions': d.get('html_instructions', ''),
        'polyline': d['polyline']['points'],
    }
    try:
        return {**base_info, **{
            'type': d['transit_details']['line']['vehicle']['type'],
            'line_name': ' - '.join((d['transit_details']['headsign'], d['transit_details']['line']['name'])),
            'num_stops': d['transit_details']['num_stops'],
            'departure_stop': d['transit_details']['departure_stop']['name'],
            'departure_time': parse_time(d['transit_details']['departure_time']),
            'arrival_stop': d['transit_details']['arrival_stop']['name'],
            'arrival_time': parse_time(d['transit_details']['arrival_time'])
        }}
    except KeyError:  # some directions might not have public transportation details
        return base_info


def parse_response(d):
    """
    Prettifies the JSON returned from the Google API call. For example, since Travlendar is not using waypoints,
    each response will contain a 'leg' with a single element (thus is convenient to remove this useless key from the
    dict).
    """
    # When travel mode for a step is "WALKING", we need to go a level of 'steps' deeper to actually get atomic details.
    try:
        steps = chain(
            *[[step] if step['travel_mode'] != 'WALKING' else step['steps'] for step in d['legs'][0]['steps']])
    except KeyError:  # this happens when walking directions are asked directly, detailed steps are given directly
        steps = [step for step in d['legs'][0]['steps']]

    return {**parse_details(d['legs'][0]), **{
        'start_address': d['legs'][0]['start_address'],
        'end_address': d['legs'][0]['end_address'],
        'bounds': d['bounds'],
        'polyline': d['overview_polyline']['points'],
        'steps': [{**parse_details(step), **parse_step_details(step)} for step in steps],
        'cached': False  # this overview was not returned from the Redis cache
    }}


def create_overview(steps):
    """
    Creates an overview given a series of steps.
    """
    return {
        'start_lat': steps[0]['start_lat'],
        'start_lng': steps[0]['start_lng'],
        'end_lat': steps[-1]['end_lat'],
        'end_lng': steps[-1]['end_lng'],
        'distance': sum(step['distance'] for step in steps),
        'duration': sum(step['duration'] for step in steps),
        'start_address': "tmp address",
        'end_address': "tmp address",
        'bounds': {
            'northeast': {'lat': max(step['start_lat'] for step in steps),
                          'lng': max(step['start_lng'] for step in steps)},
            'southwest': {'lat': min(step['start_lat'] for step in steps),
                          'lng': min(step['start_lng'] for step in steps)}
        },
        'polyline': ''.join(step['polyline'] for step in steps),
        'steps': steps,
        'cached': True
    }


def get_overview(arrival_time, departure_time, destination, mode, origin, transit_mode):
    """
    Gets an overview, performing the necessary logic in order to acquire travel information either from Google Maps or
    from the cached results.

    :param arrival_time:
    :param departure_time:
    :param destination:
    :param mode:
    :param origin:
    :param transit_mode:
    :return:
    """
    logger.info(f"Requested directions with following parameters: {locals()}")
    coords = f"{origin},{destination}".split(',')
    key = COORD_KEY_FORMAT.format(*map(lambda x: round(float(x), DECIMAL_PRECISION), coords), mode)
    ids = r.get(key)
    if ids and mode != 'transit':  # transit solutions are asked every time to the API (timetables might differ)
        steps = [json.loads(r.get(STEP_KEY_FORMAT.format(id))) for id in json.loads(ids)]
        overviews = [create_overview(steps)]
    else:
        gmaps = googlemaps.Client(key=GOOGLE_API_KEY)
        # Asks for alternatives if travel mode is transit
        result = gmaps.directions(origin, destination, mode=mode, departure_time=departure_time,
                                  arrival_time=arrival_time, transit_mode=transit_mode, alternatives=mode == 'transit')
        overviews = []
        for el in result:
            overview = parse_response(el)
            # Cache steps, individually and all pair combination
            if len(overview['steps']) < 100: # doesn't cache if too many steps are present
                ids = []
                for step in overview['steps']:
                    if step['travel_mode'] != 'TRANSIT':  # steps that use public transportation are not cached
                        r.set(STEP_KEY_FORMAT.format(r.get('counter') or 0), json.dumps(step))
                        ids.append(r.incr('counter') - 1)  # stores value of last id
                cache_steps(overview['steps'], ids)
            overviews.append(overview)
    if request.args.get('mode') == 'bicycling':
        for overview in overviews:
            fix_cycling_duration(overview)
    return overviews


@compute.route('/compute', methods=['GET'])
def get_directions():
    """
    Performs a call to Google Maps Directions API with the googlemaps module and returns the results with selected
    information. Note that origin and destination MUST be expressed in lat,long format
    """
    origin = request.args.get('origin')
    destination = request.args.get('destination')
    departure_time = request.args.get('departure_time')
    arrival_time = request.args.get('arrival_time')
    # cycling is treated as walking
    mode = request.args.get('mode') if request.args.get('mode') != 'bicycling' else 'walking'
    transit_mode = request.args.get('transit_mode')  # list of accepted public transportation means
    try:
        return jsonify(get_overview(arrival_time, departure_time, destination, mode, origin, transit_mode))
    except ValueError as e:  # origin and destination are not given in coordinates
        logger.error(e)
        abort(400)  # bad request


@compute.route('/duration', methods=['GET'])
def get_travel_time():
    """
    Return travel time in seconds for the given trip
    """
    origin = request.args.get('origin')
    destination = request.args.get('destination')
    departure_time = request.args.get('departure_time')
    arrival_time = request.args.get('arrival_time')
    # cycling is treated as walking
    mode = request.args.get('mode') if request.args.get('mode') != 'bicycling' else 'walking'
    transit_mode = request.args.get('transit_mode')  # list of accepted public transportation means
    try:
        overviews = get_overview(arrival_time, departure_time, destination, mode, origin, transit_mode)
        if overviews:
            return jsonify(min(overview['duration'] for overview in overviews))
        else:
            return jsonify(0)
    except ValueError as e:  # origin and destination are not given in coordinates
        logger.error(e)
        abort(400)  # bad request