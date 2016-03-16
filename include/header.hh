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


#ifndef HEADER_HH_3106508416__H_
#define HEADER_HH_3106508416__H_


#include "boost/any.hpp"
#include "avro/Specific.hh"
#include "avro/Encoder.hh"
#include "avro/Decoder.hh"

struct Header {
    std::string sourceSystem;
    std::string sourceModule;
    int64_t time;
};

namespace avro {
template<> struct codec_traits<Header> {
    static void encode(Encoder& e, const Header& v) {
        avro::encode(e, v.sourceSystem);
        avro::encode(e, v.sourceModule);
        avro::encode(e, v.time);
    }
    static void decode(Decoder& d, Header& v) {
        avro::decode(d, v.sourceSystem);
        avro::decode(d, v.sourceModule);
        avro::decode(d, v.time);
    }
};

}
#endif
