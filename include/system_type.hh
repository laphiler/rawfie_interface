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


#ifndef _HOME_GLAMDRING_PRUEBAS_KAFKA_AVROCPPHEADERS_INCLUDE_SYSTEM_TYPE_HH_1138202156__H_
#define _HOME_GLAMDRING_PRUEBAS_KAFKA_AVROCPPHEADERS_INCLUDE_SYSTEM_TYPE_HH_1138202156__H_


#include "boost/any.hpp"
#include "avro/Specific.hh"
#include "avro/Encoder.hh"
#include "avro/Decoder.hh"

enum SystemType {
    UUV,
    USV,
    UGV,
    UAV,
    FIXED,
};

namespace avro {
template<> struct codec_traits<SystemType> {
    static void encode(Encoder& e, SystemType v) {
        e.encodeEnum(v);
    }
    static void decode(Decoder& d, SystemType& v) {
        v = static_cast<SystemType>(d.decodeEnum());
    }
};

}
#endif
