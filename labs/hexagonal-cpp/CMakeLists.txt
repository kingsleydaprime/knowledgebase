cmake_minimum_required(VERSION 3.25)
project(shop LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
add_compile_options(-Wall -Wextra -Werror)

# The domain links nothing: it only ever sees its own headers.
add_library(domain domain/src/domain.cpp)
target_include_directories(domain PUBLIC domain/include)

# Adapters depend on the domain.
add_library(adapters INTERFACE)
target_include_directories(adapters INTERFACE adapters/include)
target_link_libraries(adapters INTERFACE domain)

enable_testing()
add_executable(test_place_order tests/test_place_order.cpp)
target_link_libraries(test_place_order PRIVATE adapters)
add_test(NAME place_order COMMAND test_place_order)
