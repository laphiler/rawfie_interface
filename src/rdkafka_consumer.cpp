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

template <class T>
void RdKafkaConsumer::msg_consume(RdKafka::Message* message, T* read_msg) {
	//Location *payload;
	
    int err_code = message->err();
    if(err_code ==  RdKafka::ERR_NO_ERROR){
      /* Real message */
      std::cout << "Read msg at offset " << message->offset() << std::endl;
      if (message->key()) {
        std::cout << "Key: " << *message->key() << std::endl;
      }
      //payload = static_cast<Location *>(message->payload());
      read_msg = static_cast<T *>(message->payload());
      //std::cout << '(' << payload->latitude << ')' << std::endl;  
        
    }else if(err_code == RdKafka::ERR__UNKNOWN_TOPIC or err_code == RdKafka::ERR__UNKNOWN_PARTITION){
      std::cerr << "Consume failed: " << message->errstr() << std::endl;
    }else{
      /* Errors */
      std::cerr << "Consume failed: " << message->errstr() << std::endl;
   }
}

template <class T>
int RdKafkaConsumer::consumeMsg(T *read_msg){
    //Start consumer for topic+partition at start offset
     
   /* RdKafka::ErrorCode resp = kafka_consumer->start(kafka_topic, partition, start_offset);    
    if (resp != RdKafka::ERR_NO_ERROR) {
      std::cerr << "Failed to start consumer: " << RdKafka::err2str(resp) << std::endl;
      exit(1);
    }*/
    // Consume messages
    
	RdKafka::Message *kafka_msg = kafka_consumer->consume(kafka_topic, partition, 1000);
	msg_consume(kafka_msg, read_msg);
	delete kafka_msg;     
	kafka_consumer->poll(0);
}


class RwfConsumerInterface{
    public:

        // Variables
        ros::NodeHandle n;
        ros::Publisher  pubTwist;
		
		Location Loc;
		RdKafkaConsumer *rd_kafka_consumer;
		float pos_x, pos_y, desired_freq_;

		
        // Methods
        RwfConsumerInterface()
        {
            ROS_INFO("Setup");
            ros::NodeHandle np("~");
            desired_freq_ = 5.0;
			
            pos_x = 0.0;
            pos_y = 0.0;
            //pubTwist = n.advertise<geometry_msgs::Twist>(twist_topic, 1);

			rd_kafka_consumer = new RdKafkaConsumer(0,"test");
            ROS_INFO("Setup finished");
        };


        void start()
        {
            ROS_INFO("Starting");
            
            ros::Rate r(desired_freq_);
            while(ros::ok())
            {								
				rd_kafka_consumer->consumeMsg(&Loc);
				pos_x = Loc.n;
				pos_y = Loc.e;
				ROS_INFO("Location: x:%f  y:%f", pos_x, pos_y);
		
                r.sleep();
            }
            ros::shutdown();

        };

}; //end of class

int main(int argc, char** argv){

	ros::init(argc, argv, "RwfInterface");
	ros::Time::init();

	RwfConsumerInterface RwfConsumerInterface_= RwfConsumerInterface();

	RwfConsumerInterface_.start();

	return 0;
	
};

