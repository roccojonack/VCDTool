//#include "cxxopts.hpp"
#include "CLIParser.h"
#include "vcdtool.h"
#include <vector>
#include <boost/timer/timer.hpp>
#include "json/json.h"

using namespace boost::timer;
/*!
@brief Standalone test function to allow testing of the VCD file parser.
*/
int main (int argc, char** argv)
{

    CLIParser *CLISingleton = new CLIParser(argc, argv);
    cpu_timer timer;
    std::string infile (CLISingleton->get<std::string>("VCD"));
    std::string outfile (infile);
    if (CLISingleton->is_set("preprocessing")) {
        outfile = "tmp_patched.vcd";
        std::cout << "preprocessing of "  <<  infile << std::endl;
        clean_signal_names(infile, outfile);
        std::cout << timer.format() << '\n';
    }

    if (!outfile.size()) {
        std::cout << "no file to parse; finishing up" << std::endl;
        return 0;
    };
    VCDFileParser parser;
    std::cout << "parsing of " << outfile << std::endl;
    VCDFile *trace = parser.parse_file(outfile);
    std::cout << "parsing of " << outfile << " done with time " << timer.format();
    VCDAnalyzer VCDAnalyzer1(trace, CLISingleton);

    std::vector<std::string> filterVector;
    std::string file = CLISingleton->get<std::string>("file");
    std::string outputdir = CLISingleton->get<std::string>("outputdirectory");
    readFilter(file, filterVector);
    
    if (trace)
    {
        Json::Value root;
 
        std::cout << "scope traversal of " << outfile << std::endl;
        VCDAnalyzer1.start_analysis(filterVector, root);
        if (outputdir.size())
        {
            std::ofstream outp;
            outp.open(outputdir);
            std::ofstream out(outputdir, std::ofstream::out);
            out << VCDAnalyzer1.m_root << std::endl;
        }
        else {
            std::cout << VCDAnalyzer1.m_root << std::endl;
        }
        std::cout << "scope traversal done with time "<< timer.format();

        delete trace;

        std::cout << "finishing up" << std::endl;
        return 0;
    }
    else
    {
        std::cout << "Parse Failed." << std::endl;
        return 1;
    }
}
