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

serializer = MessageSerializer(client)

consumer = KafkaConsumer('LaserScan',
                         bootstrap_servers=['localhost:9092'])


for msg in consumer:
	#print msg.partition
	if msg.partition == 6 :
		decoded_object = serializer.decode_message(msg.value)
		print ("RANGES:",decoded_object.get('ranges'))
		print ("INTENSITIES",decoded_object.get('intensities'))
                                                 
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

