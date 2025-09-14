import time

# Game state
device = None
paddle_x = 0
ball_pos = [0.0, 0.0]
ball_vel = [0.0, 0.0]
bricks = []
lives = 3
score = 0
game_started = False
game_over = False

# Game configuration
PADDLE_WIDTH = 24
PADDLE_HEIGHT = 4
BALL_SIZE = 3
BRICK_WIDTH = 16
BRICK_HEIGHT = 6
NUM_BRICK_ROWS = 4
NUM_BRICK_COLS = 8

def init(d):
    """Initialize the game."""
    global device, lives, score, game_over
    device = d
    lives = 3
    score = 0
    game_over = False
    _create_bricks()
    _reset_level()

def _create_bricks():
    """Create the grid of bricks."""
    global bricks
    bricks = []
    for row in range(NUM_BRICK_ROWS):
        for col in range(NUM_BRICK_COLS):
            x = col * BRICK_WIDTH
            y = row * BRICK_HEIGHT + 10 # Offset from top
            bricks.append([x, y])

def _reset_level():
    """Reset paddle and ball for a new life."""
    global paddle_x, ball_pos, ball_vel, game_started
    paddle_x = (device.width - PADDLE_WIDTH) // 2
    ball_pos = [paddle_x + PADDLE_WIDTH // 2, device.height - PADDLE_HEIGHT - BALL_SIZE - 1]
    ball_vel = [2.0, -2.0]
    game_started = False

def handle_input(key):
    """Handle user input."""
    global paddle_x, game_started

    if game_over:
        if key == 'START':
            init(device)
        elif key == 'SELECT':
            return False
        return True

    if key == 'A_LEFT':
        paddle_x -= 5
    elif key == 'D':
        paddle_x += 5
    elif (key == 'START' or key == 'B') and not game_started:
        game_started = True
    elif key == 'SELECT':
        return False

    # Clamp paddle
    if paddle_x < 0:
        paddle_x = 0
    if paddle_x > device.width - PADDLE_WIDTH:
        paddle_x = device.width - PADDLE_WIDTH
    
    return True

def _update_game_state():
    """Update game logic."""
    global ball_pos, ball_vel, lives, score, game_over

    if not game_started:
        # Ball follows paddle
        ball_pos[0] = paddle_x + PADDLE_WIDTH // 2
        return

    ball_pos[0] += ball_vel[0]
    ball_pos[1] += ball_vel[1]

    # Wall collision
    if ball_pos[0] < 0 or ball_pos[0] > device.width - BALL_SIZE:
        ball_vel[0] *= -1
    if ball_pos[1] < 0:
        ball_vel[1] *= -1

    # Bottom wall (lose life)
    if ball_pos[1] > device.height - BALL_SIZE:
        lives -= 1
        if lives <= 0:
            game_over = True
        else:
            _reset_level()
        return

    # Paddle collision
    if (
        paddle_x < ball_pos[0] < paddle_x + PADDLE_WIDTH and
        device.height - PADDLE_HEIGHT - BALL_SIZE < ball_pos[1]
    ):
        ball_vel[1] *= -1
        # Simple angle change based on hit location
        ball_vel[0] += (ball_pos[0] - (paddle_x + PADDLE_WIDTH / 2)) * 0.1

    # Brick collision
    for brick in bricks[:]:
        bx, by = brick
        if (
            bx < ball_pos[0] < bx + BRICK_WIDTH and
            by < ball_pos[1] < by + BRICK_HEIGHT
        ):
            bricks.remove(brick)
            score += 10
            ball_vel[1] *= -1
            break
    
    if not bricks:
        # Win condition
        _create_bricks()
        _reset_level()

def draw(draw):
    """Draw the game screen."""
    _update_game_state()

    draw.rectangle(device.bounding_box, outline="black", fill="black")

    if game_over:
        draw.text((20, 20), "GAME OVER", fill="white")
        draw.text((20, 35), f"Score: {score}", fill="white")
        return

    # Draw paddle
    draw.rectangle((paddle_x, device.height - PADDLE_HEIGHT, paddle_x + PADDLE_WIDTH, device.height), fill="white")

    # Draw ball
    ball_x, ball_y = int(ball_pos[0]), int(ball_pos[1])
    draw.rectangle((ball_x, ball_y, ball_x + BALL_SIZE, ball_y + BALL_SIZE), fill="white")

    # Draw bricks
    for brick in bricks:
        draw.rectangle((brick[0], brick[1], brick[0] + BRICK_WIDTH - 1, brick[1] + BRICK_HEIGHT - 1), outline="black", fill="white")

    # Draw UI
    draw.text((2, 0), f"Score: {score}", fill="white")
    draw.text((device.width - 20, 0), f"L: {lives}", fill="white")

    if not game_started:
        draw.text((20, 40), "Press START", fill="white")
