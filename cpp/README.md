# C++ Project

A modern C++ project template with CMake and Google Test integration.

## Project Structure

```
cpp/
├── CMakeLists.txt
├── include/         # Header files
├── src/            # Source files
│   ├── CMakeLists.txt
│   └── main.cpp
└── tests/          # Test files
    ├── CMakeLists.txt
    └── main_test.cpp
```

## Building the Project

```bash
# Create a build directory
mkdir build
cd build

# Configure the project
cmake ..

# Build the project
cmake --build .

# Run tests
ctest
```

## Features

- Modern C++ (C++20)
- CMake build system
- Google Test integration
- Warning flags enabled
- Separate source and test directories

## Requirements

- CMake 3.15 or higher
- C++20 compatible compiler
- Git (for fetching Google Test) 