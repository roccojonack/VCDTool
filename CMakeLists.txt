cmake_minimum_required(VERSION 3.12)
LIST(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR}/SystemC-Components/cmake)

if (POLICY CMP0048)
	cmake_policy(SET CMP0048 NEW)
endif()
project(VCDTool VERSION 0.0.2 LANGUAGES CXX)

#include(GitFunctions)
#get_info_from_git()

option(SANITIZER  "Enable address sanitizer"   OFF)
option(ENABLE_COVERAGE "Enable code coverage" OFF)
option(ENABLE_SANITIZER "Enable address sanitizer" OFF)
option(ENABLE_PROFILING "Enable profiling " OFF)

include(ConanInline)
# include(GNUInstallDirs)

# set(RELAX "-Wno-unused-parameter -Wno-unused-variable -Wno-unused-but-set-variable  -Wno-deprecated-declarations") # -fsanitize=address")
# Compiler Options
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)
# set debugging friendly optimization for debug build

#SET(CMAKE_CXX_FLAGS_DEBUG "-Og -ggdb ${RELAX}")
SET(CMAKE_CXX_FLAGS_DEBUG "-ggdb -fno-omit-frame-pointer ${RELAX} -Wa,--nocompress-debug-sections -Wl,--compress-debug-sections=none")
#SET(CMAKE_C_FLAGS_DEBUG "-Og -ggdb ${RELAX}")
SET(CMAKE_C_FLAGS_DEBUG "-ggdb ${RELAX} -Wa,--nocompress-debug-sections -Wl,--compress-debug-sections=none")

# set non-aggressive optimization level for debug build
SET(CMAKE_CXX_FLAGS_RELEASE "-O2 ${RELAX}")
SET(CMAKE_C_FLAGS_RELEASE "-O2 ${RELAX}")

# add address sanitizer
if(SANITIZER)
  set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fsanitize=address")
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fsanitize=address")
endif()

if(EN_PROFILE) 
	set(CMAKE_CXX_FLAGS "-pg ${CMAKE_CXX_FLAGS}")
endif()

if(ENABLE_COVERAGE)
    include(CodeCoverage)
    append_coverage_compiler_flags()
    set(COVERAGE_EXCLUDES "${NCore3_SOURCE_DIR}/osci-lib/scc/*" "/engr/dev/tools/*" "$ENV{HOME}/.conan/*")
endif()

set(CLANG_FORMAT_EXCLUDE_PATTERNS "/test/" "/osci-lib/" "/build/")
find_package(ClangFormat)

#conan_check()
#conan_add_remote(NAME conan-center URL https://center.conan.io INDEX 0)
#conan_add_remote(NAME arteris URL http://conan.arteris.com:9300 INDEX 1)

# Boost on CentOS 7 quirks: the b2 of conan-center is build against a newer libstdc++ and therefore does not run
# with the oooooold libs on CentOS 7. Therefore we build our own version of b2 if it is not there
#set(B2_META $ENV{HOME}/.conan/data/b2/4.5.0/_/_/metadata.json)
#if(DEFINED ENV{CONAN_USER_HOME})
#	set(B2_META $ENV{CONAN_USER_HOME}/.conan/data/b2/4.5.0/_/_/metadata.json)
#endif()
#if(NOT EXISTS ${B2_META})
#	conan_configure(REQUIRES b2/4.5.0)
#	conan_cmake_autodetect(settings)
#	conan_cmake_install(PATH_OR_REFERENCE . BUILD b2 SETTINGS ${settings})
#endif()
# Boost on CentOS 7 quirks end

#conan_configure(REQUIRES boost/1.70.0 yaml-cpp/0.6.3  lz4/1.9.3 zlib/1.2.8
#                GENERATORS cmake
#                OPTIONS boost:without_stacktrace=True boost:fPIC=True boost:shared=False boost:header_only=False
#                )

#if(CMAKE_BUILD_TYPE STREQUAL "RelWithDebInfo")
#	conan_install(BUILD_TYPE Release)
#else()
#	conan_install()
#endif()
#conan_setup(TARGETS)

set(Boost_NO_BOOST_CMAKE ON) #  Don't do a find_package in config mode before searching for a regular boost install.

# setup_conan(TARGETS)
# add_subdirectory(osci-lib)
add_subdirectory(src)
# add_subdirectory(test)

enable_testing()

#configure_file(manifest.json.in manifest.json)
#install(FILES ${CMAKE_BINARY_DIR}/manifest.json	DESTINATION .)
