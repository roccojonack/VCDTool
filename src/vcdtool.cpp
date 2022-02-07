
#include "VCDFileParser.hpp"
#include "vcdtool.h"

void print_scope_signals(VCDFile * trace, VCDScope * scope, std::string local_parent)
{
    for(VCDSignal * signal : scope -> signals) {
        std::cout << signal -> hash << "\t" << trace->get_signal_values(signal -> hash)->size() << "\t"
                    << local_parent << "." << signal -> reference;

        if(signal -> size > 1) {
            std::cout << "[" << signal -> lindex << ":" << signal -> rindex << "]";
        } else if (signal -> lindex >= 0) {
            std::cout << "[" << signal -> lindex << "]";
        }
        
        std::cout << std::endl;

    }
}

void traverse_scope(std::string parent, VCDFile * trace, VCDScope * scope, bool instances, bool fullpath)
{
    std::string local_parent = parent;

    if (parent.length())
        local_parent += ".";
    local_parent += scope->name;
    if (instances)
        std::cout << "Scope: " << local_parent  << std::endl;
    if (fullpath)
        print_scope_signals(trace, scope, local_parent);
    for (auto child : scope->children)
        traverse_scope(local_parent, trace, child, instances, fullpath);
}

void clean_signal_names(std::string file_name, std::string out_file_name)
{
    std::ifstream ifs (file_name, std::ifstream::in);
    std::ofstream ofs (out_file_name, std::ofstream::out);
    std::regex signal_name_re("^\\$var\\s+(wire|real)\\s+(\\d+)\\s+(\\S+)\\s+(\\S+)\\s+(.*)");
    if (ifs.is_open()) {
        std::smatch m; 
        std::string myString;
        while (std::getline(ifs, myString)) {
            if (std::regex_search(myString, m, signal_name_re)) {
                std::string tmp = m[4];
                size_t found = tmp.find(":");
                if (found != std::string::npos) {
                    std::replace( tmp.begin(), tmp.end(), ':', '_'); 
                    unsigned int i=0;
                    for (auto x : m)  {
                        if (i==0) {
                             myString =  "$var";  i = 1; continue;
                        };
                       if (i==4) {
                            myString =  myString + " " + tmp;   
                        }
                        else {
                            std::string tmpS = m[i];
                            myString =  myString + " " + tmpS;   
                           std::cout << "need to subpatch:" << tmpS << ":" << myString << std::endl;
                       };
                        i++;
                    }
                    std::cout << "need to patch:" << tmp << ":" << myString << std::endl;
                }             
            };
            ofs << myString << std::endl;
        }
    };
    ifs.close();
    ofs.close();
};
