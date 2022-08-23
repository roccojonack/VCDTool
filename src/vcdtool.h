#include "VCDFileParser.hpp"
#include <iostream>
#include <fstream>
#include <regex>
#include "json/json.h"

#pragma once
// function footprint
int  convertVCDVector2uint(VCDValue *);
void print_scope_signals(VCDFile *, VCDScope *, std::string, std::ostream &);
void print_stat_signals(VCDFile * , VCDScope * , std::string , Json::Value& );
void traverse_scope(std::string , VCDFile * , VCDScope * , bool , bool , bool, std::vector<std::string>, std::ostream&, Json::Value&);
void clean_signal_names(std::string, std::string );
bool readFilter(std::string , std::vector<std::string>& );
