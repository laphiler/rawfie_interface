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


#include <rdkafka_producer.h>

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



RdKafkaProducer::RdKafkaProducer(int partition, std::string topic){
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
     * Create producer using accumulated global configuration.
     */
	kafka_producer = RdKafka::Producer::create(conf, errstr);
    if (!kafka_producer) {
      std::cerr << "Failed to create producer: " << errstr << std::endl;
      exit(1);
    }

    std::cout << "% Created producer " << kafka_producer->name() << std::endl;

    /*
     * Create topic handle.
     */
    kafka_topic = RdKafka::Topic::create(kafka_producer, topic_str,
						   tconf, errstr);
    if (!kafka_topic) {
      std::cerr << "Failed to create topic: " << errstr << std::endl;
      exit(1);
    }


};


RdKafkaProducer::~RdKafkaProducer(){
	
    delete kafka_topic;
    delete kafka_producer;
    
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
int RdKafkaProducer::sendMsg(T msg){
	
	RdKafka::ErrorCode resp = kafka_producer->produce(kafka_topic, partition,
		  RdKafka::Producer::RK_MSG_COPY, const_cast<T *>(&msg), sizeof(msg), NULL, NULL);

	if (resp != RdKafka::ERR_NO_ERROR)
	   std::cerr << "% Produce failed: " << RdKafka::err2str(resp) << std::endl;
	else
	   std::cerr << "% Produced message (" << sizeof(msg) << " bytes)" << std::endl;

	kafka_producer->poll(0);


	return 0;
}



class RwfInterface{
    public:

        // Variables
        ros::NodeHandle n;
        ros::Publisher  pubTwist;
		ros::Subscriber sub_battery_state;
        ros::Subscriber sub_emergency_stop;
        ros::Subscriber summit_odom_sub;
        

        geometry_msgs::Quaternion q,odom_q;
        geometry_msgs::Pose odom_pose;
        tf::Quaternion q_tf,odom_q_tf;
        std::string twist_topic,odom_topic;
        std_msgs::Float32 odom_yaw_deg,odom_posX,odom_posY;

        float desired_freq_;
        float posX;
        float posY;
        float yaw_y_rad;
        double roll, pitch, yaw, odom_roll, odom_pitch, odom_yaw;
        unsigned long int sec;
		
		Location Loc;
		Attitude Att;
		Header Head;
		RdKafkaProducer *location_producer, *attitude_producer, *header_producer;
		
        // Methods
        RwfInterface()
        {
            ROS_INFO("Setup");
            ros::NodeHandle np("~");
            desired_freq_ = 5.0;
			
            posX = 0.0;
            posY = 0.0;

            np.param<std::string>("Odom_topic", odom_topic, "/summit_xl/odom");

            pubTwist = n.advertise<geometry_msgs::Twist>(twist_topic, 1);

			sub_battery_state = n.subscribe("/summit_xl_controller/battery", 1,&RwfInterface::BatteryCallback,this);
            sub_emergency_stop = n.subscribe("/summit_xl_controller/emergency_stop", 1,&RwfInterface::ESCallback,this);
            summit_odom_sub = n.subscribe<nav_msgs::Odometry>(odom_topic, 1,&RwfInterface::SummitOdomCallback,this);

			location_producer = new RdKafkaProducer(0, "test");
			attitude_producer = new RdKafkaProducer(1, "test");
			header_producer = new RdKafkaProducer(2, "test");

            ROS_INFO("Setup finished");
        };




        void start()
        {
            ROS_INFO("Starting");
            
            ros::Rate r(desired_freq_);
            while(ros::ok())
            {								
				Loc.n = odom_pose.position.x;
				Loc.e = odom_pose.position.y;				
				location_producer->sendMsg(Loc);
				ROS_INFO("Location Produced");

				Att.phi = odom_roll;
				Att.theta = odom_pitch;
				Att.psi = odom_yaw;
				attitude_producer->sendMsg(Att);
				ROS_INFO("Attitude Produced");
				
				sec= time(NULL);
				Head.sourceSystem = "TestSystem";
				Head.sourceModule = "SummitTest";
				Head.time = sec;
				header_producer->sendMsg(Head);
				ROS_INFO("Header Produced");				
				
                r.sleep();
            }
            ros::shutdown();

        };



        ////////////////////////
        // Callback functions //
        ////////////////////////

        void BatteryCallback(const std_msgs::Float32& battery_voltage)
        {

        };


        void ESCallback(const std_msgs::Bool& emergency_stop)
        {

        };

        //odometry

		void SummitOdomCallback(const nav_msgs::Odometry::ConstPtr& odom_msg)
		{

				odom_pose= odom_msg->pose.pose;
				odom_q = odom_pose.orientation;

				tf::quaternionMsgToTF(odom_q,odom_q_tf);
				tf::Matrix3x3(odom_q_tf).getRPY(odom_roll, odom_pitch, odom_yaw);

		};


}; //end of class

int main(int argc, char** argv){

	ros::init(argc, argv, "RwfInterface");
	ros::Time::init();

	RwfInterface RwfInterface_= RwfInterface();

	RwfInterface_.start();

	return 0;
	
};

/*
int main (int argc, char **argv) {
  
	RdKafkaProducer producer(0, "test");
	Location c1;
	c1.latitude = 1;
	 
	unsigned long int sec= time(NULL);
	std::cout<<sec<<std::endl;
	
	for(int i= 0; i<10; i++){
		//producer.sendMsg(double(i+100));
		producer.sendMsg(c1);
		sleep(1);
		c1.latitude += 1;
	}

	return 0;
}
*/
