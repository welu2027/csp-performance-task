import pygame
import random

pygame.init()

COLS, ROWS = 10, 20
CELL = 30
WIDTH = COLS * CELL + 160
HEIGHT = ROWS * CELL

BLACK  = (0, 0, 0)
WHITE  = (255, 255, 255)
GRAY   = (40, 40, 40)
BORDER = (80, 80, 80)

SHAPES = [
    [[1,1,1,1]],
    [[1,1],[1,1]],
    [[0,1,0],[1,1,1]],
    [[1,0,0],[1,1,1]],
    [[0,0,1],[1,1,1]],
    [[1,1,0],[0,1,1]],
    [[0,1,1],[1,1,0]],
]

COLORS = [
    (0,   240, 240),
    (240, 240,   0),
    (160,   0, 240),
    (0,    0,  240),
    (240, 160,   0),
    (240,   0,   0),
    (0,   240,   0),
]

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tetris")
clock = pygame.time.Clock()
font_big  = pygame.font.SysFont("monospace", 28, bold=True)
font_small = pygame.font.SysFont("monospace", 18)

def new_piece():
    idx = random.randrange(len(SHAPES))
    return {"shape": SHAPES[idx], "color": COLORS[idx],
            "x": COLS // 2 - len(SHAPES[idx][0]) // 2, "y": 0}

def rotate(shape):
    return [list(row) for row in zip(*shape[::-1])]

def valid(board, piece, ox=0, oy=0, shape=None):
    s = shape if shape else piece["shape"]
    for r, row in enumerate(s):
        for c, cell in enumerate(row):
            if cell:
                nx, ny = piece["x"] + c + ox, piece["y"] + r + oy
                if nx < 0 or nx >= COLS or ny >= ROWS:
                    return False
                if ny >= 0 and board[ny][nx]:
                    return False
    return True

def lock(board, piece):
    for r, row in enumerate(piece["shape"]):
        for c, cell in enumerate(row):
            if cell:
                board[piece["y"] + r][piece["x"] + c] = piece["color"]

def clear_lines(board):
    full = [r for r in range(ROWS) if all(board[r])]
    for r in full:
        del board[r]
        board.insert(0, [None] * COLS)
    return len(full)

def draw_cell(surface, x, y, color):
    rect = pygame.Rect(x * CELL, y * CELL, CELL - 1, CELL - 1)
    pygame.draw.rect(surface, color, rect)
    highlight = tuple(min(255, v + 60) for v in color)
    pygame.draw.rect(surface, highlight, rect, 2)

def draw_board(surface, board):
    for r in range(ROWS):
        for c in range(COLS):
            if board[r][c]:
                draw_cell(surface, c, r, board[r][c])
            else:
                pygame.draw.rect(surface, GRAY,
                    pygame.Rect(c * CELL, r * CELL, CELL - 1, CELL - 1))

def draw_piece(surface, piece):
    for r, row in enumerate(piece["shape"]):
        for c, cell in enumerate(row):
            if cell:
                draw_cell(surface, piece["x"] + c, piece["y"] + r, piece["color"])

def draw_ghost(surface, board, piece):
    ghost = dict(piece)
    while valid(board, ghost, oy=1):
        ghost = {**ghost, "y": ghost["y"] + 1}
    for r, row in enumerate(ghost["shape"]):
        for c, cell in enumerate(row):
            if cell:
                rect = pygame.Rect((ghost["x"] + c) * CELL, (ghost["y"] + r) * CELL,
                                   CELL - 1, CELL - 1)
                pygame.draw.rect(surface, (60, 60, 60), rect)
                pygame.draw.rect(surface, BORDER, rect, 1)

def draw_next(surface, piece):
    label = font_small.render("NEXT", True, WHITE)
    surface.blit(label, (COLS * CELL + 20, 20))
    for r, row in enumerate(piece["shape"]):
        for c, cell in enumerate(row):
            if cell:
                rx = COLS * CELL + 20 + c * CELL
                ry = 50 + r * CELL
                pygame.draw.rect(surface, piece["color"],
                    pygame.Rect(rx, ry, CELL - 1, CELL - 1))

def draw_held(surface, piece):
    label = font_small.render("HOLD", True, WHITE)
    surface.blit(label, (COLS * CELL + 20, 140))
    if piece is None:
        return
    for r, row in enumerate(piece["shape"]):
        for c, cell in enumerate(row):
            if cell:
                rx = COLS * CELL + 20 + c * CELL
                ry = 170 + r * CELL
                pygame.draw.rect(surface, piece["color"],
                    pygame.Rect(rx, ry, CELL - 1, CELL - 1))

def draw_sidebar(surface, score, level, lines):
    x = COLS * CELL + 10
    surface.blit(font_small.render(f"SCORE", True, WHITE), (x, 280))
    surface.blit(font_big.render(str(score), True, WHITE), (x, 305))
    surface.blit(font_small.render(f"LEVEL", True, WHITE), (x, 360))
    surface.blit(font_big.render(str(level), True, WHITE), (x, 385))
    surface.blit(font_small.render(f"LINES", True, WHITE), (x, 440))
    surface.blit(font_big.render(str(lines), True, WHITE), (x, 465))

LINE_SCORES = [0, 100, 300, 500, 800]

def fall_speed(level):
    return max(50, 500 - (level - 1) * 45)

def game_over_screen(score):
    screen.fill(BLACK)
    screen.blit(font_big.render("GAME OVER", True, (240, 0, 0)),  (WIDTH // 2 - 90, HEIGHT // 2 - 50))
    screen.blit(font_small.render(f"Score: {score}", True, WHITE), (WIDTH // 2 - 50, HEIGHT // 2))
    screen.blit(font_small.render("R to restart  Q to quit", True, BORDER), (WIDTH // 2 - 110, HEIGHT // 2 + 40))
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True
                if event.key == pygame.K_q:
                    return False

def main():
    while True:
        board = [[None] * COLS for _ in range(ROWS)]
        piece = new_piece()
        next_piece = new_piece()
        score = 0
        level = 1
        total_lines = 0
        fall_timer = 0
        das_timer = 0
        das_delay = 170
        das_repeat = 50
        move_dir = 0
        move_held = False
        paused = False
        held_piece = None
        can_hold = True
        running = True

        while running:
            dt = clock.tick(60)
            if not paused:
                fall_timer += dt

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        paused = not paused
                    if paused:
                        continue
                    if event.key == pygame.K_c:
                        if can_hold:
                            can_hold = False
                            idx = COLORS.index(piece["color"])
                            saved = {"shape": SHAPES[idx], "color": COLORS[idx],
                                     "x": COLS // 2 - len(SHAPES[idx][0]) // 2, "y": 0}
                            if held_piece is None:
                                held_piece = saved
                                piece = next_piece
                                next_piece = new_piece()
                            else:
                                prev = held_piece
                                held_piece = saved
                                piece = {**prev,
                                         "x": COLS // 2 - len(prev["shape"][0]) // 2, "y": 0}
                            fall_timer = 0
                    if event.key == pygame.K_UP:
                        rot = rotate(piece["shape"])
                        if valid(board, piece, shape=rot):
                            piece["shape"] = rot
                        elif valid(board, piece, ox=1, shape=rot):
                            piece["x"] += 1; piece["shape"] = rot
                        elif valid(board, piece, ox=-1, shape=rot):
                            piece["x"] -= 1; piece["shape"] = rot
                    if event.key == pygame.K_SPACE:
                        while valid(board, piece, oy=1):
                            piece["y"] += 1
                        lock(board, piece)
                        cleared = clear_lines(board)
                        total_lines += cleared
                        score += LINE_SCORES[cleared] * level
                        level = total_lines // 10 + 1
                        piece = next_piece
                        next_piece = new_piece()
                        fall_timer = 0
                        can_hold = True
                        if not valid(board, piece):
                            running = False
                    if event.key == pygame.K_DOWN:
                        move_dir = 0
                    if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                        move_dir = -1 if event.key == pygame.K_LEFT else 1
                        move_held = False
                        das_timer = 0
                        if valid(board, piece, ox=move_dir):
                            piece["x"] += move_dir
                if event.type == pygame.KEYUP:
                    if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                        move_dir = 0

            if paused:
                label = font_big.render("PAUSED", True, WHITE)
                screen.blit(label, (COLS * CELL // 2 - label.get_width() // 2, HEIGHT // 2 - 20))
                pygame.display.flip()
                continue

            keys = pygame.key.get_pressed()
            if keys[pygame.K_DOWN]:
                fall_timer += dt * 9

            if move_dir:
                das_timer += dt
                threshold = das_repeat if move_held else das_delay
                if das_timer >= threshold:
                    das_timer = 0
                    move_held = True
                    if valid(board, piece, ox=move_dir):
                        piece["x"] += move_dir

            if fall_timer >= fall_speed(level):
                fall_timer = 0
                if valid(board, piece, oy=1):
                    piece["y"] += 1
                else:
                    lock(board, piece)
                    cleared = clear_lines(board)
                    total_lines += cleared
                    score += LINE_SCORES[cleared] * level
                    level = total_lines // 10 + 1
                    piece = next_piece
                    next_piece = new_piece()
                    can_hold = True
                    if not valid(board, piece):
                        running = False

            screen.fill(BLACK)
            draw_board(screen, board)
            draw_ghost(screen, board, piece)
            draw_piece(screen, piece)
            pygame.draw.line(screen, BORDER, (COLS * CELL, 0), (COLS * CELL, HEIGHT), 2)
            draw_next(screen, next_piece)
            draw_held(screen, held_piece)
            draw_sidebar(screen, score, level, total_lines)
            pygame.display.flip()

        if not game_over_screen(score):
            pygame.quit()
            return

main()