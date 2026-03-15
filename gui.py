import tkinter as tk
import random
from bfs_solver import bfs_solver
from dfs_solver import dfs_solver

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
LEFT_PANEL_WIDTH = 250
CANVAS_SIZE = 800
DELAY = 10
WALL_CHANCE = 0.38

window = tk.Tk()
window.title("Maze Solver")
window.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

current_maze = []
current_path = None
current_visited_order = []
current_step = 0
is_animating = False


# ---------- UI SETUP ----------
left_frame = tk.Frame(window, width=LEFT_PANEL_WIDTH, height=WINDOW_HEIGHT, bg="lightgray")
left_frame.pack(side="left", fill="y")
left_frame.pack_propagate(False)

right_frame = tk.Frame(window, width=WINDOW_WIDTH - LEFT_PANEL_WIDTH, height=WINDOW_HEIGHT)
right_frame.pack(side="right", fill="both", expand=True)

label_title = tk.Label(left_frame, text="Maze Controls", font=("Arial", 16, "bold"), bg="lightgray")
label_title.pack(pady=20)

algorithm_var = tk.StringVar(value="BFS")

label_algorithm = tk.Label(left_frame, text="Choose Algorithm:", font=("Arial", 12), bg="lightgray")
label_algorithm.pack(pady=10)

tk.Radiobutton(left_frame, text="BFS", variable=algorithm_var, value="BFS", bg="lightgray").pack()
tk.Radiobutton(left_frame, text="DFS", variable=algorithm_var, value="DFS", bg="lightgray").pack()

label_rows = tk.Label(left_frame, text="Rows:", font=("Arial", 12), bg="lightgray")
label_rows.pack(pady=(20, 5))
entry_rows = tk.Entry(left_frame)
entry_rows.pack()
entry_rows.insert(0, "20")

label_cols = tk.Label(left_frame, text="Cols:", font=("Arial", 12), bg="lightgray")
label_cols.pack(pady=(20, 5))
entry_cols = tk.Entry(left_frame)
entry_cols.pack()
entry_cols.insert(0, "20")

result_label = tk.Label(
    left_frame,
    text="Generate a maze, then click Solve",
    font=("Arial", 11),
    bg="lightgray",
    wraplength=220,
    justify="left"
)
result_label.pack(pady=20)

canvas = tk.Canvas(right_frame, width=CANVAS_SIZE, height=CANVAS_SIZE, bg="white")
canvas.pack(padx=20, pady=20)


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
            elif cell == 'S':
                color = 'green'
            elif cell == 'E':
                color = 'red'
            elif (row, column) in path_set:
                color = 'yellow'
            elif (row, column) in visited_set:
                color = 'light blue'
            else:
                color = 'white'

            canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='gray')

            if cell in ['S', 'E']:
                font_size = max(8, cell_size // 2)
                canvas.create_text(
                    x1 + cell_size / 2,
                    y1 + cell_size / 2,
                    text=cell,
                    fill='white',
                    font=('Arial', font_size, 'bold')
                )


# ---------- MAZE GENERATION ----------
def make_odd_size(number):
    if number < 5:
        return 5
    if number % 2 == 0:
        return number + 1
    return number



def get_two_step_neighbors(row, column, rows, cols, visited_cells):
    neighbors = []
    directions = [(-2, 0), (2, 0), (0, -2), (0, 2)]

    for row_change, column_change in directions:
        new_row = row + row_change
        new_column = column + column_change

        if 1 <= new_row < rows - 1 and 1 <= new_column < cols - 1:
            if (new_row, new_column) not in visited_cells:
                neighbors.append((new_row, new_column))

    return neighbors



def generate_perfect_maze(rows, cols):
    rows = make_odd_size(rows)
    cols = make_odd_size(cols)

    maze = [['#' for _ in range(cols)] for _ in range(rows)]
    stack = [(1, 1)]
    visited_cells = {(1, 1)}
    maze[1][1] = '.'

    while stack:
        row, column = stack[-1]
        neighbors = get_two_step_neighbors(row, column, rows, cols, visited_cells)

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



def generate_random_maze(rows, cols):
    return generate_perfect_maze(rows, cols)


# ---------- ANIMATION ----------
def animate_search():
    global current_step, is_animating

    if current_step <= len(current_visited_order):
        visited_set = set(current_visited_order[:current_step])
        path_set = set(current_path) if current_path and current_step == len(current_visited_order) else set()
        draw_maze(visited_set, path_set)
        current_step += 1
        window.after(DELAY, animate_search)
    else:
        is_animating = False


# ---------- BUTTON ACTIONS ----------
def solve_maze():
    global current_path, current_visited_order, current_step, is_animating

    if not current_maze or is_animating:
        return

    if algorithm_var.get() == "BFS":
        current_path, visited_count, runtime, current_visited_order = bfs_solver(current_maze)
    else:
        current_path, visited_count, runtime, current_visited_order = dfs_solver(current_maze)

    current_step = 0
    is_animating = True

    if current_path is None:
        result_label.config(
            text=(
                f"Algorithm: {algorithm_var.get()}\n"
                f"No Path Found\n"
                f"Visited: {visited_count}\n"
                f"Runtime: {runtime:.7f} seconds"
            )
        )
    else:
        result_label.config(
            text=(
                f"Algorithm: {algorithm_var.get()}\n"
                f"Path Length: {len(current_path) - 1}\n"
                f"Visited: {visited_count}\n"
                f"Runtime: {runtime:.7f} seconds"
            )
        )

    animate_search()


def generate_maze():
    global current_maze, current_path, current_visited_order, current_step, is_animating

    try:
        rows = int(entry_rows.get())
        cols = int(entry_cols.get())
    except ValueError:
        result_label.config(text="Rows and Cols must be integers")
        return

    if rows < 5 or cols < 5:
        result_label.config(text="Rows and Cols must be at least 5")
        return

    current_maze = generate_random_maze(rows, cols)
    rows = len(current_maze)
    cols = len(current_maze[0])
    current_path = None
    current_visited_order = []
    current_step = 0
    is_animating = False
    result_label.config(text=f"Generated maze: {rows} x {cols} (perfect maze)")
    draw_maze()


# ---------- BUTTONS ----------
tk.Button(left_frame, text="Generate Maze", width=18, command=generate_maze).pack(pady=10)
tk.Button(left_frame, text="Solve", width=18, command=solve_maze).pack(pady=10)


# ---------- STARTUP MAZE ----------
current_maze = [
    ['#', '#', '#', '#', '#', '#', '#'],
    ['#', 'S', '.', '.', '.', '.', '#'],
    ['#', '.', '#', '#', '#', '.', '#'],
    ['#', '.', '.', 'E', '#', '.', '#'],
    ['#', '.', '#', '.', '#', '.', '#'],
    ['#', '.', '.', '.', '.', '.', '#'],
    ['#', '#', '#', '#', '#', '#', '#']
]

draw_maze()
window.mainloop()
