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
import WGS
import rospy
import actionlib
from move_base_msgs.msg import * 

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
from kafka import SimpleProducer, KafkaClient, KafkaConsumer
import avro.schema
import io, random
from avro.io import DatumWriter



DEFAULT_FREQ = 10.0
MAX_FREQ = 500.0

	
# Class Template of Robotnik component for Pyhton
class RKConsumer:
	
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
		self.goal_received = False
		self.goal_sent = False
		self.abort_received = False
		
		self.rp = rospkg.RosPack()

		self.tranformWGS = WGS.WGS84toNED()

			
	def setup(self):
		'''
			Initializes de hand
			@return: True if OK, False otherwise
		'''
		'''
		Initialize the client
		'''
		
		#self.client = CachedSchemaRegistryClient(url='http://localhost:8081')
		self.client = CachedSchemaRegistryClient(url='http://eagle5.di.uoa.gr:8081')

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
		#self.odom_sub = rospy.Subscriber('/odom', Odometry, self.OdomCb, queue_size = 10)
		# Service Servers
		# self.service_server = rospy.Service('~service', Empty, self.serviceCb)
		# Service Clients
		# self.service_client = rospy.ServiceProxy('service_name', ServiceMsg)
		# ret = self.service_client.call(ServiceMsg)
		
		self.ros_initialized = True
		
		
		'''
		consumer = KafkaConsumer('Header',
								 group_id='UGV_Header',
								 bootstrap_servers=['localhost:9092'])
								 

		attitude_consumer = KafkaConsumer('Attitude',
								 group_id='UGV_Attitude',
								 bootstrap_servers=['localhost:9092'])                         


		location_consumer = KafkaConsumer('Location',
								 group_id='UGV_Location',
								 bootstrap_servers=['localhost:9092']) 
								                         

		self.location_consumer = KafkaConsumer('UGV_Location',
				 bootstrap_servers=['localhost:9092']) 
				
		self.abort_consumer = KafkaConsumer('UGV_Abort',
				 bootstrap_servers=['localhost:9092'])  				 
								 
        '''                       
		
		self.goal_consumer = KafkaConsumer('UGV_Goto',
						bootstrap_servers=['eagle5.di.uoa.gr:9092'])  
								 
								 
		
		# 'eagle5.di.uoa.gr:9092'
		# 'eagle5.di.uoa.gr:2181";	
		# 'localhost:9092'
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
					 
		# decode a message from kafka
		'''
		for msg in consumer:
			decoded_object = self.serializer.decode_message(msg.value)
			print decoded_object
			break

		for msg in attitude_consumer:
			attitude_decoded_object = self.serializer.decode_message(msg.value)
			print attitude_decoded_object
			break
		
		try:
			
			for msg in self.location_consumer:
				location_decoded_object = self.serializer.decode_message(msg.value)
				print location_decoded_object
				break
			
		except:
			pass
		'''
		try:
			for msg in self.goal_consumer:
				
				goal_decoded_object = self.serializer.decode_message(msg.value)
				goal_location = goal_decoded_object.get('location')
				goal_header = goal_decoded_object.get('header')
				
				#(41.186809, -8.703597) origin matosinhos/pass to radians
				pointA = {'latitude' : 0.718845850137 , 'longitude' : -0.151905701075,'height' : 0}
				pointB = {}

				pointB['latitude'] = goal_location.get('latitude')
				pointB['longitude'] = goal_location.get('longitude')
				pointB['height'] = goal_location.get('height')
				ned = self.tranformWGS.displacement(pointA,pointB)
				print ned
				goal_x = ned.get('north')
				goal_y = ned.get('east')
				goal_time = goal_header.get('time')
				self.goal_received = True
				print ("Goal Received")
				break
		except :
			pass
		'''	
		try:
			for msg in self.goal_consumer:
				goal_decoded_object = self.serializer.decode_message(msg.value)
				goal_location = goal_decoded_object.get('location')
				goal_header = goal_decoded_object.get('header')
				goal_x = goal_location.get('n')
				goal_y = goal_location.get('e')
				goal_time = goal_header.get('time')
				self.goal_received = True
				print ("Goal Received")
				break
		except :
			pass
		'''
		'''	
		try:
			for msg in self.abort_consumer:
				abort_decoded_object = self.serializer.decode_message(msg.value)
				abort_header = abort_decoded_object.get('header')
				abort_time = abort_header.get('time')

				self.abort_received = True
				print ("Abort command Received")
				break
		except :
			pass
			
		'''	
		
		if self.goal_received:
			#Simple Action Client
			self.sac = actionlib.SimpleActionClient('move_base', MoveBaseAction )

			#create goal
			goal = MoveBaseGoal()
			
			#set goal
			goal.target_pose.pose.position.x = goal_x
			goal.target_pose.pose.position.y = goal_y
			goal.target_pose.pose.orientation.w = 1
			print goal.target_pose.pose
			goal.target_pose.header.frame_id = 'odom'
			goal.target_pose.header.stamp = rospy.Time.now()

			#start listner
			print ("Waiting for server to come up")			
			self.sac.wait_for_server()
			#send goal
			self.sac.send_goal(goal)
			print ("Goal Sent")
			self.goal_received = False
			self.goal_sent = True

		#finish
		if self.goal_sent:
			self.sac.wait_for_result(rospy.Duration.from_sec(5.0))
			#print self.sac.get_state()
				
			if self.sac.get_state()== 3 :		   
				rospy.loginfo("the base reached the goal")
				self.goal_sent = False
				print self.sac.get_result()
							
			if (self.sac.get_state()!= 1 and self.sac.get_state()!= 3) or self.abort_received :
				self.sac.cancel_goal()
				rospy.loginfo("Navigation Failed")
				self.goal_sent = False
				self.abort_received = False
				print self.sac.get_result()
		
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
	
	"""
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

	rospy.init_node("RKConsumer")
	
	
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
			
	
	rc_node = RKConsumer(args)
	
	rospy.loginfo('%s: starting'%(_name))

	rc_node.start()


if __name__ == "__main__":
	main()
