# This is an example of how to sequence a patient from the OMOP database
# Note: this file should be run from a location where it can import the mcs package (e.g., parent directory of mcs)

import pyodbc
import getpass
from MedicalCodingSequence import *

# SQL server config
sql_config = {
    'driver': 'ODBC Driver 17 for SQL Server',
    'server': '<server address>',
    'database': '<user>',
    'uid': '<user>'
}

pwd=getpass.getpass()
conn = pyodbc.connect(**sql_config, pwd=pwd)
cursor = conn.cursor()

# Get all conditions, drugs, procedures, and measurements for a person
person_id = 123456789
sql = """
        (SELECT co.condition_concept_id AS concept_id, co.condition_start_datetime AS start_datetime
        FROM dbo.condition_occurrence co
        WHERE co.person_id = ?)
        UNION ALL
        (SELECT do.drug_concept_id AS concept_id, do.drug_exposure_start_datetime AS start_datetime
        FROM dbo.drug_exposure do
        WHERE do.person_id = ?)
        UNION ALL
        (SELECT po.procedure_concept_id AS concept_id, po.procedure_datetime AS start_datetime
        FROM dbo.procedure_occurrence po
        WHERE po.person_id = ?)
        UNION ALL
        (SELECT m.measurement_concept_id AS concept_id, m.measurement_datetime AS start_datetime
        FROM dbo.measurement m
        WHERE m.person_id = ?)
    """
cursor.execute(sql, person_id, person_id, person_id, person_id)
res = cursor.fetchall()

# Create TemporalSequencer and add records
ts = TemporalSequencer(metadata={'person_id': person_id})
for x in res:
    ts.add_data(x[1], x[0])

# Serialize in strict temporal order (no shuffling)
print('strict order')
ser = ts.serialize(shuffle_level=None)
print(ser)

# Serialize with codes within the same day shuffled
print('shuffle @ days')
ser = ts.serialize(shuffle_level='d')
print(ser)