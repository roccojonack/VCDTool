
#include "VCDFileParser.hpp"

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
