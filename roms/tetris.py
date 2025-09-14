import time
import random

# Game state
device = None
field = []
score = 0
lines = 0
level = 1
game_over = False

# Tetrominoes and colors (monochrome)
SHAPES = [
    [[1, 1, 1, 1]], # I
    [[1, 1], [1, 1]], # O
    [[0, 1, 0], [1, 1, 1]], # T
    [[0, 0, 1], [1, 1, 1]], # L
    [[1, 0, 0], [1, 1, 1]], # J
    [[0, 1, 1], [1, 1, 0]], # S
    [[1, 1, 0], [0, 1, 1]]  # Z
]

current_piece = None
current_pos = [0, 0]
fall_timer = 0

FIELD_WIDTH = 10
FIELD_HEIGHT = 16
BLOCK_SIZE = 4

def init(d):
    global device, field, score, lines, level, game_over
    device = d
    field = [[0] * FIELD_WIDTH for _ in range(FIELD_HEIGHT)]
    score = 0
    lines = 0
    level = 1
    game_over = False
    _new_piece()

def _new_piece():
    global current_piece, current_pos
    current_piece = random.choice(SHAPES)
    current_pos = [FIELD_WIDTH // 2 - len(current_piece[0]) // 2, 0]
    if _collides(current_piece, current_pos):
        global game_over
        game_over = True

def _collides(piece, pos):
    for r, row in enumerate(piece):
        for c, cell in enumerate(row):
            if cell:
                field_r, field_c = pos[1] + r, pos[0] + c
                if not (0 <= field_c < FIELD_WIDTH and 0 <= field_r < FIELD_HEIGHT and not field[field_r][field_c]):
                    return True
    return False

def _lock_piece():
    for r, row in enumerate(current_piece):
        for c, cell in enumerate(row):
            if cell:
                field[current_pos[1] + r][current_pos[0] + c] = 1
    _check_lines()
    _new_piece()

def _check_lines():
    global field, score, lines, level
    cleared_lines = 0
    new_field = [row for row in field if not all(row)]
    cleared_lines = FIELD_HEIGHT - len(new_field)
    if cleared_lines > 0:
        lines += cleared_lines
        score += (cleared_lines ** 2) * 100
        level = 1 + lines // 10
        field = [[0] * FIELD_WIDTH for _ in range(cleared_lines)] + new_field

def handle_input(key):
    global current_pos, current_piece
    if game_over:
        if key == 'START': init(device)
        elif key == 'SELECT': return False
        return True

    new_pos = list(current_pos)
    if key == 'A_LEFT': new_pos[0] -= 1
    elif key == 'D': new_pos[0] += 1
    
    if not _collides(current_piece, new_pos):
        current_pos = new_pos

    if key == 'S': # Soft drop
        new_pos = [current_pos[0], current_pos[1] + 1]
        if not _collides(current_piece, new_pos):
            current_pos = new_pos

    if key == 'B' or key == 'START': # Rotate
        rotated = list(zip(*current_piece[::-1]))
        if not _collides(rotated, current_pos):
            current_piece = rotated
    
    if key == 'SELECT': return False
    return True

def _update_game_state():
    global fall_timer, current_pos
    fall_speed = 20 - level
    if fall_speed < 1: fall_speed = 1

    fall_timer += 1
    if fall_timer > fall_speed:
        fall_timer = 0
        new_pos = [current_pos[0], current_pos[1] + 1]
        if _collides(current_piece, new_pos):
            _lock_piece()
        else:
            current_pos = new_pos

def draw(draw):
    if not game_over: _update_game_state()

    draw.rectangle(device.bounding_box, outline="black", fill="black")
    
    if game_over:
        draw.text((30, 20), "GAME OVER", fill="white")
        draw.text((30, 35), f"Score: {score}", fill="white")
        return

    # Draw field and locked blocks
    field_x_offset = (device.width - (FIELD_WIDTH * BLOCK_SIZE)) // 2
    for r, row in enumerate(field):
        for c, cell in enumerate(row):
            if cell:
                draw.rectangle((field_x_offset + c * BLOCK_SIZE, r * BLOCK_SIZE, 
                                field_x_offset + (c + 1) * BLOCK_SIZE - 1, (r + 1) * BLOCK_SIZE - 1), fill="white")

    # Draw current piece
    for r, row in enumerate(current_piece):
        for c, cell in enumerate(row):
            if cell:
                draw.rectangle((field_x_offset + (current_pos[0] + c) * BLOCK_SIZE, (current_pos[1] + r) * BLOCK_SIZE,
                                field_x_offset + (current_pos[0] + c + 1) * BLOCK_SIZE - 1, (current_pos[1] + r + 1) * BLOCK_SIZE - 1), fill="white")

    # Draw UI
    draw.text((2, 0), f"S:{score}", fill="white")
    draw.text((2, 10), f"L:{lines}", fill="white")
    draw.text((2, 20), f"LVL:{level}", fill="white")
