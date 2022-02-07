#include "VCDFileParser.hpp"
#include <iostream>
#include <fstream>
#include <regex>
#pragma once

// function footprint
void print_scope_signals(VCDFile * trace, VCDScope * scope, std::string local_parent);

void traverse_scope(std::string parent, VCDFile * trace, VCDScope * scope, bool instances, bool fullpath);

void clean_signal_names(std::string, std::string );
