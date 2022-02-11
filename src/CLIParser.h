/*
 * CLIParser.h
 *
 *  Created on: Mar 19, 2019
 *      Author: eyck
 */

#pragma once

#include <boost/program_options.hpp>
#include <memory>

class CLIParser {
public:
    CLIParser(int argc, char* argv[]);
    static CLIParser *getSingletonObject();

    virtual ~CLIParser();

    bool is_valid() { return valid; }

    const boost::program_options::variables_map& vm() { return vm_; }

    bool is_set(const char* option) { return vm_.count(option) != 0; }

    template <typename T> const T& get(const char* option) { return vm_[option].as<T>(); }

private:
    void build();
    bool valid;
    boost::program_options::variables_map vm_;
    boost::program_options::options_description desc;
    //static  CLIParser *instance;
};

