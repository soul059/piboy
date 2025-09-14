import time
import random

# Game state
device = None
player_pos = [0, 0]
lives = 0
score = 0
game_over = False
homes = [] # Positions of filled homes

# Config
STEP_Y = 8
PLAYER_SIZE = 6
LANES = [
    {'type': 'road', 'speed': 1, 'objects': []}, # y = 56
    {'type': 'road', 'speed': -1.5, 'objects': []}, # y = 48
    {'type': 'road', 'speed': 2, 'objects': []}, # y = 40
    {'type': 'safe'}, # y = 32 (middle bank)
    {'type': 'river', 'speed': -1, 'objects': []}, # y = 24
    {'type': 'river', 'speed': 1.5, 'objects': []}, # y = 16
    {'type': 'river', 'speed': -2, 'objects': []}  # y = 8
]

def init(d):
    global device, lives, score, game_over, homes
    device = d
    lives = 3
    score = 0
    game_over = False
    homes = []
    _reset_player()
    _init_lanes()

def _init_lanes():
    for i, lane in enumerate(LANES):
        if lane['type'] != 'safe':
            lane['objects'] = []
            y = 56 - i * STEP_Y
            for _ in range(random.randint(2, 4)):
                x = random.randint(0, device.width)
                width = random.randint(20, 40)
                lane['objects'].append([x, y, width])

def _reset_player():
    global player_pos
    player_pos = [device.width // 2, 56]

def handle_input(key):
    global player_pos
    if game_over:
        if key == 'START': init(device)
        elif key == 'SELECT': return False
        return True

    if key == 'W': player_pos[1] -= STEP_Y
    elif key == 'S': player_pos[1] += STEP_Y
    elif key == 'A_LEFT': player_pos[0] -= 8
    elif key == 'D': player_pos[0] += 8
    elif key == 'SELECT': return False

    if player_pos[0] < 0: player_pos[0] = 0
    if player_pos[0] > device.width - PLAYER_SIZE: player_pos[0] = device.width - PLAYER_SIZE
    if player_pos[1] > 56: player_pos[1] = 56
    return True

def _update_game_state():
    global player_pos, lives, score, game_over

    # Move objects in lanes
    for lane in LANES:
        if lane['type'] != 'safe':
            for obj in lane['objects']:
                obj[0] += lane['speed']
                if obj[0] > device.width: obj[0] = -obj[2]
                elif obj[0] < -obj[2]: obj[0] = device.width

    # Check player status
    lane_index = (56 - player_pos[1]) // STEP_Y
    if not (0 <= lane_index < len(LANES)):
        _lose_life()
        return

    current_lane = LANES[lane_index]
    on_object = False
    if current_lane['type'] == 'road':
        for obj in current_lane['objects']:
            if obj[0] < player_pos[0] < obj[0] + obj[2]:
                _lose_life()
                return
    elif current_lane['type'] == 'river':
        for obj in current_lane['objects']:
            if obj[0] < player_pos[0] < obj[0] + obj[2]:
                on_object = True
                player_pos[0] += current_lane['speed']
                break
        if not on_object:
            _lose_life()
            return

    # Check for reaching home
    if player_pos[1] <= 0:
        score += 100
        homes.append(list(player_pos))
        _reset_player()
        if len(homes) >= 5: # Win condition
            score += 1000
            init(device)

def _lose_life():
    global lives, game_over
    lives -= 1
    if lives <= 0:
        game_over = True
    else:
        _reset_player()

def draw(draw):
    if not game_over: _update_game_state()

    draw.rectangle(device.bounding_box, outline="black", fill="black")

    if game_over:
        draw.text((20, 20), "GAME OVER", fill="white")
        draw.text((20, 35), f"Score: {score}", fill="white")
        return

    # Draw lanes and objects
    for lane in LANES:
        if lane['type'] != 'safe':
            for obj in lane['objects']:
                draw.rectangle((obj[0], obj[1], obj[0] + obj[2], obj[1] + PLAYER_SIZE), fill="white")

    # Draw player
    draw.rectangle((player_pos[0], player_pos[1], player_pos[0] + PLAYER_SIZE, player_pos[1] + PLAYER_SIZE), fill="white")

    # Draw homes
    for home in homes:
        draw.rectangle((home[0], 0, home[0] + PLAYER_SIZE, PLAYER_SIZE), fill="white")

    # Draw UI
    draw.text((2, 0), f"S:{score}", fill="white")
    draw.text((device.width - 20, 0), f"L:{lives}", fill="white")
