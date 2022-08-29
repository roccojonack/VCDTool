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
git clone --recursive git@github.com:roccojonack/VCDTool.git
cd VCDTool
setenv BOOST_ROOT /scratch/rocco/workarea/tools/boost_1_70_0-gcc-6.3.0-install
setenv VCDPARSER_ROOT /scratch/rocco/workarea/tools/verilog-vcd-parser
mkdir build; cd build
cmake ..
make -j
