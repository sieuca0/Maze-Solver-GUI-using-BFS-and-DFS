import tkinter as tk
import random
from bfs_solver import bfs_solver
from dfs_solver import dfs_solver
import time

# Constanst/ Global var
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
LEFT_PANEL_WIDTH = 250
CANVAS_SIZE = 800
DELAY = 10

window = tk.Tk()
window.title("Maze Solver")
window.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

current_maze = []
current_path = None
current_visited_order = []
current_step = 0
animating = False
animation_start_time = None
algorithm_runtime = 0

# UI setup
# Left panel for control system
left_panel = tk.Frame(window, width=LEFT_PANEL_WIDTH, height=WINDOW_HEIGHT, bg="#3160B0")
left_panel.pack(side="left", fill="y")
left_panel.pack_propagate(False)

# Right panel for maze visualizer
right_panel = tk.Frame(window, width=WINDOW_WIDTH - LEFT_PANEL_WIDTH, height=WINDOW_HEIGHT, bg= "white")
right_panel.pack(side="right", fill="both", expand=True)

label_title = tk.Label(left_panel, text="Setting", font=("Arial", 16, "bold"), bg="#3160B0", fg="white")
label_title.pack(pady=20)

algorithm_var = tk.StringVar(value="BFS")

label_algorithm = tk.Label(left_panel, text="Choose Algorithm:", font=("Arial", 12), bg="#3160B0", fg="white")
label_algorithm.pack(pady=10)

tk.Radiobutton(left_panel, text="BFS", variable=algorithm_var, value="BFS", bg="#3160B0", fg="white").pack()
tk.Radiobutton(left_panel, text="DFS", variable=algorithm_var, value="DFS", bg="#3160B0", fg="white").pack()

label_rows = tk.Label(left_panel, text="Rows:", font=("Arial", 12), bg="#3160B0", fg="white")
label_rows.pack(pady=(20, 5))
entry_rows = tk.Entry(left_panel)
entry_rows.pack()
entry_rows.insert(0, "20")

label_cols = tk.Label(left_panel, text="Columns:", font=("Arial", 12), bg="#3160B0", fg="white")
label_cols.pack(pady=(20, 5))
entry_cols = tk.Entry(left_panel)
entry_cols.pack()
entry_cols.insert(0, "20")

result_label = tk.Label(left_panel, text="Generate a maze, then click Solve", font=("Arial", 11), bg="#3160B0", wraplength=220, justify="left", fg="white")

canvas = tk.Canvas(right_panel, width=CANVAS_SIZE, height=CANVAS_SIZE, bg="white")
canvas.pack(padx=20, pady=20)


# ---------- MAZE GENERATION ----------
def make_odd_size(number):
    if number < 5:
        return 5
    if number % 2 == 0:
        return number + 1
    return number


def build_maze(rows, cols):
    rows = make_odd_size(rows)
    cols = make_odd_size(cols)

    maze = [['#' for _ in range(cols)] for _ in range(rows)]
    stack = [(1, 1)]
    visited_cells = {(1, 1)}
    maze[1][1] = '.'

    def get_unvisited_neighbors(row, column):
        neighbors = []
        directions = [(-2, 0), (2, 0), (0, -2), (0, 2)]

        for row_change, column_change in directions:
            new_row = row + row_change
            new_column = column + column_change

            if 1 <= new_row < rows - 1 and 1 <= new_column < cols - 1:
                if (new_row, new_column) not in visited_cells:
                    neighbors.append((new_row, new_column))

        return neighbors

    while stack:
        row, column = stack[-1]
        neighbors = get_unvisited_neighbors(row, column)

        if neighbors:
            new_row, new_column = random.choice(neighbors)
            wall_row = (row + new_row) // 2
            wall_column = (column + new_column) // 2

            maze[wall_row][wall_column] = '.'
            maze[new_row][new_column] = '.'
            visited_cells.add((new_row, new_column))
            stack.append((new_row, new_column))
        else:
            stack.pop()

    maze[1][1] = 'S'
    maze[rows - 2][cols - 2] = 'E'

    if rows > 3:
        maze[rows - 3][cols - 2] = '.'
    if cols > 3:
        maze[rows - 2][cols - 3] = '.'

    return maze


# ---------- DRAWING ----------
def get_cell_size():
    if not current_maze:
        return 20
    rows = len(current_maze)
    cols = len(current_maze[0])
    return max(5, min(CANVAS_SIZE // cols, CANVAS_SIZE // rows))


def draw_maze(visited_set=None, path_set=None):
    if visited_set is None:
        visited_set = set()
    if path_set is None:
        path_set = set()

    canvas.delete("all")

    if not current_maze:
        return

    cell_size = get_cell_size()
    rows = len(current_maze)
    cols = len(current_maze[0])
    maze_width = cols * cell_size
    maze_height = rows * cell_size
    offset_x = (CANVAS_SIZE - maze_width) // 2
    offset_y = (CANVAS_SIZE - maze_height) // 2

    for row in range(rows):
        for column in range(cols):
            x1 = offset_x + column * cell_size
            y1 = offset_y + row * cell_size
            x2 = x1 + cell_size
            y2 = y1 + cell_size
            cell = current_maze[row][column]

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

            canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=outline)

            if cell in ['S', 'E']:
                font_size = max(8, cell_size // 2)
                canvas.create_text(
                    x1 + cell_size / 2,
                    y1 + cell_size / 2,
                    text=cell,
                    fill='white',
                    font=('Arial', font_size, 'bold')
                )


def update_result_label(algorithm, path, visited_count, runtime, animation_runtime=None):

    if path is None:
        path_text = "No Path Found"
    else:
        path_text = f"Path Length: {len(path) - 1}"

    text = (
        f"Algorithm: {algorithm}\n"
        f"{path_text}\n"
        f"Visited: {visited_count}\n"
        f"Runtime: {runtime:.7f} seconds"
    )

    if animation_runtime is not None:
        text += f"\nAnimation Runtime: {animation_runtime:.7f} seconds"

    result_label.config(text=text)


def finish_animation():
    global animating, animation_start_time

    animating = False
    draw_maze(set(), set(current_path))

    if animation_start_time is None:
        return

    animation_runtime = time.perf_counter() - animation_start_time
    update_result_label(
        algorithm_var.get(),
        current_path,
        len(current_visited_order),
        algorithm_runtime,
        animation_runtime
    )
    animation_start_time = None

# ---------- ANIMATION ----------
def animate_search():
    global current_step

    if current_step <= len(current_visited_order):
        visited_set = set(current_visited_order[:current_step])
        path_set = set(current_path) if current_path and current_step == len(current_visited_order) else set()
        draw_maze(visited_set, path_set)
        current_step += 1
        window.after(DELAY, animate_search)
    else:
        finish_animation()


# ---------- BUTTON ACTIONS ----------
def solve_maze_button():
    global current_path, current_visited_order, current_step, animating, animation_start_time, algorithm_runtime

    if not current_maze or animating:
        return

    if algorithm_var.get() == "BFS":
        current_path, visited_count, algorithm_runtime, current_visited_order = bfs_solver(current_maze)
    else:
        current_path, visited_count, algorithm_runtime, current_visited_order = dfs_solver(current_maze)

    current_step = 0
    animating = True
    animation_start_time = time.perf_counter()

    update_result_label(algorithm_var.get(), current_path, visited_count, algorithm_runtime)
    animate_search()

def generate_maze_button():
    global current_maze, current_path, current_visited_order, current_step, animating

    try:
        rows = int(entry_rows.get())
        cols = int(entry_cols.get())
    except ValueError:
        result_label.config(text="Rows and Cols must be integers")
        return

    if rows < 5 or cols < 5:
        result_label.config(text="Rows and Cols must be at least 5")
        return

    current_maze = build_maze(rows, cols)
    rows = len(current_maze)
    cols = len(current_maze[0])
    current_path = None
    current_visited_order = []
    current_step = 0
    animating = False
    result_label.config(text=f"Generated maze: {rows} x {cols}")
    draw_maze()


# Buttons generator
tk.Button(left_panel, text="Generate Maze", width=18, command=generate_maze_button, bg="white", fg="#3160B0").pack(pady=10)
tk.Button(left_panel, text="Solve", width=18, command=solve_maze_button, bg="white", fg="#3160B0").pack(pady=10)

#Display the result info 
result_label.pack(pady=20)

window.mainloop()
