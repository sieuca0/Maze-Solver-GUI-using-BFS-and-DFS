# Tkinter is used to build the GUI window, buttons, labels, and canvas.
# random is used to choose the next cell while generating the maze.
# time is used to measure the animation runtime.
import tkinter as tk
import random
from bfs_solver import bfs_solver
from dfs_solver import dfs_solver
import time

#Basic window size and global variables for the maze solver GUI
WINDOW_HEIGHT = 920
LEFT_PANEL_WIDTH = 300
CANVAS_SIZE = WINDOW_HEIGHT
WINDOW_WIDTH = LEFT_PANEL_WIDTH + CANVAS_SIZE
DELAY = 10

#Create the main Tkinter window
window = tk.Tk()
window.title("Maze Solver")
window.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
window.resizable(False, False)

#Global state variables for the current maze, solution path, animation steps, and timing
current_maze = []
current_path = None
current_visited_order = []
current_step = 0
animating = False
animation_start_time = None
algorithm_runtime = 0
cell_rectangles = {}

#UI setup for the left control panel and right canvas panel
# Left panel for control system
left_panel = tk.Frame(window, width=LEFT_PANEL_WIDTH, height=WINDOW_HEIGHT, bg="#3160B0")
left_panel.pack(side="left", fill="y")
left_panel.pack_propagate(False)

# Right panel for maze visualizer
right_panel = tk.Frame(window, width=CANVAS_SIZE, height=CANVAS_SIZE, bg="white")
right_panel.pack(side="right", fill="none", expand=False)
right_panel.pack_propagate(False)

#Title label for the control panel
label_title = tk.Label(left_panel, text="Setting", font=("Arial", 20, "bold"), bg="#3160B0", fg="white")
label_title.pack(pady=20)

#StringVar stores the currently selected algorithm, BFS = default value
algorithm_var = tk.StringVar(value="BFS")

#Label and radio buttons for algorithm selection
label_algorithm = tk.Label(left_panel, text="Choose Algorithm:", font=("Arial", 16), bg="#3160B0", fg="white")
label_algorithm.pack(pady=10)

tk.Radiobutton(left_panel, text="BFS", variable=algorithm_var, value="BFS", bg="#3160B0", fg="white").pack()
tk.Radiobutton(left_panel, text="DFS", variable=algorithm_var, value="DFS", bg="#3160B0", fg="white").pack()

#Reminder label to tell the user the minimum maze size requirement
input_reminder_label = tk.Label(left_panel, text="Rows and columns\n must be at least 5", font=("Arial", 16), bg="#3160B0", fg="white")
input_reminder_label.pack(pady=(20, 0))

#Input box for the number of rows in the maze
label_rows = tk.Label(left_panel, text="Rows:", font=("Arial", 16), bg="#3160B0", fg="white")
label_rows.pack(pady=(20, 5))
entry_rows = tk.Entry(left_panel)
entry_rows.pack()
entry_rows.insert(0, "20")

#Input box for the number of columns in the maze
label_columns = tk.Label(left_panel, text="Columns:", font=("Arial", 16), bg="#3160B0", fg="white")
label_columns.pack(pady=(10, 5))
entry_columns = tk.Entry(left_panel)
entry_columns.pack(pady = (0, 10))
entry_columns.insert(0, "20")

#Label to display result text such as runtime, path length, and visited cells
result_label = tk.Label(left_panel, text="Generate maze, then click Solve", font=("Arial", 16), bg="#3160B0", wraplength=220, justify="left", fg="white")

#Canvas is used to draw the maze and the animation on the right panel
canvas = tk.Canvas(right_panel, width=CANVAS_SIZE, height=CANVAS_SIZE, bg="white", highlightthickness=0)
canvas.pack(fill="both", expand=True)


#---------------------------Maze generation functions---------------------------
#The maze is generated using DFS backtracking.
#It starts with all walls, then opens paths by moving to unvisited neighbors
#that are 2 cells away and breaking the wall in between.
#Because each new path is connected from the current path,
#the maze stays connected instead of creating random isolated spaces.
#S is placed at the top-left area, and E is placed near the bottom-right area.
#Cells around E are also opened, so there is at least one path leading into the end point.
#--------------------------------------------------------------------------------

#This function makes sure rows and columns stay as odd numbers.
#The generator jumps 2 cells at a time, and the middle cell will be a wall.
#so odd rows and columns can help
#to keeps the wall and path pattern look like #.#.#.#.#
#and helps avoid uneven edges or single walls in the maze.
def make_odd_size(number):
    if number < 5:   #Set a minimum size so the maze is not too small
        return 5
    if number % 2 == 0:   #If the input is even, add 1 to make it odd
        return number + 1
    return number

#Build the maze using DFS backtracking.
#Start with all walls, then carve paths by moving to unvisited neighbors 2 cells away.
def build_maze(rows, columns):
    rows = make_odd_size(rows)   #Adjust rows to an odd number for good looking maze structure
    columns = make_odd_size(columns)   #Adjust columns to an odd number for good looing maze structure

    maze = [['#' for _ in range(columns)] for _ in range(rows)]   #Start with a maze full of walls
    stack = [(1, 1)]   #Stack is used for DFS backtracking during maze generation
    visited_cells = {(1, 1)}   #Keep track of which path cells have already been visited
    maze[1][1] = '.'   #Open the starting generation cell

    #Find all valid unvisited neighbors 2 cells away from the current cell.
    #Moving by 2 keeps one wall cell between path cells.
    def get_unvisited_neighbors(row, column):
        neighbors = []   #Store all possible next cells that can be carved into paths
        directions = [(2, 0), (0, 2), (-2, 0), (0, -2)]   #Down, right, up, left by 2 cells
        
        #Loop to jump 2 cells in the preferred direction order
        for row_change, column_change in directions:
            new_row = row + row_change
            new_column = column + column_change

            if 1 <= new_row < rows - 1 and 1 <= new_column < columns - 1:
                if (new_row, new_column) not in visited_cells:
                    neighbors.append((new_row, new_column))

        return neighbors

    #Run DFS backtracking until there are no more cells left in the stack
    while stack:
        row, column = stack[-1]   #Look at the current cell on the top of the stack
        neighbors = get_unvisited_neighbors(row, column)   #Get all unvisited neighbors from the current cell

        if neighbors:
            new_row, new_column = random.choice(neighbors)   #Randomly choose the next cell to make the maze less predictable
            wall_row = (row + new_row) // 2   #Find the wall row between current and next cell
            wall_column = (column + new_column) // 2   #Find the wall column between current and next cell

            maze[wall_row][wall_column] = '.'   #Break the wall between the two cells
            maze[new_row][new_column] = '.'   #Open the new cell as a path
            visited_cells.add((new_row, new_column))   #Mark the new cell as visited
            stack.append((new_row, new_column))   #Move forward to continue DFS generation
        else:
            stack.pop()   #Backtrack if there are no more unvisited neighbors

    #Place the start and end points after the maze paths are created
    maze[1][1] = 'S'   #Start point
    maze[rows - 2][columns - 2] = 'E'   #End point

    if rows > 3:   #Open a nearby cell so the end is reachable more clearly
        maze[rows - 3][columns - 2] = '.'
    if columns > 3:   #Open another nearby cell around the end if needed
        maze[rows - 2][columns - 3] = '.'

    return maze   #Return the completed maze to the GUI

#Calculate the size of each maze cell so the maze fits inside the canvas.
#Square mazes can fill the canvas more fully, while rectangular mazes keep their shape.
def get_cell_dimensions():
    if not current_maze:   #Default size before any maze is generated
        return 20, 20, 0, 0

    rows = len(current_maze)
    columns = len(current_maze[0])

    if rows == columns:   #Square mazes can use the full canvas without stretching
        cell_width = CANVAS_SIZE / columns
        cell_height = CANVAS_SIZE / rows
        offset_x = 0
        offset_y = 0
    else:   #Rectangular mazes should keep square cells and stay centered
        cell_size = min(CANVAS_SIZE / columns, CANVAS_SIZE / rows)
        cell_width = cell_size
        cell_height = cell_size
        maze_width = columns * cell_width
        maze_height = rows * cell_height
        offset_x = (CANVAS_SIZE - maze_width) / 2
        offset_y = (CANVAS_SIZE - maze_height) / 2

    return cell_width, cell_height, offset_x, offset_y

#Draw the base maze on the canvas.
#The maze is drawn once, then animation only changes cell colors later.
def draw_maze(visited_set=None, path_set=None):
    global cell_rectangles

    if visited_set is None:
        visited_set = set()
    if path_set is None:
        path_set = set()

    canvas.delete("all")   #Clear the old drawing before drawing the new frame
    cell_rectangles = {}

    if not current_maze:   #Do not draw anything if no maze exists yet
        return

    rows = len(current_maze)
    columns = len(current_maze[0])
    cell_width, cell_height, offset_x, offset_y = get_cell_dimensions()

    for row in range(rows):
        for column in range(columns):
            x1 = offset_x + column * cell_width
            y1 = offset_y + row * cell_height
            x2 = x1 + cell_width
            y2 = y1 + cell_height
            cell = current_maze[row][column]   #Get the current maze character for this cell

            if cell == '#':
                color = 'black'
                outline = ''
            elif cell == 'S':
                color = '#3160B0'
                outline = '#3160B0'
            elif cell == 'E':
                color = '#E06623'
                outline = '#E06623'
            elif (row, column) in path_set:
                color = '#DA4848'
                outline = ''
            elif (row, column) in visited_set:
                color = '#76D2DB'
                outline = ''
            else:
                color = '#F7F6E5'
                outline = ''

            rect_id = canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=outline)   #Draw the cell rectangle
            cell_rectangles[(row, column)] = rect_id

            if cell in ['S', 'E']:
                font_size = max(8, int(min(cell_width, cell_height) / 2))
                canvas.create_text(
                    x1 + cell_width / 2,
                    y1 + cell_height / 2,
                    text=cell,
                    fill='white',
                    font=('Arial', font_size, 'bold')
                )


#Change only the color of visited cells or final path cells.
#This is faster than redrawing the full maze every animation step.
def update_cell_colors(visited_cells=None, path_cells=None):
    if visited_cells is None:
        visited_cells = []
    if path_cells is None:
        path_cells = []

    for row, column in visited_cells:
        if (row, column) in cell_rectangles and current_maze[row][column] not in ['S', 'E', '#']:
            canvas.itemconfig(cell_rectangles[(row, column)], fill='#76D2DB', outline='')

    for row, column in path_cells:
        if (row, column) in cell_rectangles and current_maze[row][column] not in ['S', 'E', '#']:
            canvas.itemconfig(cell_rectangles[(row, column)], fill='#DA4848', outline='')

#Update the result label with algorithm name, path information, visited count, and runtimes
def update_result_label(algorithm, path, visited_count, runtime, animation_runtime=None):

    if path is None:   #If there is no path, show a failure message
        path_text = "No Path Found"
    else:   #If a path exists, show the number of steps in that path
        path_text = f"Path Length: {len(path) - 1}"

    text = (f"Algorithm: {algorithm}\n" f"{path_text}\n" f"Visited: {visited_count}\n"f"Algorithm Runtime: {runtime:.7f} seconds")

    if animation_runtime is not None:   #Only show animation runtime after the animation is finished
        text += f"\nAnimation Runtime: {animation_runtime:.7f} seconds"

    result_label.config(text=text)


#Finish the animation, draw the final path, and update the label with animation runtime
def finish_animation():
    global animating, animation_start_time

    animating = False   #Mark the animation as finished so the user can run again
    draw_maze()   #Redraw the base maze before showing the final path
    update_cell_colors(path_cells=current_path)   #Color only the final solution path

    if animation_start_time is None:   #Safety check in case animation timing was not started
        return

    animation_runtime = time.perf_counter() - animation_start_time   #Measure how long the full animation took
    update_result_label(
        algorithm_var.get(),
        current_path,
        len(current_visited_order),
        algorithm_runtime,
        animation_runtime
    )
    animation_start_time = None   #Reset animation timer for the next run

#Animate the search one step at a time by coloring only new visited cells
#instead of redrawing the whole maze every frame.
def animate_search():
    global current_step, animation_start_time

    if current_step <= len(current_visited_order):   #Keep animating until all visited cells have been shown
        if current_step < len(current_visited_order):
            update_cell_colors(visited_cells=[current_visited_order[current_step]])   #Color only the newest visited cell
        elif current_path:
            update_cell_colors(path_cells=current_path)   #Show the final path on the last step

        if animation_start_time is not None:   #Show animation runtime while the animation is still running
            current_animation_runtime = time.perf_counter() - animation_start_time
            update_result_label(
                algorithm_var.get(),
                current_path,
                len(current_visited_order),
                algorithm_runtime,
                current_animation_runtime
            )

        current_step += 1   #Move to the next animation step
        window.after(DELAY, animate_search)   #Schedule the next animation frame after a short delay
    else:
        finish_animation()   #Finish when all visited cells have already been drawn


#Solve the current maze using the selected algorithm, then start the animation
def solve_maze_button():
    global current_path, current_visited_order, current_step, animating, animation_start_time, algorithm_runtime

    if not current_maze or animating:   #Do nothing if no maze exists or an animation is already running
        return

    if algorithm_var.get() == "BFS":   #Run BFS if the BFS radio button is selected
        current_path, visited_count, algorithm_runtime, current_visited_order = bfs_solver(current_maze)
    else:   #Otherwise run DFS
        current_path, visited_count, algorithm_runtime, current_visited_order = dfs_solver(current_maze)

    current_step = 0   #Reset the animation step counter
    animating = True   #Lock the buttons from starting another animation during the current run
    animation_start_time = time.perf_counter()   #Start timing the search animation
    draw_maze()   #Draw the maze once before animation starts
    update_result_label(algorithm_var.get(), current_path, visited_count, algorithm_runtime)   #Show algorithm results before the animation finishes
    animate_search()   #Start the step-by-step search animation

#Generate a new maze based on the row and column input from the GUI
def generate_maze_button():
    global current_maze, current_path, current_visited_order, current_step, animating

    try:   #Try to convert the row and column input into integers
        rows = int(entry_rows.get())
        columns = int(entry_columns.get())
    except ValueError:   #Show an error if the input is not a valid integer
        result_label.config(text="Rows and columns must be integers")
        return

    if rows < 5 or columns < 5:   #Reject very small sizes because they do not make a nice maze
        result_label.config(text="Rows and columns must be at least 5")
        return

    current_maze = build_maze(rows, columns)   #Create the maze using the input size
    rows = len(current_maze)
    columns = len(current_maze[0])
    current_path = None   #Clear the previous solution path
    current_visited_order = []   #Clear the previous visited order used for animation
    current_step = 0   #Reset the animation step counter
    animating = False   #Make sure no animation is marked as running
    result_label.config(text=f"Generated maze: {rows} x {columns}")   #Display the generated maze size in the result label
    draw_maze()   #Draw the new maze on the canvas


#Buttons for generating and solving the maze
tk.Button(left_panel, text="Generate Maze", width=18, command=generate_maze_button, bg="white", fg="#3160B0").pack(pady=10)
tk.Button(left_panel, text="Solve", width=18, command=solve_maze_button, bg="white", fg="#3160B0").pack(pady=10)

#Display the result label under the buttons
result_label.pack(pady=20)

#Start the Tkinter event loop to keep the window running
window.mainloop()
