cmake_minimum_required(VERSION 3.25)
project(shop LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
add_compile_options(-Wall -Wextra -Werror)

# One library target per feature. PUBLIC include dirs are its API; PRIVATE ones stay inside.
add_library(users users/src/users.cpp)
target_include_directories(users PUBLIC users/include)

add_library(orders orders/src/orders.cpp)
target_include_directories(orders PUBLIC orders/include PRIVATE orders/src)
target_link_libraries(orders PUBLIC users)

# The composition root.
add_executable(shop app/main.cpp)
target_link_libraries(shop PRIVATE orders)

enable_testing()
add_executable(test_orders tests/test_orders.cpp)
target_link_libraries(test_orders PRIVATE orders)
add_test(NAME orders COMMAND test_orders)
