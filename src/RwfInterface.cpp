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


#include "rdkafka_producer.h"


using namespace std;


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
		
		Location Loc;
		RdKafkaProducer *location_producer;
        // Methods
        RwfInterface()
        {
            ROS_INFO("Setup");
            ros::NodeHandle np("~");
            desired_freq_ = 50.0;
			
            posX = 0.0;
            posY = 0.0;

            np.param<std::string>("Odom_topic", odom_topic, "/summit_xl/odom");

            pubTwist = n.advertise<geometry_msgs::Twist>(twist_topic, 1);

			sub_battery_state = n.subscribe("/summit_xl_controller/battery", 1,&RwfInterface::BatteryCallback,this);
            sub_emergency_stop = n.subscribe("/summit_xl_controller/emergency_stop", 1,&RwfInterface::ESCallback,this);
            summit_odom_sub = n.subscribe<nav_msgs::Odometry>(odom_topic, 1,&RwfInterface::SummitOdomCallback,this);

			location_producer = new RdKafkaProducer(0, "test");
            ROS_INFO("Setup finished");
        };




        void start()
        {
            ROS_INFO("Starting");
            
            ros::Rate r(desired_freq_);
            while(ros::ok()){				
				int s  = 3;
				Loc.n = odom_pose.position.x;
				Loc.e = odom_pose.position.y;				
				location_producer->sendMsg(Loc);
				ROS_INFO("Location Produced");

				/*RdKafkaProducer attitude_producer(1, "test");
				Attitude Att;
				Att.phi = odom_roll;
				Att.theta = odom_pitch;
				Att.psi = odom_yaw;
				attitude_producer.sendMsg(Att);
				ROS_INFO("Attitude Produced");*/

				
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
}
