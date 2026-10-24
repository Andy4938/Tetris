from piece import Piece
from board import Board
from collections import deque


def movegen_s_piece(piece: Piece, board: Board):

    S_CELLS = [[
        (index % 3, index//3)
        for index, filled, in enumerate(shape)
        if filled
    ] 
    for shape in Piece.MINO_MAPS['s']]

    possible_moves = []

    def is_valid_state(x, y, rotation):

        rows = len(board.matrix)
        cols = len(board.matrix[0])

        for dx, dy in S_CELLS[rotation % 4]:

            #x and y positions of the piece on the board (global coordinates)
            board_x = x + dx
            board_y = y + dy

            if not (0 <= board_y < rows and 0 <= board_x < cols):
                return False
            if board.matrix[board_y][board_x]:
                return False

        return True

    def stop(x, y, rotation):
        return not is_valid_state(x, y+1, rotation)
        

    def findMoves(x, y, rotation):

        start = (x, y, rotation % 4)
        visited = {start}
        # right 0, left 1, down 2
        q = deque()
        if is_valid_state(*start):
            q.append((start, []))

        while(len(q) > 0):

            (x, y, rotation), path = q.popleft()

            if stop(x, y, rotation):
                possible_moves.append({
                    "state": (x, y, rotation),
                    "path": path
                })

            candidates = [
                ("right", (x + 1, y, rotation)),
                ("left", (x - 1, y, rotation)),
                ("down", (x, y + 1, rotation)),
                ("ccw",   (x, y, (rotation + 1) % 4)),
                ("180",   (x, y, (rotation + 2) % 4)),
                ("cw",    (x, y, (rotation + 3) % 4)),
            ]

            for action, next_state in candidates:
                if next_state in visited:
                    continue

                if not is_valid_state(*next_state):
                    continue

                visited.add(next_state)
                q.append((next_state, path + [action]))

    findMoves(piece.x, piece.y, piece.rotation)

    return possible_moves

    






    

if __name__ == "__main__":
    from types import SimpleNamespace

    piece = Piece("s", 0, True)

    board = SimpleNamespace(
        matrix=[[None for _ in range(10)] for _ in range(40)]
    )

    moves = movegen_s_piece(piece, board)

    print("Landing states:", len(moves))

    for move in moves:
        print("State:", move["state"])
        print("Path:", move["path"])
        print()

    assert len(moves) == 34, f"Expected 34, got {len(moves)}"

