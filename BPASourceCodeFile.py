from heapq import heappush, heappop

def to_2d_array(one_d_board):
    """Converts a 1 dimensional puzzle state board to a 2D array representation. Assumes 4 rows and
    4 columns"""
    return [one_d_board[i * 4:(i + 1) * 4] for i in range((len(one_d_board) + 4 - 1) // 4)]


# making move cost:
# tile 1-9: 1 unit
# tile 10-15: 10 units
def val_multiplier(val):
    if val == 0:
        return 0
    elif 0 < val < 10:
        return 1
    elif 10 <= val <= 15:
        return 10


class PuzzleState:
    """Core component. Represents a configuration of the pieces on the puzzle board.
    Includes:
    parent_id         - The PuzzleState object that spawned this instance, (Integer)
    id_no             - Unique identifier (Integer)
    board_state_1d    - The state of the board represented as a 1 dimensional array.
    board_state       - The state of the board as a 2D array. This is used to compute the h2 heuristic
    goal_puzzle_state - The state of the board we are trying to get to. This is used to compute the
                        estimated heuristics. This may be better as a global var?
    h1_of_n           - h1 heuristic
    h2_of_n           - h2 heuristic
    g_of_n            - Summation of cost to reach this state so far, computed from parent states
    f1_of_n           - g_of_n + h1_of_n
    f2_of_n           - g_of_n + h2_of_n
    depth             - How far down in the tree this state is. Used solely for BFS"""

    def __init__(self, board_state_1d, goal_state=None, parent_id=None, depth=0, cost_so_far=0):
        self.parent_id = parent_id
        self.id_no = id(self)
        self.board_state_1d = board_state_1d
        self.board_state = to_2d_array(board_state_1d)
        self.goal_puzzle_state = goal_state
        self.h1_of_n = self.estimated_cost_to_goal_h1()
        self.h2_of_n = self.estimated_cost_to_goal_h2()
        self.g_of_n = cost_so_far
        self.f1_of_n = self.g_of_n + self.h1_of_n
        self.f2_of_n = self.g_of_n + self.h2_of_n
        self.depth = depth

    # h1: estimated cost of taking board B to the goal
    # state G is the number of tiles in B that are not in
    # the correct location as required by G
    def estimated_cost_to_goal_h1(self):
        # silly hack. We want to instantiate the goal state as a PuzzleState object, but it shouldn't
        # have a goal state itself. Maybe it should just be itself, that might work?
        # Anyway, now the goal_puzzle_state attr on the goal_state object is None, so the h1
        # and h2 assignments will break, since the estimated cost for both will be 0, we just default it
        if self.goal_puzzle_state is None:
            return 0
        else:
            count = 0
            for idx, piece in enumerate(self.board_state_1d):
                if piece is not self.goal_puzzle_state.board_state_1d[idx]:
                    multiplier = val_multiplier(piece)
                    count += multiplier
            return count - 1

    # h2: the sum of the smallest number of moves for
    # each tile not at its final location, to reach its final
    # location
    def estimated_cost_to_goal_h2(self):
        if self.goal_puzzle_state is None:
            return 0
        else:
            total = 0
            for piece in range(1, 16):
                [cur_row, cur_col] = self.find(piece)
                [goal_row, goal_col] = self.goal_puzzle_state.find(piece)
                multiplier = val_multiplier(piece)
                difference = multiplier * (abs(goal_row - cur_row) + abs(goal_col - cur_col))
                total += difference
            return total

    def find(self, val):
        for row in range(4):
            for col in range(4):
                if self.board_state[row][col] == val:
                    return row, col


    def describe(self):
        print("State Description: ")
        print("Board: ", self.board_state_1d)
        print("g(n): ", self.g_of_n)
        print("h1(n): ", self.h1_of_n)
        print("h2(n): ", self.h2_of_n)
        print("f1(n): ", self.f1_of_n)
        print("f2(n): ", self.f2_of_n)
        print("ID: ", self.id_no)
        print("Parent ID: ", self.parent_id)

    # making move cost:
    # tile 1-9: 1 unit
    # tile 10-15: 10 units
    def move_cost(self, target_pos):
        val_being_moved = self.board_state_1d[target_pos]
        if 0 < val_being_moved < 10:
            return 1
        elif 10 <= val_being_moved <= 15:
            return 10

    def move(self, direction):
        dirs = {"up": -4, "right": 1, "down": 4, "left": -1}
        zero_pos = self.board_state_1d.index(0)
        target_pos = zero_pos + dirs[direction]
        new_board = self.board_state_1d[:]
        cost = self.move_cost(target_pos)
        cost_so_far = self.g_of_n + cost
        new_board[zero_pos], new_board[target_pos] = new_board[target_pos], new_board[zero_pos]
        return PuzzleState(new_board, self.goal_puzzle_state, self.id_no, self.depth + 1, cost_so_far)

    def expand(self):
        "Return value PuzzleState expansions of the current PuzzleState"
        [row, col] = self.find(0)
        valid_moves = []
        if row > 0:
            valid_moves.append("up")
        if row < 3:
            valid_moves.append("down")
        if col > 0:
            valid_moves.append("left")
        if col < 3:
            valid_moves.append("right")
        return list(map(self.move, valid_moves))


# Almost definitely a better way to do this...
def get_parent_state(state, closed_list):
    for closed_state in closed_list:
        if closed_state.id_no == state.parent_id:
            return closed_state


def get_state_path(end_state, closed_list):
    cur_state = end_state
    path = [end_state]
    while cur_state.depth is not 0:
        parent_state = get_parent_state(cur_state, closed_list)
        path.append(parent_state)
        cur_state = parent_state
    return path


# outputs
# sequence of state descriptions, first state is goal,
# last is start_state
# length of path in terms of number of moves,
# count of nodes added to open list and count in closed list
# sequence of state descs using A* h1 algorithm
def print_success_message(end_state, closed_list, added_to_open_list, method):
    print ("\n\nSolved with ", method, " method!")
    path = get_state_path(end_state, closed_list)
    print("\nPath (end->start): ")
    for s in path:
        s.describe()
        print("\n")
    print("Number of moves: ", len(path) - 1)
    print("Nodes added to open list: ", added_to_open_list)
    print("Nodes added to closed list: ", len(closed_list))


def solve(start_board, goal_board, method):
    """Find a path from the start_board to the goal_board.
    Options for methods are:
    bfs: breadth first search
    a_star_h1: A* search using h1 in assignment
    a_star_h2: A* search using h2 in assignment"""
    open_list = []
    closed_list = []
    goal_state = PuzzleState(goal_board)
    start_state = PuzzleState(start_board, goal_state)
    heappush(open_list, (0, start_state.id_no, start_state))
    added_to_open_list = 0
    has_solved = False
    while not has_solved:
        cur_state = heappop(open_list)[2]
        if cur_state.board_state_1d == goal_board:
            print_success_message(cur_state, closed_list, added_to_open_list, method)
            has_solved = True
        else:
            closed_list.append(cur_state)
            expansions = cur_state.expand()
            for new_state in expansions:
                added_to_open_list += 1
                # Push expansions to the open_list, priority is determined by the first value in the
                # tuple (depth for bfs, f1 for a_star_h1, f2 for a_star_h2
                # In cases where there are equal prioities, we supply the state's id number, which
                # will always be unique
                if method == "bfs":
                    heappush(open_list, (new_state.depth, new_state.id_no, new_state))
                elif method == "a_star_h1":
                    heappush(open_list, (new_state.f1_of_n, new_state.id_no, new_state))
                elif method == "a_star_h2":
                    heappush(open_list, (new_state.f2_of_n, new_state.id_no, new_state))


def solve_all(start_board, goal_board):
    print("Solving for: \nstart_board: ", start_board, "\ngoal_board: ", goal_board)
    solve(start_board, goal_board, "bfs")
    solve(start_board, goal_board, "a_star_h1")
    solve(start_board, goal_board, "a_star_h2")


start_board1 = [5, 1, 3, 4, 2, 10, 6, 8, 13, 9, 7, 12, 0, 14, 11, 15]
start_board2 = [1, 0, 3, 4, 5, 2, 7, 8, 9, 6, 15, 11, 13, 10, 14, 12]
start_board3 = [2, 0, 3, 4, 1, 5, 7, 8, 9, 6, 10, 12, 13, 14, 11, 15]
goal_board = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 0]


def to_int_arr(input_list):
    arr = []
    for s in input_list.split():
        arr.append(int(float(s)))
    return arr


start_board = input("Enter the start board as a 1x16 list, separated by spaces (no brackets): ")
goal_board = input("Enter the goal board as a 1x16 list, separated by spaces (no brackets): ")

solve_all(to_int_arr(start_board), to_int_arr(goal_board))
