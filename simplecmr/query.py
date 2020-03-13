import os
import json
import time
import warnings
import datetime
import requests
import requests_cache
from pprint import pformat
from simplecmr import utils
from simplecmr.result import Collections, Granules


class Query:
    def __init__(self, conceptid=None, shortName=None, spatialExtent=None,
                 startTime=None, endTime=None, maxResults=10,cache=True):
        """

        """

        # setting basic parameters for a query
        self.BASE_URL = "https://cmr.earthdata.nasa.gov/search"
        self.FORMAT = 'umm_json_v1_4'

        if cache:
            expire_after = datetime.timedelta(hours=1)
            requests_cache.install_cache(backend='memory',expire_after=expire_after)

        payload = {}

        if conceptid is not None:
            payload['concept_id'] = conceptid

            if shortName is not None:
                warnings.warn("parameters conceptid and shortName are mutually "
                              "exclusive...using conceptid for search")
        elif shortName is not None:
            payload['short_name'] = shortName

        # validate that the maxResults keyword is within reasonable boundes
        if (maxResults > 2000) or (maxResults < 1):
            raise ValueError(
                "Specified maximum results must be greater than 1 and less than 2001")
        else:
            payload['page_size'] = maxResults

        # check the inputs for the datetime information
        if (startTime is not None) or (endTime is not None):
            temporalExtent = ','
            if startTime is not None:
                if type(startTime) is not datetime.datetime:
                    startTime = utils.decode_date(startTime)
                temporalExtent = startTime.strftime(
                    "%Y-%m-%dT%H:%M:%SZ") + temporalExtent
            if endTime is not None:
                if type(endTime) is not datetime.datetime:
                    endTime = utils.decode_date(endTime)
                temporalExtent = temporalExtent + \
                    eDt.strftime("%Y-%m-%dT%H:%M:%SZ")
            # add temporal information to the request parameters
            payload['temporal'] = temporalExtent

        # check that spatial extent is defined
        if spatialExtent is not None:
            # construct the spatial bounding box from inputs
            try:
                spatialExtent = [str(i).strip() for i in spatialExtent]
                bbox = ','.join(spatialExtent)
                payload['bounding_box'] = bbox

            except Exception as e:
                raise ValueError('Error parsing the spatialExtent information.\n '
                                 'See the followign error for details: {}'.format(e))

        # set the request parameters to class object
        self.payload = payload

        return

    def __repr__(self):
        strRepr = pformat(self.items, depth=2)
        return f'CMR Query with the following arguments:\n{strRepr}'

    @property
    def collections(self):
        """
        Property of a Query will return a list of OrderedDicts that
        contain the metadata information for all collections that meet
        the criteria of query

        Return:
            result.Collections: list of OrderedDicts with metadata information for collections
        """

        queryUrl = os.path.join(
            self.BASE_URL, "collections.{}".format(self.FORMAT))

        data = self._send_request(queryUrl)

        return Collections(data)

    @property
    def granules(self):
        """
        Property of a Query will return a list of OrderedDicts that
        contain the metadata information for all collections that meet
        the criteria of query

        Returns:
            result.Granules: list of OrderedDicts with metadata information for granules
        """

        queryUrl = os.path.join(
            self.BASE_URL, "granules.{}".format(self.FORMAT))

        data = self._send_request(queryUrl)

        return Granules(data)

    def _send_request(self, url):
        """
        Helper function that wraps a request and returns the results

        Args:
            url (string): URL string of the website to request data from

        Returns:
            data (dict): Dictionary of data returned from server

        Raises:
            requests.HTTPError: Raises error when request returns an error or has
                a status code that is not 200
        """

        try:
            r = requests.get(url, params=self.payload)
        except Exception as e:
            raise requests.HTTPError(e)

        if r.status_code == 200:
            data = r.json()
        else:
            raise requests.HTTPError('Provided query "{}" return error code {}'.format(
                r.url, r.status_code)
            )

        return data
