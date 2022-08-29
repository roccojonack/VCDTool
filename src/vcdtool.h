#include "VCDFileParser.hpp"
#include <iostream>
#include <fstream>
#include <regex>
#include "json/json.h"
#include "CLIParser.h"

#pragma once
int  convertVCDVector2uint(VCDValue *);
bool readFilter(std::string , std::vector<std::string>& );
void clean_signal_names(std::string, std::string);

class VCDAnalyzer
{
    public:
        VCDAnalyzer(VCDFile *trace, CLIParser *CLISingleton) { 
            m_trace = trace;
            instances = CLISingleton->is_set("instances");
            fullpath  = CLISingleton->is_set("fullpath");
            stats     = CLISingleton->is_set("stats");
            header    = CLISingleton->is_set("header");
        };
        // function footprint
        void start_analysis(std::vector<std::string>  filterVector, Json::Value& root)
        {
            if (header) {
                root["Version"] = m_trace->version ;
                root["Comment"] = m_trace->comment ;
                root["Date"] = m_trace->date ;
                root["Count"] = m_trace->get_signals()->size() ;
                root["Begin"] = m_trace->get_timestamps()->front();
                root["End"] = m_trace->get_timestamps()->back() ;
            }
            traverse_scope(std::string(""), m_trace, m_trace->root_scope, instances, fullpath, stats, filterVector, root);
        };
        VCDFile *m_trace;
        bool instances;
        bool fullpath;
        bool stats;
        bool header; 
        void print_scope_signals(VCDFile *, VCDScope *, std::string, Json::Value &);
        void print_stat_signals(VCDFile *, VCDScope *, std::string, Json::Value &);
        void traverse_scope(std::string, VCDFile *, VCDScope *, bool, bool, bool, std::vector<std::string>, Json::Value &);
};