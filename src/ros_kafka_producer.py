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
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Point, Quaternion
import tf

from robotnik_msgs.msg import State
from confluent.schemaregistry.client import CachedSchemaRegistryClient
from confluent.schemaregistry.serializers import MessageSerializer, Util
from kafka import SimpleProducer, KafkaClient
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
		
		self.rp = rospkg.RosPack()
		self.Header_path_file = os.path.join(self.rp.get_path('rawfie_interface'), 'Avro_Schemas/uxv', 'header.avsc')
		self.Attitude_path_file = os.path.join(self.rp.get_path('rawfie_interface'), 'Avro_Schemas/uxv', 'attitude.avsc')
		self.Location_path_file = os.path.join(self.rp.get_path('rawfie_interface'), 'Avro_Schemas/uxv', 'location.avsc')
			
	def setup(self):
		'''
			Initializes de hand
			@return: True if OK, False otherwise
		'''
		'''
		Some helper methods in util to get a schema
		'''
		
		#avro_schema = Util.parse_schema_from_file(r'/Kafka_python/tests2/python-confluent-schemaregistry/Avro_Schemas/header.avsc')
		#self.avro_schema = Util.parse_schema_from_string(open(r'/home/glamdring/catkin_ws/src/rawfie_interface/Avro_Schemas/header.avsc').read())
		self.Header_avro_schema = Util.parse_schema_from_string(open(self.Header_path_file).read())
		self.Attitude_avro_schema = Util.parse_schema_from_string(open(self.Attitude_path_file).read())
		self.Location_avro_schema = Util.parse_schema_from_string(open(self.Location_path_file).read())

		'''
		Initialize the client
		'''
		
		self.client = CachedSchemaRegistryClient(url='http://localhost:8081')
		'''
			# Schema operations
		'''
		'''
		Register a schema for a subject
		'''
		
		self.Header_schema_id = self.client.register('UGV_Header', self.Header_avro_schema)
		self.Attitude_schema_id = self.client.register('UGV_Attitude', self.Attitude_avro_schema)
		self.Location_schema_id = self.client.register('UGV_Location', self.Location_avro_schema)
		'''
		Get the version of a schema
		'''
		
		self.Header_schema_version = self.client.get_version('UGV_Header', self.Header_avro_schema)
		self.Attitude_schema_version = self.client.get_version('UGV_Attitude', self.Attitude_avro_schema)
		self.Location_schema_version = self.client.get_version('UGV_Location', self.Location_avro_schema)
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
		self.odom_sub = rospy.Subscriber('/odom', Odometry, self.OdomCb, queue_size = 10)
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
		
		Header_record = {"sourceSystem": "Testbed1", "sourceModule": "UGV Summit_XL_1", "time": now.secs}
		Attitude_record = {"header":{"sourceSystem": r"Testbed1", r"sourceModule": "UGV Summit_XL_1", "time": now.secs}, "phi": 1.854, "theta": 3.041, "psi": 2.031}
		Location_record = {"latitude": 0, "longitude": 0, "height": 0, "n": self.location_x, "e": self.location_y, "d": 0, "depth": 0, "altitude": 0}

		'''
			use the schema id directly
		'''
		encoded_Header = self.serializer.encode_record_with_schema_id(self.Header_schema_id, Header_record)
		encoded_Attitude = self.serializer.encode_record_with_schema_id(self.Attitude_schema_id, Attitude_record)
		encoded_Location = self.serializer.encode_record_with_schema_id(self.Location_schema_id, Location_record)
		'''
		use an existing schema and topic
		this will register the schema to the right subject based
		on the topic name and then serialize
		'''
		#encoded = serializer.encode_record_with_schema('my_topic', avro_schema, record)
		'''
		encode a record with the latest schema for the topic
		this is not efficient as it queries for the latest
		schema each time
		'''
		#encoded = serializer.encode_record_for_topic('my_kafka_topic', record)

		'''
		To send messages synchronously
		'''
		kafka = KafkaClient('localhost:9092')
		Header_producer = SimpleProducer(kafka)
		Attitude_producer = SimpleProducer(kafka)
		Location_producer = SimpleProducer(kafka)
		'''
		Kafka topic
		'''
		Header_topic = "Header"
		Header_producer.send_messages(Header_topic, encoded_Header)
		Attitude_topic = "Attitude"
		Attitude_producer.send_messages(Attitude_topic, encoded_Attitude)
		Location_topic = "Location"
		Location_producer.send_messages(Location_topic, encoded_Location)
		
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
		odom_q = odom_pose.orientation;
		# use the angles with orientation_euler.x, orientation_euler.y, orientation_euler.z
		self.orientation_euler = tf.transformations.euler_from_quaternion( odom_q )
		self.location_x = odom_pose.position.x
		self.location_y = odom_pose.position.y
		
		# DEMO
		rospy.loginfo('Odom received:: x:%f',odom_pose.position.x)
				
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
