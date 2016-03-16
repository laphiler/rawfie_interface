from confluent.schemaregistry.client import CachedSchemaRegistryClient
from confluent.schemaregistry.serializers import MessageSerializer, Util
from kafka import SimpleProducer, KafkaClient, KafkaProducer, KeyedProducer, Murmur2Partitioner
import avro.schema
import io, random
from avro.io import DatumWriter
from kafka.common import KafkaError

avro_schema = Util.parse_schema_from_string(open('/home/glamdring/catkin_ws/src/rawfie_interface/Avro_Schemas/commands/goto.avsc').read())

# Initialize the client
#client = CachedSchemaRegistryClient(url='http://localhost:8081')
client = CachedSchemaRegistryClient(url='http://eagle5.di.uoa.gr:8081')

# Schema operations

# register a schema for a subject
schema_id = client.register('Goto', avro_schema)
# fetch a schema by ID
avro_schema = client.get_by_id(schema_id)
# get the latest schema info for a subject
schema_id,avro_schema,schema_version = client.get_latest_schema('Goto')

# get the version of a schema
schema_version = client.get_version('Goto', avro_schema)
# Compatibility tests
#is_compatible = client.test_compatibility('my_subject', another_schema)

# One of NONE, FULL, FORWARD, BACKWARD
new_level = client.update_compatibility('NONE','my_subject')
current_level = client.get_compatibility('my_subject')

# Message operations

# encode a record to put onto kafka
serializer = MessageSerializer(client)
#record = {"sourceSystem": r"test2", r"sourceModule": "test1", "time": 2543534346L}
record = {"header":{"sourceSystem": r"test2", r"sourceModule": "test1", "time": 2543534346L}, "location":{"latitude":  0.718852663, "longitude": -0.151914668, "height": 0, 
						"n": 0.0, "e": 0.0, "d": 0, "depth": 0, "altitude": 0}, "speed": 1.0, "timeout": 5.0}

# use the schema id directly
encoded = serializer.encode_record_with_schema_id(schema_id, record)


kafka = KafkaClient('eagle5.di.uoa.gr:9092')


producer = KafkaProducer(bootstrap_servers=['eagle5.di.uoa.gr:9092'])
# Kafka topic
partition = 6
key = "rawfie.rob.xl-1"
topic = "Goto"
#producer.send_messages(topic, encoded)
# Asynchronous by default
future = producer.send(topic, partition=6, value=encoded)


# Block for 'synchronous' sends
try:
    record_metadata = future.get(timeout=10)
except KafkaError:
    # Decide what to do if produce request failed...
    log.exception()
    pass

# Successful result returns assigned partition and offset
print (record_metadata.topic)
print (record_metadata.partition)
print (record)



'''
# produce json messages
producer = KafkaProducer(value_serializer=lambda m: json.dumps(m).encode('ascii'))
producer.send('json-topic', {'key': 'value'})

# configure multiple retries
producer = KafkaProducer(retries=5)





# Note that some methods may throw exceptions if
# the registry cannot be reached, decoding/encoding fails,
# or IO fails

# some helper methods in util to get a schema
#avro_schema = Util.parse_schema_from_file('/home/glamdring/Kafka_python/Avro_Schemas/header.avsc')
#avro_schema = Util.parse_schema_from_file('/home/glamdring/Kafka_python/Avro_Schemas/attitude.avsc')
#avro_schema = Util.parse_schema_from_string(open('/home/glamdring/catkin_ws/src/rawfie_interface/Avro_Schemas/uxv/Location.avsc').read())


'''
