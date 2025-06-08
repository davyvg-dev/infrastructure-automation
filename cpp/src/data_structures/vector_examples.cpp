#include <vector>
#include <iostream>
#include <string>

void vectorBasics() {
    // 1. Creating vectors
    std::vector<int> numbers;                    // Empty vector
    std::vector<int> numbers2(5, 10);            // Vector with 5 elements, each initialized to 10
    std::vector<int> numbers3 = {1, 2, 3, 4, 5}; // Vector initialized with values
    
    // 2. Accessing elements
    // Using operator[]
    int first = numbers3[0];     // Access first element (no bounds checking)
    int last = numbers3[4];      // Access last element
    
    // Using at() (with bounds checking)
    try {
        int element = numbers3.at(2);  // Access element at index 2
        // numbers3.at(10);            // This would throw std::out_of_range
    } catch (const std::out_of_range& e) {
        std::cout << "Index out of range: " << e.what() << std::endl;
    }
    
    // Using front() and back()
    int firstElement = numbers3.front();  // Get first element
    int lastElement = numbers3.back();    // Get last element
    
    // 3. Modifying vectors
    // Adding elements
    numbers.push_back(1);        // Add element at the end
    numbers.emplace_back(2);     // More efficient way to add element at the end
    
    // Inserting elements
    numbers.insert(numbers.begin(), 0);           // Insert at beginning
    numbers.insert(numbers.begin() + 2, 5);       // Insert at specific position
    
    // Removing elements
    numbers.pop_back();          // Remove last element
    numbers.erase(numbers.begin());               // Remove first element
    numbers.erase(numbers.begin() + 1);           // Remove element at specific position
    
    // 4. Vector information
    size_t size = numbers.size();        // Get number of elements
    bool isEmpty = numbers.empty();      // Check if vector is empty
    size_t capacity = numbers.capacity(); // Get current capacity
    
    // 5. Resizing and reserving
    numbers.resize(10);          // Resize to 10 elements (new elements are default-initialized)
    numbers.reserve(100);        // Reserve space for 100 elements (doesn't create elements)
    
    // 6. Iterating over vectors
    // Using range-based for loop (C++11)
    for (const int& num : numbers) {
        std::cout << num << " ";
    }
    
    // Using iterators
    for (auto it = numbers.begin(); it != numbers.end(); ++it) {
        std::cout << *it << " ";
    }
    
    // Using index
    for (size_t i = 0; i < numbers.size(); ++i) {
        std::cout << numbers[i] << " ";
    }
    
    // 7. Vector of custom types
    struct Person {
        std::string name;
        int age;
    };
    
    std::vector<Person> people;
    people.push_back({"Alice", 25});
    people.emplace_back("Bob", 30);  // More efficient for custom types
    
    // 8. Clearing and swapping
    numbers.clear();              // Remove all elements
    numbers.swap(numbers2);       // Swap contents of two vectors
    
    // 9. Vector of vectors (2D vector)
    std::vector<std::vector<int>> matrix(3, std::vector<int>(3, 0));  // 3x3 matrix of zeros
    
    // 10. Common algorithms with vectors
    std::sort(numbers.begin(), numbers.end());           // Sort vector
    auto it = std::find(numbers.begin(), numbers.end(), 5);  // Find element
    if (it != numbers.end()) {
        std::cout << "Found 5 at position: " << (it - numbers.begin()) << std::endl;
    }
}

// Example of a function that takes a vector as parameter
void processVector(const std::vector<int>& vec) {
    // Pass by const reference to avoid copying
    for (const int& num : vec) {
        std::cout << num << " ";
    }
}

// Example of a function that returns a vector
std::vector<int> createVector() {
    return {1, 2, 3, 4, 5};  // Return value optimization (RVO) makes this efficient
}

int main() {
    vectorBasics();
    return 0;
} 