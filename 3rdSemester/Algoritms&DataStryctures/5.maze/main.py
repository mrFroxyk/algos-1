import copy
import random
from PIL import Image, ImageDraw
import click
from ipdb import set_trace as st
import sys

sys.setrecursionlimit(10**5)

PATH_COLOR = (255, 255, 255)
SOLVE_PATH_COLOR = (100, 100, 100)
WALL_COLOR = (0, 0, 0)

Matrix = list[list[int]]
Point = tuple[int, int]


def get_dist_between_points(start_pos: Point, end_pos: Point) -> int:
    """Calculate the shortest distance between two positions."""
    return (abs(start_pos[0] - end_pos[0]) + abs(start_pos[1] - end_pos[1])) // 2


def find_element_in_matrix(matrix: Matrix, target: int) -> list[int] | None:
    """Find the target value in a 2D matrix."""
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            if matrix[i][j] == target:
                return [i, j]
    return None


class Maze:
    """Maze handler for generating, solving, and manipulating mazes."""

    def __init__(self, rows: int = 1, cols: int = 1, filename: str = "output") -> None:
        """Initialize the Maze object."""
        self.rows_fixed = rows * 2 + 1
        self.cols_fixed = cols * 2 + 1
        self.index = 2
        self.maze: Matrix = None
        self.path = None
        self.generation_states = []
        self.solving_states = []
        self.filename = filename

    def generate_maze(self) -> None:
        """Generate a maze and save generation states in generation_states variable."""
        # empty maze
        self.maze = [[0] * self.cols_fixed for _ in range(self.rows_fixed)]

        self.generation_states.append(copy.deepcopy(self.maze))

        # borders
        self.maze = [
            [
                1
                if i in (0, self.rows_fixed - 1) or j in (0, self.cols_fixed - 1)
                else 0
                for j in range(self.cols_fixed)
            ]
            for i in range(self.rows_fixed)
        ]
        self.generation_states.append(copy.deepcopy(self.maze))

        # make support walls
        for i in range(2, self.rows_fixed, 2):
            for j in range(0, self.cols_fixed, 2):
                self.maze[i][j] = 1

        self.generation_states.append(copy.deepcopy(self.maze))

        # first row indecies
        for j in range(1, self.cols_fixed, 2):
            self.maze[1][j] = self.index
            self.index += 1

        for i in range(1, self.rows_fixed, 2):
            # right walls
            for j in range(1, self.cols_fixed - 2, 2):
                if random.choice([True, False]):
                    self.maze[i][j + 1] = 1

                else:
                    if self.maze[i][j] == self.maze[i][j + 2]:
                        self.maze[i][j + 1] = 1

                    else:
                        temp = copy.copy(self.maze[i][j + 2])

                        for k in range(1, self.cols_fixed, 2):
                            if self.maze[i][k] == temp:
                                self.maze[i][k] = self.maze[i][j]

            # bottom walls
            for j1 in range(1, self.cols_fixed, 2):
                if i != self.rows_fixed - 2:
                    self.maze[i + 2][j1] = self.maze[i][j1]

                    if random.choice([True, False]):
                        # place wall under the cell if exist an exit with the same index
                        count = 0
                        temp = copy.copy(self.maze[i][j1])

                        for z in range(1, self.cols_fixed, 2):
                            if self.maze[i][z] == temp and self.maze[i + 1][z] == 0:
                                count += 1

                        if count > 1:
                            self.maze[i + 1][j1] = 1
                            self.maze[i + 2][j1] = self.index
                            self.index += 1

            # update states
            self.generation_states.append(copy.deepcopy(self.maze))

        # last line
        for i in range(1, self.cols_fixed - 2, 2):
            if (
                self.maze[self.rows_fixed - 2][i]
                != self.maze[self.rows_fixed - 2][i + 2]
            ):
                self.maze[self.rows_fixed - 2][i + 1] = 0
                temp = copy.copy(self.maze[self.rows_fixed - 2][i + 2])

                for z in range(1, self.cols_fixed, 2):
                    if self.maze[self.rows_fixed - 2][z] == temp:
                        self.maze[self.rows_fixed - 2][z] = self.maze[
                            self.rows_fixed - 2
                        ][i]

        self.generation_states.append(copy.deepcopy(self.maze))

        # delete trash
        for i in range(1, self.rows_fixed, 2):
            for j in range(1, self.cols_fixed, 2):
                self.maze[i][j] = 0
        self.index = 2

    # def generate_maze(self):
    #     """Generate a simple maze with random walls."""

    #     self.maze = [[0] * self.cols_fixed for _ in range(self.rows_fixed)]
    #     # Создать границы
    #     for i in range(self.rows_fixed):
    #         self.maze[i][0] = 1
    #         self.maze[i][self.cols_fixed - 1] = 1
    #     for j in range(self.cols_fixed):
    #         self.maze[0][j] = 1
    #         self.maze[self.rows_fixed - 1][j] = 1

    #     # Случайно добавить внутренние стены
    #     for i in range(1, self.rows_fixed - 1):
    #         for j in range(1, self.cols_fixed - 1):
    #             if random.random() < 0.3:  # 30% шанс создать стену
    #                 self.maze[i][j] = 1

    #     self.print_maze()
    def print_maze(self) -> None:
        """Print the maze in console."""
        for i in range(self.cols_fixed // 2):
            print("___", end="")
        print()
        for i in range(1, self.rows_fixed, 2):
            print("|", end="")
            for j in range(1, self.cols_fixed, 2):
                if self.maze[i][j + 1] == 1 and self.maze[i + 1][j]:
                    print("__|", end="")
                elif self.maze[i][j + 1] == 1:
                    print("  |", end="")
                elif self.maze[i + 1][j] == 1:
                    print("___", end="")
                elif i == self.rows_fixed - 2 and self.maze[i][j + 1] == 0:
                    print("___", end="")
                else:
                    print("   ", end="")
            print()

    def print_solved_maze(self) -> None:
        """Print the solved maze layout in console."""
        for i in range(self.cols_fixed // 2):
            print("___", end="")
        print()
        for i in range(1, self.rows_fixed, 2):
            print("|", end="")
            for j in range(1, self.cols_fixed, 2):
                if (
                    self.maze[i][j + 1] == 1
                    and self.maze[i + 1][j]
                    and [i, j] in self.path
                ):
                    print("_=|", end="")
                elif self.maze[i][j + 1] == 1 and [i, j] in self.path:
                    print(" =|", end="")
                elif self.maze[i + 1][j] == 1 and [i, j] in self.path:
                    print("_=_", end="")
                elif (
                    i == self.rows_fixed - 2
                    and self.maze[i][j + 1] == 0
                    and [i, j] in self.path
                ):
                    print("_=_", end="")
                elif self.maze[i][j + 1] == 1 and self.maze[i + 1][j]:
                    print("__|", end="")
                elif self.maze[i][j + 1] == 1:
                    print("  |", end="")
                elif self.maze[i + 1][j] == 1:
                    print("___", end="")
                elif i == self.rows_fixed - 2 and self.maze[i][j + 1] == 0:
                    print("___", end="")
                elif [i, j] in self.path:
                    print(" = ", end="")
                else:
                    print("   ", end="")
            print()

    def solve_maze(self, start: Point, end: Point) -> None:
        """Solve the maze from a given start position to an end position."""
        if any(x % 2 == 0 for x in start) or any(x % 2 == 0 for x in end):
            raise ValueError("start&end coord must be odd")

        if start == end:
            raise ValueError("start coord equal with end")

        max_value = max(self.rows_fixed, self.cols_fixed)
        if not (
            1 <= start[0] <= max_value
            and 1 <= start[1] <= max_value
            and 1 <= end[0] <= max_value
            and 1 <= end[1] <= max_value
        ):
            raise ValueError("Size solve value out of range")

        def a_way_out(maze: list[Matrix], start_pos: Point, end_pos: Point) -> None:
            """Recursive function to find a way out in the maze using backtracking."""
            maze[start_pos[0]][start_pos[1]][1] = 1
            self.solving_states.append(maze[start_pos[0]][start_pos[1]][2])
            ways = []

            def try_move(direction, distance) -> None:
                """Attempt to move in a specific direction from the current position and update the maze state."""

                new_pos_wall = (
                    start_pos[0] + direction[0],
                    start_pos[1] + direction[1],
                )
                new_pos = (
                    start_pos[0] + direction[0] * distance,
                    start_pos[1] + direction[1] * distance,
                )

                if (
                    maze[new_pos_wall[0]][new_pos_wall[1]] != 1
                    and maze[new_pos[0]][new_pos[1]][1] != 1
                ):
                    maze[new_pos[0]][new_pos[1]] = [
                        get_dist_between_points(new_pos, end_pos),
                        0,
                        maze[start_pos[0]][start_pos[1]][2]
                        + [[new_pos[0], new_pos[1]]],
                    ]
                    ways.append(maze[new_pos[0]][new_pos[1]])


            try_move((0, 1), 2)
            try_move((-1, 0), 2)
            try_move((1, 0), 2)
            try_move((0, -1), 2)
            shortest_ways = list(filter(lambda x: not x[1], ways))
            shortest_ways.sort(key=lambda x: x[0])
            if any(sublist[:2] == [0, 0] for sublist in shortest_ways):
                return

            if shortest_ways:
                new_start = find_element_in_matrix(maze, shortest_ways[0])
                a_way_out(maze, new_start, end_pos)

            else:
                new_start = [1, 1]
                for i in range(1, self.rows_fixed, 2):
                    for j in range(1, self.cols_fixed, 2):
                        if maze[i][j][0] != 0 and maze[i][j][1] != 1:
                            if maze[i][j][0] < maze[new_start[0]][new_start[1]][0]:
                                new_start = [i, j]
                a_way_out(maze, new_start, end_pos)

        solving_maze = copy.deepcopy(self.maze)
        for i in range(1, self.rows_fixed, 2):
            for j in range(1, self.cols_fixed, 2):
                solving_maze[i][j] = [0, 0, 0]

        solving_maze[start[0]][start[1]] = [
            get_dist_between_points(start, end),
            0,
            [list(start)],
        ]
        self.solving_states.append(solving_maze[start[0]][start[1]][2])

        a_way_out(solving_maze, start, end)

        self.solving_states.append(solving_maze[end[0]][end[1]][2])
        self.path = solving_maze[end[0]][end[1]][2]

        # st()

    def import_maze_from_file(self, filename: str) -> None:
        """Import a maze from a text file."""
        with open(filename, "r", encoding="utf-8") as file:
            maze_data = [list(map(int, line.strip())) for line in file.readlines()]
            self.maze = maze_data
            self.rows_fixed = len(maze_data)
            self.cols_fixed = len(maze_data[0])

    def import_maze_from_image(self, filename) -> None:
        """Import a maze from an image file."""
        image = Image.open(filename)
        width, height = image.size
        maze_data = []

        for y in range(1, height, 20):
            row = []
            

            for x in range(1, width, 20):
                pixel = image.getpixel((x, y))

                if pixel == WALL_COLOR:
                    row.append(1)

                elif pixel == PATH_COLOR:
                    row.append(0)

                else:
                    raise ValueError("Unknown pixel color in the image")

            maze_data.append(row)

        self.maze = maze_data
        self.rows_fixed = len(maze_data)
        self.cols_fixed = len(maze_data[0])
    
        self.print_maze()



    def export_maze_to_file(self) -> None:
        """Export the maze to a text file."""
        with open(self.filename, "w", encoding="utf-8") as file:
            for row in self.maze:
                file.write("".join(map(str, row)) + "\n")

    def create_maze_png(self, maze: Matrix) -> Image.Image:
        """Create an image of a labyrinth with a solution path if there is one."""

        cell_size = 20  # Adjust cell size as needed

        width = self.cols_fixed * cell_size
        height = self.rows_fixed * cell_size
        img = Image.new("RGB", (width, height), PATH_COLOR)
        draw = ImageDraw.Draw(img)
        maze = self.maze

        # Draw the maze walls
        for i in range(self.rows_fixed):
            for j in range(self.cols_fixed):
                if maze[i][j] == 1:
                    draw.rectangle(
                        [
                            (j * cell_size, i * cell_size),
                            ((j + 1) * cell_size, (i + 1) * cell_size),
                        ],
                        fill=WALL_COLOR,
                    )

        frames = []
        for path_cell in self.path:
            x, y = path_cell
            draw.rectangle(
                [
                    ((y + 0.2) * cell_size, (x + 0.2) * cell_size),
                    ((y + 0.8) * cell_size, (x + 0.8) * cell_size),
                ],
                fill=SOLVE_PATH_COLOR,
            )
            # Save a copy of the current state of the image
            frames.append(img.copy())

        # Save the animation as a GIF
        frames[0].save(
            f"{self.filename}.gif",
            save_all=True,
            append_images=frames[1:],  # Append frames after the first one
            optimize=True,
            duration=200,
            loop=0,
        )
        return img



def validate_import_file(ctx, param, value):
    if value:
        if value.endswith('.png') or value.endswith('.txt'):
            return value
        raise click.BadParameter("Unsupported import file format. Use .png for images or .txt for text.")

@click.command()
@click.option(
    '--size',
    type=str,
    help="Maze size in the format 'rows,cols'."
)
@click.option(
    '--start-end',
    type=str,
    help="Indices for solving in the format 'start_row,start_col,end_row,end_col'."
)
@click.option(
    '--import-file',
    type=click.Path(exists=True),
    callback=validate_import_file,
    help="Path to the import file."
)
@click.option(
    '--filename',
    type=str,
    help="Name of the output files."
)
@click.option(
    '--console-output',
    is_flag=True,
    help="Output the maze in console."
)
@click.option(
    '--text-output',
    is_flag=True,
    help="Output the maze in textfile."
)
@click.option(
    '--image-output',
    is_flag=True,
    help="Output the maze in image."
)
def main(size, start_end, import_file, filename, console_output, text_output, image_output):
    """Entrypoint for Maze Generator and Solver CLI."""
    maze = None

    if size:
        size_parts = size.split(',')
        if len(size_parts) != 2:
            raise click.BadParameter("Provide dimensions in the format 'rows,cols'.")

        rows, cols = map(int, size_parts)
        maze = Maze(rows, cols)
        maze.generate_maze()
        maze.print_maze()

    if import_file:
        maze = Maze()
        if import_file.endswith('.png'):
            maze.import_maze_from_image(import_file)
        elif import_file.endswith('.txt'):
            maze.import_maze_from_file(import_file)

    if maze is None:
        raise click.UsageError("Provide maze size or import a maze for solving.")

    if start_end:
        solve_parts = start_end.split(',')
        if len(solve_parts) != 4:
            raise click.BadParameter(
                "Provide solving coordinates in the format 'start_row,start_col,end_row,end_col'."
            )

        start = list(map(int, solve_parts[:2]))
        end = list(map(int, solve_parts[2:]))
        maze.solve_maze(start, end)

        if console_output:
            maze.print_maze()
            if maze.path:
                maze.print_solved_maze()

    if filename:
        if text_output:
            maze.export_maze_to_file(filename + '.txt')

        if image_output:
            maze.create_maze_png(maze.maze).save(filename + '_output.png', 'PNG')

    if not start_end:
        if console_output:
            maze.print_maze()

        if filename:
            if text_output:
                maze.export_maze_to_file(filename + '.txt')

            if image_output:
                maze.create_maze_png(maze.maze).save(filename + '.png', 'PNG')

if __name__ == '__main__':
    main()
