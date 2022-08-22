# VCDTool
parsing and analyzing VCD files

# build inststructions
relies on repo verilog-vcd-parser to be build; should become subproject
go to build and do 
    make -f ../Makefile

# testing
./vcdtool -h
./vcdtool -u --VCD ../test/my_db.vcd

# todo
improve cmake
make verilog-vcd-parser a subproject
setting up tests
remove histograms for hit and miss counters

# clones (make submodule)
 git clone git@github.com:ben-marchal/verilog...
 git clone git@github.com:Arteris-IP/SystemC-Components.git
  