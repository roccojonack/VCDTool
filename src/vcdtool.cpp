
#include "VCDFileParser.hpp"
#include "vcdtool.h"
#include <numeric>
#include "json/json.h"

// converts a VCDValue into unsigned integer; error returns -1
// a real value will be casted to unsigned integer!
int convertVCDVector2uint(VCDValue *val)
{
    VCDBitVector *vecval;
    std::string fullVector("");
    switch (val->get_type())
    {
    case (VCD_SCALAR):
        fullVector = VCDValue::VCDBit2Char(val->get_value_bit());
        return std::stoi(fullVector, nullptr, 2);
        break;
    case (VCD_VECTOR):
        vecval = val->get_value_vector();
        for (auto it = vecval->begin(); it != vecval->end(); ++it)
        {
            fullVector += VCDValue::VCDBit2Char(*it);
        }
        return std::stoi(fullVector, nullptr, 2);
        break;
    case (VCD_REAL):
        return (unsigned int) val->get_value_real();
        break;
    default:
        return -1;
        break;
    }
};

void traverse_scope(std::string parent, VCDFile * trace, VCDScope * scope, 
                bool instances, bool fullpath, bool stats, 
                std::vector<std::string> filterVector, std::ostream& output, Json::Value& root)
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
                print_stat_signals(trace, scope, local_parent, root[scope->name]);
            else
                print_scope_signals(trace, scope, local_parent, output);
        }
        else {
            output << "no match on Scope: " << local_parent << std::endl;
        }
    }

    for (auto child : scope->children) {
        if (scope->name)
            traverse_scope(local_parent, trace, child, instances, fullpath, stats, filterVector, output, root[scope->name]);
        else
            traverse_scope(local_parent, trace, child, instances, fullpath, stats, filterVector, output, root);
    };
};


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
};

void print_stat_signals(VCDFile * trace, VCDScope * scope, std::string local_parent, Json::Value& root)
{
        std::regex cycle_counter_re("^(.*)(busy|idle|wait|running|EvictCounter|HitCounter|MissCounter|ValidCounter|WriteBackCounter|MrdReqs|mrd_skid_buffer_occupancy)");
        std::smatch m;
        double end_time = trace->get_timestamps()->back();
        for (VCDSignal *signal : scope->signals)
        { // iterating over all signals in current scope
            std::vector<unsigned int> Values;
            std::vector<double> WeightedValues;
            std::map<unsigned int, double> HistValues;
            VCDTime current_time = 0;
            VCDTime previous_time = 0;
            VCDTime first_transition = 0;
            VCDTime last_transition = 0;
            if (trace->get_signal_values(signal->hash)->size() < 2 ) continue; // print only values which toggle at least one time
            Json::Value json_tmp; 
            json_tmp["name"] = signal->reference;
            if (std::regex_search(signal->reference, m, cycle_counter_re))
            { // those are values for which a historgram doesn't make sense as they are running counters
                    VCDValue *val = trace->get_signal_values(signal->hash)->back()->value;
                    json_tmp["max"] = convertVCDVector2uint(val);
            }
            else
            {
                    for (auto i = trace->get_signal_values(signal->hash)->begin(); i != trace->get_signal_values(signal->hash)->end(); ++i)
                    {
                        VCDValue *val = (*i)->value;
                        current_time = (*i)->time;
                        if (first_transition==0) first_transition=(*i)->time;
                        last_transition=(*i)->time;
                        if (Values.size())
                        {
                            WeightedValues.push_back(Values.back() * (current_time - previous_time));
                            if (HistValues.find(Values.back()) != HistValues.end())
                            {
                                HistValues[Values.back()] += (current_time - previous_time);
                            }
                            else
                            {
                                HistValues[Values.back()] = (current_time - previous_time);
                            }
                        }
                        previous_time = current_time;
                        Values.push_back(convertVCDVector2uint(val));
                    }
                    WeightedValues.push_back(Values.back() * (end_time - previous_time));
                    if (HistValues.find(Values.back()) != HistValues.end())
                    {
                        HistValues[Values.back()] += (end_time - previous_time);
                    }
                    else
                    {
                        HistValues[Values.back()] = (end_time - previous_time);
                    }
                    auto min_value = *std::min_element(Values.begin(), Values.end());
                    auto max_value = *std::max_element(Values.begin(), Values.end());
                    float average = accumulate(WeightedValues.begin(), WeightedValues.end(), 0) / end_time;
                    output << "\thistogram:";
                    Json::Value json_hist; 
                    for (auto i = min_value; i <= max_value; ++i)
                    {
                        if (HistValues.find(i) != HistValues.end())
                        {
                            std::string s = std::to_string(i);
                            json_hist[s] = HistValues[i];
                        }
                    }
                    json_tmp["first"] = first_transition;
                    json_tmp["last"] = last_transition;
                    json_tmp["max"] = max_value;
                    json_tmp["min"] = min_value;
                    json_tmp["avg"] = average;
                    json_tmp["key"] = signal->hash;
                    json_tmp["histogram"] = json_hist;
                    json_tmp["transitions"] = trace->get_signal_values(signal->hash)->size();
            };
            root.append(json_tmp);
        }
};

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
    if (inFile.size()) {
        std::ifstream ifs (inFile, std::ifstream::in);
        std::string myString;
        std::cout << "opening file " << inFile << std::endl;
        while (std::getline(ifs, myString)) {
            myVector.push_back(myString);
        };
        return true;
    }
    return false;
};
