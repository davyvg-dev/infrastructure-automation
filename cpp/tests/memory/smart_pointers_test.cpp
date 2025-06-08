#include <gtest/gtest.h>
#include <memory>
#include <vector>

// TODO: Implement these classes and functions
// 1. Implement a custom unique_ptr class
// 2. Implement a custom shared_ptr class
// 3. Implement a custom weak_ptr class
// 4. Implement a custom make_unique function
// 5. Implement a custom make_shared function

// Test cases to guide your implementation
TEST(SmartPointers, UniquePtrBasic) {
    // TODO: Implement a basic unique_ptr that can:
    // 1. Own a resource
    // 2. Transfer ownership
    // 3. Automatically clean up when it goes out of scope
    
    // Think about:
    // - How will you handle the pointer?
    // - What happens when the unique_ptr is moved?
    // - How will you prevent copying?
}

TEST(SmartPointers, SharedPtrBasic) {
    // TODO: Implement a basic shared_ptr that can:
    // 1. Share ownership of a resource
    // 2. Track reference count
    // 3. Clean up when last reference is gone
    
    // Think about:
    // - How will you track references?
    // - What happens when a shared_ptr is copied?
    // - How will you handle thread safety?
}

TEST(SmartPointers, WeakPtrBasic) {
    // TODO: Implement a basic weak_ptr that can:
    // 1. Observe a shared_ptr without affecting its lifetime
    // 2. Check if the observed resource is still valid
    // 3. Convert to shared_ptr when needed
    
    // Think about:
    // - How will you track the observed resource?
    // - What happens when the resource is deleted?
    // - How will you implement the lock() function?
}

TEST(SmartPointers, MakeUnique) {
    // TODO: Implement make_unique that:
    // 1. Creates a unique_ptr with a new object
    // 2. Handles constructor arguments
    // 3. Provides exception safety
    
    // Think about:
    // - How will you handle different constructor arguments?
    // - What happens if construction fails?
    // - How will you ensure exception safety?
}

TEST(SmartPointers, MakeShared) {
    // TODO: Implement make_shared that:
    // 1. Creates a shared_ptr with a new object
    // 2. Handles constructor arguments
    // 3. Provides exception safety
    // 4. Allocates the control block and object together
    
    // Think about:
    // - How will you allocate the control block and object together?
    // - What happens if construction fails?
    // - How will you ensure exception safety?
}

// Advanced test cases
TEST(SmartPointers, CustomDeleter) {
    // TODO: Implement support for custom deleters in your smart pointers
    // Think about:
    // - How will you store the deleter?
    // - How will you call the deleter?
    // - What type should the deleter be?
}

TEST(SmartPointers, ArraySupport) {
    // TODO: Implement array support in your smart pointers
    // Think about:
    // - How will you handle array allocation?
    // - How will you handle array deletion?
    // - What special considerations are needed for arrays?
}

// Memory leak detection
TEST(SmartPointers, NoMemoryLeaks) {
    // TODO: Ensure your implementations don't leak memory
    // Think about:
    // - How will you test for memory leaks?
    // - What edge cases could cause leaks?
    // - How will you handle exceptions?
} 