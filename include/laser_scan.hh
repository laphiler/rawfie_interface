/**
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */


#ifndef _HOME_GLAMDRING_PRUEBAS_KAFKA_AVROCPPHEADERS_LASER_SCAN_HH_1598239383__H_
#define _HOME_GLAMDRING_PRUEBAS_KAFKA_AVROCPPHEADERS_LASER_SCAN_HH_1598239383__H_


#include "boost/any.hpp"
#include "avro/Specific.hh"
#include "avro/Encoder.hh"
#include "avro/Decoder.hh"
#include "header.hh"

struct LaserScan {
    Header header;
    float angle_min;
    float angle_max;
    float angle_increment;
    float time_increment;
    float scan_time;
    float range_min;
    float range_max;
    std::vector<float > ranges;
    std::vector<float > intensities;
};

namespace avro {
template<> struct codec_traits<LaserScan> {
    static void encode(Encoder& e, const LaserScan& v) {
        avro::encode(e, v.header);
        avro::encode(e, v.angle_min);
        avro::encode(e, v.angle_max);
        avro::encode(e, v.angle_increment);
        avro::encode(e, v.time_increment);
        avro::encode(e, v.scan_time);
        avro::encode(e, v.range_min);
        avro::encode(e, v.range_max);
        avro::encode(e, v.ranges);
        avro::encode(e, v.intensities);
    }
    static void decode(Decoder& d, LaserScan& v) {
        avro::decode(d, v.header);
        avro::decode(d, v.angle_min);
        avro::decode(d, v.angle_max);
        avro::decode(d, v.angle_increment);
        avro::decode(d, v.time_increment);
        avro::decode(d, v.scan_time);
        avro::decode(d, v.range_min);
        avro::decode(d, v.range_max);
        avro::decode(d, v.ranges);
        avro::decode(d, v.intensities);
    }
};

}
#endif
