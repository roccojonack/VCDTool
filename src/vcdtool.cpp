
#include "VCDFileParser.hpp"
#include "vcdtool.h"
#include <numeric>

void print_scope_signals(VCDFile * trace, VCDScope * scope, std::string local_parent, std::ostream& output)
{
    for(VCDSignal * signal : scope -> signals) {
        output << signal -> hash << "\t" << trace->get_signal_values(signal -> hash)->size() << "\t"
                    << local_parent << "." << signal -> reference;
        if(signal -> size > 1) {
            output << "[" << signal -> lindex << ":" << signal -> rindex << "]";
        } else if (signal -> lindex >= 0) {
             output<< "[" << signal -> lindex << "]";
        }
        
        output << std::endl;

    }
}

void traverse_scope(std::string parent, VCDFile * trace, VCDScope * scope, 
                bool instances, bool fullpath, bool stats, 
                std::vector<std::string> filterVector, std::ostream& output)
{
    std::string local_parent = parent;
    bool foundScope = true;
    if (parent.length())
        local_parent += ".";
    local_parent += scope->name;
    if (filterVector.size()) {
        foundScope = false;
        for (auto i : filterVector) {
            std::regex name_re("^"+i+"(.*)");
            std::smatch m; 
            if (std::regex_search(local_parent, m, name_re)) {
                foundScope = true;
                break;
            }
        }
    }
    if (instances) {
        if (foundScope) {
             output << "Scope: " << local_parent << std::endl;
        }
        else {
            output << "no match on Scope: " << local_parent << std::endl;
        }
    }        
    
    if (fullpath) {
        if (foundScope) {
            if (stats)
                print_stat_signals(trace, scope, local_parent, output);
            else
                print_scope_signals(trace, scope, local_parent, output);
        }
        else {
            output << "no match on Scope: " << local_parent << std::endl;
        }
    }

    for (auto child : scope->children)
        traverse_scope(local_parent, trace, child, instances, fullpath, stats, filterVector, output);
}

void print_stat_signals(VCDFile * trace, VCDScope * scope, std::string local_parent, std::ostream& output)
{

    double end_time = trace->get_timestamps()->back();
    for (VCDSignal *signal : scope->signals)
    {
        std::vector<unsigned int> Values;
        std::vector<double> WeightedValues;
        std::map<unsigned int, double> HistValues;
        VCDTime current_time = 0;
        VCDTime previous_time = 0;
        for (auto i = trace->get_signal_values(signal->hash)->begin(); i != trace->get_signal_values(signal->hash)->end(); ++i)
        {
            VCDValue *val = (*i)->value;
            current_time  = (*i)->time;
            if (Values.size()) {
                WeightedValues.push_back(Values.back()*(current_time-previous_time));
                // output << "\t dbg" <<  Values.back() << " " << (current_time-previous_time);
                if (HistValues.find(Values.back())!=HistValues.end()) {
                    HistValues[Values.back()] += (current_time - previous_time);
                }
                else {
                    HistValues[Values.back()] = (current_time - previous_time);
                }
            }
            previous_time = current_time;
            VCDBitVector *vecval;
            std::string fullVector("");
            switch (val->get_type())
            {
            case (VCD_SCALAR):
                fullVector = VCDValue::VCDBit2Char(val -> get_value_bit());
                Values.push_back(std::stoi(fullVector,nullptr,2));
                break;
            case (VCD_VECTOR):
                vecval = val->get_value_vector();
                for (auto it = vecval->begin(); it != vecval->end(); ++it)
                {
                    fullVector += VCDValue::VCDBit2Char(*it);
                }
                Values.push_back(std::stoi(fullVector, nullptr, 2));
                break;
            case (VCD_REAL):
                output << val -> get_value_real();
                break;
            default:
                break;
            }
        }
        WeightedValues.push_back(Values.back()*(end_time-previous_time));
        //output << "\t dbg" <<  Values.back() << " " << (end_time-previous_time);
        if (HistValues.find(Values.back())!=HistValues.end()) {
            HistValues[Values.back()] += (end_time - previous_time);
        }
        else {
            HistValues[Values.back()] = (end_time - previous_time);
        }
        output << "\tmax:" << *std::max_element(Values.begin(), Values.end()) ;
        output << "\tmin:" << *std::min_element(Values.begin(), Values.end()) ;
        float average = accumulate( WeightedValues.begin(), WeightedValues.end(), 0) / end_time;
        output << "\thistogram:";
        for (auto i:HistValues) {
            output << i.first << "/" << i.second << ";";
        }
        output << "\taverage:" << average;
        output << "\tkey:" <<signal -> hash 
                << "\tsize:" << trace->get_signal_values(signal -> hash)->size()
                << "\tname:" << local_parent << "." << signal -> reference;
        if(signal -> size > 1) {
            output << "[" << signal -> lindex << ":" << signal -> rindex << "]";
        } else if (signal -> lindex >= 0) {
            output << "[" << signal -> lindex << "]";
        }
        
        output << std::endl;
    }
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

bool readFilter(std::string inFile, std::vector<std::string>& myVector)
{
    if (inFile.size())
    {
        std::ifstream ifs (inFile, std::ifstream::in);
        std::string myString;
        std::cout << "opening file " << inFile << std::endl;
        while (std::getline(ifs, myString)) {
            myVector.push_back(myString);
        };
        return true;
    }
    return false;
}
