#EXAMPLE

from confluent.schemaregistry.client import CachedSchemaRegistryClient
from confluent.schemaregistry.serializers import MessageSerializer, Util
from kafka import SimpleProducer, KafkaClient, KafkaConsumer
from kafka.common import TopicPartition

# Note that some methods may throw exceptions if
# the registry cannot be reached, decoding/encoding fails,
# or IO fails

# Initialize the client
client = CachedSchemaRegistryClient(url='http://localhost:8081')
#client = CachedSchemaRegistryClient(url='http://eagle5.di.uoa.gr:8081')

# Schema operations

# get the latest schema info for a subject
'''
Header_schema_id,Header_avro_schema,Header_schema_version = client.get_latest_schema('UGV_Header')
Attitude_schema_id,Attitude_avro_schema,Attitude_schema_version = client.get_latest_schema('UGV_Attitude')
Location_schema_id,Location_avro_schema,Location_schema_version = client.get_latest_schema('UGV_Location')
'''
# Compatibility tests
#is_compatible = client.test_compatibility('my_subject', another_schema)
"""
# One of NONE, FULL, FORWARD, BACKWARD
new_level = client.update_compatibility('NONE','my_subject')
current_level = client.get_compatibility('my_subject')
"""
# Message operations


serializer = MessageSerializer(client)

consumer = KafkaConsumer('GoTo',
                         bootstrap_servers=['localhost:9092'])


for msg in consumer:
	print("Something")
	print msg
	decoded_object = serializer.decode_message(msg.value)
	print decoded_object
                                                 
'''
location_consumer = KafkaConsumer('UGV_Location',
                         bootstrap_servers=['localhost:9092'])   
				  
                         
# decode a message from kafka
for msg in location_consumer:
	print("Something")
	location_decoded_object = serializer.decode_message(msg.value)
	locmsg_x = location_decoded_object.get('n')
	locmsg_y = location_decoded_object.get('e')

	print msg.key
	print "Location Received:: x:%d y:%d" % (locmsg_x, locmsg_y)
'''

# TESTS WITH PARTITIONS
'''
location_consumer = KafkaConsumer( group_id='UGV_Location1',
                         bootstrap_servers=['localhost:9092'])
topic_part_obj1 = TopicPartition('Location1', 0)                       
topic_part_obj2 = TopicPartition('Location1', 1)                       
topic_part_obj3 = TopicPartition('Location1', 2)                       
topic_part_obj4 = TopicPartition('Location1', 3)                       
topic_part_obj5 = TopicPartition('Location1', 4)                       
topic_part_obj6 = TopicPartition('Location1', 5)                       
topic_part_obj7 = TopicPartition('Location1', 6)                       
location_consumer.assign([topic_part_obj1,topic_part_obj2,topic_part_obj3,topic_part_obj4,
							topic_part_obj5,topic_part_obj6]) 
print location_consumer.assignment()							
while True:
	something = bool(location_consumer.poll())
	if something:
		print(location_consumer.poll())
		exit()
	else:
		print("None")                        
#location_consumer.subscribe(['Location1'])  
#print location_consumer.committed(topic_part_obj)  
'''

'''
try:
	for msg in location_consumer:
		location_decoded_object = self.serializer.decode_message(msg.value)
		locmsg_location = location_decoded_object.get('location')
		locmsg_x = locmsg_location.get('n')
		locmsg_y = locmsg_location.get('e')
		print "Location Received:: x:%d y:%d" % (locmsg_x, locmsg_y)
		break
except :
	print("exception")
	pass
'''
'''
for msg in location_consumer:
	print("Something")
	location_decoded_object = serializer.decode_message(msg.value)
	locmsg_x = location_decoded_object.get('n')
	locmsg_y = location_decoded_object.get('e')

	print "Location Received:: x:%d y:%d" % (locmsg_x, locmsg_y)
'''
