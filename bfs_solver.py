from collections import deque
import time

def bfs_solver(maze):
    start_time = time.perf_counter()

    start = None
    end = None

    for i in range(len(maze)): #loop to find the start and end points
        for j in range(len(maze[0])):
            if maze[i][j] == "S":
                start = (i, j)
            elif maze[i][j] == "E":
                end = (i, j)

    if start is None or end is None: #if the start or end is not found, return None
        return None, 0, 0.0, [] 

    visited = set()
    queue = deque([start])
    parent = {}
    visited_order = []
    visited_count = 0
    visited.add(start)

    while queue:
        current = queue.popleft()
        visited_order.append(current)
        visited_count += 1

        if current == end:
            path = []
            while current in parent:
                path.append(current)
                current = parent[current]
            path.append(start)
            path.reverse()
            runtime = time.perf_counter() - start_time
            return path, visited_count, runtime, visited_order

        row, column = current
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for row_change, column_change in directions:
            new_row, new_column = row + row_change, column + column_change
            
            if 0 <= new_row < len(maze) and 0 <= new_column < len(maze[0]):
                if maze[new_row][new_column] != '#' and (new_row, new_column) not in visited:
                    visited.add((new_row, new_column))
                    parent[(new_row, new_column)] = current
                    queue.append((new_row, new_column))

    runtime = time.perf_counter() - start_time
    return None, visited_count, runtime, visited_order


if __name__ == "__main__":
    maze = [
        ['#', '#', '#', '#', '#', '#', '#'],
        ['#', 'S', '.', '.', '.', '.', '#'],
        ['#', '.', '#', '#', '#', '.', '#'],
        ['#', '.', '.', 'E', '#', '.', '#'],
        ['#', '.', '#', '.', '#', '.', '#'],
        ['#', '.', '.', '.', '.', '.', '#'],
        ['#', '#', '#', '#', '#', '#', '#']
    ]

    path, visited_count, runtime, visited_order = bfs_solver(maze)
    print("Path:", path)
    print("Visited Count:", visited_count)
    print("Runtime:", f"{runtime:.7f}", "seconds")
    print("Visited Order:", visited_order)
