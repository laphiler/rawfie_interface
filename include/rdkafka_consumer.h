

#ifndef __KAFKA_PRODUCER_H
	#define __KAFKA_PRODUCER_H

#include <librdkafka/rdkafkacpp.h>
#include "avro/Encoder.hh"
#include "avro/Decoder.hh"
#include "location.hh"
#include "attitude.hh"
#include "header.hh"
#include <iostream>
#include <string>
#include <cstdlib>
#include <cstdio>
#include <csignal>
#include <cstring>
#include <getopt.h>
	
class ExampleDeliveryReportCb : public RdKafka::DeliveryReportCb {
 public:
  void dr_cb (RdKafka::Message &message) {
    std::cout << "Message delivery for (" << message.len() << " bytes): " <<
        message.errstr() << std::endl;
  }
};

class ExampleEventCb : public RdKafka::EventCb {
 public:
  void event_cb (RdKafka::Event &event) {
    switch (event.type())
    {
      case RdKafka::Event::EVENT_ERROR:
        std::cerr << "ERROR (" << RdKafka::err2str(event.err()) << "): " <<
            event.str() << std::endl;
        if (event.err() == RdKafka::ERR__ALL_BROKERS_DOWN)
          exit(-1);
        break;

      case RdKafka::Event::EVENT_STATS:
        std::cerr << "\"STATS\": " << event.str() << std::endl;
        break;

      case RdKafka::Event::EVENT_LOG:
        fprintf(stderr, "LOG-%i-%s: %s\n",
                event.severity(), event.fac().c_str(), event.str().c_str());
        break;

      default:
        std::cerr << "EVENT " << event.type() <<
            " (" << RdKafka::err2str(event.err()) << "): " <<
            event.str() << std::endl;
        break;
    }
  }
};


/* Use of this partitioner is pretty pointless since no key is provided
 * in the produce() call. */
class MyHashPartitionerCb : public RdKafka::PartitionerCb {
 public:
  int32_t partitioner_cb (const RdKafka::Topic *topic, const std::string *key,
                          int32_t partition_cnt, void *msg_opaque) {
    return djb_hash(key->c_str(), key->size()) % partition_cnt;
  }
 private:

  static inline unsigned int djb_hash (const char *str, size_t len) {
    unsigned int hash = 5381;
    for (size_t i = 0 ; i < len ; i++)
      hash = ((hash << 5) + hash) + str[i];
    return hash;
  }
};


class RdKafkaConsumer{
	protected:
	
	std::string brokers;// = "localhost";
	std::string errstr;
	std::string topic_str;
	int32_t partition;
	int64_t start_offset;

	MyHashPartitionerCb hash_partitioner;

	/*
	* Create configuration objects
	*/
	RdKafka::Conf *conf;
	RdKafka::Conf *tconf;
	
	ExampleEventCb ex_event_cb;
	ExampleDeliveryReportCb ex_dr_cb;
	RdKafka::Consumer *kafka_consumer;
	RdKafka::Topic *kafka_topic;

	public:
	
	RdKafkaConsumer(int partition, std::string topic);
	~RdKafkaConsumer();
	template <class T>
	int consumeMsg(T *read_msg);
	template <class T> 
	void msg_consume(RdKafka::Message* message, T* read_msg);
		
};

#endif
