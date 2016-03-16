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


#ifndef __LOCATION_H_
#define __LOCATION_H_


#include "boost/any.hpp"
#include "avro/Specific.hh"
#include "avro/Encoder.hh"
#include "avro/Decoder.hh"

struct location_avsc_Union__0__ {
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
    location_avsc_Union__0__();
};

struct location_avsc_Union__1__ {
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
    location_avsc_Union__1__();
};

struct Location {
    typedef location_avsc_Union__0__ depth_t;
    typedef location_avsc_Union__1__ altitude_t;
    double latitude;
    double longitude;
    float height;
    double n;
    double e;
    double d;
    depth_t depth;
    altitude_t altitude;
};

inline
float location_avsc_Union__0__::get_float() const {
    if (idx_ != 0) {
        throw avro::Exception("Invalid type for union");
    }
    return boost::any_cast<float >(value_);
}

void location_avsc_Union__0__::set_float(const float& v) {
    idx_ = 0;
    value_ = v;
}

inline
float location_avsc_Union__1__::get_float() const {
    if (idx_ != 0) {
        throw avro::Exception("Invalid type for union");
    }
    return boost::any_cast<float >(value_);
}

void location_avsc_Union__1__::set_float(const float& v) {
    idx_ = 0;
    value_ = v;
}

inline location_avsc_Union__0__::location_avsc_Union__0__() : idx_(0), value_(float()) { }
inline location_avsc_Union__1__::location_avsc_Union__1__() : idx_(0), value_(float()) { }
namespace avro {
template<> struct codec_traits<location_avsc_Union__0__> {
    static void encode(Encoder& e, location_avsc_Union__0__ v) {
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
    static void decode(Decoder& d, location_avsc_Union__0__& v) {
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

template<> struct codec_traits<location_avsc_Union__1__> {
    static void encode(Encoder& e, location_avsc_Union__1__ v) {
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
    static void decode(Decoder& d, location_avsc_Union__1__& v) {
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

template<> struct codec_traits<Location> {
    static void encode(Encoder& e, const Location& v) {
        avro::encode(e, v.latitude);
        avro::encode(e, v.longitude);
        avro::encode(e, v.height);
        avro::encode(e, v.n);
        avro::encode(e, v.e);
        avro::encode(e, v.d);
        avro::encode(e, v.depth);
        avro::encode(e, v.altitude);
    }
    static void decode(Decoder& d, Location& v) {
        avro::decode(d, v.latitude);
        avro::decode(d, v.longitude);
        avro::decode(d, v.height);
        avro::decode(d, v.n);
        avro::decode(d, v.e);
        avro::decode(d, v.d);
        avro::decode(d, v.depth);
        avro::decode(d, v.altitude);
    }
};

}
#endif
