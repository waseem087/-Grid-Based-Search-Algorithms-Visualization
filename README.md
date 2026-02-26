# Artificial Intelligence  
## Assignment 1 – Grid-Based Search Algorithms Visualization

### 1. Introduction
This assignment implements and visualizes four fundamental search algorithms on a 2D grid:  

- Breadth-First Search (BFS)  
- Depth-First Search (DFS)  
- Uniform Cost Search (UCS)  
- A* Search (Manhattan & Euclidean Heuristics)  

The program provides a fully interactive Graphical User Interface (GUI) where users can:  

- Define grid dimensions  
- Place start and goal positions  
- Add/remove blocked cells  
- Assign traversal costs  
- Select an algorithm  
- Visualize visited nodes and final path  
<img width="1463" height="1002" alt="image" src="https://github.com/user-attachments/assets/a8c18d4f-fd7d-4ae1-91c8-dfae314e7311" />



**Constraints followed:**  

- Grid uses 0-based indexing  
- Internal representation: 0 → Free, 1 → Blocked  
- No Python built-in data structures like `heapq`  
- No `.append()`, `.pop()` or slicing for frontier  
- Manual Stack, Queue, and MinHeap implemented  
- Proper boundary checks included  

---

### 2. System Overview

#### 2.1 Grid Representation
- Implemented as a 2D array: `grid[row][col]`  
- Values: 0 → Free, 1 → Blocked  
- Separate cost grid for UCS: `costs[row][col]` (default 1, user can assign higher positive values)

#### 2.2 GUI Components
- Grid resizing (10×10 to 50×50)  
- Cell editing (free/blocked)  
- Setting start and goal  
- Setting traversal cost (UCS)  
- Selecting algorithm  
- Run, Clear, Reset buttons  
- Animated visualization  

---

### 3. Data Structures Implementation

#### 3.1 Queue (BFS)
- Fixed-size array, FIFO  
- Operations: `enqueue`, `dequeue`, `is_empty`  
- O(1) per operation  

#### 3.2 Stack (DFS)
- Fixed-size array, LIFO  
- Operations: `push`, `pop`, `is_empty`  
- O(1) per operation  

#### 3.3 MinHeap (UCS & A*)
- Array-based binary heap  
- Manual bubble-up/down  
- Custom comparison:  
  - UCS → priority by g  
  - A* → priority by f = g + h  
- Insert / Remove Min → O(log n)  

---

### 4. Algorithm Implementation

#### 4.1 BFS
- Explores level-by-level, guarantees shortest path  
- Uses Queue (FIFO)  
- Time/Space Complexity: O(R×C)  
- Optimal: Yes  
<img width="535" height="547" alt="image" src="https://github.com/user-attachments/assets/dc0310b7-5385-4f4f-b082-b3bab05e4143" />

#### 4.2 DFS
- Explores fully along branches, not guaranteed shortest path  
- Uses Stack (LIFO)  
- Time/Space Complexity: O(R×C)  
- Optimal: No  
<img width="534" height="544" alt="image" src="https://github.com/user-attachments/assets/c981e7b8-d9ba-42d7-8316-b46d2018c086" />


#### 4.3 UCS
- Expands node with smallest cumulative cost (g)  
- Uses MinHeap  
- Guarantees least-cost path  
- Time Complexity: O(RC log(RC)), Space: O(RC)  
- Optimal: Yes  
<img width="553" height="544" alt="image" src="https://github.com/user-attachments/assets/909d06be-c4ff-415b-8f06-2a450b7dc265" />

#### 4.4 A*
- Priority f = g + h  
- Heuristics: Manhattan, Euclidean (admissible)  
- Uses closed set to avoid re-expansion  
- Time Complexity: O(RC log(RC)), Space: O(RC)  
- Optimal: Yes  
<img width="547" height="541" alt="image" src="https://github.com/user-attachments/assets/d825f59e-64a4-45e6-ac04-a268f2ee473b" />
<img width="540" height="549" alt="image" src="https://github.com/user-attachments/assets/f586295f-1115-477b-aa91-3d0d8c1b2b71" />

---

### 5. Visualization
- Visited cells → Light Blue  
- Final path → Yellow  
- UCS displays total cost  
- Steps: Select algorithm → Run → Animated visualization  

---

### 6. Comparison

| Algorithm | Optimal | Uses Cost | Uses Heuristic | Typical Behavior |
|-----------|---------|-----------|----------------|----------------|
| BFS       | Yes     | No        | No             | Explores level-by-level |
| DFS       | No      | No        | No             | Explores deeply |
| UCS       | Yes     | Yes       | No             | Expands cheapest node |
| A*        | Yes     | Yes       | Yes            | Guided search using heuristic |

---

### 7. Observations
- BFS → shortest steps  
- DFS → faster exploration but longer path  
- UCS → cheapest path when costs differ  
- A* → fewer nodes explored due to heuristic guidance  
- Manhattan heuristic generally faster than Euclidean  

---

### 8. Conclusion
- Successfully implements & visualizes 4 search algorithms  
- GUI allows interactive testing and comparison  
- Demonstrates understanding of: Graph search, Priority queues, Heuristics, Path reconstruction, Time-space complexity tradeoffs  
- All required features implemented correctly
