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


#ifndef _HOME_GLAMDRING_PRUEBAS_KAFKA_AVROCPPHEADERS_INCLUDE_UNIT_HH_1237501830__H_
#define _HOME_GLAMDRING_PRUEBAS_KAFKA_AVROCPPHEADERS_INCLUDE_UNIT_HH_1237501830__H_


#include "boost/any.hpp"
#include "avro/Specific.hh"
#include "avro/Encoder.hh"
#include "avro/Decoder.hh"

enum Unit {
    AMPERE,
    VOLT,
    BIT,
    BYTE,
    KILOGRAM,
    DECIBEL,
    KELVIN,
    PASCAL,
    HERTZ,
    METER,
    METER_PER_SECOND,
    METER_PER_SECOND_PER_SECOND,
    SECOND,
    SIEMENS_PER_METER,
    NTU,
    NEWTON,
    PERCENT,
    PARTS_PER_MILLION,
    PARTS_PER_BILLION,
    PSU,
    RADIAN,
    RADIAN_PER_SECOND,
    ROTATION_PER_MINUTE,
};

namespace avro {
template<> struct codec_traits<Unit> {
    static void encode(Encoder& e, Unit v) {
        e.encodeEnum(v);
    }
    static void decode(Decoder& d, Unit& v) {
        v = static_cast<Unit>(d.decodeEnum());
    }
};

}
#endif
