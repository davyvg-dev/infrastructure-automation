add_library(${PROJECT_NAME}_lib
    main.cpp
    trading_solution.cpp
)

target_include_directories(${PROJECT_NAME}_lib
    PUBLIC
        ${PROJECT_SOURCE_DIR}/include
) 