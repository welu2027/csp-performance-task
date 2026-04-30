import pygame, random

pygame.init()
pygame.key.set_repeat(170, 50)

COLS, ROWS, CELL = 10, 20, 30
screen = pygame.display.set_mode((COLS * CELL + 150, ROWS * CELL))
pygame.display.set_caption("Tetris")
clock = pygame.time.Clock()
font = pygame.font.SysFont("monospace", 18, bold=True)
small = pygame.font.SysFont("monospace", 13)

PIECES = [
    ([[1,1,1,1]],       (0, 240, 240)),
    ([[1,1],[1,1]],     (240, 240, 0)),
    ([[0,1,0],[1,1,1]], (160, 0, 240)),
    ([[1,0,0],[1,1,1]], (0, 0, 240)),
    ([[0,0,1],[1,1,1]], (240, 160, 0)),
    ([[1,1,0],[0,1,1]], (240, 0, 0)),
    ([[0,1,1],[1,1,0]], (0, 240, 0)),
]
SCORES = [0, 100, 300, 500, 800]


def new_piece():
    shape, color = random.choice(PIECES)
    return {"shape": shape, "color": color, "x": COLS // 2 - len(shape[0]) // 2, "y": 0}

def spawn(shape, color):
    return {"shape": shape, "color": color, "x": COLS // 2 - len(shape[0]) // 2, "y": 0}

def rotate(shape):
    return [list(row) for row in zip(*shape[::-1])]

def fits(board, piece, ox=0, oy=0, shape=None):
    for r, row in enumerate(shape or piece["shape"]):
        for c, val in enumerate(row):
            if val:
                x, y = piece["x"] + c + ox, piece["y"] + r + oy
                if x < 0 or x >= COLS or y >= ROWS or (y >= 0 and board[y][x]):
                    return False
    return True

def lock(board, piece):
    for r, row in enumerate(piece["shape"]):
        for c, val in enumerate(row):
            if val:
                board[piece["y"] + r][piece["x"] + c] = piece["color"]

def clear_lines(board):
    full = [r for r in range(ROWS) if all(board[r])]
    for r in full:
        del board[r]
        board.insert(0, [None] * COLS)
    return len(full)

def draw_mini(surface, shape, color, x, y):
    for r, row in enumerate(shape):
        for c, val in enumerate(row):
            if val:
                pygame.draw.rect(surface, color, (x + c * CELL, y + r * CELL, CELL - 1, CELL - 1))

def draw_key(label, x, y, held):
    color = (255, 255, 100) if held else (70, 70, 70)
    pygame.draw.rect(screen, color, (x, y, 30, 24), border_radius=4)
    pygame.draw.rect(screen, (150, 150, 150), (x, y, 30, 24), 1, border_radius=4)
    screen.blit(small.render(label, True, (0, 0, 0) if held else (180, 180, 180)), (x + 4, y + 5))

def draw_keys(keys_held):
    bx, by = COLS * CELL + 15, 490
    draw_key(" ^", bx + 34, by, keys_held["up"])
    draw_key(" <", bx,      by + 28, keys_held["left"])
    draw_key(" v", bx + 34, by + 28, keys_held["down"])
    draw_key(" >", bx + 68, by + 28, keys_held["right"])
    pygame.draw.rect(screen, (255, 255, 100) if keys_held["space"] else (70, 70, 70), (bx, by + 62, 102, 20), border_radius=4)
    pygame.draw.rect(screen, (150, 150, 150), (bx, by + 62, 102, 20), 1, border_radius=4)
    screen.blit(small.render("SPACE=drop", True, (0,0,0) if keys_held["space"] else (180,180,180)), (bx + 6, by + 65))
    screen.blit(small.render(f"C=hold  ESC=pause", True, (100, 200, 255)), (bx - 5, by + 88))

def draw(board, piece, next_p, held_p, score, level, lines, paused, keys_held):
    screen.fill((0, 0, 0))

    for r in range(ROWS):
        for c in range(COLS):
            pygame.draw.rect(screen, board[r][c] or (35, 35, 35), (c * CELL, r * CELL, CELL - 1, CELL - 1))

    ghost = dict(piece)
    while fits(board, ghost, oy=1):
        ghost = {**ghost, "y": ghost["y"] + 1}
    for r, row in enumerate(ghost["shape"]):
        for c, val in enumerate(row):
            if val:
                pygame.draw.rect(screen, (60, 60, 60), ((ghost["x"] + c) * CELL, (ghost["y"] + r) * CELL, CELL - 1, CELL - 1))

    draw_mini(screen, piece["shape"], piece["color"], piece["x"] * CELL, piece["y"] * CELL)

    sx = COLS * CELL + 10
    pygame.draw.line(screen, (80, 80, 80), (COLS * CELL, 0), (COLS * CELL, ROWS * CELL), 2)
    screen.blit(font.render("NEXT", True, (255, 255, 255)), (sx, 5))
    draw_mini(screen, next_p["shape"], next_p["color"], sx, 28)
    screen.blit(font.render("HOLD", True, (255, 255, 255)), (sx, 118))
    if held_p:
        draw_mini(screen, held_p["shape"], held_p["color"], sx, 141)
    screen.blit(font.render("Score", True, (160, 160, 160)), (sx, 248))
    screen.blit(font.render(str(score), True, (255, 255, 255)), (sx, 268))
    screen.blit(font.render("Level", True, (160, 160, 160)), (sx, 308))
    screen.blit(font.render(str(level), True, (255, 255, 255)), (sx, 328))
    screen.blit(font.render("Lines", True, (160, 160, 160)), (sx, 368))
    screen.blit(font.render(str(lines), True, (255, 255, 255)), (sx, 388))

    draw_keys(keys_held)

    if paused:
        screen.blit(font.render("PAUSED", True, (255, 255, 0)), (COLS * CELL // 2 - 40, ROWS * CELL // 2))

    pygame.display.flip()


def game_over(score):
    screen.fill((0, 0, 0))
    screen.blit(font.render("GAME OVER", True, (240, 0, 0)), (70, ROWS * CELL // 2 - 20))
    screen.blit(font.render(f"Score: {score}", True, (255, 255, 255)), (80, ROWS * CELL // 2 + 10))
    screen.blit(font.render("R=restart  Q=quit", True, (100, 100, 100)), (40, ROWS * CELL // 2 + 40))
    pygame.display.flip()
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_q):
                return False
            if e.type == pygame.KEYDOWN and e.key == pygame.K_r:
                return True


def main():
    while True:
        board = [[None] * COLS for _ in range(ROWS)]
        piece = new_piece()
        next_p = new_piece()
        held_p = None
        can_hold = True
        score, level, total_lines = 0, 1, 0
        fall_timer = 0
        paused = False
        keys_held = {"up": False, "left": False, "right": False, "down": False, "space": False}

        while True:
            dt = clock.tick(60)
            if not paused:
                fall_timer += dt

            k = pygame.key.get_pressed()
            keys_held = {
                "up":    k[pygame.K_UP],
                "left":  k[pygame.K_LEFT],
                "right": k[pygame.K_RIGHT],
                "down":  k[pygame.K_DOWN],
                "space": k[pygame.K_SPACE],
            }

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    return
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        paused = not paused
                        continue
                    if paused:
                        continue
                    if e.key == pygame.K_UP:
                        rot = rotate(piece["shape"])
                        for ox in (0, 1, -1):
                            if fits(board, piece, ox=ox, shape=rot):
                                piece["x"] += ox
                                piece["shape"] = rot
                                break
                    if e.key == pygame.K_LEFT and fits(board, piece, ox=-1):
                        piece["x"] -= 1
                    if e.key == pygame.K_RIGHT and fits(board, piece, ox=1):
                        piece["x"] += 1
                    if e.key == pygame.K_DOWN and fits(board, piece, oy=1):
                        piece["y"] += 1
                    if e.key == pygame.K_SPACE:
                        while fits(board, piece, oy=1):
                            piece["y"] += 1
                        lock(board, piece)
                        n = clear_lines(board)
                        total_lines += n
                        score += SCORES[n] * level
                        level = total_lines // 10 + 1
                        piece = next_p
                        next_p = new_piece()
                        fall_timer = 0
                        can_hold = True
                        if not fits(board, piece):
                            break
                    if e.key == pygame.K_c and can_hold:
                        can_hold = False
                        s, col = piece["shape"], piece["color"]
                        if held_p is None:
                            held_p = spawn(s, col)
                            piece = next_p
                            next_p = new_piece()
                        else:
                            held_p, piece = spawn(s, col), spawn(held_p["shape"], held_p["color"])
                        fall_timer = 0
            else:
                if not paused and fall_timer >= max(50, 500 - (level - 1) * 45):
                    fall_timer = 0
                    if fits(board, piece, oy=1):
                        piece["y"] += 1
                    else:
                        lock(board, piece)
                        n = clear_lines(board)
                        total_lines += n
                        score += SCORES[n] * level
                        level = total_lines // 10 + 1
                        piece = next_p
                        next_p = new_piece()
                        can_hold = True
                        if not fits(board, piece):
                            break

                draw(board, piece, next_p, held_p, score, level, total_lines, paused, keys_held)
                continue
            break

        if not game_over(score):
            pygame.quit()
            return

main()