This package helps to convert clinical data into Medical Coding Sequences.


# TemporalSequencer
Convert timestamped coding data into temporal sequences.
The temporal sequencer supports shuffling codes within a specified level of
temporal precision, e.g., shuffling all codes that occur on the same day.
Can also add include metadata (e.g., person_id, age, sex, etc) which get
serialized at the beginning.


## Usage

### Examples
Code:
``` Python
from MedicalCodingSequence import *
from datetime import datetime
ts = TemporalSequencer(metadata={'person_id': 42})
ts.add_data(timestamp=datetime(1955, 11, 12, 22, 4, 0, 0), code=4198400)
ts.add_data(timestamp=datetime(2015, 10, 21, 0, 0, 0, 123456), code=4060282)
ts.add_data(timestamp=datetime(1985, 7, 3, 1, 2, 3, 456789), code=37606318)
print(ts.serialize())
```

Output:
```
{"person_id": 42}	(1955-11-12_22:04:00.000000, 4198400)	(1985-07-03_01:02:03.456789, 37606318)	(2015-10-21_00:00:00.123456, 4060282)
```

See `example_temporalsequence_omop.py` for an example of sequencing patient
data from an OMOP database.

### Notes
1. Timestamps retain full precision in serialized output regardless of
`shuffle_level` setting
1. Metadata must be JSON serializable. For example, for DOB, convert
Python `datetime` objects to string first since `datetime` objects are not
JSON serializable.
