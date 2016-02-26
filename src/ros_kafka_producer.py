#!/usr/bin/env python

# Software License Agreement (BSD License)
#
# Copyright (c) 2015, Robotnik Automation SLL
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
#  * Neither the name of Robotnik Automation SSL nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import rospy 

import time, threading

import os
import rospkg

# Messages
from std_msgs.msg import Float32
from nav_msgs.msg import Odometry
from sensor_msgs.msg import NavSatFix
from rescuer_ardu_ptu.msg import ardu_ptu

from geometry_msgs.msg import Point, Quaternion
import tf

from robotnik_msgs.msg import State
from confluent.schemaregistry.client import CachedSchemaRegistryClient
from confluent.schemaregistry.serializers import MessageSerializer, Util
from kafka import SimpleProducer, KafkaClient, KafkaProducer, KeyedProducer,Murmur2Partitioner
import avro.schema
import io, random
from avro.io import DatumWriter

DEFAULT_FREQ = 10.0
MAX_FREQ = 500.0

	
# Class Template of Robotnik component for Pyhton
class RComponent:
	
	def __init__(self, args):
		
		self.node_name = rospy.get_name().replace('/','')
		self.desired_freq = args['desired_freq'] 
		# Checks value of freq
		if self.desired_freq <= 0.0 or self.desired_freq > MAX_FREQ:
			rospy.loginfo('%s::init: Desired freq (%f) is not possible. Setting desired_freq to %f'%(self.node_name,self.desired_freq, DEFAULT_FREQ))
			self.desired_freq = DEFAULT_FREQ
	
		
		self.real_freq = 0.0
		
		# Saves the state of the component
		self.state = State.INIT_STATE
		# Saves the previous state
		self.previous_state = State.INIT_STATE
		# flag to control the initialization of the component
		self.initialized = False
		# flag to control the initialization of ROS stuff
		self.ros_initialized = False
		# flag to control that the control loop is running
		self.running = False
		# Variable used to control the loop frequency
		self.time_sleep = 1.0 / self.desired_freq
		# State msg to publish
		self.msg_state = State()
		# Timer to publish state
		self.publish_state_timer = 1
		
		self.t_publish_state = threading.Timer(self.publish_state_timer, self.publishROSstate)
		
		self.location_x = 0.0
		self.location_y = 0.0
		self.roll = 0.0
		self.pitch = 0.0
		self.yaw = 0.0
		self.battery_voltage = 53.0
		self.battery_value = 100
		self.minutes = 1
		
		self.latitude = 0.0
		self.longitude = 0.0
		self.altitude = 0.0
		self.temperature = 0.0
		
		self.rp = rospkg.RosPack()
		self.Attitude_path_file = os.path.join(self.rp.get_path('rawfie_interface'), 'Avro_Schemas/uxv', 'Attitude.avsc')
		self.Location_path_file = os.path.join(self.rp.get_path('rawfie_interface'), 'Avro_Schemas/uxv', 'Location.avsc')
		self.FuelUsage_path_file = os.path.join(self.rp.get_path('rawfie_interface'), 'Avro_Schemas/uxv', 'FuelUsage.avsc')
		self.SensorReadingScalar_path_file = os.path.join(self.rp.get_path('rawfie_interface'), 'Avro_Schemas/uxv', 'SensorReadingScalar.avsc')
		
		
		#self.Status_path_file = os.path.join(self.rp.get_path('rawfie_interface'), 'Avro_Schemas', 'UxVHealthStatus.avsc')
			
	def setup(self):
		'''
			Initializes de hand
			@return: True if OK, False otherwise
		'''
		'''
		Some helper methods in util to get a schema
		'''
		

		self.Attitude_avro_schema = Util.parse_schema_from_string(open(self.Attitude_path_file).read())
		self.Location_avro_schema = Util.parse_schema_from_string(open(self.Location_path_file).read())
		self.FuelUsage_avro_schema = Util.parse_schema_from_string(open(self.FuelUsage_path_file).read())
		self.SensorReadingScalar_avro_schema = Util.parse_schema_from_string(open(self.SensorReadingScalar_path_file).read())
		
		
		#self.Status_avro_schema = Util.parse_schema_from_string(open(self.Status_path_file).read())

		'''
		Initialize the client
		'''
		
		#self.client = CachedSchemaRegistryClient(url='http://localhost:8081')
		self.client = CachedSchemaRegistryClient(url='http://eagle5.di.uoa.gr:8081')
		'''
			# Schema operations
		'''
		'''
		Register a schema for a subject
		'''
		
		self.Attitude_schema_id = self.client.register('UGV_Attitude', self.Attitude_avro_schema)
		self.Location_schema_id = self.client.register('UGV_Location', self.Location_avro_schema)
		self.FuelUsage_schema_id = self.client.register('UGV_FuelUsage', self.FuelUsage_avro_schema)
		self.SensorReadingScalar_schema_id = self.client.register('UGV_SensorReadingScalar', self.SensorReadingScalar_avro_schema)
		
		
		#self.Status_schema_id = self.client.register('UGV_Status', self.Status_avro_schema)
		'''
		Get the version of a schema
		'''
		
		self.Attitude_schema_version = self.client.get_version('UGV_Attitude', self.Attitude_avro_schema)
		self.Location_schema_version = self.client.get_version('UGV_Location', self.Location_avro_schema)
		self.FuelUsage_schema_version = self.client.get_version('UGV_FuelUsage', self.FuelUsage_avro_schema)
		self.SensorReadingScalar_schema_version = self.client.get_version('UGV_SensorReadingScalar', self.SensorReadingScalar_avro_schema)
		
		
		#self.Status_schema_version = self.client.get_version('UGV_Status', self.Status_avro_schema)
		'''
			# Compatibility tests
		'''
		#is_compatible = client.test_compatibility('my_subject', another_schema)
		'''
		One of NONE, FULL, FORWARD, BACKWARD
		'''
		#self.new_level = self.client.update_compatibility('NONE','my_subject')
		#self.current_level = self.client.get_compatibility('my_subject')
		'''
		Create Serializer
		'''
		
		self.serializer = MessageSerializer(self.client)
		
		self.initialized = True
		
		return 0
		
		
	def rosSetup(self):
		'''
			Creates and inits ROS components
		'''
		if self.ros_initialized:
			return 0
		
		# Publishers
		self._state_publisher = rospy.Publisher('~state', State, queue_size=10)
		# Subscribers
		# topic_name, msg type, callback, queue_size
		self.odom_sub = rospy.Subscriber('/summit_xl/odom', Odometry, self.OdomCb, queue_size = 10)
		self.gps_sub = rospy.Subscriber('/mavros/gps/fix', NavSatFix, self.GpsCb, queue_size = 10)
		self.ptu_sub = rospy.Subscriber('/ardu_ptu/data', ardu_ptu, self.PtuCb, queue_size = 10)
		self.battery_sub = rospy.Subscriber('/summit_xl_controller/battery', Float32, self.BatteryCb, queue_size = 10)
		# Service Servers
		# self.service_server = rospy.Service('~service', Empty, self.serviceCb)
		# Service Clients
		# self.service_client = rospy.ServiceProxy('service_name', ServiceMsg)
		# ret = self.service_client.call(ServiceMsg)
		
		self.ros_initialized = True
		
		self.publishROSstate()
		
		return 0
		
		
	def shutdown(self):
		'''
			Shutdowns device
			@return: 0 if it's performed successfully, -1 if there's any problem or the component is running
		'''
		if self.running or not self.initialized:
			return -1
		rospy.loginfo('%s::shutdown'%self.node_name)
		
		# Cancels current timers
		self.t_publish_state.cancel()
		
		self._state_publisher.unregister()
		
		self.initialized = False
		
		return 0
	
	
	def rosShutdown(self):
		'''
			Shutdows all ROS components
			@return: 0 if it's performed successfully, -1 if there's any problem or the component is running
		'''
		if self.running or not self.ros_initialized:
			return -1
		
		# Performs ROS topics & services shutdown
		self._state_publisher.unregister()
		
		self.ros_initialized = False
		
		return 0
			
	
	def stop(self):
		'''
			Creates and inits ROS components
		'''
		self.running = False
		
		return 0
	
	
	def start(self):
		'''
			Runs ROS configuration and the main control loop
			@return: 0 if OK
		'''
		self.rosSetup()
		
		if self.running:
			return 0
			
		self.running = True
		
		self.controlLoop()
		
		return 0
	
	
	def controlLoop(self):
		'''
			Main loop of the component
			Manages actions by state
		'''
		
		while self.running and not rospy.is_shutdown():
			t1 = time.time()
			
			if self.state == State.INIT_STATE:
				self.initState()
				
			elif self.state == State.STANDBY_STATE:
				self.standbyState()
				
			elif self.state == State.READY_STATE:
				self.readyState()
				
			elif self.state == State.EMERGENCY_STATE:
				self.emergencyState()
				
			elif self.state == State.FAILURE_STATE:
				self.failureState()
				
			elif self.state == State.SHUTDOWN_STATE:
				self.shutdownState()
				
			self.allState()
			
			t2 = time.time()
			tdiff = (t2 - t1)
			
			
			t_sleep = self.time_sleep - tdiff
			
			if t_sleep > 0.0:
				try:
					rospy.sleep(t_sleep)
				except rospy.exceptions.ROSInterruptException:
					rospy.loginfo('%s::controlLoop: ROS interrupt exception'%self.node_name)
					self.running = False
			
			t3= time.time()
			self.real_freq = 1.0/(t3 - t1)
		
		self.running = False
		# Performs component shutdown
		self.shutdownState()
		# Performs ROS shutdown
		self.rosShutdown()
		rospy.loginfo('%s::controlLoop: exit control loop'%self.node_name)
		
		return 0
		
		
	def rosPublish(self):
		'''
			Publish topics at standard frequency
		'''
					
		return 0
		
	
	def initState(self):
		'''
			Actions performed in init state
		'''
		
		if not self.initialized:
			self.setup()
			
		else: 		
			self.switchToState(State.STANDBY_STATE)
		
		
		return
	
	
	def standbyState(self):
		'''
			Actions performed in standby state
		'''
		self.switchToState(State.READY_STATE)
		
		return
	
	
	def readyState(self):
		'''
			Actions performed in ready state
		'''
		now = rospy.get_rostime()
		#rospy.loginfo("Current time %i %i", now.secs, now.nsecs)
		
		''' Battery fake value for simulation
		if (now.secs // 60) > self.minutes:
			self.minutes = self.minutes + 1
			self.battery_voltage = 53.0 - self.minutes * 0.1
		'''	
		if 47.0 <= self.battery_voltage <= 53.0:
			self.battery_value = 15.0 * self.battery_voltage - 695.0
		if 43.0 <= self.battery_voltage <= 47.0:
			self.battery_value = 5.0 * self.battery_voltage - 215.0
			
		## Record definition
		
		Attitude_record = {"header":{"sourceSystem": r"rawfie.rob.xl-1", r"sourceModule": "Navigation", "time": now.secs}, "phi": self.roll, "theta": self.pitch, "psi": self.yaw}
		Location_record = {"header":{"sourceSystem": r"rawfie.rob.xl-1", r"sourceModule": "Navigation", "time": now.secs},"latitude": self.latitude, 
								"longitude": self.longitude, "height": self.altitude, "n": self.location_x, "e": self.location_y, "d": 0 }
		FuelUsage_record = {"header":{"sourceSystem": r"rawfie.rob.xl-1", r"sourceModule": "UGV Summit_XL_1", "time": now.secs}, "value": int(self.battery_value)}
		SensorReadingScalar_record = {"header":{"sourceSystem": r"rawfie.rob.xl-1", r"sourceModule": "UGV Summit_XL_1", "time": now.secs}, "value": self.temperature , "unit": "KELVIN"}
		
		
		#Status_enum = {"header":{"sourceSystem": r"Testbed1", r"sourceModule": "UGV Summit_XL_1", "time": now.secs}, "status": "OK"}

		'''
			use the schema id directly
		'''
		encoded_Attitude = self.serializer.encode_record_with_schema_id(self.Attitude_schema_id, Attitude_record)
		encoded_Location = self.serializer.encode_record_with_schema_id(self.Location_schema_id, Location_record)
		encoded_FuelUsage = self.serializer.encode_record_with_schema_id(self.FuelUsage_schema_id, FuelUsage_record)
		encoded_SensorReadingScalar = self.serializer.encode_record_with_schema_id(self.SensorReadingScalar_schema_id, SensorReadingScalar_record)
		#encoded_Status = self.serializer.encode_record_with_schema_id(self.Status_schema_id, Status_enum)


		'''
		To send messages synchronously
		'''
		#kafka = KafkaClient('localhost:9092')
		kafka = KafkaClient('eagle5.di.uoa.gr:9092')
		'''		
		Attitude_producer = SimpleProducer(kafka)
		Location_producer = SimpleProducer(kafka)
		FuelUsage_producer = SimpleProducer(kafka)
		SensorReadingScalar_producer = SimpleProducer(kafka)
		Status_producer = SimpleProducer(kafka)
		'''
		Attitude_keyed_producer = KafkaProducer(bootstrap_servers=['eagle5.di.uoa.gr:9092'])
		Location_keyed_producer = KafkaProducer(bootstrap_servers=['eagle5.di.uoa.gr:9092'])
		FuelUsage_keyed_producer = KafkaProducer(bootstrap_servers=['eagle5.di.uoa.gr:9092'])
		SensorReadingScalar_keyed_producer = KafkaProducer(bootstrap_servers=['eagle5.di.uoa.gr:9092'])
		#Status_keyed_producer = KeyedProducer(kafka, partitioner=Murmur2Partitioner)
		'''
		Kafka topic
		'''
		partition = 6
		#key = "rawfie.rob.xl-1"
		'''
		Attitude_topic = "UGV_Attitude"
		Location_topic = "UGV_Location"
		FuelUsage_topic = "UGV_FuelUsage"
		SensorReadingScalar_topic = "UGV_SensorReadingScalar"
		Status_topic = "UGV_Status"
		
		Attitude_producer.send_messages(Attitude_topic, encoded_Attitude)
		Location_producer.send_messages(Location_topic, encoded_Location)
		FuelUsage_producer.send_messages(FuelUsage_topic, encoded_FuelUsage)
		SensorReadingScalar_producer.send_messages(SensorReadingScalar_topic, encoded_SensorReadingScalar)
		#Status_producer.send_messages(Status_topic, encoded_Status)
		'''
		#KEYED TESTS
		Attitude_keyed_topic = "Attitude"
		Location_keyed_topic = "Location"
		FuelUsage_keyed_topic = "FuelUsage"
		SensorReadingScalar_keyed_topic = "SensorReadingScalar"
		#Status_keyed_topic = "Status2"
		
		# Asynchronous by default
		Attitude_future = Attitude_keyed_producer.send(Attitude_keyed_topic, partition=6, value=encoded_Attitude)
		# Block for 'synchronous' sends
		try:
			Attitude_record_metadata = Attitude_future.get(timeout=5)
		except KafkaError:
			# Decide what to do if produce request failed...
			log.exception()
			pass
			
		# Asynchronous by default
		Location_future = Location_keyed_producer.send(Location_keyed_topic, partition=6, value=encoded_Location)
		# Block for 'synchronous' sends
		try:
			Location_record_metadata = Location_future.get(timeout=5)
		except KafkaError:
			# Decide what to do if produce request failed...
			log.exception()
			pass
			
		# Asynchronous by default
		FuelUsage_future = FuelUsage_keyed_producer.send(FuelUsage_keyed_topic, partition=6, value=encoded_FuelUsage)
		# Block for 'synchronous' sends
		try:
			FuelUsage_record_metadata = FuelUsage_future.get(timeout=5)
		except KafkaError:
			# Decide what to do if produce request failed...
			log.exception()
			pass
			
		# Asynchronous by default
		SensorReadingScalar_future = SensorReadingScalar_keyed_producer.send(SensorReadingScalar_keyed_topic, partition=6, value=encoded_SensorReadingScalar)
		# Block for 'synchronous' sends
		try:
			SensorReadingScalar_record_metadata = SensorReadingScalar_future.get(timeout=5)
		except KafkaError:
			# Decide what to do if produce request failed...
			log.exception()
			pass

		return
		
	
	def shutdownState(self):
		'''
			Actions performed in shutdown state 
		'''
		if self.shutdown() == 0:
			self.switchToState(State.INIT_STATE)
		
		return
	
	
	def emergencyState(self):
		'''
			Actions performed in emergency state
		'''
		
		return
	
	
	def failureState(self):
		'''
			Actions performed in failure state
		'''
		
			
		return
	
	
	def switchToState(self, new_state):
		'''
			Performs the change of state
		'''
		if self.state != new_state:
			self.previous_state = self.state
			self.state = new_state
			rospy.loginfo('%s::switchToState: %s'%(self.node_name, self.stateToString(self.state)))
		
		return
	
		
	def allState(self):
		'''
			Actions performed in all states
		'''
		self.rosPublish()
		
		return
	
	
	def stateToString(self, state):
		'''
			@param state: state to set
			@type state: State
			@returns the equivalent string of the state
		'''
		if state == State.INIT_STATE:
			return 'INIT_STATE'
				
		elif state == State.STANDBY_STATE:
			return 'STANDBY_STATE'
			
		elif state == State.READY_STATE:
			return 'READY_STATE'
			
		elif state == State.EMERGENCY_STATE:
			return 'EMERGENCY_STATE'
			
		elif state == State.FAILURE_STATE:
			return 'FAILURE_STATE'
			
		elif state == State.SHUTDOWN_STATE:
			return 'SHUTDOWN_STATE'
		else:
			return 'UNKNOWN_STATE'
	
		
	def publishROSstate(self):
		'''
			Publish the State of the component at the desired frequency
		'''
		self.msg_state.state = self.state
		self.msg_state.state_description = self.stateToString(self.state)
		self.msg_state.desired_freq = self.desired_freq
		self.msg_state.real_freq = self.real_freq
		self._state_publisher.publish(self.msg_state)
		
		self.t_publish_state = threading.Timer(self.publish_state_timer, self.publishROSstate)
		self.t_publish_state.start()
	
	
	def OdomCb(self, msg):
		'''
			Callback for summit_xl Odometry
			@param msg: received message
			@type msg: nav_msgs/Odometry
		'''

		odom_pose = msg.pose.pose;
		odom_q = (
			odom_pose.orientation.x,
			odom_pose.orientation.y,
			odom_pose.orientation.z,
			odom_pose.orientation.w)
		# use the angles with orientation_euler.x, orientation_euler.y, orientation_euler.z
		orientation_euler = tf.transformations.euler_from_quaternion( odom_q )
		self.roll = orientation_euler[0]
		self.pitch = orientation_euler[1]
		self.yaw = orientation_euler[2]
		self.location_x = odom_pose.position.x
		self.location_y = odom_pose.position.y
		
		# DEMO
		#rospy.loginfo('Odom received:: x:%f',odom_pose.position.x)
		
	def GpsCb(self, msg):
		'''
			Callback for summit_xl Odometry
			@param msg: received message
			@type msg: nav_msgs/Odometry
		'''
		latitude_deg = msg.latitude
		self.latitude = latitude_deg * (3.141592653589793238/180)
		longitude_deg = msg.longitude
		self.longitude = longitude_deg * (3.141592653589793238/180) 
		self.altitude = msg.altitude
		
		# DEMO
		#rospy.loginfo('Odom received:: x:%f',odom_pose.position.x)
		
	def PtuCb(self,msg):
		
		self.temperature = msg.temperature_1 + 273
	
	def BatteryCb(self,msg):
		
		self.battery_voltage = msg.data 
	
				
	"""
	def serviceCb(self, req):
		'''
			ROS service server
			@param req: Required action
			@type req: std_srv/Empty
		'''
		# DEMO
		rospy.loginfo('RComponent:serviceCb')	
	"""	
		
def main():

	rospy.init_node("rcomponent")
	
	
	_name = rospy.get_name().replace('/','')
	
	arg_defaults = {
	  'topic_state': 'state',
	  'desired_freq': DEFAULT_FREQ,
	}
	
	args = {}
	
	for name in arg_defaults:
		try:
			if rospy.search_param(name): 
				args[name] = rospy.get_param('~%s'%(name)) # Adding the name of the node, because the para has the namespace of the node
			else:
				args[name] = arg_defaults[name]
			#print name
		except rospy.ROSException, e:
			rospy.logerr('%s: %s'%(e, _name))
			
	
	rc_node = RComponent(args)
	
	rospy.loginfo('%s: starting'%(_name))

	rc_node.start()


if __name__ == "__main__":
	main()
