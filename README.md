# VCDTool
parsing and analyzing VCD files

# build inststructions
relies on repo verilog-vcd-parser to be build; should become subproject
go to build and do 
    make -f ../Makefile

# testing
./vcdtool -h
./vcdtool -u ../test/my_db.vcd

# todo
change to cmake
make verilog-vcd-parser a subproject
preprocessing of VCD to remore : from name string
seting tests
