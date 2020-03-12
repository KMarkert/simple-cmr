import os
import requests
import warnings
from pathlib import Path
from pprint import pformat
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor


class Collections:
    def __init__(self,ummResponse):
        """
        Collections class that extracts the most relevant metadata properties from
        CMR collections and stores them as a dictionary for all collections in reponse
        """

        # tuple of keys to extract from the server response for collections
        keepKeys = (
            'native-id',
            'concept-id',
            'provider-id',
            'ShortName',
            'EntryTitle',
            'ProcessingLevel',
            'SpatialExtent',
            'ScienceKeywords',
            'TemporalExtents',
            'Abstract',
            'RelatedUrls',
            'revision-date',
            'Version',
        )

        topLevelKeys = list(ummResponse['items'][0].keys())

        collections = []
        for item in ummResponse['items']:
            md = item[topLevelKeys[0]]
            for k in topLevelKeys[1:]:
                md.update(item[k])
            metadataKeys = md.keys()
            collections.append(OrderedDict({k: md[k] for k in keepKeys if k in metadataKeys}))

        self.items = collections

        return

    def __repr__(self):
        strRepr = pformat(self.items, depth=4)
        return f'CMR Collection Query result:\n{strRepr}'


class Granules:
    def __init__(self, ummResponse):
        """
        Granules class that extracts the most relevant metadata properties from
        CMR granules and stores them as a dictionary for all granules in reponse
        """

        # tuple of keys to extract from the server response for granules
        keepKeys = (
            'concept-id',
            'RelatedUrls',
            'SpatialExtent',
            'TemporalExtent',
            'GranuleUR',
            'revision-date'
        )

        topLevelKeys = list(ummResponse['items'][0].keys())

        granules = []
        for item in ummResponse['items']:
            md = item[topLevelKeys[0]]
            for k in topLevelKeys[1:]:
                md.update(item[k])

            metadataKeys = md.keys()
            granules.append(OrderedDict({k: md[k] for k in keepKeys if k in metadataKeys}))

        self.items = granules

        return

    def __repr__(self):
        strRepr = pformat(self.items, depth=4)
        return f'CMR Granule Query result:\n{strRepr}'

    @property
    def length(self):
        return len(self.items)

    def fetch(self, credentials, directory='./', limit=None, maxWorkers=2):
        """
        Method to pull the granules from the CMR response to local directory
        uses asynchronous calls to speed up downloading multiple files

        Args:
            credentials (tuple|list): Earthdata username and password needed to download data

        Kwargs:
            directory (string): relative or absolute path to download files too,
                default = current working directory
            limit (int): maximum number of granules to download,
                default = None (get all granules)
            marWorkers (int): maximum threads to execute granule fetching asynchronously,
                default = 2

        Returns:
            None
        """

        if maxWorkers < 1:
            warnings.warn("the specified maxWorkers is less than the minimum (1) "
                "using at least 1 worker")
            maxWorkers = 1


        if limit is not None:
            maxIters = min(limit, len(self.items))
        else:
            maxIters = len(self.items)

        outDir = Path(directory)

        itemsToGet = self.items[:maxIters]

        # send download requests asynchronously
        with ThreadPoolExecutor(maxWorkers) as executor:
            executor.map(lambda x: self._granule_request(
                x, credentials, outDir), itemsToGet)

        return

    @staticmethod
    def _granule_request(item, credentials, outDir):
        """
        Helper method to request granule download, used for asynchronous calls

        Args:
            item (dict): Granule response
            credentials(list|tuple): Earthdata username and password needed to download data
            outDir (pathlib.Path): out directory to save data too
        """

        urls = item['RelatedUrls']
        source = dict([('URL', url['URL'])
                       for url in urls if url['Type'] == 'GET DATA'])
        with requests.Session() as s:
            s.auth = credentials
            authGateway = s.request('get', source['URL'])
            r = s.get(authGateway.url, auth=credentials)

            _, fileName = os.path.split(source['URL'])

            outFile = outDir / fileName
            outFile.write_bytes(r.content)

        return
