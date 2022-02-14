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
change to cmake
make verilog-vcd-parser a subproject
setting up tests
add JSON for output formating