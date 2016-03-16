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


#ifndef _HOME_GLAMDRING_PRUEBAS_KAFKA_AVROCPPHEADERS_INCLUDE_SYSTEM_INFO_HH_3865642743__H_
#define _HOME_GLAMDRING_PRUEBAS_KAFKA_AVROCPPHEADERS_INCLUDE_SYSTEM_INFO_HH_3865642743__H_


#include "boost/any.hpp"
#include "avro/Specific.hh"
#include "avro/Encoder.hh"
#include "avro/Decoder.hh"
#include "header.hh"
#include "system_type.hh"


struct SystemInfo {
    Header header;
    std::string vendor;
    std::string model;
    SystemType type;
    std::string name;
    std::string owner;
};

namespace avro {
template<> struct codec_traits<SystemInfo> {
    static void encode(Encoder& e, const SystemInfo& v) {
        avro::encode(e, v.header);
        avro::encode(e, v.vendor);
        avro::encode(e, v.model);
        avro::encode(e, v.type);
        avro::encode(e, v.name);
        avro::encode(e, v.owner);
    }
    static void decode(Decoder& d, SystemInfo& v) {
        avro::decode(d, v.header);
        avro::decode(d, v.vendor);
        avro::decode(d, v.model);
        avro::decode(d, v.type);
        avro::decode(d, v.name);
        avro::decode(d, v.owner);
    }
};

}
#endif
