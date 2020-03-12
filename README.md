# simple-cmr
Python package to query NASA's Common Metadata Repository with a simple and intuitive API

## Philosophy
The NASA Common Metadata Repository hosts a wealth of information related to Earth Observation data. However, so much information can be cumbersome to those that are not fully aware of what everything is or what information can be extracted from the database.

`simple-cmr` aims to provide a simplified interface to work with the NASA CMR including submitting a query, accessing important metadata, and retrieving data for use. This package is intended for practitioners to provide a simple interface to script searching for known datasets and downloading the data. This package is not meant to be a discovery tool, users would ideally know what data they want to search for.

## Example
This is a simple example where one provides a collection concept ID (assuming one knows it) and space/time information to identify the granules that meet the criteria.

In this case we will be searching the Suomi-NPP ATMS Brightness Temperature collection (`C1442068516-GES_DISC`) over Southeast Asia for March 1, 2020.


```python
import simplecmr as scmr

# construct query
query = scmr.Query(conceptid="C1442068516-GES_DISC", startTime='2020-03-01', endTime='2020-03-02', spatialExtent=[90,10,110,30], maxResults=10)

# print the granule information
query.granules

# download the first five granules that meet our query
query.granules.fetch((<username>,<password>),limit=5)
```

## Contributing
Contributions are welcome, and they are greatly appreciated! Every
little bit helps, and credit will always be given.

You can contribute in many ways:

### Types of Contributions

#### Report Bugs

Report bugs at https://github.com/kmarkert/simple-cmr/issues.

If you are reporting a bug, please include:

* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

#### Fix Bugs

Look through the GitHub issues for bugs. Anything tagged with "bug" is open to whoever wants to implement it.

#### Implement Features

Look through the GitHub issues for features. Anything tagged with "feature" is open to whoever wants to implement it.

#### Submit Feedback

The best way to send feedback is to file an issue at https://github.com/kmarkert/simple-cmr/issues.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions are welcome :smile:
