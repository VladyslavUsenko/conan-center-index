cmake_minimum_required(VERSION 3.1)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(Flatbuffers REQUIRED CONFIG)
if(TARGET flatbuffers::flatbuffers_shared)
    set(FLATBUFFERS_TARGET flatbuffers::flatbuffers_shared)
else()
    set(FLATBUFFERS_TARGET flatbuffers::flatbuffers)
endif()

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} ${FLATBUFFERS_TARGET})
if(FLATBUFFERS_HEADER_ONLY)
    target_compile_definitions(${PROJECT_NAME} PRIVATE FLATBUFFERS_HEADER_ONLY)
endif()
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)

if(NOT (CMAKE_CROSSCOMPILING AND FLATBUFFERS_HEADER_ONLY)) # due to missing package id of build requirement if header_only
    add_executable(sample_binary sample_binary.cpp)
    target_link_libraries(sample_binary ${FLATBUFFERS_TARGET})
    set_property(TARGET sample_binary PROPERTY CXX_STANDARD 11)

    set(MONSTER_GENERATED_HEADER ${CMAKE_CURRENT_BINARY_DIR}/monster_generated.h)
    set(MONSTER_FBS ${CMAKE_CURRENT_SOURCE_DIR}/monster.fbs)
    add_custom_command(
        OUTPUT ${MONSTER_GENERATED_HEADER}
        COMMAND $<TARGET_FILE:flatbuffers::flatc>
                --cpp
                -o ${CMAKE_CURRENT_BINARY_DIR}
                ${MONSTER_FBS}
        DEPENDS ${MONSTER_FBS}
    )
    add_custom_target(generate_monster_header DEPENDS ${MONSTER_GENERATED_HEADER})
    add_dependencies(sample_binary generate_monster_header)
    target_include_directories(sample_binary PRIVATE ${CMAKE_CURRENT_BINARY_DIR})
endif()
