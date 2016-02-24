#EXAMPLE

from confluent.schemaregistry.client import CachedSchemaRegistryClient
from confluent.schemaregistry.serializers import MessageSerializer, Util
from kafka import SimpleProducer, KafkaClient, KafkaProducer, KeyedProducer, Murmur2Partitioner
import avro.schema
import io, random
from avro.io import DatumWriter

# Note that some methods may throw exceptions if
# the registry cannot be reached, decoding/encoding fails,
# or IO fails

# some helper methods in util to get a schema
#avro_schema = Util.parse_schema_from_file('/home/glamdring/Kafka_python/Avro_Schemas/header.avsc')
#avro_schema = Util.parse_schema_from_file('/home/glamdring/Kafka_python/Avro_Schemas/attitude.avsc')
#avro_schema = Util.parse_schema_from_string(open('/home/glamdring/catkin_ws/src/rawfie_interface/Avro_Schemas/uxv/Location.avsc').read())
avro_schema = Util.parse_schema_from_string(open('/home/glamdring/catkin_ws/src/rawfie_interface/Avro_Schemas/commands/goto.avsc').read())

# Initialize the client
client = CachedSchemaRegistryClient(url='http://localhost:8081')
#client = CachedSchemaRegistryClient(url='http://eagle5.di.uoa.gr:8081')

# Schema operations

# register a schema for a subject
schema_id = client.register('UGV_Goto', avro_schema)
# fetch a schema by ID
avro_schema = client.get_by_id(schema_id)
# get the latest schema info for a subject
schema_id,avro_schema,schema_version = client.get_latest_schema('UGV_Goto')

# get the version of a schema
schema_version = client.get_version('UGV_Goto', avro_schema)
# Compatibility tests
#is_compatible = client.test_compatibility('my_subject', another_schema)

# One of NONE, FULL, FORWARD, BACKWARD
new_level = client.update_compatibility('NONE','my_subject')
current_level = client.get_compatibility('my_subject')

# Message operations

# encode a record to put onto kafka
serializer = MessageSerializer(client)
#record = {"sourceSystem": r"test2", r"sourceModule": "test1", "time": 2543534346L}
record = {"header":{"sourceSystem": r"test2", r"sourceModule": "test1", "time": 2543534346L}, "location":{"latitude": 0.718849142991, "longitude": -0.151899739806, "height": 0, 
						"n": 2.0, "e": 2.0, "d": 0, "depth": 0, "altitude": 0}, "speed": 1.0, "timeout": 5.0}
#record = {"header":{"sourceSystem": r"test2", r"sourceModule": "test1", "time": 2543534346L}, "latitude": 0, "longitude": 0, "height": 0, 
#						"n": 2.0, "e": 2.0, "d": 0, "depth": 0, "altitude": 0}

# use the schema id directly
encoded = serializer.encode_record_with_schema_id(schema_id, record)

# use an existing schema and topic
# this will register the schema to the right subject based
# on the topic name and then serialize
#encoded = serializer.encode_record_with_schema('my_topic', avro_schema, record)

# encode a record with the latest schema for the topic
# this is not efficient as it queries for the latest
# schema each time
#encoded = serializer.encode_record_for_topic('my_kafka_topic', record)


# To send messages synchronously
kafka = KafkaClient('localhost:9092')
#kafka = KafkaClient('eagle5.di.uoa.gr:9092')
producer = SimpleProducer(kafka)
#producer = KafkaProducer()
#producer = KeyedProducer(kafka)
#producer = KeyedProducer(kafka, partitioner=Murmur2Partitioner)


# Kafka topic
partition = 6
key = "rawfie.rob.xl-1"
topic = "GoTo"
#producer.send_messages(topic, encoded)
#producer.send(topic, encoded, key, partition)
#producer.send_messages(topic, b'rawfie.rob.xl-1', encoded)

producer.send_messages(topic, encoded)
print 
'''
while True:
	if raw_input("Press Enter to continue..."):
		producer.send_messages(topic, encoded)
'''
