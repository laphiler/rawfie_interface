/*
 * librdkafka - Apache Kafka C library
 *
 * Copyright (c) 2014, Magnus Edenhill
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * 1. Redistributions of source code must retain the above copyright notice,
 *    this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright notice,
 *    this list of conditions and the following disclaimer in the documentation
 *    and/or other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 */

/**
 * Apache Kafka consumer & producer example programs
 * using the Kafka driver from librdkafka
 * (https://github.com/edenhill/librdkafka)
 */
#include <rdkafka_consumer.h>
#include <typeinfo>

#include <ros/ros.h>
#include <tf/transform_listener.h>
#include <tf/transform_datatypes.h>
#include "geometry_msgs/PoseStamped.h"
#include <tf/LinearMath/Matrix3x3.h>
#include <vector>
#include <geometry_msgs/Twist.h>
#include <std_msgs/Float32.h>
#include <std_msgs/String.h>
#include <std_msgs/Bool.h>
#include <math.h>
#include <string>
#include <nav_msgs/Odometry.h>

#include <iostream>
#include <sys/time.h>

#include <move_base_msgs/MoveBaseAction.h>
#include <actionlib/client/simple_action_client.h>



RdKafkaConsumer::RdKafkaConsumer(int partition, std::string topic){
	brokers = "localhost";
	
	this->partition = partition;
	this->topic_str = topic;
	start_offset = RdKafka::Topic::OFFSET_BEGINNING;
	conf = RdKafka::Conf::create(RdKafka::Conf::CONF_GLOBAL);
	tconf = RdKafka::Conf::create(RdKafka::Conf::CONF_TOPIC);
	
	/*
	* Set configuration properties
	*/
	conf->set("metadata.broker.list", brokers, errstr);
	conf->set("event_cb", &ex_event_cb, errstr);
	 /* Set delivery report callback */
    conf->set("dr_cb", &ex_dr_cb, errstr);

    /*
     * Create consumer using accumulated global configuration.
     */
    kafka_consumer = RdKafka::Consumer::create(conf, errstr);
    if (!kafka_consumer) {
      std::cerr << "Failed to create consumer: " << errstr << std::endl;
      exit(1);
    }
    std::cout << "% Created consumer " << kafka_consumer->name() << std::endl;
    /*
     * Create topic handle.
     */
    kafka_topic = RdKafka::Topic::create(kafka_consumer, topic_str,
						   tconf, errstr);
    if (!kafka_topic) {
      std::cerr << "Failed to create topic: " << errstr << std::endl;
      exit(1);
    }
    /*
     * Start consumer.
     */
    RdKafka::ErrorCode resp = kafka_consumer->start(kafka_topic, partition, start_offset);    
    if (resp != RdKafka::ERR_NO_ERROR) {
      std::cerr << "Failed to start consumer: " << RdKafka::err2str(resp) << std::endl;
      exit(1);
    }
}

RdKafkaConsumer::~RdKafkaConsumer(){
	
    delete kafka_topic;
    delete kafka_consumer;
        
	/*
   * Wait for RdKafka to decommission.
   * This is not strictly needed (when check outq_len() above), but
   * allows RdKafka to clean up all its resources before the application
   * exits so that memory profilers such as valgrind wont complain about
   * memory leaks.
   */
	RdKafka::wait_destroyed(5000);
}



RdKafka::Message *RdKafkaConsumer::consumeMsg(){
    // Consume messages
	RdKafka::Message *kafka_msg = kafka_consumer->consume(kafka_topic, partition, 1000);

    int err_code = kafka_msg->err();
    if(err_code ==  RdKafka::ERR_NO_ERROR){
      /* Real message */
      std::cout << "Read msg at offset " << kafka_msg->offset() << ", len = " << kafka_msg->len() << std::endl;
      if (kafka_msg->key()) {
        std::cout << "Key: " << *kafka_msg->key() << std::endl;
      }
    }else if(err_code == RdKafka::ERR__UNKNOWN_TOPIC or err_code == RdKafka::ERR__UNKNOWN_PARTITION){
      std::cerr << "Consume failed: " << kafka_msg->errstr() << std::endl;
      return NULL;
    }else{
      /* Errors */
      std::cerr << "Consume failed: " << kafka_msg->errstr() << std::endl;
      return NULL;
	}
	
	return kafka_msg;
	
	//delete kafka_msg;     
	//kafka_consumer->poll(0);
}


class RwfConsumerInterface{
    public:

		typedef actionlib::SimpleActionClient<move_base_msgs::MoveBaseAction> MoveBaseClient;

        // Variables
        ros::NodeHandle n;
        ros::Publisher  pubTwist;
		
		RdKafkaConsumer *kafka_loc_consumer;
		RdKafkaConsumer *kafka_goto_consumer;
		RdKafkaConsumer *kafka_att_consumer;
		RdKafkaConsumer *kafka_head_consumer;
		float pos_x, pos_y, desired_freq_;
		bool active_goal;
        move_base_msgs::MoveBaseGoal goal;
		MoveBaseClient *ac;
		
        // Methods
        RwfConsumerInterface()
        {
            ROS_INFO("Setup");
            ros::NodeHandle np("~");
            desired_freq_ = 10.0;
			
            pos_x = 0.0;
            pos_y = 0.0;
            active_goal=false;
            //pubTwist = n.advertise<geometry_msgs::Twist>(twist_topic, 1);

			kafka_loc_consumer = new RdKafkaConsumer(0,"location");
			kafka_goto_consumer = new RdKafkaConsumer(0,"goto");
			kafka_att_consumer = new RdKafkaConsumer(0,"attitude");
			kafka_head_consumer = new RdKafkaConsumer(0,"header");
			
			ac = new MoveBaseClient("move_base", true);
            ROS_INFO("Setup finished");
        };


        void start()
        {
            ROS_INFO("Starting");
            
            ros::Rate r(desired_freq_);
            while(ros::ok())
            {	
				ros::spinOnce();
				
				/*Location
				RdKafka::Message *kafka_loc_msg;
				Location *Loc;
				
				ROS_INFO("Location Consumer");
				kafka_loc_msg = kafka_loc_consumer->consumeMsg();
				if(kafka_loc_msg!=NULL){
					Loc = static_cast<Location *>(kafka_loc_msg->payload());
					ROS_INFO("Location: x:%f  y:%f", Loc->n, Loc->e);
				}
				/*Attitude
				RdKafka::Message *kafka_att_msg;
				Attitude *Att;
								
				ROS_INFO("Attitude Consumer");
				kafka_att_msg = kafka_loc_consumer->consumeMsg();
				if(kafka_att_msg!=NULL){
					Att = static_cast<Attitude *>(kafka_att_msg->payload());
					ROS_INFO("Attitude: phi:%f  theta:%f psi:%f", Att->phi, Att->theta, Att->psi);
				}
				/*Head*/
				RdKafka::Message *kafka_head_msg;
				Header *Head;				
				
				ROS_INFO("Header Consumer");
				kafka_head_msg = kafka_head_consumer->consumeMsg();
				if(kafka_head_msg!=NULL){
					Head = static_cast<Header *>(kafka_head_msg->payload());
					//if(typeid(Head->sourceSystem) == typeid(std::string))
					//std::cout << "Hola" <<  Head->sourceSystem.empty() << std::endl;
					//ROS_INFO("Header: sourceSystem:%s  sourceModule:%s  time:%ld", Head->sourceSystem.c_str(), Head->sourceModule.c_str(), Head->time);
					ROS_INFO("time:%ld",  Head->time);
				}
				/* Goto */
				RdKafka::Message *kafka_goto_msg;
				Goto *Got;
				
				kafka_goto_msg = kafka_goto_consumer->consumeMsg();
				if(kafka_goto_msg!=NULL){
					Got = static_cast<Goto *>(kafka_goto_msg->payload());
					pos_x = Got->location.n;
					pos_y = Got->location.e;
					ROS_INFO("Goto: x:%f  y:%f", pos_x, pos_y);

					while(!ac->waitForServer(ros::Duration(5.0)))
					{
					  ROS_INFO("Waiting for the move_base action server to come up");
					}

					if(!active_goal)
					{
					   //we'll send a goal to the robot
					   goal.target_pose.header.frame_id = "base_link";
					   goal.target_pose.header.stamp = ros::Time::now();
					   goal.target_pose.pose.position.x = pos_x;
					   goal.target_pose.pose.position.y = pos_y;
					   goal.target_pose.pose.orientation = tf::createQuaternionMsgFromYaw(0);

					   ROS_INFO("Sending goal");
					   ac->sendGoal(goal);
					   active_goal = true;
					}

				   ac->waitForResult(ros::Duration(1.0));

				   if(ac->getState() == actionlib::SimpleClientGoalState::SUCCEEDED)
				   {
					 ROS_INFO("the base reached the goal");
					 active_goal=false;
				   }
				   else if(ac->getState() != actionlib::SimpleClientGoalState::ACTIVE)
				   {
					 ROS_INFO("Navigation Failed");
				   }
				}
				
                r.sleep();
            }
            ros::shutdown();

        };
        

}; //end of class

int main(int argc, char** argv){

	ros::init(argc, argv, "RwfConsumerInterface");
	ros::Time::init();

	RwfConsumerInterface RwfConsumerInterface_= RwfConsumerInterface();

	RwfConsumerInterface_.start();

	return 0;
	
};

