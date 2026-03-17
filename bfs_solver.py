from collections import deque
import time


#Run Breadth-First Search (BFS) on the maze to find the shortest path
#from the start cell 'S' to the end cell 'E'.
def bfs_solver(maze):
    start_time = time.perf_counter()   #Start timing the BFS runtime

    start = None   #Store the (row, column) position of 'S'
    end = None     #Store the (row, column) position of 'E'

    #Scan the maze to find the start and end points
    for i in range(len(maze)):
        for j in range(len(maze[0])):
            if maze[i][j] == "S":
                start = (i, j)
            elif maze[i][j] == "E":
                end = (i, j)

    #If 'S' or 'E' is missing, there is no valid path to search
    if start is None or end is None:
        return None, 0, 0.0, []

    visited = set()               #Keep track of cells that were already visited
    queue = deque([start])        #Use a queue to control BFS order (FIFO)
    parent = {}                   #Store the parent of each cell to rebuild the path later
    visited_order = []            #Store the visit order for the animation
    visited_count = 0             #Count how many cells BFS visits
    visited.add(start)            #Mark the start cell as visited

    #Run BFS until there are no more cells left to explore
    while queue:
        current = queue.popleft()   #Take the next cell from the front of the queue
        visited_order.append(current)
        visited_count += 1

        #If BFS reaches the end cell, rebuild the path by following the parent map backward
        if current == end:
            path = []
            while current in parent:
                path.append(current)
                current = parent[current]
            path.append(start)              #Add the start cell
            path.reverse()                  #Reverse the path so it goes from start to end
            runtime = time.perf_counter() - start_time
            return path, visited_count, runtime, visited_order

        row, column = current
        directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]   #Down, right, up, left

        #Check all four neighboring cells
        for row_change, column_change in directions:
            new_row, new_column = row + row_change, column + column_change

            #Stay inside the maze and skip walls or already visited cells
            if 0 <= new_row < len(maze) and 0 <= new_column < len(maze[0]):
                if maze[new_row][new_column] != '#' and (new_row, new_column) not in visited:
                    visited.add((new_row, new_column))
                    parent[(new_row, new_column)] = current   #Remember which cell led to this neighbor
                    queue.append((new_row, new_column))       #Add it to the queue to explore later

    #If the queue becomes empty without reaching 'E', then no path exists
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
