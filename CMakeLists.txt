cmake_minimum_required(VERSION 2.8.3)
project(rawfie_interface)


find_package(catkin REQUIRED COMPONENTS
  roscpp
  std_msgs
  std_srvs
  diagnostic_msgs
  diagnostic_updater
)

## System dependencies are found with CMake's conventions
# find_package(Boost REQUIRED COMPONENTS system)


###################################
## catkin specific configuration ##
###################################
## The catkin_package macro generates cmake config files for your package
## Declare things to be passed to dependent projects
## INCLUDE_DIRS: uncomment this if you package contains header files
## LIBRARIES: libraries you create in this project that dependent projects also need
## CATKIN_DEPENDS: catkin_packages dependent projects also need
## DEPENDS: system dependencies of this project that dependent projects also need
catkin_package(
    INCLUDE_DIRS include
#  LIBRARIES rcomponent
#  CATKIN_DEPENDS roscpp std_msgs
  DEPENDS rdkafka++ rdkafka avrocpp
)

###########
## Build ##
###########


include_directories(
   include
  ${catkin_INCLUDE_DIRS}
)

## Declare a cpp executable
#add_executable(rcomponent_node src/rcomponent.cpp)

add_executable(RwfInterface src/rdkafka_producer.cpp)

## Add cmake target dependencies of the executable/library
## as an example, message headers may need to be generated before nodes
#add_dependencies(rcomponent_node robotnik_msgs_generate_messages_cpp)


## Specify libraries to link a library or executable target against
#target_link_libraries(rcomponent_node
#   ${catkin_LIBRARIES}
#)

target_link_libraries(RwfInterface
  rdkafka++
  rdkafka
  avrocpp
  ${catkin_LIBRARIES} 
)
