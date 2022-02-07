
SRC_DIR         ?= ../src
BUILD_DIR       ?= ../build
DEP_PATH        ?= ../../verilog-vcd-parser/build

CXXFLAGS        += -I$(BUILD_DIR) -I$(SRC_DIR) -I$(DEP_PATH) -g -std=c++0x

VCD_SRC         ?= $(SRC_DIR)/VCDFile.cpp \
                   $(SRC_DIR)/VCDValue.cpp \
                   $(SRC_DIR)/VCDFileParser.cpp

VCD_PARSER        ?= $(BUILD_DIR)/vcd-parse

VCDTOOL        ?= $(BUILD_DIR)/vcdtool
VCDTOOL_SRC    ?= $(SRC_DIR)/vcdtool.cpp \
					$(SRC_DIR)/main.cpp 
VCDTOOL_OBJ     = $(patsubst $(SRC_DIR)/%.cpp,$(BUILD_DIR)/%.o,$(VCDTOOL_SRC))

all : $(VCDTOOL)

$(BUILD_DIR)/%.o : $(SRC_DIR)/%.cpp
	$(CXX) $(CXXFLAGS) -o $@ -c $^

$(VCDTOOL) : $(VCDTOOL_OBJ)
	$(CXX) $(CXXFLAGS) -o $@ $^ -lverilog-vcd-parser -L$(DEP_PATH) 

clean:
	rm -rf $(VCDTOOL) $(VCDTOOL_OBJ)
