import logging
import unittest
import warnings
from itertools import combinations_with_replacement

import redis
from flask_testing import TestCase

from src import create_app, r, setup_logging


class AppTest(TestCase):
    DB_COPY = 1

    def create_app(self):
        app = create_app()
        app.config['TESTING'] = True
        app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = False
        setup_logging(path='../../logging.json', tofile=False)
        self.logger = logging.getLogger(__name__)
        return app

    def setUp(self):
        for k in r.keys():  # moves all keys to the copy database
            r.move(k, self.DB_COPY)
        self.logger.info(f"Performed SetUp")

    def tearDown(self):
        r.flushdb()
        copy_db = redis.StrictRedis(host='localhost', port=6379, db=self.DB_COPY)
        for k in copy_db.keys():  # moves keys back to production db
            copy_db.move(k, 0)
        self.logger.info(f"Performed teardown")

    def make_call(self, endpoint='compute', origin='45.4842721,9.2368349', destination='45.468359,9.1761419', mode='driving'):
        """
        Makes a call to the GET endpoint
        :param origin: Lat/lng coordinates for starting point. Defaults to Piazza Enrico Bottini
        :param destination: Lat/lng coordinates for ending point. Defaults to Piazzale Luigi Cadorna
        :param mode: Mode of transit. Defaults to 'driving'.
        :return: the result given by the GET endpoint
        """
        with warnings.catch_warnings():  # suppresses warnings on unclosed sockets
            warnings.simplefilter("ignore", ResourceWarning)
            return self.client.get(f'/{endpoint}?' + '&'.join(f"{k}={v}" for k, v in locals().items()))

    def test_404(self):
        """
        Checks that a 404 error is returned if origin and destination are not given in latitude/longitude coordinates
        """
        response = self.make_call(origin='Milano Lambrate', destination='Milano Cadorna')
        self.assert400(response)

    def test_cache(self):
        """
        Checks correctness of caching system inside GET endpoint.
        """
        response = self.make_call().json[0]
        self.assertFalse(response['cached'])  # a call has ben made to Google API
        # each step is saved
        self.assertEqual(len(r.keys(pattern=r'step*')), int(r.get('counter')))
        self.assertEqual(int(r.get('counter')), len(response['steps']))
        pairs = set((i, j) for (i, o), (j, d) in combinations_with_replacement(list(enumerate(response['steps'])), 2) if i <= j)
        self.assertEqual(len(r.keys(pattern=r'origin*')), len(pairs))  # each combination is cached
        for i, j in pairs:
            origin, destination = response['steps'][i], response['steps'][j]
            resp = self.make_call(origin=f"{origin['start_lat']},{origin['start_lng']}",
                                      destination=f"{destination['end_lat']},{destination['end_lng']}").json[0]
            # No new API calls are made, cached results are returned for each possible combination of origin/dest
            self.assertEqual(origin['start_lat'], resp['start_lat'])  # all coordinates should match
            self.assertEqual(origin['start_lng'], resp['start_lng'])
            self.assertEqual(destination['end_lat'], resp['end_lat'])
            self.assertEqual(destination['end_lng'], resp['end_lng'])
            self.assertTrue(resp['cached'])
        # New API call is made for transit directions. We can't recycle driving directions for this one.
        response = self.make_call(mode='transit').json
        self.assertFalse(response[0]['cached'])
        self.assertTrue(len(response) > 1)  # when asking for transit directions it should yield multiple alternatives
        # driving directions should be cached already
        response = self.make_call().json[0]
        self.assertTrue(response['cached'])
        # Walking directions should not be cached
        walking = self.make_call(mode='walking').json[0]
        self.assertFalse(walking['cached'])
        # Bicycling should be treated as walking but 3 times as fast
        bicycling = self.make_call(mode='bicycling').json[0]
        self.assertTrue(bicycling['cached'])
        self.assertEqual(walking['duration'], 3 * bicycling['duration'])

    def test_duration(self):
        response = self.make_call(endpoint='duration')
        self.assertIsInstance(response.json, int)

    def test_response(self):
        self.logger.info(self.make_call().json[0])

if __name__ == '__main__':
    unittest.main()
