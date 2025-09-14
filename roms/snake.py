import random
import time

# Game configuration
GRID_SIZE = 4

# Game state
device = None
snake = []
food = ()
direction = "RIGHT"
score = 0
game_over = False
last_update_time = 0
update_interval = 0.2 # Slower update for normal speed

def init(d):
    """Initialize the game."""
    global device, snake, food, direction, score, game_over, last_update_time
    device = d
    start_x = (device.width // (2 * GRID_SIZE)) * GRID_SIZE
    start_y = (device.height // (2 * GRID_SIZE)) * GRID_SIZE
    snake = [
        (start_x, start_y),
        (start_x - GRID_SIZE, start_y),
        (start_x - 2 * GRID_SIZE, start_y)
    ]
    food = _place_food()
    direction = "RIGHT"
    score = 0
    game_over = False
    last_update_time = time.time()

def _place_food():
    """Place food in a random spot on the grid."""
    while True:
        x = random.randint(0, (device.width // GRID_SIZE) - 1) * GRID_SIZE
        y = random.randint(0, (device.height // GRID_SIZE) - 1) * GRID_SIZE
        if (x, y) not in snake:
            return (x, y)

def handle_input(key):
    """Handle user input."""
    global direction
    if game_over:
        if key == 'START' or key == 'B':
            init(device) # Restart game
        elif key == 'SELECT':
            return False # Exit
        return True

    if key == 'W' and direction != "DOWN":
        direction = "UP"
    elif key == 'S' and direction != "UP":
        direction = "DOWN"
    elif key == 'A_LEFT' and direction != "RIGHT":
        direction = "LEFT"
    elif key == 'D' and direction != "LEFT":
        direction = "RIGHT"
    elif key == 'SELECT':
        return False # Exit to menu
    
    return True

def _update_game_state():
    """Update the snake and check for collisions."""
    global snake, food, score, game_over

    if game_over:
        return

    head = snake[0]
    new_head = ()
    if direction == "UP":
        new_head = (head[0], head[1] - GRID_SIZE)
    elif direction == "DOWN":
        new_head = (head[0], head[1] + GRID_SIZE)
    elif direction == "LEFT":
        new_head = (head[0] - GRID_SIZE, head[1])
    elif direction == "RIGHT":
        new_head = (head[0] + GRID_SIZE, head[1])

    # Check for collisions
    if (
        new_head in snake or
        new_head[0] < 0 or new_head[0] >= device.width or
        new_head[1] < 0 or new_head[1] >= device.height
    ):
        game_over = True
        return

    snake.insert(0, new_head)

    # Check for food
    if new_head == food:
        score += 1
        food = _place_food()
    else:
        snake.pop()

def draw(draw):
    """Draw the game on the screen."""
    global last_update_time
    
    current_time = time.time()
    if not game_over and (current_time - last_update_time > update_interval):
        _update_game_state()
        last_update_time = current_time

    # Clear screen
    draw.rectangle(device.bounding_box, outline="black", fill="black")

    if game_over:
        draw.text((10, 10), "Game Over", fill="white")
        draw.text((10, 25), f"Score: {score}", fill="white")
        draw.text((10, 40), "START=retry", fill="white")
        draw.text((10, 50), "SELECT=exit", fill="white")
        return

    # Draw food
    draw.rectangle((food[0], food[1], food[0] + GRID_SIZE - 1, food[1] + GRID_SIZE - 1), fill="white")

    # Draw snake
    for segment in snake:
        draw.rectangle((segment[0], segment[1], segment[0] + GRID_SIZE - 1, segment[1] + GRID_SIZE - 1), fill="white")

    # Draw score
    draw.text((2, 2), f"Score: {score}", fill="white")