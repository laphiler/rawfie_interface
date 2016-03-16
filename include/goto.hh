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


#ifndef _HOME_GLAMDRING_PRUEBAS_KAFKA_AVROCPPHEADERS_INCLUDE_GOTO_HH_3461367651__H_
#define _HOME_GLAMDRING_PRUEBAS_KAFKA_AVROCPPHEADERS_INCLUDE_GOTO_HH_3461367651__H_


#include "boost/any.hpp"
#include "avro/Specific.hh"
#include "avro/Encoder.hh"
#include "avro/Decoder.hh"
#include "header.hh"
#include "location.hh"


struct goto_avsc_Union__0__ {
private:
    size_t idx_;
    boost::any value_;
public:
    size_t idx() const { return idx_; }
    float get_float() const;
    void set_float(const float& v);
    bool is_null() const {
        return (idx_ == 1);
    }
    void set_null() {
        idx_ = 1;
        value_ = boost::any();
    }
    goto_avsc_Union__0__();
};

struct Goto {
    typedef goto_avsc_Union__0__ speed_t;
    Header header;
    Location location;
    speed_t speed;
    float timeout;
};

inline
float goto_avsc_Union__0__::get_float() const {
    if (idx_ != 0) {
        throw avro::Exception("Invalid type for union");
    }
    return boost::any_cast<float >(value_);
}

void goto_avsc_Union__0__::set_float(const float& v) {
    idx_ = 0;
    value_ = v;
}

inline goto_avsc_Union__0__::goto_avsc_Union__0__() : idx_(0), value_(float()) { }
namespace avro {
template<> struct codec_traits<goto_avsc_Union__0__> {
    static void encode(Encoder& e, goto_avsc_Union__0__ v) {
        e.encodeUnionIndex(v.idx());
        switch (v.idx()) {
        case 0:
            avro::encode(e, v.get_float());
            break;
        case 1:
            e.encodeNull();
            break;
        }
    }
    static void decode(Decoder& d, goto_avsc_Union__0__& v) {
        size_t n = d.decodeUnionIndex();
        if (n >= 2) { throw avro::Exception("Union index too big"); }
        switch (n) {
        case 0:
            {
                float vv;
                avro::decode(d, vv);
                v.set_float(vv);
            }
            break;
        case 1:
            d.decodeNull();
            v.set_null();
            break;
        }
    }
};

template<> struct codec_traits<Goto> {
    static void encode(Encoder& e, const Goto& v) {
        avro::encode(e, v.header);
        avro::encode(e, v.location);
        avro::encode(e, v.speed);
        avro::encode(e, v.timeout);
    }
    static void decode(Decoder& d, Goto& v) {
        avro::decode(d, v.header);
        avro::decode(d, v.location);
        avro::decode(d, v.speed);
        avro::decode(d, v.timeout);
    }
};

}
#endif
