#include <gtest/gtest.h>
#include <vector>
#include <list>
#include <deque>
#include <map>
#include <unordered_map>
#include <set>
#include <unordered_set>
#include <stack>
#include <queue>

// TODO: Implement these functions and understand when to use each data structure
// For each test case:
// 1. Implement the function using the specified data structure
// 2. Think about why this data structure is appropriate
// 3. Consider the time and space complexity
// 4. Think about alternative data structures and their trade-offs

// Vector: Dynamic array with contiguous memory
// Pros: Fast random access, cache-friendly, efficient iteration
// Cons: Slow insertions/deletions in the middle, reallocation on growth
TEST(Containers, VectorOperations) {
    // TODO: Implement these functions
    // 1. Insert elements at the end
    // 2. Access elements by index
    // 3. Remove elements from the end
    // 4. Find an element
    // 5. Sort the vector

    std::vector<int> vec;
    vec.emplace_back(1);
    vec.emplace_back(2);
    vec.emplace_back(3);
    vec.emplace_back(4);
    vec.emplace_back(5);
    vec.emplace_back(6);
    vec.emplace_back(7);
    int test = vec.at(0);
    vec.pop_back();
    auto it = std::find(vec.begin(), vec.end(), 1);
    std::sort(vec.begin(), vec.end());

    // Think about:
    // - When is a vector the best choice?
    // when you want to store elements and access them by index. when i know the size in advance. when i need contiguous memory
    // - What operations are efficient/inefficient?
    //access from the middle inefficient. insert at the front is O(n) as you need to push all elements back, insert at the back is O(1)
    // - How does memory allocation work?
    //a vector allocates memory in blocks. when you reserve memory. it allocates a block of memory and then you can add elements to it
    // - What happens when the vector grows?
    //it allocates a new block of memory
}

// List: Doubly-linked list
// Pros: Fast insertions/deletions anywhere, no reallocation
// Cons: No random access, extra memory for links, not cache-friendly
TEST(Containers, ListOperations) {
    // TODO: Implement these functions
    std::list<int> listy;
    // 1. Insert elements at any position
    listy.emplace_back(1);
    listy.push_back(2);
    listy.insert(listy.begin() + 2, 3); // WRONG

    auto it = listy.begin();
    std::advance(it, 2);
    listy.insert(it, 3);
    
    // 2. Remove elements from any position
    listy.erase(listy.at(0)); //wrong
    auto it = listy.begin();
    listy.erase(it);
    listy.pop_back();
    listy.pop_front();
    // 3. Merge two sorted lists
    std::list<int> listy2;
    listy2.push_back(4);
    listy2.push_back(5);
    listy2.push_back(6);
    listy2.push_back(7);
    listy.merge(listy2);
    // 4. Reverse the list
    listy.reverse();
    // 5. Find an element
    auto it = std::find(listy.begin(), listy.end(), 1);
    // 6. Sort the list
    listy.sort();

    // Think about:
    // - When is a list better than a vector?
    // - What are the memory implications?
    // - How does iteration performance compare to vector?
}

// Map: Balanced binary tree (usually red-black tree)
// Pros: Keys are always sorted, efficient lookups
// Cons: Slower than unordered_map for most operations
TEST(Containers, MapOperations) {
    // TODO: Implement these functions
    
    // 1. Insert key-value pairs
    
    // 2. Find a value by key
    // 3. Remove a key-value pair
    // 4. Iterate in sorted order
    // 5. Find the closest key to a given value
    
    // Think about:
    // - When do you need sorted keys?
    // - What's the time complexity of operations?
    // - How does it compare to unordered_map?
}

// Unordered Map: Hash table
// Pros: Very fast lookups, insertions, and deletions
// Cons: Keys are not sorted, hash collisions can affect performance
TEST(Containers, UnorderedMapOperations) {
    // TODO: Implement these functions
    // 1. Insert key-value pairs
    // 2. Find a value by key
    // 3. Remove a key-value pair
    // 4. Handle hash collisions
    // 5. Rehash when load factor is high
    
    // Think about:
    // - When is unordered_map better than map?
    // - How do hash collisions affect performance?
    // - What's a good hash function?
}

// Set: Balanced binary tree of unique elements
// Pros: Elements are always sorted, efficient lookups
// Cons: Slower than unordered_set for most operations
TEST(Containers, SetOperations) {
    // TODO: Implement these functions
    // 1. Insert unique elements
    // 2. Find an element
    // 3. Remove an element
    // 4. Perform set operations (union, intersection, difference)
    // 5. Find the closest element to a given value
    
    // Think about:
    // - When do you need a set instead of a vector?
    // - What are the advantages of sorted elements?
    // - How does it compare to unordered_set?
}

// Stack: LIFO (Last In, First Out) container
// Pros: Simple interface, efficient push/pop operations
// Cons: Limited access to elements
TEST(Containers, StackOperations) {
    // TODO: Implement these functions
    // 1. Push elements
    // 2. Pop elements
    // 3. Check if the stack is empty
    // 4. Get the top element
    // 5. Implement a stack using a vector
    
    // Think about:
    // - What problems are best solved with a stack?
    // - How would you implement a stack using other containers?
    // - What are the performance characteristics?
}

// Queue: FIFO (First In, First Out) container
// Pros: Simple interface, efficient enqueue/dequeue operations
// Cons: Limited access to elements
TEST(Containers, QueueOperations) {
    // TODO: Implement these functions
    // 1. Enqueue elements
    // 2. Dequeue elements
    // 3. Check if the queue is empty
    // 4. Get the front element
    // 5. Implement a queue using a deque
    
    // Think about:
    // - When is a queue the right choice?
    // - How does it compare to other containers?
    // - What are the performance characteristics?
}

// Performance Comparison
TEST(Containers, PerformanceComparison) {
    // TODO: Implement these functions
    // 1. Compare insertion performance
    // 2. Compare lookup performance
    // 3. Compare memory usage
    // 4. Compare iteration performance
    // 5. Compare sorting performance
    
    // Think about:
    // - How do you measure performance?
    // - What factors affect performance?
    // - How do you choose the right container?
}

// Real-world Applications
TEST(Containers, RealWorldApplications) {
    // TODO: Implement these functions
    // 1. Implement a simple cache using unordered_map
    // 2. Implement a task scheduler using priority_queue
    // 3. Implement a simple database index using map
    // 4. Implement a simple undo system using stack
    // 5. Implement a simple message queue using queue
    
    // Think about:
    // - How do real-world requirements affect container choice?
    // - What are the trade-offs in each application?
    // - How do you handle edge cases?
} 