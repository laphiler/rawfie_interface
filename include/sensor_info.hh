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


#ifndef _HOME_GLAMDRING_PRUEBAS_KAFKA_AVROCPPHEADERS_INCLUDE_SENSOR_INFO_HH_3008351982__H_
#define _HOME_GLAMDRING_PRUEBAS_KAFKA_AVROCPPHEADERS_INCLUDE_SENSOR_INFO_HH_3008351982__H_


#include "boost/any.hpp"
#include "avro/Specific.hh"
#include "avro/Encoder.hh"
#include "avro/Decoder.hh"
#include "header.hh"
#include "sensor_type.hh"


struct SensorInfo {
    Header header;
    std::string vendor_name;
    std::string product_name;
    std::string serial;
    std::vector<SensorType> types;
};

namespace avro {
template<> struct codec_traits<SensorInfo> {
    static void encode(Encoder& e, const SensorInfo& v) {
        avro::encode(e, v.header);
        avro::encode(e, v.vendor_name);
        avro::encode(e, v.product_name);
        avro::encode(e, v.serial);
        avro::encode(e, v.types);
    }
    static void decode(Decoder& d, SensorInfo& v) {
        avro::decode(d, v.header);
        avro::decode(d, v.vendor_name);
        avro::decode(d, v.product_name);
        avro::decode(d, v.serial);
        avro::decode(d, v.types);
    }
};

}
#endif
