#include "VCDFileParser.hpp"
#include <iostream>
#include <fstream>
#include <regex>
#pragma once

// function footprint
void print_scope_signals(VCDFile * , VCDScope * , std::string , std::ostream&);
void print_stat_signals(VCDFile * , VCDScope * , std::string , std::ostream&);
void traverse_scope(std::string , VCDFile * , VCDScope * , bool , bool , bool, std::vector<std::string>, std::ostream&);
void clean_signal_names(std::string, std::string );
bool readFilter(std::string , std::vector<std::string>& );
