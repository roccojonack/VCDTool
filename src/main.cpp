//#include "cxxopts.hpp"
#include "CLIParser.h"
#include "vcdtool.h"
#include <vector>

/*!
@brief Standalone test function to allow testing of the VCD file parser.
*/
int main (int argc, char** argv)
{

    CLIParser *CLISingleton = new CLIParser(argc, argv);

    std::string infile (CLISingleton->get<std::string>("VCD"));
    std::string outfile (infile);
    if (CLISingleton->is_set("preprocessing")) {
        outfile = "tmp_patched.vcd";
        std::cout << "preprocessing of "  <<  infile << std::endl;
        clean_signal_names(infile, outfile);
    }

    if (!outfile.size()) {
        std::cout << "no file to parse; finishing up" << std::endl;
        return 0;
    };    
    VCDFileParser parser;
    std::cout << "parsing of " << outfile << std::endl;
    VCDFile *trace = parser.parse_file(outfile);
    std::cout << "parsing of " << outfile << " done" << std::endl;
    bool instances = CLISingleton->is_set("instances");
    bool fullpath = CLISingleton->is_set("fullpath");
    bool stats = CLISingleton->is_set("stats");
    std::vector<std::string> filterVector;
    std::string file = CLISingleton->get<std::string>("file");
    readFilter(file, filterVector);

    if (trace) {
        if (CLISingleton->is_set("header")) {
            std::cout << "Version:       " << trace->version << std::endl;
            std::cout << "Comment:       " << trace->comment << std::endl;
            std::cout << "Date:          " << trace->date << std::endl;
            std::cout << "Signal count:  " << trace->get_signals()->size() << std::endl;
            std::cout << "Times Recorded:" << trace->get_timestamps()->size() << std::endl;
            if (fullpath)
                std::cout << "Hash\tToggles\tFull signal path\n";
        }
        // Print out every signal in every scope.
        std::cout << "scope traversal of " << outfile << std::endl;
        traverse_scope(std::string(""), trace, trace->root_scope, instances, fullpath, stats, filterVector);

        delete trace;

        std::cout << "finishing up" << std::endl;
        return 0;
    } else {
        std::cout << "Parse Failed." << std::endl;
        return 1;
    }
}
