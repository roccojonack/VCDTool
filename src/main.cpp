// #include "cxxopts.hpp"
#include "CLIParser.h"
#include "vcdtool.h"
#include <vector>
#include <boost/timer/timer.hpp>
#include "json/json.h"
#include <fstream>

using namespace boost::timer;
/*!
@brief VCD file parser with optional JSON output of all active (at least one transaction) signals
*/
int main(int argc, char **argv)
{
    CLIParser *CLISingleton = new CLIParser(argc, argv);
    cpu_timer timer;
    std::string infile(CLISingleton->get<std::string>("VCD"));
    std::string file = CLISingleton->get<std::string>("file");
    std::string outputdir = CLISingleton->get<std::string>("outputdirectory");
    std::string designinfofile = CLISingleton->get<std::string>("designinfofile");
    std::string outfile(infile);

    if (!infile.size())
    {
        std::cout << "need at least a VCD file to process" << std::endl;
        return 1;
    }
    if (CLISingleton->is_set("preprocessing"))
    {
        outfile = ".patched.vcd";
        std::cout << "preprocessing of " << infile << std::endl;
        clean_signal_names(infile, outfile);
        std::cout << timer.format() << '\n';
    }

    VCDFileParser parser;
    std::cout << "parsing of " << outfile << " starts" << std::endl;
    VCDFile *trace = parser.parse_file(outfile);
    std::cout << "parsing of " << outfile << " done with time " << timer.format();
    if (!trace)
    {
        std::cout << "Parse Failed." << std::endl;
        return 1;
    }

    std::vector<std::string> filterVector;
    if (file.size())
        readFilter(file, filterVector);
    if (designinfofile.size())
    {
        std::ifstream f(designinfofile);
        Json::Value root;
        f >> root;
    };

    VCDAnalyzer VCDAnalyzer1(trace, CLISingleton);
    std::cout << "scope traversal of " << outfile << " starts" << std::endl;
    VCDAnalyzer1.start_analysis(filterVector);
    if (outputdir.size())
    {
        std::ofstream outp;
        outp.open(outputdir);
        std::ofstream out(outputdir, std::ofstream::out);
        out << VCDAnalyzer1.m_root << std::endl;
    }
    else
    {
        std::cout << VCDAnalyzer1.m_root << std::endl;
    }
    std::cout << "scope traversal done with time " << timer.format();
    delete trace;
    std::cout << "finishing up" << std::endl;
    return 0;
}
