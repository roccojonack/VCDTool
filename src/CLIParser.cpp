/*
 * CLIParser.cpp
 *
 *  Created on: Mar 19, 2019
 *      Author: eyck
 */

#include "CLIParser.h"
//#include <scc/report.h>
//#include "scc/report.h"
#include <iostream>
#include <stdexcept>

namespace po = boost::program_options;
//using namespace sc_core;
//using namespace ArterisVComp;

//static logging::log_level syscLogLut[] = {logging::NONE,  logging::FATAL,  logging::ERROR, logging::WARNING,
//                                          scc::log::INFO, scc::log::DEBUG, logging::TRACE, logging::DBGTRACE};

CLIParser::CLIParser(int argc, char* argv[])
: desc("Options")
, valid(false) {

    build();
    try {
        // po::store(po::parse_command_line(argc, argv, desc), vm_); // can throw
        po::store(po::command_line_parser(argc, argv).options(desc).run(), vm_); // can throw
        // --help option
        if(vm_.count("help")) {
            std::cout << "Arteris IP NCore architectural simulator" << std::endl << desc << std::endl;
        }
        po::notify(vm_); // throws on error, so do after help in case there are any problems
        valid = true;
    } catch(po::error& e) {
        std::cerr << "ERROR: " << e.what() << std::endl << std::endl;
        std::cerr << desc << std::endl;
    }
    //if(vm_.count("verbose")) { // NONE, FATAL, ERROR, WARNING, INFO, DEBUG, TRACE
        //auto log_level = std::min(6, vm_["verbose"].as<int>());
        //sc_report_handler::set_actions(SC_ID_MORE_THAN_ONE_SIGNAL_DRIVER_, SC_DO_NOTHING);
        //sc_report_handler::set_actions(SC_FATAL, SC_DISPLAY | SC_THROW);
        //scc::init_logging(syscLogLut[log_level]);
    //} else {
      //  scc::init_logging();
    //}
    //instance = this;
}

void CLIParser::build() {
    // clang-format off
    desc.add_options()
            ("help,h",              "Print help message")
            //("verbose,v",   po::value<int>()->default_value(3), "Sets logging verbosity (0=NONE, 1=FATAL, 2=ERROR, 3=WARN, 4=INFO, 5=DEBUG, 6=TRACE)")
            ("trace,t",             "enable tracing")
            ("instances,i",         "Show only instances")
            ("header",              "Show header")
            ("preprocessing,p",     "preprocessing VCD")
            ("stats,t",             "print the stats of VCD signals")
            ("fullpath,u",          "Show full signal path")
            ("start,s",     po::value<double>()->default_value(0),      "Start time (default to 0)")
            ("end,e",       po::value<double>()->default_value(-1),         "End time (default to end of file/-1)")
            ("file,f",      po::value<std::string>()->default_value(""),    "filename containing scopes and signal name regex")
            ("outputdirectory,o",      po::value<std::string>()->default_value(""),    "directory with outputfiles")
            ("VCD",         po::value<std::string>()->default_value(""),    "VCD input file")
        ;
    // clang-format on
}

CLIParser::~CLIParser() = default;
CLIParser* CLIParser::getSingletonObject() {
    //if(!instance) {
    //    instance = new CLIParser(argc, char* argv[]);
    //};
    //return instance;
};

