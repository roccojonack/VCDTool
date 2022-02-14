
SRC_DIR         ?= ../src
BUILD_DIR       ?= ../build
DEP_PATH        ?= ../../verilog-vcd-parser/build

CXXFLAGS        += -I$(BUILD_DIR) -I$(SRC_DIR) -I$(DEP_PATH) -I/scratch/rocco/workarea/tools/boost_1_70_0-gcc-6.3.0-install/include -g -std=c++11

VCD_SRC         ?= $(SRC_DIR)/VCDFile.cpp \
                   $(SRC_DIR)/VCDValue.cpp \
                   $(SRC_DIR)/VCDFileParser.cpp

VCD_PARSER        ?= $(BUILD_DIR)/vcd-parse

VCDTOOL        ?= $(BUILD_DIR)/vcdtool
VCDTOOL_SRC    ?= $(SRC_DIR)/vcdtool.cpp $(SRC_DIR)/CLIParser.cpp \
					$(SRC_DIR)/main.cpp 
VCDTOOL_OBJ     = $(patsubst $(SRC_DIR)/%.cpp,$(BUILD_DIR)/%.o,$(VCDTOOL_SRC))

all : $(VCDTOOL)

$(BUILD_DIR)/%.o : $(SRC_DIR)/%.cpp
	$(CXX) $(CXXFLAGS) -o $@ -c $^

$(VCDTOOL) : $(VCDTOOL_OBJ)
	$(CXX) $(CXXFLAGS) -o $@ -lboost_program_options  $^ -lboost_program_options -lboost_timer -lverilog-vcd-parser -L$(DEP_PATH) -L/scratch/rocco/workarea/tools/boost_1_70_0-gcc-6.3.0-install/lib

clean:
	rm -rf $(VCDTOOL) $(VCDTOOL_OBJ)
