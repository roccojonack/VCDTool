cmake_minimum_required(VERSION 3.12)
set    ( EXEC_NAME VCDTool )
project( ${EXEC_NAME} )

find_package(Boost 1.70 REQUIRED COMPONENTS iostreams program_options regex timer system)

message(STATUS " Library  - ${Boost_LIBRARIES}")
message(STATUS " DIR  - ${Boost_INCLUDE_DIRS}")

# build executable
FILE(GLOB MyCSources *.cpp json/*.cpp)
link_directories($ENV{VCDPARSER_ROOT}/build)
add_executable(${PROJECT_NAME} ${MyCSources})
#add_library(${PROJECT_NAME}  STATIC ${MyCSources})
target_link_libraries( ${PROJECT_NAME} PUBLIC verilog-vcd-parser)
target_link_libraries( ${PROJECT_NAME} PUBLIC ${Boost_LIBRARIES} )
# target_link_libraries( ${PROJECT_NAME} PUBLIC CONAN_PKG::yaml-cpp)
target_include_directories(${PROJECT_NAME} PRIVATE $ENV{VCDPARSER_ROOT}/build)
target_include_directories(${PROJECT_NAME} PRIVATE ${Boost_INCLUDE_DIRS})
target_include_directories(${PROJECT_NAME} PRIVATE ${CMAKE_CURRENT_LIST_DIR}/)
link_directories($ENV{VCDPARSER_ROOT}/build)

enable_testing()
set (failRegex "ERROR") 
set (passRegex "finishing up")

if(CMAKE_BUILD_TYPE STREQUAL "Coverage")
	include(CodeCoverage)
	APPEND_COVERAGE_COMPILER_FLAGS()
	set(CMAKE_CXX_FLAGS  "${CMAKE_CXX_FLAGS} -O0")
#   setup_target_for_coverage(test ${TEST_TARGET} coverage)
endif()
#set(COVERAGE_LCOV_EXCLUDES 'dir1/*' 'dir/2*')

file(GLOB TEST_VCD "${CMAKE_SOURCE_DIR}/test/*.vcd")
message("binary=" ${CMAKE_BINARY_DIR})
foreach(TESTFILE ${TEST_VCD})
    message("search dir for VCD tests =" ${TESTFILE})
    add_test(NAME     VCD_${TESTFILE} 
         COMMAND    ${CMAKE_BINARY_DIR}/src/${EXEC_NAME} --VCD ${TESTFILE} -u -a
       WORKING_DIRECTORY  ${CMAKE_BINARY_DIR})
    
    set_tests_properties ( VCD_${TESTFILE}
       PROPERTIES
       FAIL_REGULAR_EXPRESSION "${failRegex}"
    )
    set_tests_properties ( VCD_${TESTFILE}
       PROPERTIES
       PASS_REGULAR_EXPRESSION "${passRegex}"
   )
endforeach()

file(GLOB TEST_FC_VCD "${CMAKE_SOURCE_DIR}/test/fc/*.vcd")
message("binary=" ${CMAKE_BINARY_DIR})
foreach(TESTFILE ${TEST_FC_VCD})
    message("search dir for VCD FC tests =" ${TESTFILE})
    add_test(NAME     VCD_FC_${TESTFILE} 
         COMMAND    ${CMAKE_BINARY_DIR}/src/${EXEC_NAME} --VCD ${TESTFILE} -p -u -a
       WORKING_DIRECTORY  ${CMAKE_BINARY_DIR})
    
    set_tests_properties ( VCD_FC_${TESTFILE}
       PROPERTIES
       FAIL_REGULAR_EXPRESSION "${failRegex}"
    )
    set_tests_properties ( VCD_FC_${TESTFILE}
       PROPERTIES
       PASS_REGULAR_EXPRESSION "${passRegex}"
   )
endforeach()

#install and doc steps
install(TARGETS       ${EXEC_NAME}
        RUNTIME       DESTINATION bin
        LIBRARY       DESTINATION ${CMAKE_INSTALL_LIBDIR}
        ARCHIVE       DESTINATION ${CMAKE_INSTALL_LIBDIR}
)

# install examples
#INSTALL (FILES ${TOPLEVEL_DIR}/test/configs/CodaCache_1M_synth.csr.json         DESTINATION test/configs)
#INSTALL (FILES ${TOPLEVEL_DIR}/test/STL/example.stl                             DESTINATION test/STL)
# INSTALL (FILES ${Boost_LIBRARIES}       DESTINATION ${TOPLEVEL_DIR}/install/lib )

