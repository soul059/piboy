import time

# Game state
device = None
ball_pos = [0.0, 0.0]
ball_vel = [0.0, 0.0]
player_y = 0
ai_y = 0
player_score = 0
ai_score = 0

PADDLE_HEIGHT = 16
PADDLE_WIDTH = 4
BALL_SIZE = 4
MAX_BALL_SPEED_X = 5

def init(d):
    """Initialize the game."""
    global device, player_y, ai_y, player_score, ai_score
    device = d
    player_y = (device.height - PADDLE_HEIGHT) // 2
    ai_y = (device.height - PADDLE_HEIGHT) // 2
    player_score = 0
    ai_score = 0
    _reset_ball()

def _reset_ball(winner='player'):
    """Reset the ball to the center."""
    global ball_pos, ball_vel
    ball_pos = [device.width / 2.0, device.height / 2.0]
    if winner == 'player':
        ball_vel = [3.0, 1.0]
    else:
        ball_vel = [-3.0, 1.0]

def handle_input(key):
    """Handle user input."""
    global player_y
    player_speed = 4
    if key == 'W':
        player_y -= player_speed
    elif key == 'S':
        player_y += player_speed
    elif key == 'SELECT':
        return False

    if player_y < 0:
        player_y = 0
    if player_y > device.height - PADDLE_HEIGHT:
        player_y = device.height - PADDLE_HEIGHT
    
    return True

def _update_game_state():
    """Update game state."""
    global ball_pos, ball_vel, ai_y, player_score, ai_score

    ball_pos[0] += ball_vel[0]
    ball_pos[1] += ball_vel[1]

    if ball_pos[1] < 0 or ball_pos[1] > device.height - BALL_SIZE:
        ball_vel[1] *= -1

    # Player paddle collision
    if ball_vel[0] < 0 and PADDLE_WIDTH >= ball_pos[0] and player_y < ball_pos[1] < player_y + PADDLE_HEIGHT:
        ball_vel[0] *= -1
        if abs(ball_vel[0]) < MAX_BALL_SPEED_X:
            ball_vel[0] *= 1.1
    
    # AI paddle collision
    if ball_vel[0] > 0 and device.width - PADDLE_WIDTH - BALL_SIZE <= ball_pos[0] and ai_y < ball_pos[1] < ai_y + PADDLE_HEIGHT:
        ball_vel[0] *= -1
        if abs(ball_vel[0]) < MAX_BALL_SPEED_X:
            ball_vel[0] *= 1.1

    if ball_pos[0] < 0:
        ai_score += 1
        _reset_ball('ai')
    elif ball_pos[0] > device.width:
        player_score += 1
        _reset_ball('player')

    # Refined AI
    ai_speed = 3
    ai_center = ai_y + PADDLE_HEIGHT // 2
    if ai_center < ball_pos[1] - 5:
        ai_y += ai_speed
    elif ai_center > ball_pos[1] + 5:
        ai_y -= ai_speed
    
    if ai_y < 0:
        ai_y = 0
    if ai_y > device.height - PADDLE_HEIGHT:
        ai_y = device.height - PADDLE_HEIGHT

def draw(draw):
    """Draw the game."""
    _update_game_state()

    draw.rectangle(device.bounding_box, outline="black", fill="black")
    
    for i in range(0, device.height, 4):
        draw.line([(device.width // 2, i), (device.width // 2, i + 2)], fill="white")

    draw.rectangle((0, player_y, PADDLE_WIDTH - 1, player_y + PADDLE_HEIGHT), fill="white")
    draw.rectangle((device.width - PADDLE_WIDTH, ai_y, device.width - 1, ai_y + PADDLE_HEIGHT), fill="white")
    
    # Use integer positions for drawing the ball to prevent artifacts
    ball_x, ball_y = int(ball_pos[0]), int(ball_pos[1])
    draw.rectangle((ball_x, ball_y, ball_x + BALL_SIZE - 1, ball_y + BALL_SIZE - 1), fill="white")

    draw.text((device.width // 2 - 20, 2), str(player_score), fill="white")
    draw.text((device.width // 2 + 14, 2), str(ai_score), fill="white")