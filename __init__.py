from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict
from random import shuffle
import json

class MedicalCodingSequencer(ABC):
    """ Abstract Base Class for medical coding sequencers """
    def __init__(self):
        super().__init__()

    @abstractmethod
    def sequence(self):
        return None

    @abstractmethod
    def serialize(self, output_file):
        pass


class TemporalRecord:
    """ A single instance of a timestamped record """
    def __init__(self, timestamp: datetime, code: Any):
        self.timestamp = timestamp
        self.code = code

    def serialize(self):
        """ String representation of the format (timestamp, code) """
        return f'({self.timestamp.strftime("%Y-%m-%d_%H:%M:%S.%f")}, {self.code})'

    @staticmethod
    def read(input_str):
        """ Reads the string representation back into a TemporalRecord object """
        input_list = input_str[1:-1].split(', ')
        timestamp = datetime.strptime(input_list[0], '%Y-%m-%d_%H:%M:%S.%f')
        code = input_list[1]
        return TemporalRecord(timestamp, code)


class TemporalSequencer(MedicalCodingSequencer):
    """ Converts a list of TemporalRecords (not necessarily ordered) into an ordered Temporal Sequence """
    _shuffle_dict = {
        'd': '%Y-%m-%d',
        'H': '%Y-%m-%d_%H',
        'M': '%Y-%m-%d_%H:%M',
        'S': '%Y-%m-%d_%H:%M:%S',
        'f': '%Y-%m-%d_%H:%M:%S.%f',
    }

    def __init__(self, metadata: Dict = None, sep: str = '\t'):
        """  Constructor

        Params
        ======
        metadata: dict - Metadata about this container object. For example, the container object could be a patient,
                  and metadata may include person_id. Must be JSON serializable.
        sep: str - Separator character. Default: tab
        """
        self.data = list()

        if metadata is None:
            self.metadata = dict()
        else:
            if type(metadata) is dict:
                self.metadata = metadata
            else:
                raise ValueError()

        self.sep = sep
        self._shuffle_level = None
        self._sequenced = False
        super().__init__()

    def add_data(self, timestamp: datetime, code: Any):
        """ Adds timestamp and code to the data to be sequenced """
        self.data.append(TemporalRecord(timestamp, code))
        self._sequenced = False

    def add_temporal_record(self, ts: TemporalRecord):
        """ Adds TemporalRecord to the data to be sequenced """
        self.data.append(ts)
        self._sequenced = False

    def sequence(self, shuffle_level: str = None, reverse=False):
        """ Sequences the data

        Params
        ======
        shuffle_level: str - Indicates which time unit to shuffle records on. None - no shuffling. Otherwise,
                specified using strftime codes. For example, use '%d' to shuffle all codes recorded on
                the same day. Supported values:
                '%d' - day
                '%H' - hour
                '%M' - minute
                '%S' - second
                '%f' - microsecond
                None - No shuffling
        reverse: bool - True to sort with most recent records first. Default: False
        """
        if shuffle_level is not None and (type(shuffle_level) is not str or shuffle_level not in TemporalSequencer._shuffle_dict.keys()):
            raise ValueError()
        self._shuffle_level = shuffle_level

        # First, sort strictly by timestamp
        self.data.sort(key=lambda x: x.timestamp, reverse=reverse)

        if shuffle_level is not None:
            # Shuffle records that occur at the same time level
            fmt = TemporalSequencer._shuffle_dict[shuffle_level]
            new_seq = list()
            current_datetime = None
            current_group = list()
            for r in self.data:
                # Convert the datetime to a string of a certain precision as a crude way of ignoring lower precision

                new_datetime = r.timestamp.strftime(fmt)
                if new_datetime != current_datetime:
                    # Shuffle the current group of records and add them to the new sequence
                    shuffle(current_group)
                    new_seq.extend(current_group)

                    # Start keeping track of the new group of records
                    current_datetime = new_datetime
                    current_group = list()
                current_group.append(r)
            self.data = new_seq

        self._sequenced = True

    def serialize(self, shuffle_level: str = None, reverse=False):
        """ Sequences the data and serializes to a string representation

        Params
        ======
        shuffle_level: str - Indicates which time unit to shuffle records on. See the
                       documentation for the sequence method for more details.
        reverse: bool - True to sort with most recent records first. Default: False

        Returns
        =======
        String serialization of temporal coding sequence
        """
        if not self._sequenced or self._shuffle_level != shuffle_level:
            self.sequence(shuffle_level, reverse)

        seq_str = ''
        if self.metadata is None:
            self.metadata = dict()
        seq_str += json.dumps(self.metadata) + self.sep
        seq_str += self.sep.join([r.serialize() for r in self.data])
        return seq_str

    @staticmethod
    def read(input_str: str, sep='\t'):
        """ Reads the serialized temporal coding sequence back into a TemporalSequencer object

        Params
        ======
        input_str: str - Input string to read
        sep: str - Separator character

        Returns
        =======
        TemporalSequencer object
        """
        input_list = input_str.split(sep)
        metadata = json.loads(input_list.pop(0))
        ts = TemporalSequencer(metadata=metadata, sep=sep)
        for r in input_list:
            tr = TemporalRecord.read(r)
            ts.add_temporal_record(tr)
        ts._sequenced = True
        return ts
