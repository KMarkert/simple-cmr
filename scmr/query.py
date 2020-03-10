import os
import fire
import json
import time
import requests
import datetime
import pandas as pd
from pprint import pprint
from collections import OrderedDict


class Query:
    def __init__(self, spatialExtent=None, startTime=None, endTime=None,
                 processingLevel=None, topic=None, term=None, variable=None,
                 maxResults=10):

        self.BASE_URL = "https://cmr.earthdata.nasa.gov/search"
        self.processingLvls = ['1A', '1B', '2', '3', '4']
        self.FORMAT = 'umm_json_v1_4'

        payload = {}

        if maxResults > 2000:
            raise ValueError(
                "Specified maximum results must be less than 2000")
        elif maxResults < 1:
            raise ValueError("Specified maximum results must be at least 1")
        else:
            payload['page_size'] = maxResults

        if processingLevel is not None:
            processingLevel = [processingLevel] if type(
                processingLevel) == str else processingLevel
            processingLevel = [str(i) for i in processingLevel]

            levels = []
            for i in processingLevel:
                if i not in self.processingLvls:
                    raise ValueError('Specified processing level {} not valid.\n '
                                     'Please select one of the following: {}'.format(
                                         i, ' '.join(self.processingLvls)
                                     ))
                else:
                    levels.append(i)

            payload['processing_level_id'] = levels

        if (startTime is not None) | (endTime is not None):
            temporalExtent = ','
            if startTime is not None:
                sDt = Utils.decode_date(startTime)
                temporalExtent = sDt.strftime(
                    "%Y-%m-%dT%H:%M:%SZ") + temporalExtent
            if endTime is not None:
                eDt = Utils.decode_date(endTime)
                temporalExtent = temporalExtent + \
                    eDt.strftime("%Y-%m-%dT%H:%M:%SZ")
            payload['temporal'] = temporalExtent

        if spatialExtent is not None:
            try:
                spatialExtent = [str(i).strip() for i in spatialExtent]
                bbox = ','.join(spatialExtent)
                payload['bounding_box'] = bbox

            except Exception as e:
                raise ValueError('Error parsing the spatialExtent information.\n '
                                 'See the followign error for details: {}'.format(e))

        if topic is not None:
            payload['science_keywords[0]\\[topic]'] = topic

        if term is not None:
            payload['science_keywords[0]\\[term]'] = term

        if variable is not None:
            payload['science_keywords[0]\\[variable-level-1]'] = variable

        self.payload = payload

        return

    def __repr__(self):
        return 'CMR Query with the following arguments:\n{}'.format(
            json.dumps(self.payload, indent=2)
        )

    def getCollections(self, asPandas=False, saveFile=False):

        queryUrl = os.path.join(
            self.BASE_URL, "collections.{}".format(self.FORMAT))

        data = self._format_outputs(
            self._send_request(queryUrl, self.payload),
            saveFile=saveFile, asPandas=asPandas
        )

        return data

    def getGranules(self, asPandas=False, saveFile=False):
        queryUrl = os.path.join(
            self.BASE_URL, "granules.{}".format(self.FORMAT))

        data = self._format_outputs(
            self._send_request(queryUrl, self.payload),
            saveFile=saveFile, asPandas=asPandas
        )

        return data

    def _send_request(self, url, payload):
        r = requests.get(url, params=self.payload)

        if r.status_code == 200:
            data = json.loads(r.content.decode())
        else:
            raise RuntimeError('Provided query "{}" return error code {}'.format(
                r.url, r.status_code)
            )

        return data

    def _format_outputs(self, data, saveFile=False, asPandas=False):
        if asPandas:
            if len(data['items']) < 1:
                raise RuntimeError(
                    'Query resturned no data, please check query parameters')

            x = self._parse_native(data)
            df = pd.DataFrame(x)

            if saveFile:
                fileName = 'query_result_{}.csv'.format(int(time.time()))
                df.to_csv(fileName)

            data = df

        else:
            if saveFile:
                fileName = 'query_result_{}.json'.format(int(time.time()))
                with open(fileName, 'w') as f:
                    json.dump(data, f, indent=2)

        return data

    def _parse_native(self, dictionary):
        results = dictionary['items']
        outList = []
        for i in results:
            outList.append(Utils.flatten_dict(i))

        return outList


class Utils:
    def __init__(self):
        return

    @staticmethod
    def merge_dicts(d1, d2):
        """Merges two dictionaries together and aggregates values by key
        """
        result = dict(d1)
        try:
            for k, v in d2.items():
                if k in result:
                    result[k] = result[k].union([v])
                else:
                    result[k] = set([v])
        except Exception as e:
            result
        return result

    @staticmethod
    def flatten_dict(d):
        """Flattens a nested dictionary and aggregates keys
        Args:
          d: (dict|OrderedDict) nested dictionary to flatten
        Returns:
          out: (dict|OrderedDict) flattened dictionary
        """
        out = {}
        for k, v in d.items():
            if (type(v) is OrderedDict) | (type(v) is dict):
                x = Utils.flatten_dict(v)
                out = {**out, **x}
            elif (type(v) is list) | (type(v) is tuple):
                for i in v:
                    if (type(i) is OrderedDict) | (type(i) is dict):
                        x = Utils.flatten_dict(i)
                        out = Utils.merge_dicts(out, x)
                    else:
                        out = {**out, **{k: v}}
                        break
            else:
                out = {**out, **{k: v}}
        return out

    @staticmethod
    def decode_date(string):
        """Decodes a date from a command line argument, returning msec since epoch".
        Args:
          string: See AssetSetCommand class comment for the allowable
            date formats.
        Returns:
          long, datetime object
        Raises:
          ValueError: if string does not conform to a legal date format.
        """

        try:
            return int(string)
        except ValueError:
            date_formats = ['%Y%m%d',
                            '%Y-%m-%d',
                            '%Y-%m-%dT%H:%M:%S',
                            '%Y-%m-%dT%H:%M:%S.%f']
            for date_format in date_formats:
                try:
                    dt = datetime.datetime.strptime(string, date_format)
                    return dt
                except ValueError:
                    continue
        raise ValueError('Invalid format for date: "%s".' % string)


if __name__ == "__main__":
    fire.Fire(Query)
