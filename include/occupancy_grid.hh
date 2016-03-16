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


#ifndef _HOME_GLAMDRING_PRUEBAS_KAFKA_AVROCPPHEADERS_INCLUDE_OCCUPANCY_GRID_HH_3106578650__H_
#define _HOME_GLAMDRING_PRUEBAS_KAFKA_AVROCPPHEADERS_INCLUDE_OCCUPANCY_GRID_HH_3106578650__H_


#include "boost/any.hpp"
#include "avro/Specific.hh"
#include "avro/Encoder.hh"
#include "avro/Decoder.hh"
#include "header.hh"
#include "location.hh"

struct OccupancyGrid {
    Header header;
    int64_t map_load_time;
    float map_resolution;
    int32_t map_width;
    int32_t map_height;
    Location origin;
    std::vector<int32_t > data;
};

namespace avro {
template<> struct codec_traits<OccupancyGrid> {
    static void encode(Encoder& e, const OccupancyGrid& v) {
        avro::encode(e, v.header);
        avro::encode(e, v.map_load_time);
        avro::encode(e, v.map_resolution);
        avro::encode(e, v.map_width);
        avro::encode(e, v.map_height);
        avro::encode(e, v.origin);
        avro::encode(e, v.data);
    }
    static void decode(Decoder& d, OccupancyGrid& v) {
        avro::decode(d, v.header);
        avro::decode(d, v.map_load_time);
        avro::decode(d, v.map_resolution);
        avro::decode(d, v.map_width);
        avro::decode(d, v.map_height);
        avro::decode(d, v.origin);
        avro::decode(d, v.data);
    }
};

}
#endif
