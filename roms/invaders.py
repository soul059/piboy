import time
import random

# Game state
device = None
player_x = 0
player_bullets = []
aliens = []
alien_bullets = []
alien_direction = 1
alien_move_timer = 0
lives = 3
score = 0
game_over = False

# Config
PLAYER_SPEED = 4
BULLET_SPEED = 5
ALIEN_MOVE_INTERVAL = 15
ALIEN_SHOOT_CHANCE = 0.01

def init(d):
    """Initialize the game."""
    global device, lives, score, game_over, player_x, aliens
    device = d
    lives = 3
    score = 0
    game_over = False
    player_x = device.width // 2
    aliens = []
    player_bullets.clear()
    alien_bullets.clear()
    _create_aliens()

def _create_aliens():
    """Create the grid of aliens."""
    for row in range(3):
        for col in range(8):
            x = col * 12 + 10
            y = row * 10 + 5
            aliens.append([x, y])

def handle_input(key):
    """Handle user input."""
    global player_x
    if game_over:
        if key == 'START': init(device)
        elif key == 'SELECT': return False
        return True

    if key == 'A_LEFT': player_x -= PLAYER_SPEED
    elif key == 'D': player_x += PLAYER_SPEED
    elif key == 'B' or key == 'START':
        if len(player_bullets) < 3: # Limit bullets on screen
            player_bullets.append([player_x, device.height - 10])
    elif key == 'SELECT': return False

    if player_x < 0: player_x = 0
    if player_x > device.width - 8: player_x = device.width - 8
    return True

def _update_game_state():
    """Update all game logic."""
    global alien_move_timer, alien_direction, lives, score, game_over

    # Move player bullets
    for bullet in player_bullets[:]:
        bullet[1] -= BULLET_SPEED
        if bullet[1] < 0: player_bullets.remove(bullet)

    # Move alien bullets
    for bullet in alien_bullets[:]:
        bullet[1] += BULLET_SPEED
        if bullet[1] > device.height: alien_bullets.remove(bullet)

    # Move aliens
    alien_move_timer += 1
    move_down = False
    if alien_move_timer > ALIEN_MOVE_INTERVAL:
        alien_move_timer = 0
        for alien in aliens:
            alien[0] += alien_direction
            if alien[0] < 0 or alien[0] > device.width - 8:
                move_down = True
        if move_down:
            alien_direction *= -1
            for a in aliens: a[1] += 4

    # Alien shooting
    if random.random() < ALIEN_SHOOT_CHANCE and aliens:
        shooter = random.choice(aliens)
        alien_bullets.append([shooter[0] + 3, shooter[1] + 5])

    # Collisions
    for p_bullet in player_bullets[:]:
        for alien in aliens[:]:
            if abs(p_bullet[0] - alien[0]) < 5 and abs(p_bullet[1] - alien[1]) < 5:
                player_bullets.remove(p_bullet)
                aliens.remove(alien)
                score += 10
                break

    for a_bullet in alien_bullets[:]:
        if abs(a_bullet[0] - player_x) < 5 and a_bullet[1] > device.height - 10:
            alien_bullets.remove(a_bullet)
            lives -= 1
            if lives <= 0: game_over = True
            break
    
    if not aliens:
        _create_aliens()

def draw(draw):
    """Draw the game screen."""
    if not game_over: _update_game_state()

    draw.rectangle(device.bounding_box, outline="black", fill="black")

    if game_over:
        draw.text((20, 20), "GAME OVER", fill="white")
        draw.text((20, 35), f"Score: {score}", fill="white")
        return

    # Draw player
    draw.rectangle((player_x, device.height - 8, player_x + 8, device.height), fill="white")

    # Draw aliens
    for alien in aliens:
        draw.rectangle((alien[0], alien[1], alien[0] + 6, alien[1] + 4), fill="white")

    # Draw bullets
    for bullet in player_bullets: draw.rectangle((bullet[0], bullet[1], bullet[0] + 1, bullet[1] + 3), fill="white")
    for bullet in alien_bullets: draw.rectangle((bullet[0], bullet[1], bullet[0] + 1, bullet[1] + 3), fill="white")

    # Draw UI
    draw.text((2, 0), f"Score: {score}", fill="white")
    draw.text((device.width - 20, 0), f"L: {lives}", fill="white")
