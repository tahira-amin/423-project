from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math


from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18
from OpenGL.GLUT import GLUT_BITMAP_TIMES_ROMAN_24
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_12
from OpenGL.GLUT import GLUT_BITMAP_9_BY_15


# Camera variables
camera_pos = [0, -800, 400]
camera_angle = 0
camera_mode = "static"  # "static" or "free"
camera_distance = 600

# Game state
game_state = "menu"  # "menu", "mode_select", "element_select", "level_select", "playing", "game_over"
game_mode = "pvp"  # "pvp" or "pvai"
current_turn = 1  # 1 or 2
phase = "attack"  # "attack", "defend", "resolution"
winner = 0
round_number = 1
level = "easy"  # "easy", "medium", "hard"

# AI variables
ai_decision_timer = 0
ai_reaction_delay = 0.8  # Current reaction delay for defense (randomized per attack)
ai_executing = False

# Player data
player1 = {
    "element": None,
    "hp": 100,
    "st": 0,
    "pos": [0, -400, 30],
    "color": [1, 0, 0],
    "status": None,
    "status_rounds": 0,
    "stun_original_hp": None,
    "attack_type": "basic",
    "move_speed": 40,
    "jump_height": 0,
    "vel": 0
}

player2 = {
    "element": None,
    "hp": 100,
    "st": 0,
    "pos": [0, 400, 30],
    "color": [0, 0, 1],
    "status": None,
    "status_rounds": 0,
    "stun_original_hp": None,
    "attack_type": "basic",
    "move_speed": 40,
    "jump_height": 0,
    "vel": 0,
    "ai_target_x": None,
    "ai_moving": False
}

# Element colors and names
element_colors = {
    "FIR": [1.0, 0.2, 0.0],    # Fire - Red
    "WTR": [0.0, 0.4, 1.0],    # Water - Blue
    "ELC": [1.0, 1.0, 0.0],    # Electric - Yellow
    "ERT": [0.2, 0.8, 0.2],    # Earth - Green
    "WND": [0.6, 0.6, 0.6],    # Wind - Grey
    "ICE": [0.0, 1.0, 1.0]     # Ice - Cyan
}

element_names = {
    "FIR": "Fire", "WTR": "Water", "ELC": "Electric",
    "ERT": "Earth", "WND": "Wind", "ICE": "Ice"
}

# Crosshair variables
crosshair_pos = 0
crosshair_direction = 1
crosshair_speed = 200  # Units per second
crosshair_visible = True
crosshair_timer = 0
crosshair_size = 40

# Attack variables
active_attack = None
pending_attack_data = None  # Stores attack data during delay period
attack_travel_time = 0
attack_progress = 0
last_time = 0

# Timing variables
defend_timer = 0
attack_timer = 0
pause = False
attack_fire_delay = 0  # Delay before attack fires after camera switch
attack_ready = False  # Whether attack is ready to move

# Popup message variables
popup_message = ""
popup_timer = 0
popup_duration = 2.0  # Display for 2 seconds

# Game over animation variables
game_over_animation = False
game_over_timer = 0
game_over_duration = 3.0  # 3 seconds of animation before showing final screen
loser_rotation = 0  # Rotation angle for falling animation
game_over_camera_angle = 0  # Orbiting camera angle for game over state
winner_jump_cycle = 0  # Winner celebration jump cycle

# Camera animation variables
camera_animating = False
camera_anim_progress = 0
camera_anim_duration = 1.0  # 1 second animation
camera_start_y = 0
camera_target_y = 0
camera_start_look_y = 0
camera_target_look_y = 0

# Arena bounds
ARENA_WIDTH = 350
ARENA_LENGTH = 450

# Danger zone (medium difficulty)
danger_zone_x = 0  # Center X position of danger zone
danger_zone_width = 120  # Width of danger zone
danger_zone_timer = 0  # Time spent in danger zone

# Watchtower (hard difficulty)
active_watchtower = None  # "left" or "right"
watchtower_bullet = None  # Active bullet from watchtower
watchtower_bullet_progress = 0
watchtower_bullet2 = None  # Second bullet from non-active watchtower
watchtower_bullet2_progress = 0
watchtower_cooldown = 0  # Cooldown between shots
watchtower_sequence_active = False  # Whether the two-shot sequence is running
watchtower_order = []  # Firing order of towers ["left", "right"] randomized each turn
watchtower_next_index = 0  # Index into watchtower_order for next shot
watchtower_fire_delay = 0  # Countdown to next tower firing
watchtower_telegraph_time = 0.8  # Seconds to charge (blue->red) before firing

# Menu background AI battle (decorative only - does not affect gameplay)
menu_bg_player1 = {
    "element": "FIR",
    "hp": 100,
    "st": 0,
    "pos": [0, -300, 30],
    "color": [1, 0.2, 0],
    "status": None,
    "status_rounds": 0,
    "attack_type": "basic",
    "move_speed": 40,
    "jump_height": 0,
    "vel": 0
}

menu_bg_player2 = {
    "element": "ICE",
    "hp": 100,
    "st": 0,
    "pos": [0, 300, 30],
    "color": [0, 1, 1],
    "status": None,
    "status_rounds": 0,
    "attack_type": "basic",
    "move_speed": 40,
    "jump_height": 0,
    "vel": 0
}

menu_bg_attack = None  # Active attack in menu background
menu_bg_attack_progress = 0
menu_bg_current_turn = 1  # Which AI is attacking in menu
menu_bg_phase = "attack"  # "attack" or "defend"
menu_bg_attack_timer = 0
menu_bg_defend_timer = 0
menu_camera_angle = 0  # Orbiting camera angle for menu

def initialize_game():
    """Reset game to initial state"""
    global player1, player2, game_state, current_turn, active_attack, winner
    global round_number, phase, danger_zone_timer
    global active_watchtower, watchtower_bullet, watchtower_bullet2, watchtower_cooldown
    global ai_decision_timer, ai_executing
    global game_over_animation, game_over_timer, loser_rotation, game_over_camera_angle, winner_jump_cycle
    
    player1["hp"] = 100
    player1["st"] = 0
    player1["pos"] = [0, -400, 30]
    player1["status"] = None
    player1["status_rounds"] = 0
    player1["attack_type"] = "basic"
    player1["move_speed"] = 40
    player1["jump_height"] = 0
    player1["vel"] = 0
    
    player2["hp"] = 100
    player2["st"] = 0
    player2["pos"] = [0, 400, 30]
    player2["status"] = None
    player2["status_rounds"] = 0
    player2["attack_type"] = "basic"
    player2["move_speed"] = 40
    player2["jump_height"] = 0
    player2["vel"] = 0
    player2["ai_target_x"] = None
    player2["ai_moving"] = False
    
    # In AI mode, player 1 always goes first
    if game_mode == "pvai":
        current_turn = 1
    else:
        current_turn = random.randint(1, 2)
    
    active_attack = None
    winner = 0
    round_number = 1
    phase = "attack"
    game_state = "playing"
    danger_zone_timer = 0
    active_watchtower = None
    watchtower_bullet = None
    watchtower_bullet2 = None
    watchtower_cooldown = 0
    watchtower_sequence_active = False
    watchtower_order = []
    watchtower_next_index = 0
    watchtower_fire_delay = 0
    ai_decision_timer = 0
    ai_executing = False
    game_over_animation = False
    game_over_timer = 0
    loser_rotation = 0
    game_over_camera_angle = 0
    winner_jump_cycle = 0
    reset_crosshair()
    
    # Initialize danger zone for medium difficulty
    if level == "medium":
        randomize_danger_zone()

def randomize_danger_zone():
    """Randomize danger zone position for medium difficulty"""
    global danger_zone_x
    
    if level != "medium":
        return
    
    # Random position along X axis, avoiding edges
    max_x = ARENA_WIDTH - danger_zone_width / 2 - 30
    min_x = -ARENA_WIDTH + danger_zone_width / 2 + 30
    danger_zone_x = random.uniform(min_x, max_x)
    print(f"Danger zone positioned at X={danger_zone_x:.1f}")

def reset_crosshair():
    """Reset crosshair to initial state"""
    global crosshair_pos, crosshair_direction, crosshair_visible, crosshair_timer
    global crosshair_size
    
    crosshair_pos = 0
    crosshair_direction = 1
    crosshair_visible = True
    crosshair_timer = 0
    
    attacker = player1 if current_turn == 1 else player2
    if attacker["attack_type"] == "basic":
        crosshair_size = 20
    elif attacker["attack_type"] == "signature":
        crosshair_size = 30
    else:
        crosshair_size = 60

def draw_dimming_overlay():
    """Draw semi-transparent overlay for menu text readability"""
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Enable blending for transparency
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    # Draw semi-transparent black overlay (70% opacity)
    glColor4f(0.0, 0.0, 0.0, 0.7)
    glBegin(GL_QUADS)
    glVertex2f(0, 0)
    glVertex2f(1000, 0)
    glVertex2f(1000, 800)
    glVertex2f(0, 800)
    glEnd()
    
    glDisable(GL_BLEND)
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_bar(x, y, width, height, fill_percentage, color):
    """Draw a filled bar for HP/ST display"""
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Draw border
    glColor3f(1, 1, 1)
    glBegin(GL_LINE_LOOP)
    glVertex2f(x, y)
    glVertex2f(x + width, y)
    glVertex2f(x + width, y + height)
    glVertex2f(x, y + height)
    glEnd()
    
    # Draw filled portion
    fill_width = width * max(0, min(1, fill_percentage))
    glColor3f(color[0], color[1], color[2])
    glBegin(GL_QUADS)
    glVertex2f(x, y)
    glVertex2f(x + fill_width, y)
    glVertex2f(x + fill_width, y + height)
    glVertex2f(x, y + height)
    glEnd()
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_text(x, y, text, font=None):
    """Draw text on screen"""
    if font is None:
        font = GLUT_BITMAP_HELVETICA_18
    
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_popup():
    """Draw popup message at top of screen"""
    global popup_message, popup_timer
    
    if popup_message and popup_timer < popup_duration:
        # Calculate fade effect based on time
        alpha = 1.0
        if popup_timer > popup_duration - 0.5:  # Fade out in last 0.5 seconds
            alpha = (popup_duration - popup_timer) / 0.5
        
        # Draw popup at top of screen
        glColor3f(1.0 * alpha, 0.8 * alpha, 0.0)  # Yellow-orange color
        draw_text(340, 720, popup_message, GLUT_BITMAP_TIMES_ROMAN_24)

def draw_watchtowers():
    """Draw watchtowers for hard difficulty (only in PvP mode)"""
    if level != "hard" or game_mode == "pvai":
        return
    
    tower_radius = 15
    tower_height = 100
    tower_color = [0.3, 0.3, 0.3]  # Dark grey
    
    # Left watchtower
    glPushMatrix()
    glTranslatef(-ARENA_WIDTH, 0, 0)
    glColor3f(tower_color[0], tower_color[1], tower_color[2])
    quadric = gluNewQuadric()
    gluCylinder(quadric, tower_radius, tower_radius, tower_height, 20, 20)
    # Cap on top
    glTranslatef(0, 0, tower_height)
    gluDisk(quadric, 0, tower_radius, 20, 1)
    glPopMatrix()
    
    # Right watchtower
    glPushMatrix()
    glTranslatef(ARENA_WIDTH, 0, 0)
    glColor3f(tower_color[0], tower_color[1], tower_color[2])
    quadric = gluNewQuadric()
    gluCylinder(quadric, tower_radius, tower_radius, tower_height, 20, 20)
    # Cap on top
    glTranslatef(0, 0, tower_height)
    gluDisk(quadric, 0, tower_radius, 20, 1)
    glPopMatrix()

    # Laser sights track defender during defend phase in PvP hard
    if (game_state == "playing" and phase == "defend" and level == "hard" and game_mode == "pvp" and watchtower_sequence_active):
        defender = player2 if current_turn == 1 else player1
        next_tower = watchtower_order[watchtower_next_index] if watchtower_next_index < len(watchtower_order) else None
        base_blue = (0.0, 0.6, 1.0)
        for side in ["left", "right"]:
            tower_x = -ARENA_WIDTH if side == "left" else ARENA_WIDTH
            tower_y = 0
            tower_z = 80
            # Charge color: blue -> red as timer approaches fire
            ratio = 0.0
            if side == next_tower and watchtower_fire_delay <= watchtower_telegraph_time:
                ratio = max(0.0, min(1.0, 1.0 - (watchtower_fire_delay / watchtower_telegraph_time)))
            color_r = base_blue[0] * (1 - ratio) + 1.0 * ratio
            color_g = base_blue[1] * (1 - ratio) + 0.0 * ratio
            color_b = base_blue[2] * (1 - ratio) + 0.0 * ratio
            glColor3f(color_r, color_g, color_b)
            glBegin(GL_LINES)
            glVertex3f(tower_x, tower_y, tower_z)
            glVertex3f(defender["pos"][0], defender["pos"][1], defender["pos"][2] + 10)
            glEnd()
    
    # Highlight active tower with red glow
    if phase == "defend" and active_watchtower:
        glPushMatrix()
        if active_watchtower == "left":
            glTranslatef(-ARENA_WIDTH, 0, tower_height - 10)
        else:
            glTranslatef(ARENA_WIDTH, 0, tower_height - 10)
        glColor3f(1.0, 0.0, 0.0)  # Red glow
        gluSphere(gluNewQuadric(), tower_radius * 0.8, 16, 16)
        glPopMatrix()

def draw_watchtower_bullet(bullet):
    """Draw bullet from watchtower"""
    if bullet is None:
        return
    
    glPushMatrix()
    glTranslatef(bullet["x"], bullet["y"], bullet["z"])
    
    # Calculate direction to face target
    dx = bullet["target_x"] - bullet["start_x"]
    dy = bullet["target_y"] - bullet["start_y"]
    dz = bullet["target_z"] - bullet["start_z"]
    
    # Draw as small red sphere
    glColor3f(1.0, 0.2, 0.0)  # Bright red
    gluSphere(gluNewQuadric(), 8, 12, 12)
    
    # Add trail effect
    glColor3f(1.0, 0.5, 0.0)  # Orange trail
    gluSphere(gluNewQuadric(), 5, 8, 8)
    
    glPopMatrix()

def draw_danger_zone():
    """Draw the danger zone square for medium difficulty"""
    if level != "medium":
        return
    
    # Determine defender's side based on current turn
    # During attack phase: next turn's player will defend
    # During defend phase: current opponent is defending
    if phase == "attack":
        defender_side_y = 400 if current_turn == 1 else -400
    else:  # defend phase
        defender_side_y = 400 if current_turn == 1 else -400
    
    # Draw white square on the ground at defender's side (fixed Y position)
    half_width = danger_zone_width / 2
    zone_depth = 100  # Depth along Y axis
    
    # Main white square
    glBegin(GL_QUADS)
    glColor3f(1.0, 1.0, 1.0)  # Pure white for better visibility
    
    glVertex3f(danger_zone_x - half_width, defender_side_y - zone_depth/2, 3)
    glVertex3f(danger_zone_x + half_width, defender_side_y - zone_depth/2, 3)
    glVertex3f(danger_zone_x + half_width, defender_side_y + zone_depth/2, 3)
    glVertex3f(danger_zone_x - half_width, defender_side_y + zone_depth/2, 3)
    glEnd()

def draw_arena():
    """Draw the 3D arena with tennis court style"""
    # Player 1 side (red/brown court at bottom)
    glBegin(GL_QUADS)
    glColor3f(0.6, 0.2, 0.2)  # Red-brown color
    glVertex3f(-ARENA_WIDTH, -ARENA_LENGTH, 0)
    glVertex3f(ARENA_WIDTH, -ARENA_LENGTH, 0)
    glVertex3f(ARENA_WIDTH, 0, 0)
    glVertex3f(-ARENA_WIDTH, 0, 0)
    glEnd()
    
    # Player 2 side (purple/blue court at top)
    glBegin(GL_QUADS)
    glColor3f(0.4, 0.3, 0.7)  # Purple-blue color
    glVertex3f(-ARENA_WIDTH, 0, 0)
    glVertex3f(ARENA_WIDTH, 0, 0)
    glVertex3f(ARENA_WIDTH, ARENA_LENGTH, 0)
    glVertex3f(-ARENA_WIDTH, ARENA_LENGTH, 0)
    glEnd()
    
    # Player 1 boundary area (light gray)
    glBegin(GL_QUADS)
    glColor3f(0.7, 0.7, 0.75)
    glVertex3f(-ARENA_WIDTH, -ARENA_LENGTH - 50, 0)
    glVertex3f(ARENA_WIDTH, -ARENA_LENGTH - 50, 0)
    glVertex3f(ARENA_WIDTH, -ARENA_LENGTH, 0)
    glVertex3f(-ARENA_WIDTH, -ARENA_LENGTH, 0)
    glEnd()
    
    # Player 2 boundary area (light gray)
    glBegin(GL_QUADS)
    glColor3f(0.7, 0.7, 0.75)
    glVertex3f(-ARENA_WIDTH, ARENA_LENGTH, 0)
    glVertex3f(ARENA_WIDTH, ARENA_LENGTH, 0)
    glVertex3f(ARENA_WIDTH, ARENA_LENGTH + 50, 0)
    glVertex3f(-ARENA_WIDTH, ARENA_LENGTH + 50, 0)
    glEnd()
    
    # Center divider (white barrier/net)
    glBegin(GL_QUADS)
    glColor3f(0.9, 0.9, 0.9)  # White
    glVertex3f(-ARENA_WIDTH, -10, 0)
    glVertex3f(ARENA_WIDTH, -10, 0)
    glVertex3f(ARENA_WIDTH, 10, 0)
    glVertex3f(-ARENA_WIDTH, 10, 0)
    glEnd()
    
    # Net/barrier vertical segments (white pillars on net)
    glColor3f(0.85, 0.85, 0.85)
    segment_width = ARENA_WIDTH * 2 / 10
    for i in range(11):
        x_pos = -ARENA_WIDTH + i * segment_width
        glPushMatrix()
        glTranslatef(x_pos, 0, 0)
        glScalef(segment_width * 0.15, 20, 30)
        glutSolidCube(1)
        glPopMatrix()
    
    # Boundary walls (outer perimeter)
    glBegin(GL_QUADS)
    glColor3f(0.5, 0.5, 0.55)
    
    # Back wall (player 1 side)
    glVertex3f(-ARENA_WIDTH, -ARENA_LENGTH - 50, 0)
    glVertex3f(ARENA_WIDTH, -ARENA_LENGTH - 50, 0)
    glVertex3f(ARENA_WIDTH, -ARENA_LENGTH - 50, 100)
    glVertex3f(-ARENA_WIDTH, -ARENA_LENGTH - 50, 100)
    
    # Front wall (player 2 side)
    glVertex3f(-ARENA_WIDTH, ARENA_LENGTH + 50, 0)
    glVertex3f(ARENA_WIDTH, ARENA_LENGTH + 50, 0)
    glVertex3f(ARENA_WIDTH, ARENA_LENGTH + 50, 100)
    glVertex3f(-ARENA_WIDTH, ARENA_LENGTH + 50, 100)
    
    # Left wall
    glVertex3f(-ARENA_WIDTH, -ARENA_LENGTH - 50, 0)
    glVertex3f(-ARENA_WIDTH, ARENA_LENGTH + 50, 0)
    glVertex3f(-ARENA_WIDTH, ARENA_LENGTH + 50, 100)
    glVertex3f(-ARENA_WIDTH, -ARENA_LENGTH - 50, 100)
    
    # Right wall
    glVertex3f(ARENA_WIDTH, -ARENA_LENGTH - 50, 0)
    glVertex3f(ARENA_WIDTH, ARENA_LENGTH + 50, 0)
    glVertex3f(ARENA_WIDTH, ARENA_LENGTH + 50, 100)
    glVertex3f(ARENA_WIDTH, -ARENA_LENGTH - 50, 100)
    glEnd()

def draw_player(player):
    """Draw a player as a large sphere"""
    glPushMatrix()
    
    # Calculate jump offset for winner celebration
    jump_offset = 0
    if game_state == "game_over" and game_over_animation:
        winner_player = player1 if winner == 1 else player2
        if player == winner_player:
            # Winner jumps continuously with smooth sine wave
            jump_offset = abs(math.sin(winner_jump_cycle)) * 60
    
    glTranslatef(player["pos"][0], player["pos"][1], player["pos"][2] + player["jump_height"] + jump_offset)
    
    # Apply rotation if this is the loser during game over animation
    if game_state == "game_over" and game_over_animation:
        loser = player2 if winner == 1 else player1
        if player == loser:
            glRotatef(loser_rotation, 0, 1, 0)  # Rotate around Y-axis to fall sideways
    
    # Main body sphere
    glColor3f(player["color"][0], player["color"][1], player["color"][2])
    gluSphere(gluNewQuadric(), 30, 32, 32)
    
    # Lighter top hemisphere (head) for detail
    glColor3f(
        min(1, player["color"][0] + 0.3),
        min(1, player["color"][1] + 0.3),
        min(1, player["color"][2] + 0.3)
    )
    glPushMatrix()
    glTranslatef(0, 0, 40)
    gluSphere(gluNewQuadric(), 18, 32, 32)
    
    # Face features - facing toward arena center (negative Y for player 1, positive Y for player 2)
    # Determine which direction the player faces based on their Y position
    face_direction = 1 if player["pos"][1] < 0 else -1
    
    # Left eye (white)
    glPushMatrix()
    glTranslatef(-6, face_direction * 14, 3)
    glColor3f(1, 1, 1)
    gluSphere(gluNewQuadric(), 4, 16, 16)
    # Left pupil (black)
    glTranslatef(-1, face_direction * 2, 3)
    glColor3f(0, 0, 0)
    gluSphere(gluNewQuadric(), 2, 16, 16)
    glPopMatrix()
    
    # Right eye (white)
    glPushMatrix()
    glTranslatef(6, face_direction * 14, 3)
    glColor3f(1, 1, 1)
    gluSphere(gluNewQuadric(), 4, 16, 16)
    # Right pupil (black)
    glTranslatef(1, face_direction * 2, 3)
    glColor3f(0, 0, 0)
    gluSphere(gluNewQuadric(), 2, 16, 16)
    glPopMatrix()
    
    # Mouth (white rounded rectangle)
    glPushMatrix()
    glTranslatef(0, face_direction * 14, -5)
    glColor3f(1, 1, 1)
    glScalef(1.5, 1, 0.8)
    gluSphere(gluNewQuadric(), 3, 16, 16)
    glPopMatrix()
    
    # Small purple accent (nose/tongue)
    glPushMatrix()
    glTranslatef(0, face_direction * 16, -6)
    glColor3f(0.6, 0.3, 1.0)
    gluSphere(gluNewQuadric(), 1.5, 16, 16)
    glPopMatrix()
    
    glPopMatrix()
    
    glPopMatrix()

def draw_crosshair():
    """Draw aiming crosshair on opponent's side"""
    if not crosshair_visible:
        return
    
    attacker = player1 if current_turn == 1 else player2
    defender_side_y = 400 if current_turn == 1 else -400
    
    # Draw crosshair at ground level on opponent's side
    glPushMatrix()
    glTranslatef(crosshair_pos, defender_side_y, 5)
    
    glColor3f(1, 0, 0)
    
    if attacker["attack_type"] == "ultimate":
        # Large circle for ultimate
        glBegin(GL_LINE_LOOP)
        segments = 30
        for i in range(segments):
            angle = 2 * math.pi * i / segments
            x = crosshair_size * 2 * math.cos(angle)
            y = crosshair_size * 2 * math.sin(angle)
            glVertex3f(x, y, 0)
        glEnd()
        
        # Inner circle
        glBegin(GL_LINE_LOOP)
        for i in range(segments):
            angle = 2 * math.pi * i / segments
            x = crosshair_size * math.cos(angle)
            y = crosshair_size * math.sin(angle)
            glVertex3f(x, y, 0)
        glEnd()
    else:
        # Crosshair lines
        glBegin(GL_LINES)
        glVertex3f(-crosshair_size, 0, 0)
        glVertex3f(crosshair_size, 0, 0)
        glVertex3f(0, -crosshair_size, 0)
        glVertex3f(0, crosshair_size, 0)
        glEnd()
        
        # Circle
        glBegin(GL_LINE_LOOP)
        segments = 20
        for i in range(segments):
            angle = 2 * math.pi * i / segments
            x = crosshair_size * 0.8 * math.cos(angle)
            y = crosshair_size * 0.8 * math.sin(angle)
            glVertex3f(x, y, 0)
        glEnd()
    
    glPopMatrix()

def get_projectile_angles(attack, t):
    """
    Calculates direction (Z-rotation) and angle (Y-rotation) to align 
    projectile with its velocity vector along the arc.
    """
    # Look ahead factor (delta t)
    dt = 0.05
    future_t = min(1.0, t + dt)
    
    # Current Position (Linear XY, Arc Z)
    cur_x = attack["start_x"] + (attack["target_x"] - attack["start_x"]) * t
    cur_y = attack["start_y"] + (attack["target_y"] - attack["start_y"]) * t
    
    # Future Position
    fut_x = attack["start_x"] + (attack["target_x"] - attack["start_x"]) * future_t
    fut_y = attack["start_y"] + (attack["target_y"] - attack["start_y"]) * future_t
    
    # Calculate Z height based on attack type
    if attack["type"] == "signature":
        # Arc formula: H * sin(pi * t)
        cur_z = attack["start_z"] + 60 * math.sin(t * math.pi)
        fut_z = attack["start_z"] + 60 * math.sin(future_t * math.pi)
    else:
        cur_z = attack["z"]
        fut_z = attack["z"]
    
    # Velocity Vector components
    dx = fut_x - cur_x
    dy = fut_y - cur_y
    dz = fut_z - cur_z
    
    # Calculate direction (Angle on ground)
    # math.atan2(y, x) gives angle from X-axis. 
    # We convert to degrees.
    direction = math.degrees(math.atan2(dy, dx))
    
    # Calculate angle (Angle from ground up/down)
    # We need the horizontal magnitude to compare Z against.
    horiz_dist = math.sqrt(dx*dx + dy*dy)
    angle = math.degrees(math.atan2(dz, horiz_dist))
    
    return direction, angle

def draw_attack(attack):
    """Draw active attack projectile with NEW projection but OLD aesthetics"""
    if attack is None:
        return
    
    element = attack["element"]
    color = element_colors.get(element, [1, 1, 1])
    
    # Calculate progress 't' for the angle calculation
    dx_total = attack["target_x"] - attack["start_x"]
    dy_total = attack["target_y"] - attack["start_y"]
    dist_total = math.sqrt(dx_total**2 + dy_total**2)
    
    dx_curr = attack["x"] - attack["start_x"]
    dy_curr = attack["y"] - attack["start_y"]
    dist_curr = math.sqrt(dx_curr**2 + dy_curr**2)
    
    if dist_total > 0:
        t = dist_curr / dist_total
    else:
        t = 0
        
    # Get the 3D angles
    direction, angle = get_projectile_angles(attack, t)
    
    glPushMatrix()
    glTranslatef(attack["x"], attack["y"], attack["z"])
    
    # --- APPLY NEW PROJECTION ---
    glRotatef(direction, 0, 0, 1)      # Face target
    glRotatef(-angle, 0, 1, 0)   # Face up/down along arc
    
    # --- ALIGNMENT FIX ---
    # Your original models were drawn pointing along the Y-axis (Up/North).
    # The math above points along the X-axis (Forward/East).
    # We rotate -90 degrees on Z to align the models with the direction.
    glRotatef(-90, 0, 0, 1)
    
    # --- ORIGINAL AESTHETICS BELOW ---
    
    if attack["type"] == "basic":
        # Three triangle-shaped quads, one in front of the other
        triangle_configs = [
            {"y_offset": 0, "width": 50, "height": 30, "brightness": 1.0},      # Largest
            {"y_offset": 35, "width": 38, "height": 22, "brightness": 0.8},     # Medium
            {"y_offset": 65, "width": 28, "height": 15, "brightness": 0.6}      # Smallest
        ]
        
        for config in triangle_configs:
            glPushMatrix()
            # Note: We use negative offset here because your original code 
            # pushed them "back" relative to movement
            glTranslatef(0, config["y_offset"], 0)
            
            tip_y = config["height"]
            base_y = -config["height"]
            width = config["width"]
            thickness = 8
            
            glColor3f(color[0] * config["brightness"], color[1] * config["brightness"], color[2] * config["brightness"])
            
            glBegin(GL_QUADS)
            
            # Top face
            glVertex3f(0, tip_y, thickness/2)
            glVertex3f(-width/2, base_y, thickness/2)
            glVertex3f(width/2, base_y, thickness/2)
            glVertex3f(0, tip_y, thickness/2)
            
            # Bottom face
            glVertex3f(0, tip_y, -thickness/2)
            glVertex3f(width/2, base_y, -thickness/2)
            glVertex3f(-width/2, base_y, -thickness/2)
            glVertex3f(0, tip_y, -thickness/2)
            
            # Front face
            glVertex3f(0, tip_y, thickness/2)
            glVertex3f(0, tip_y, -thickness/2)
            glVertex3f(0, tip_y, -thickness/2)
            glVertex3f(0, tip_y, thickness/2)
            
            # Left side
            glVertex3f(0, tip_y, thickness/2)
            glVertex3f(0, tip_y, -thickness/2)
            glVertex3f(-width/2, base_y, -thickness/2)
            glVertex3f(-width/2, base_y, thickness/2)
            
            # Right side
            glVertex3f(0, tip_y, thickness/2)
            glVertex3f(0, tip_y, -thickness/2)
            glVertex3f(width/2, base_y, -thickness/2)
            glVertex3f(width/2, base_y, thickness/2)
            
            # Back face
            glVertex3f(-width/2, base_y, thickness/2)
            glVertex3f(width/2, base_y, thickness/2)
            glVertex3f(width/2, base_y, -thickness/2)
            glVertex3f(-width/2, base_y, -thickness/2)
            
            glEnd()
            glPopMatrix()
        
    elif attack["type"] == "signature":
        # Fireball with spheres in front of one another
        sphere_configs = [
            {"y_offset": 0, "radius": 28, "brightness": 1.0},      # Largest (front)
            {"y_offset": -30, "radius": 24, "brightness": 0.85},   # Medium-large
            {"y_offset": -55, "radius": 18, "brightness": 0.7},    # Medium-small
            {"y_offset": -75, "radius": 12, "brightness": 0.55}    # Smallest (back)
        ]
        
        for config in sphere_configs:
            glPushMatrix()
            glTranslatef(0, config["y_offset"], 0)
            glColor3f(color[0] * config["brightness"], color[1] * config["brightness"], color[2] * config["brightness"])
            gluSphere(gluNewQuadric(), config["radius"], 20, 20)
            glPopMatrix()
        
    elif attack["type"] == "ultimate":
        # Three tapered quads (narrow at front, wider at back)
        rect_configs = [
            {"y_offset": 0, "width": 180, "depth": 100, "height": 25, "brightness": 1.0},     # Largest
            {"y_offset": 50, "width": 140, "depth": 80, "height": 20, "brightness": 0.75},    # Medium
            {"y_offset": 90, "width": 100, "depth": 60, "height": 15, "brightness": 0.5}      # Smallest
        ]
        
        for config in rect_configs:
            glPushMatrix()
            glTranslatef(0, config["y_offset"], 0)
            
            w_back = config["width"] / 2      # Back width 
            w_front = config["width"] / 3     # Front width narrower
            d = config["depth"] / 2
            h = config["height"]
            
            glColor3f(color[0] * config["brightness"], color[1] * config["brightness"], color[2] * config["brightness"])
            
            glBegin(GL_QUADS)
            
            # Top face (tapered)
            glVertex3f(-w_back, -d, h)
            glVertex3f(w_back, -d, h)
            glVertex3f(w_front, d, h)
            glVertex3f(-w_front, d, h)
            
            # Bottom face (tapered)
            glVertex3f(-w_back, -d, 0)
            glVertex3f(w_back, -d, 0)
            glVertex3f(w_front, d, 0)
            glVertex3f(-w_front, d, 0)
            
            # Front face (narrow end)
            glVertex3f(-w_front, d, 0)
            glVertex3f(w_front, d, 0)
            glVertex3f(w_front, d, h)
            glVertex3f(-w_front, d, h)
            
            # Back face (wide end)
            glVertex3f(-w_back, -d, 0)
            glVertex3f(w_back, -d, 0)
            glVertex3f(w_back, -d, h)
            glVertex3f(-w_back, -d, h)
            
            # Left face (tapered)
            glVertex3f(-w_back, -d, 0)
            glVertex3f(-w_front, d, 0)
            glVertex3f(-w_front, d, h)
            glVertex3f(-w_back, -d, h)
            
            # Right face (tapered)
            glVertex3f(w_back, -d, 0)
            glVertex3f(w_front, d, 0)
            glVertex3f(w_front, d, h)
            glVertex3f(w_back, -d, h)
            
            glEnd()
            glPopMatrix()
    
    glPopMatrix()

def fire_attack():
    """Launch an attack from attacker to defender"""
    global active_attack, attack_travel_time, phase, defend_timer, attack_progress
    
    if phase != "attack":
        return
    
    attacker = player1 if current_turn == 1 else player2
    defender = player2 if current_turn == 1 else player1
    
    # Check stamina
    cost = 0
    if attacker["attack_type"] == "signature":
        cost = 20
    elif attacker["attack_type"] == "ultimate":
        cost = 100
    
    if attacker["st"] < cost:
        print(f"Not enough stamina! Need {cost}, have {attacker['st']}")
        return
    
    # Deduct stamina
    attacker["st"] -= cost
    
    # Determine target position
    target_x = crosshair_pos
    target_y = defender["pos"][1]
    
    # Apply Imbalance effect - random deviation to trajectory (50% accuracy reduction)
    if attacker["status"] == "IMBL":
        # Random deviation of ±150 pixels for 50% accuracy reduction
        imbalance_deviation = random.uniform(-150, 150)
        target_x += imbalance_deviation
        print(f"Imbalance effect: trajectory deviated by {imbalance_deviation:.1f}")
    
    # Calculate spawn offset distance from player body (spawn in front of middle body)
    body_radius = 30  # Player body sphere radius
    spawn_offset = body_radius + 40  # Spawn 40 units in front of body edge
    
    # Calculate direction vector from attacker to target
    dx = target_x - attacker["pos"][0]
    dy = target_y - attacker["pos"][1]
    distance = math.sqrt(dx*dx + dy*dy)
    
    # Normalize direction
    if distance > 0:
        dx /= distance
        dy /= distance
    else:
        # Default direction if target is directly on attacker
        dy = 1 if current_turn == 1 else -1
        dx = 0
    
    # Calculate spawn position in front of attacker body
    start_x = float(attacker["pos"][0]) + dx * spawn_offset
    start_y = float(attacker["pos"][1]) + dy * spawn_offset
    start_z = 50.0
    target_z = 50.0
    
    # Store attack data to spawn after delay
    global pending_attack_data
    pending_attack_data = {
        "type": attacker["attack_type"],
        "x": start_x,
        "y": start_y,
        "z": start_z,
        "start_x": start_x,
        "start_y": start_y,
        "start_z": start_z,
        "target_x": float(target_x),
        "target_y": float(target_y),
        "target_z": target_z,
        "element": attacker["element"],
        "speed": 0.8 if attacker["attack_type"] == "ultimate" else 1.4
    }
    
    print(f"Attack queued! Type: {attacker['attack_type']}, From: ({start_x:.1f}, {start_y:.1f}), To: ({target_x}, {target_y})")
    
    # Reset timers
    attack_travel_time = 0
    attack_progress = 0
    
    # Set attack delay (1 second after camera switch)
    global attack_fire_delay, attack_ready
    attack_fire_delay = 1.0
    attack_ready = False
    
    # Start camera animation from attacker to defender (only in PvP mode)
    global camera_animating, camera_anim_progress, camera_start_y, camera_target_y
    global camera_start_look_y, camera_target_look_y
    
    if game_mode == "pvp":
        camera_animating = True
        camera_anim_progress = 0
        
        # Set camera start position (behind attacker)
        camera_start_y = -700 if current_turn == 1 else 700
        camera_start_look_y = 200 if current_turn == 1 else -200
        
        # Set camera target position (behind defender)
        camera_target_y = 700 if current_turn == 1 else -700
        camera_target_look_y = -200 if current_turn == 1 else 200
    else:
        # In AI mode, camera stays behind player 1
        camera_animating = False
        
        # Set random AI reaction time if player 1 is attacking
        if current_turn == 1:
            global ai_reaction_delay
            if level == "hard":
                # Hard difficulty: Faster, more consistent reactions (0.3-0.5s)
                ai_reaction_delay = random.uniform(0.3, 0.7)
            else:
                # Easy difficulty: Variable reaction time (0.3-1.5s)
                rand = random.random()
                if rand < 0.4:
                   ai_reaction_delay = random.uniform(0.3, 0.6) # Fast reaction
                elif rand < 0.8:
                   ai_reaction_delay = random.uniform(0.6, 1.0) # Medium reaction
                else:
                   ai_reaction_delay = random.uniform(1.0, 1.5) # Slow reaction (might get hit)


            print(f"AI reaction time set to: {ai_reaction_delay:.2f}s")
    
    # Switch to defend phase (but don't move attack yet - wait for animation)
    phase = "defend"
    defend_timer = 0
    
    # Activate watchtower for hard difficulty (only in PvP mode)
    if level == "hard" and game_mode == "pvp":
        global active_watchtower, watchtower_sequence_active, watchtower_order, watchtower_next_index, watchtower_fire_delay
        global watchtower_bullet, watchtower_bullet2, watchtower_bullet_progress, watchtower_bullet2_progress, watchtower_cooldown
        watchtower_sequence_active = True
        watchtower_order = ["left", "right"]
        random.shuffle(watchtower_order)
        watchtower_next_index = 0
        watchtower_fire_delay = watchtower_telegraph_time  # start charging immediately
        active_watchtower = watchtower_order[0]
        watchtower_bullet = None
        watchtower_bullet2 = None
        watchtower_bullet_progress = 0
        watchtower_bullet2_progress = 0
        watchtower_cooldown = 0
        print(f"Watchtower sequence primed: {watchtower_order}")

def fire_watchtower_bullet():
    """Fire bullet from active watchtower at defender and non-active at random position"""
    global watchtower_bullet, watchtower_bullet_progress, watchtower_bullet2, watchtower_bullet2_progress
    
    if level != "hard" or active_watchtower is None:
        return
    
    defender = player2 if current_turn == 1 else player1
    
    # Determine active tower position (shoots at defender)
    tower1_x = -ARENA_WIDTH if active_watchtower == "left" else ARENA_WIDTH
    tower1_y = 0
    tower1_z = 70  # Near top of tower

    # Determine non-active tower position (shoots at random location)
    tower2_x = ARENA_WIDTH if active_watchtower == "left" else -ARENA_WIDTH
    tower2_y = 0    
    tower2_z = 70  # Near top of tower
    
    # Active tower: Target defender's current position
    target_x = defender["pos"][0]
    target_y = defender["pos"][1]
    target_z = defender["pos"][2] + 20  # Aim at center of player

    # Non-active tower: Random target on defender's side
    target2_x = random.uniform(-ARENA_WIDTH + 50, ARENA_WIDTH - 50)
    target2_y = defender["pos"][1]  
    target2_z = 5  # Aim at ground level
    
    # Active tower bullet
    watchtower_bullet = {
        "x": float(tower1_x),
        "y": float(tower1_y),
        "z": float(tower1_z),
        "start_x": float(tower1_x),
        "start_y": float(tower1_y),
        "start_z": float(tower1_z),
        "target_x": float(target_x),
        "target_y": float(target_y),
        "target_z": float(target_z),
        "speed": 2.0  # Faster than normal attacks
    }

    # Non-active tower bullet (random direction)
    watchtower_bullet2 = {
        "x": float(tower2_x),
        "y": float(tower2_y),
        "z": float(tower2_z),
        "start_x": float(tower2_x),
        "start_y": float(tower2_y),
        "start_z": float(tower2_z),
        "target_x": float(target2_x),
        "target_y": float(target2_y),
        "target_z": float(target2_z),
        "speed": 2.0  # Faster than normal attacks
    }
    
    watchtower_bullet_progress = 0
    print(f"Active watchtower fired at defender! From: ({tower1_x}, {tower1_y}, {tower1_z}) To: ({target_x:.1f}, {target_y:.1f}, {target_z:.1f})")
    
    watchtower_bullet2_progress = 0
    print(f"Non-active watchtower fired at random! From: ({tower2_x}, {tower2_y}, {tower2_z}) To: ({target2_x:.1f}, {target2_y:.1f}, {target2_z:.1f})")

def spawn_watchtower_bullet(side, target_x, target_y, target_z):
    """Spawn a single watchtower bullet from the given side toward the target position"""
    global watchtower_bullet, watchtower_bullet_progress, watchtower_bullet2, watchtower_bullet2_progress

    tower_x = -ARENA_WIDTH if side == "left" else ARENA_WIDTH
    tower_y = 0
    tower_z = 70

    bullet_data = {
        "x": float(tower_x),
        "y": float(tower_y),
        "z": float(tower_z),
        "start_x": float(tower_x),
        "start_y": float(tower_y),
        "start_z": float(tower_z),
        "target_x": float(target_x),
        "target_y": float(target_y),
        "target_z": float(target_z),
        "speed": 0.8,  # Slow projectile for dodgeable reaction time
        "side": side
    }

    if watchtower_bullet is None:
        watchtower_bullet = bullet_data
        watchtower_bullet_progress = 0
        print(f"Watchtower {side} fired first bullet at ({target_x:.1f}, {target_y:.1f}, {target_z:.1f})")
    elif watchtower_bullet2 is None:
        watchtower_bullet2 = bullet_data
        watchtower_bullet2_progress = 0
        print(f"Watchtower {side} fired second bullet at ({target_x:.1f}, {target_y:.1f}, {target_z:.1f})")

def ai_make_attack_decision():
    """AI decides which attack type to use and fires at player 1"""
    global ai_executing
    
    ai_player = player2
    target_player = player1
    
    # AI decision logic for attack type
    # If ST bar is full (>=100), always use Ultimate
    # Otherwise, randomize between basic and signature based on stamina
    
    if ai_player["st"] >= 100:
        ai_player["attack_type"] = "ultimate"
        print("AI chose ULTIMATE attack")
    elif ai_player["st"] >= 20:
        # Randomize: 70% basic, 30% signature when stamina allows
        attack_choice = random.random()
        if attack_choice > 0.7:
            ai_player["attack_type"] = "signature"
            print("AI chose SIGNATURE attack")
        else:
            ai_player["attack_type"] = "basic"
            print("AI chose BASIC attack")
    else:
        ai_player["attack_type"] = "basic"
        print("AI chose BASIC attack")
    
    reset_crosshair()
    
    # Calculate target with inaccuracy based on difficulty
    if level == "hard":
        # Hard difficulty: ±20 to ±40 pixel random offset (improved accuracy)
        inaccuracy_x = random.uniform(-40, 40)
    else:
        # Easy difficulty: ±30 to ±80 pixel random offset
        inaccuracy_x = random.uniform(-80, 80)
    
    target_x = target_player["pos"][0] + inaccuracy_x
    
    # Clamp to crosshair range
    max_range = ARENA_WIDTH - 50
    target_x = max(-max_range, min(max_range, target_x))
    
    # Set crosshair to target position
    global crosshair_pos
    crosshair_pos = target_x
    
    print(f"AI targeting: {target_x:.1f} (player at {target_player['pos'][0]:.1f}, offset: {inaccuracy_x:.1f})")
    
    # Fire the attack
    fire_attack()
    ai_executing = False

def ai_make_defense_decision():
    """AI calculates attack trajectory and dodges"""
    global ai_executing
    
    if not active_attack:
        ai_executing = False
        return
    
    ai_player = player2
    
    # Calculate where the attack is heading
    attack_target_x = active_attack["target_x"]
    
    # Calculate dodge direction (move away from attack)
    current_x = ai_player["pos"][0]
    
    # Determine which direction to dodge
    if attack_target_x > current_x:
        # Attack is to the right, dodge left
        dodge_direction = -1
    else:
        # Attack is to the left, dodge right
        dodge_direction = 1
    
    # Random dodge distance for easy difficulty (100-200 pixels)
    dodge_distance = random.uniform(100, 200)
    
    # Calculate target position
    target_x = current_x + (dodge_direction * dodge_distance)
    
    # Clamp to arena bounds
    max_x = ARENA_WIDTH - 50
    min_x = -ARENA_WIDTH + 50
    
    # If target is out of bounds, reverse direction
    if target_x > max_x or target_x < min_x:
        dodge_direction = -dodge_direction
        target_x = current_x + (dodge_direction * dodge_distance)
        # Clamp again to ensure it's within bounds
        target_x = max(min_x, min(max_x, target_x))
    
    # Set target for smooth movement instead of teleporting
    ai_player["ai_target_x"] = target_x
    ai_player["ai_moving"] = True
    
    print(f"AI dodging from {current_x:.1f} to {target_x:.1f} (distance: {dodge_distance:.1f})")
    
    # Small chance to jump (20%)
    if random.random() < 0.2 and ai_player["jump_height"] == 0:
        ai_player["vel"] = 600  # Use proper initial velocity like player jumps
        print("AI jumped while dodging")
    
    ai_executing = False

def update_menu_background(dt):
    """Update decorative AI vs AI battle in menu background - does not affect gameplay"""
    global menu_bg_attack, menu_bg_attack_progress, menu_bg_current_turn, menu_bg_phase
    global menu_bg_attack_timer, menu_bg_defend_timer, menu_camera_angle
    
    # Update orbiting camera (slow rotation around arena)
    menu_camera_angle += 10 * dt  # 10 degrees per second
    if menu_camera_angle >= 360:
        menu_camera_angle -= 360
    
    # Apply gravity to menu background players
    gravity = 1500
    for p in [menu_bg_player1, menu_bg_player2]:
        if p["jump_height"] > 0 or p["vel"] != 0:
            p["jump_height"] += p["vel"] * dt
            p["vel"] -= gravity * dt
            
            if p["jump_height"] <= 0:
                p["jump_height"] = 0
                p["vel"] = 0
    
    if menu_bg_phase == "attack":
        menu_bg_attack_timer += dt
        
        # Auto-fire attack after 1.5 seconds
        if menu_bg_attack_timer >= 1.5:
            attacker = menu_bg_player1 if menu_bg_current_turn == 1 else menu_bg_player2
            defender = menu_bg_player2 if menu_bg_current_turn == 1 else menu_bg_player1
            
            # Randomly choose attack type
            attack_choice = random.random()
            if attacker["st"] >= 100 and attack_choice > 0.7:
                attacker["attack_type"] = "ultimate"
                attacker["st"] = 0
            elif attacker["st"] >= 20 and attack_choice > 0.4:
                attacker["attack_type"] = "signature"
                attacker["st"] -= 20
            else:
                attacker["attack_type"] = "basic"
            
            # Fire attack at defender with slight randomness
            target_x = defender["pos"][0] + random.uniform(-100, 100)
            target_y = defender["pos"][1]
            
            # Calculate spawn position
            dx = target_x - attacker["pos"][0]
            dy = target_y - attacker["pos"][1]
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance > 0:
                dx /= distance
                dy /= distance
            else:
                dy = 1 if menu_bg_current_turn == 1 else -1
                dx = 0
            
            spawn_offset = 70
            start_x = float(attacker["pos"][0]) + dx * spawn_offset
            start_y = float(attacker["pos"][1]) + dy * spawn_offset
            
            menu_bg_attack = {
                "type": attacker["attack_type"],
                "x": start_x,
                "y": start_y,
                "z": 50.0,
                "start_x": start_x,
                "start_y": start_y,
                "start_z": 50.0,
                "target_x": float(target_x),
                "target_y": float(target_y),
                "target_z": 50.0,
                "element": attacker["element"],
                "speed": 0.8 if attacker["attack_type"] == "ultimate" else 1.2
            }
            
            menu_bg_attack_progress = 0
            menu_bg_phase = "defend"
            menu_bg_defend_timer = 0
            menu_bg_attack_timer = 0
    
    elif menu_bg_phase == "defend":
        menu_bg_defend_timer += dt
        
        # Update attack movement
        if menu_bg_attack:
            menu_bg_attack_progress += dt * menu_bg_attack["speed"]
            
            if menu_bg_attack_progress < 1.0:
                t = menu_bg_attack_progress
                menu_bg_attack["x"] = menu_bg_attack["start_x"] + (menu_bg_attack["target_x"] - menu_bg_attack["start_x"]) * t
                menu_bg_attack["y"] = menu_bg_attack["start_y"] + (menu_bg_attack["target_y"] - menu_bg_attack["start_y"]) * t
                
                # Arc for signature
                if menu_bg_attack["type"] == "signature":
                    arc_height = 60 * math.sin(t * math.pi)
                    menu_bg_attack["z"] = menu_bg_attack["start_z"] + arc_height
                elif menu_bg_attack["type"] == "ultimate":
                    menu_bg_attack["z"] = 10.0
                else:
                    menu_bg_attack["z"] = menu_bg_attack["start_z"]
                
                # Defender AI: dodge randomly
                defender = menu_bg_player2 if menu_bg_current_turn == 1 else menu_bg_player1
                if menu_bg_defend_timer > 0.5 and random.random() < 0.02:  # 2% chance per frame to dodge
                    dodge_dir = random.choice([-1, 1])
                    defender["pos"][0] = max(-ARENA_WIDTH + 50, min(ARENA_WIDTH - 50, 
                                             defender["pos"][0] + dodge_dir * 100))
                    # Small chance to jump
                    if random.random() < 0.3 and defender["jump_height"] == 0:
                        defender["vel"] = 600
            else:
                # Attack landed - resolve and switch turn
                attacker = menu_bg_player1 if menu_bg_current_turn == 1 else menu_bg_player2
                defender = menu_bg_player2 if menu_bg_current_turn == 1 else menu_bg_player1
                
                # Calculate hit
                hit_distance = math.sqrt(
                    (menu_bg_attack["target_x"] - defender["pos"][0])**2 +
                    (menu_bg_attack["target_y"] - defender["pos"][1])**2
                )
                
                damage = 0
                if menu_bg_attack["type"] == "basic" and hit_distance < 60:
                    damage = 10
                elif menu_bg_attack["type"] == "signature" and hit_distance < 70:
                    damage = 20
                elif menu_bg_attack["type"] == "ultimate" and hit_distance < 120:
                    damage = 40
                
                if damage > 0:
                    defender["hp"] = max(0, defender["hp"] - damage)
                    attacker["st"] = min(100, attacker["st"] + 10)
                else:
                    defender["st"] = min(100, defender["st"] + 10)
                
                # Reset if someone died
                if defender["hp"] <= 0 or attacker["hp"] <= 0:
                    # Reset both fighters with random elements
                    elements = ["FIR", "WTR", "ELC", "ERT", "WND", "ICE"]
                    menu_bg_player1["element"] = random.choice(elements)
                    menu_bg_player1["color"] = element_colors[menu_bg_player1["element"]]
                    menu_bg_player1["hp"] = 100
                    menu_bg_player1["st"] = 0
                    menu_bg_player1["pos"] = [0, -300, 30]
                    menu_bg_player1["jump_height"] = 0
                    menu_bg_player1["vel"] = 0
                    
                    menu_bg_player2["element"] = random.choice(elements)
                    menu_bg_player2["color"] = element_colors[menu_bg_player2["element"]]
                    menu_bg_player2["hp"] = 100
                    menu_bg_player2["st"] = 0
                    menu_bg_player2["pos"] = [0, 300, 30]
                    menu_bg_player2["jump_height"] = 0
                    menu_bg_player2["vel"] = 0
                
                # Clear attack and switch turn
                menu_bg_attack = None
                menu_bg_current_turn = 2 if menu_bg_current_turn == 1 else 1
                menu_bg_phase = "attack"
                menu_bg_attack_timer = 0
                menu_bg_defend_timer = 0

def update_crosshair(dt):
    """Update crosshair oscillation"""
    global crosshair_pos, crosshair_direction, crosshair_timer, crosshair_visible
    
    if phase != "attack":
        return
    
    attacker = player1 if current_turn == 1 else player2
    
    # Adjust speed based on Wind status (Imbalance)
    speed = crosshair_speed
    if attacker["status"] == "IMBL":
        speed *= 1.5  # Faster, harder to aim
    
    # Update position
    crosshair_pos += crosshair_direction * speed * dt
    
    # Bounce at boundaries
    max_x = ARENA_WIDTH - 50
    min_x = -ARENA_WIDTH + 50
    
    if crosshair_pos >= max_x:
        crosshair_pos = max_x
        crosshair_direction = -1
    elif crosshair_pos <= min_x:
        crosshair_pos = min_x
        crosshair_direction = 1
    
    # Update timer
    crosshair_timer += dt
    if crosshair_timer > 4.0:  # Visible for 4 seconds
        crosshair_visible = False

def update_attack(dt):
    """Update attack projectile movement"""
    global active_attack, phase, attack_travel_time, attack_progress, attack_ready
    
    if active_attack is None:
        return
    
    # Don't move attack until the 1-second delay has passed
    if not attack_ready:
        return
    
    attack = active_attack
    
    # Update progress (0.0 to 1.0)
    attack_progress += dt * attack["speed"]
    attack_travel_time += dt
    
    if attack_progress < 1.0:
        # Interpolate position linearly (straight line movement)
        t = attack_progress
        attack["x"] = attack["start_x"] + (attack["target_x"] - attack["start_x"]) * t
        attack["y"] = attack["start_y"] + (attack["target_y"] - attack["start_y"]) * t
        
        # Different Z behavior based on attack type
        if attack["type"] == "signature":
            # Arc trajectory for signature attack
            arc_height = 60 * math.sin(t * math.pi)
            attack["z"] = attack["start_z"] + arc_height
        elif attack["type"] == "ultimate":
            # Ground-level for ultimate
            attack["z"] = 10.0
        else:
            # Basic attack stays at constant height
            attack["z"] = attack["start_z"]
    else:
        # Attack reached target - resolve it
        resolve_attack()

def resolve_attack():
    """Calculate damage and effects when attack lands"""
    global active_attack, phase, current_turn, game_state, winner,popup_message, popup_timer
    
    attacker = player1 if current_turn == 1 else player2
    defender = player2 if current_turn == 1 else player1
    
    if active_attack is None:
        return
    
    attack = active_attack
    
    # Calculate distance between attack landing point and defender
    hit_distance = math.sqrt(
        (attack["target_x"] - defender["pos"][0])**2 +
        (attack["target_y"] - defender["pos"][1])**2
    )
    
    print(f"Attack landed! Distance from defender: {hit_distance:.1f}")
    
    # Check if defender jumped (works for basic and ultimate, not signature)
    jumped = defender["jump_height"] > 50 and (attack["type"] == "basic" or attack["type"] == "ultimate")
    
    damage = 0
    hit = False
    damage_multiplier = 1.0
    
    # Apply Cripple effect (defender takes 50% more damage)
    if defender["status"] == "CRPL":
        damage_multiplier = 1.5
    
    # Apply Weaken effect (attacker deals 80% less damage)
    if attacker["status"] == "WEAK":
        damage_multiplier *= 0.2
    
    # Get element from attack for status effect application
    element = attack.get("element", None)
    
    if jumped:
        # Successful jump dodge
        defender["st"] = min(100, defender["st"] + 30)
    elif attack["type"] == "basic":
        # Basic: can be jumped, parried, or dodged by movement
        if hit_distance < 60:
            damage = int(10 * damage_multiplier)
            hit = True
        elif hit_distance < 100:
            damage = int(6 * damage_multiplier)
            hit = True
            
    elif attack["type"] == "signature":
        # Signature: can only be parried or dodged by movement (not jumped)
        if hit_distance < 70:
            damage = int(20 * damage_multiplier)
            hit = True
            will_apply_stun = (element == "ELC")
        elif hit_distance < 110:
            damage = int(12 * damage_multiplier)
            hit = True
            
    elif attack["type"] == "ultimate":
        # Ultimate: can only be jumped (not parried or dodged by movement)
        # If not jumped, hit is guaranteed regardless of distance
        if not jumped:
            damage = int(40 * damage_multiplier)
            hit = True
            will_apply_stun = (element == "ELC")
    
    if hit:
        # Apply damage normally
        defender["hp"] = max(0, defender["hp"] - damage)
        attacker["st"] = min(100, attacker["st"] + 10)
        print(f"HIT! Damage: {damage}, Defender HP: {defender['hp']}")
        
        # Apply status effects AFTER damage (Signature/Ultimate only)
        if attack["type"] in ["signature", "ultimate"]:
            apply_status_effect(defender, attack["element"])
    else:
        # Successful dodge
        defender["st"] = min(100, defender["st"] + 10)
        print(f"MISS! Defender dodged.")
        # Show dodge popup
        popup_message = "DODGED!"
        popup_timer = 0
    
    # Check win condition first
    if defender["hp"] <= 0:
        global game_over_animation, game_over_timer, loser_rotation
        game_state = "game_over"
        winner = current_turn
        active_attack = None
        game_over_animation = True
        game_over_timer = 0
        loser_rotation = 0
        if game_mode == "pvai":
            if winner == 1:
                popup_message = "You Win!"
            else:
                popup_message = "AI Wins!"
        else:
            popup_message = f"Player {winner} Wins!"
        popup_timer = 0
        print(f"Player {winner} wins!")
        return
    
    # Clear attack and switch turn (status damage will be applied in switch_turn)
    active_attack = None
    if level == "hard" and game_mode == "pvp":
        # Extend defend phase for watchtower sequence; turn will switch after towers finish
        return
    else:
        switch_turn()

def apply_status_effect(player, element):
    """Apply status effect based on element"""
    status_map = {
        "ICE": "FRIZ",  # Freeze
        "FIR": "BURN",  # Burn
        "ELC": "STUN",  # Stun
        "ERT": "CRPL",  # Cripple
        "WND": "IMBL",  # Imbalance
        "WTR": "WEAK"   # Weaken
    }
    
    status_name = status_map.get(element, None)
    if status_name:
        # Determine player color name for popup
        player_color_name = "Red" if player == player1 else "Blue"
        
        # Special handling for Stun - save current HP and reduce to 10 for 2 rounds
        if status_name == "STUN":
            player["stun_original_hp"] = player["hp"]  # Save current HP
            player["hp"] = 10  # Reduce to 10 HP
            player["status"] = "STUN"
            player["status_rounds"] = 2  # Lasts 2 rounds
            global popup_message, popup_timer
            popup_message = f"Player {player_color_name} has been affected with STUN"
            popup_timer = 0
            print(f"Applied STUN: HP {player['stun_original_hp']} -> 10 for 2 rounds")
        else:
            player["status"] = status_name
            player["status_rounds"] = 3
            popup_message = f"Player {player_color_name} has been affected with {status_name}"
            popup_timer = 0
            print(f"Applied status: {status_name} for 3 rounds")

def apply_status_damage(player, decrement_rounds=False):
    """Apply damage/effects from status"""
    if player["status"] == "BURN" and player["status_rounds"] > 0:
        player["hp"] = max(0, player["hp"] - 5)
        print(f"BURN damage: -5 HP")
    
    # Update move speed based on status
    base_speed = 40
    if player["status"] == "FRIZ":
        player["move_speed"] = int(base_speed * 0.4)  # -60% speed
        print(f"FREEZE slow: {player['move_speed']} speed")
    # Note: Don't reset to base_speed here - let danger zone or other mechanics handle it
    
    # Only decrement rounds when specified (at start of new round)
    if decrement_rounds and player["status_rounds"] > 0:
        player["status_rounds"] -= 1
        if player["status_rounds"] == 0:
            # Stun expiring - restore original HP
            if player["status"] == "STUN" and player["stun_original_hp"] is not None:
                player["hp"] = player["stun_original_hp"]
                player["stun_original_hp"] = None
                print(f"STUN expired - HP restored to {player['hp']}")
            else:
                print(f"Status {player['status']} expired")
    
    if player["status_rounds"] <= 0:
        player["status"] = None
        # Only reset speed if no status effect
        if player["status"] is None:
            player["move_speed"] = base_speed

def switch_turn():
    """Switch to other player's turn"""
    global current_turn, phase, attack_timer, round_number
    global active_watchtower, watchtower_bullet, watchtower_bullet2, watchtower_cooldown
    global ai_decision_timer, ai_executing
    
    current_turn = 2 if current_turn == 1 else 1
    phase = "attack"
    attack_timer = 0
    
    # Reset AI variables
    ai_decision_timer = 0
    ai_executing = False
    
    # Reset watchtower
    active_watchtower = None
    watchtower_bullet = None
    watchtower_bullet2 = None
    watchtower_cooldown = 0
    watchtower_sequence_active = False
    watchtower_order = []
    watchtower_next_index = 0
    watchtower_fire_delay = 0
    
    # Track if this is the start of a new round
    is_new_round = False
    if current_turn == 1:
        round_number += 1
        is_new_round = True
        # Randomize danger zone position for new round in medium difficulty
        randomize_danger_zone()
    
    # Apply per-round stamina
    player1["st"] = min(100, player1["st"] + 5)
    player2["st"] = min(100, player2["st"] + 5)
    
    # Apply status effects - only decrement rounds at start of new round
    apply_status_damage(player1, decrement_rounds=is_new_round)
    apply_status_damage(player2, decrement_rounds=is_new_round)
    
    # Reset attack type
    attacker = player1 if current_turn == 1 else player2
    attacker["attack_type"] = "basic"
    
    reset_crosshair()

def parry_attack():
    """Attempt to parry incoming attack (only works on basic and signature attacks)"""
    global active_attack, defend_timer, popup_message, popup_timer, attack_travel_time
    
    # Parry only works on basic and signature attacks, not ultimate
    if active_attack and (active_attack["type"] == "basic" or active_attack["type"] == "signature"):
        defender = player2 if current_turn == 1 else player1
        
        # Check if attack is close enough to parry (proximity check)
        attack_distance = math.sqrt(
            (active_attack["x"] - defender["pos"][0])**2 +
            (active_attack["y"] - defender["pos"][1])**2
        )
        
        # Only allow parry if attack is within 200 units (increased from 150)
        if attack_distance > 200:
            print(f"Parry failed - attack too far ({attack_distance:.1f} units)")
            return
        
        # Check timing window (0.5 to 1.0 seconds into travel - widened window)
        if 0.5 < attack_travel_time < 1.0:
            defender["st"] = min(100, defender["st"] + 30)
            active_attack = None
            # Show parry popup
            popup_message = "NICE PARRY!"
            popup_timer = 0
            switch_turn()
        else:
            print(f"Parry failed - bad timing ({attack_travel_time:.2f}s)")

def keyboardListener(key, x, y):
    """Handle keyboard input"""
    global pause, game_state, camera_mode, current_turn, level, game_mode
    global camera_pos, camera_angle
    
    if key == b'p':
        pause = not pause
        return
    
    if key == b'r':
        if game_state == "game_over":
            game_state = "mode_select"
            player1["element"] = None
            player2["element"] = None
        return
    
    if pause:
        # Allow backspace to return to main menu from pause
        if key == b'\x08':  # Backspace key
            # Reset game state
            pause = False
            game_state = "menu"
            player1["element"] = None
            player2["element"] = None
            player1["hp"] = 100
            player1["st"] = 0
            player1["status"] = None
            player1["stun_original_hp"] = None
            player2["hp"] = 100
            player2["st"] = 0
            player2["status"] = None
            player2["stun_original_hp"] = None
            print("Returned to main menu from pause")
        return
    
    # Mode selection
    if game_state == "mode_select":
        if key == b'1':
            game_mode = "pvp"
            game_state = "element_select"
            print("Player vs Player mode selected")
        elif key == b'2':
            game_mode = "pvai"
            game_state = "element_select"
            print("Player vs AI mode selected")
        elif key == b'3':
            game_state = "how_to_play"
            print("How to Play selected")
        return
    
    # How to Play screen
    if game_state == "how_to_play":
        if key == b'\x08':  # Backspace key
            game_state = "mode_select"
        return
    
    # Element selection
    if game_state == "element_select":
        elements = [b'1', b'2', b'3', b'4', b'5', b'6']
        element_codes = ["FIR", "WTR", "ELC", "ERT", "WND", "ICE"]
        
        if key in elements:
            idx = elements.index(key)
            if player1["element"] is None:
                player1["element"] = element_codes[idx]
                player1["color"] = element_colors[element_codes[idx]]
                # In PvAI mode, auto-assign AI element and skip to level select
                if game_mode == "pvai":
                    ai_element_idx = random.randint(0, 5)
                    player2["element"] = element_codes[ai_element_idx]
                    player2["color"] = element_colors[element_codes[ai_element_idx]]
                    print(f"AI automatically assigned element: {element_names[player2['element']]}")
                    game_state = "level_select"
                # In PvP mode, wait for Player 2 selection
            elif player2["element"] is None:
                player2["element"] = element_codes[idx]
                player2["color"] = element_colors[element_codes[idx]]
                game_state = "level_select"
        return
    
    # Level selection
    if game_state == "level_select":
        if key == b'1':
            level = "easy"
            initialize_game()
        elif key == b'2':
            # Only allow medium difficulty in PvP mode
            if game_mode == "pvp":
                level = "medium"
                initialize_game()
        elif key == b'3':
            level = "hard"
            initialize_game()
        return
    
    if game_state != "playing":
        if key == b'\r':  # Enter key
            game_state = "mode_select"
        return
    
    # In AI mode, only allow player 1 to control during their turn or defense
    if game_mode == "pvai" and current_turn == 2 and phase == "attack":
        return  # Don't allow input during AI's attack phase
    
    attacker = player1 if current_turn == 1 else player2
    defender = player2 if current_turn == 1 else player1
    
    # Free camera controls (J/L/I/K)
    if camera_mode == "free":
        if key == b'i':
            camera_pos[2] += 30
            return
        elif key == b'k':
            camera_pos[2] = max(100, camera_pos[2] - 30)
            return
        elif key == b'j':
            camera_angle = (camera_angle - 10) % 360
            return
        elif key == b'l':
            camera_angle = (camera_angle + 10) % 360
            return
    
    # Attack phase controls
    if phase == "attack":
        # Movement controls for Player 1 only (A and D)
        if current_turn == 1:
            if key == b'a':
                # Player 1 moves left (negative X)
                attacker["pos"][0] = max(-ARENA_WIDTH + 50, 
                                         attacker["pos"][0] - attacker["move_speed"])
            elif key == b'd':
                # Player 1 moves right (positive X)
                attacker["pos"][0] = min(ARENA_WIDTH - 50, 
                                         attacker["pos"][0] + attacker["move_speed"])
        
        # Attack type selection (both players)
        if key == b'1':
            attacker["attack_type"] = "basic"
            reset_crosshair()
        elif key == b'2':
            if attacker["st"] >= 20:
                attacker["attack_type"] = "signature"
                reset_crosshair()
        elif key == b'3':
            if attacker["st"] >= 100:
                attacker["attack_type"] = "ultimate"
                reset_crosshair()
        
        # Fire attack (both players)
        elif key == b' ':
            fire_attack()
    
    # Defend phase controls
    elif phase == "defend":
        # In AI mode, only allow player 1 to defend when it's their turn
        if game_mode == "pvai" and current_turn == 1:
            # AI is defending, player can't control
            return
        
        # Movement controls for Player 1 (A and D)
        if current_turn == 2:  # Player 1 is defending
            if key == b'a':
                # Player 1 moves left (negative X)
                defender["pos"][0] = max(-ARENA_WIDTH + 50, 
                                         defender["pos"][0] - defender["move_speed"])
            elif key == b'd':
                # Player 1 moves right (positive X)
                defender["pos"][0] = min(ARENA_WIDTH - 50, 
                                         defender["pos"][0] + defender["move_speed"])
            elif key == b'w':
                # Player 1 jump
                if defender["jump_height"] == 0:
                    defender["vel"] = 600
            elif key == b'q':
                # Player 1 parry
                parry_attack()
        
        # Player 2 parry with Delete key
        elif current_turn == 1:  # Player 2 is defending
            if key == b'\x7f':  # Delete key
                parry_attack()
                parry_attack()

def specialKeyListener(key, x, y):
    """Handle arrow keys for player 2 controls and camera"""
    global camera_pos, camera_angle, camera_mode, camera_distance, game_state, phase, current_turn, game_mode
    
    # Player 2 controls during gameplay
    if game_state == "playing":
        attacker = player1 if current_turn == 1 else player2
        defender = player2 if current_turn == 1 else player1
        
        # Attack phase - Player 2 movement with arrow keys
        if phase == "attack" and current_turn == 2:
            if key == GLUT_KEY_LEFT:
                # Player 2 moves left from their perspective (positive X)
                attacker["pos"][0] = min(ARENA_WIDTH - 50, 
                                         attacker["pos"][0] + attacker["move_speed"])
                return
            elif key == GLUT_KEY_RIGHT:
                # Player 2 moves right from their perspective (negative X)
                attacker["pos"][0] = max(-ARENA_WIDTH + 50, 
                                         attacker["pos"][0] - attacker["move_speed"])
                return
        
        # Defend phase - Player 2 movement with arrow keys
        elif phase == "defend" and current_turn == 1:  # Player 2 is defending
            if key == GLUT_KEY_LEFT:
                # Player 2 moves left from their perspective (positive X)
                defender["pos"][0] = min(ARENA_WIDTH - 50, 
                                         defender["pos"][0] + defender["move_speed"])
                return
            elif key == GLUT_KEY_RIGHT:
                # Player 2 moves right from their perspective (negative X)
                defender["pos"][0] = max(-ARENA_WIDTH + 50, 
                                         defender["pos"][0] - defender["move_speed"])
                return
            elif key == GLUT_KEY_UP:
                # Player 2 jump
                if defender["jump_height"] == 0:
                    defender["vel"] = 600
                return
    
    # Camera controls no longer here - moved to J/L/I/K in keyboardListener
    # Arrow keys are exclusively for Player 2 gameplay controls
    pass

def mouseListener(button, state, x, y):
    """Handle mouse input"""
    global camera_mode
    
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        camera_mode = "free" if camera_mode == "static" else "static"

def setupCamera():
    """Setup camera view"""
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, 1.25, 0.1, 2500)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    # Game over: orbiting camera around arena (continues even after animation)
    if game_state == "game_over":
        radius = 600
        cam_x = radius * math.cos(math.radians(game_over_camera_angle))
        cam_y = radius * math.sin(math.radians(game_over_camera_angle))
        gluLookAt(cam_x, cam_y, 300,
                  0, 0, 60,
                  0, 0, 1)
    elif camera_mode == "static":
        # In AI mode, always stay behind player 1
        if game_mode == "pvai":
            gluLookAt(0, -700, 250,
                      0, 200, 60,
                      0, 0, 1)
        # Handle camera animation in PvP mode
        elif camera_animating:
            # Interpolate camera position during animation
            t = camera_anim_progress  # 0 to 1
            # Smooth easing (ease-in-out)
            t = t * t * (3 - 2 * t)
            
            side_y = camera_start_y + (camera_target_y - camera_start_y) * t
            look_y = camera_start_look_y + (camera_target_look_y - camera_start_look_y) * t
            
            gluLookAt(0, side_y, 250,
                      0, look_y, 60,
                      0, 0, 1)
        elif phase == "attack":
            # Behind attacker
            side_y = -700 if current_turn == 1 else 700
            look_y = 200 if current_turn == 1 else -200
            gluLookAt(0, side_y, 250,
                      0, look_y, 60,
                      0, 0, 1)
        else:
            # Behind defender
            side_y = 700 if current_turn == 1 else -700
            look_y = -200 if current_turn == 1 else 200
            gluLookAt(0, side_y, 250,
                      0, look_y, 60,
                      0, 0, 1)
    else:
        # Free camera
        cam_x = camera_distance * math.sin(math.radians(camera_angle))
        cam_y = camera_distance * math.cos(math.radians(camera_angle))
        gluLookAt(cam_x, cam_y, camera_pos[2],
                  0, 0, 50,
                  0, 0, 1)
def update_ai(dt):
    """Unified AI logic for decisions and movement"""
    global ai_decision_timer, ai_executing
    
    # 1. AI MOVEMENT LOGIC (Handles smooth sliding)
    if player2["ai_moving"] and player2["ai_target_x"] is not None:
        current_x = player2["pos"][0]
        target_x = player2["ai_target_x"]
        distance = abs(target_x - current_x)
        
        # Move 300 pixels per second
        step = 300 * dt
        
        if distance < step:
            # Arrived at target
            player2["pos"][0] = target_x
            player2["ai_moving"] = False
            player2["ai_target_x"] = None
        else:
            # Move towards target
            direction = 1 if target_x > current_x else -1
            player2["pos"][0] += step * direction

    # 2. AI DECISION LOGIC (Handles attacking and dodging)
    # Only run if not already executing an action
    if ai_executing:
        return

    # AI Attacks (when it is player 2's turn)
    if current_turn == 2 and phase == "attack":
        ai_decision_timer += dt
        if ai_decision_timer >= 0.8:  # Fixed delay for attack decisions
            ai_executing = True
            ai_decision_timer = 0
            ai_make_attack_decision()
            
    # AI Defends (when player 1 is attacking and attack is active)
    elif current_turn == 1 and phase == "defend" and active_attack and not camera_animating:
        ai_decision_timer += dt
        if ai_decision_timer >= ai_reaction_delay:  # Dynamic delay for defense
            ai_executing = True
            ai_decision_timer = 0
            ai_make_defense_decision()

def idle():
    """Update game state"""
    global defend_timer, attack_timer, last_time, popup_timer, popup_message
    global camera_animating, camera_anim_progress
    global ai_decision_timer, ai_executing
    global game_over_timer, loser_rotation, game_over_animation, game_over_camera_angle, winner_jump_cycle
    
    import time
    current_time = time.time()
    
    if last_time == 0:
        last_time = current_time
        glutPostRedisplay()
        return
    
    dt = current_time - last_time
    last_time = current_time
    
    # Cap delta time to prevent huge jumps
    if dt > 0.1:
        dt = 0.1
    
    # Menu background update (decorative AI vs AI battle)
    if game_state == "menu":
        update_menu_background(dt)
    
    # AI update
    if game_state == "playing" and not pause and game_mode == "pvai":
        update_ai(dt)
    
    # Gravity logic
    if game_state == "playing" and not pause:
        gravity = 1500
        for p in [player1, player2]:
            # Apply physics if player is in the air or moving up
            if p["jump_height"] > 0 or p["vel"] != 0:
                p["jump_height"] += p["vel"] * dt  # Move
                p["vel"] -= gravity * dt           # Gravity
                
                # Land on ground
                if p["jump_height"] <= 0:
                    p["jump_height"] = 0
                    p["vel"] = 0
        
        
    # Update camera animation
    if camera_animating:
        camera_anim_progress += dt / camera_anim_duration
        if camera_anim_progress >= 1.0:
            camera_animating = False
            camera_anim_progress = 1.0
    
    # Update attack fire delay (1 second buffer after camera switch)
    global attack_fire_delay, attack_ready, pending_attack_data, active_attack
    if pending_attack_data is not None and not attack_ready:
        if attack_fire_delay > 0:
            attack_fire_delay -= dt
            if attack_fire_delay <= 0:
                attack_fire_delay = 0
                attack_ready = True
                # Spawn the attack projectile now
                active_attack = pending_attack_data
                pending_attack_data = None
                print("Attack spawned and ready to move!")
    
    # Update popup timer
    if popup_message:
        popup_timer += dt
        if popup_timer >= popup_duration:
            popup_message = ""
            popup_timer = 0
    
    # Game over animation and background
    if game_state == "game_over":
        game_over_timer += dt
        
        # Continue orbiting camera (15 degrees per second)
        game_over_camera_angle += 15 * dt
        if game_over_camera_angle >= 360:
            game_over_camera_angle -= 360
        
        # Continue winner celebration jump cycle
        global winner_jump_cycle
        winner_jump_cycle += dt * 4  # 4 radians per second for fast jumping
        
        # Animate loser falling (only during initial animation)
        if game_over_animation:
            if game_over_timer < 1.5:
                loser_rotation = min(90, (game_over_timer / 1.5) * 90)
            else:
                loser_rotation = 90
            
            # End animation after duration
            if game_over_timer >= game_over_duration:
                game_over_animation = False
        
        glutPostRedisplay()
        return
    
    if pause or game_state != "playing":
        glutPostRedisplay()
        return
    
    if phase == "attack":
        update_crosshair(dt)
        attack_timer += dt
        
        # Auto-switch if time runs out (20 seconds)
        if attack_timer > 20:
            print("Time's up! Switching turn.")
            switch_turn()
    
    elif phase == "defend":
        # Only update attack after camera animation completes
        if not camera_animating:
            update_attack(dt)
        defend_timer += dt
        
        # Get defender reference for mechanics below
        defender = player2 if current_turn == 1 else player1
        
        # Watchtower mechanics (hard difficulty, PvP only)
        if level == "hard" and game_state == "playing" and game_mode == "pvp":
            global watchtower_bullet, watchtower_bullet_progress, watchtower_bullet2, watchtower_bullet2_progress
            global watchtower_sequence_active, watchtower_order, watchtower_next_index, watchtower_fire_delay, active_watchtower

            # Update which tower is highlighted (next to fire)
            next_tower = None
            if watchtower_sequence_active and watchtower_next_index < len(watchtower_order):
                next_tower = watchtower_order[watchtower_next_index]
            active_watchtower = next_tower

            # Countdown to fire the next tower; do not fire until main projectile resolved
            if watchtower_sequence_active and next_tower:
                if watchtower_fire_delay > 0:
                    watchtower_fire_delay -= dt
                if watchtower_fire_delay <= 0 and active_attack is None:
                    # Lock onto defender's current position at the moment of firing
                    spawn_watchtower_bullet(next_tower, defender["pos"][0], defender["pos"][1], defender["pos"][2] + 20)
                    watchtower_next_index += 1
                    if watchtower_next_index < len(watchtower_order):
                        # Short pause before second tower starts charging
                        watchtower_fire_delay = random.uniform(0.5, 1.0) + watchtower_telegraph_time
                        active_watchtower = watchtower_order[watchtower_next_index]
                    else:
                        watchtower_fire_delay = 0

            # Update bullet 1 movement
            if watchtower_bullet is not None:
                watchtower_bullet_progress += dt * watchtower_bullet["speed"]

                if watchtower_bullet_progress < 1.0:
                    t = watchtower_bullet_progress
                    watchtower_bullet["x"] = watchtower_bullet["start_x"] + (watchtower_bullet["target_x"] - watchtower_bullet["start_x"]) * t
                    watchtower_bullet["y"] = watchtower_bullet["start_y"] + (watchtower_bullet["target_y"] - watchtower_bullet["start_y"]) * t
                    watchtower_bullet["z"] = watchtower_bullet["start_z"] + (watchtower_bullet["target_z"] - watchtower_bullet["start_z"]) * t
                else:
                    hit_distance = math.sqrt(
                        (watchtower_bullet["target_x"] - defender["pos"][0])**2 +
                        (watchtower_bullet["target_y"] - defender["pos"][1])**2
                    )

                    if hit_distance < 50:
                        defender["hp"] = max(0, defender["hp"] - 10)
                        print(f"Watchtower hit! Damage: 10, HP: {defender['hp']}")
                    else:
                        print(f"Watchtower shot missed! Distance: {hit_distance:.1f}")

                    watchtower_bullet = None

            # Update bullet 2 movement
            if watchtower_bullet2 is not None:
                watchtower_bullet2_progress += dt * watchtower_bullet2["speed"]

                if watchtower_bullet2_progress < 1.0:
                    t = watchtower_bullet2_progress
                    watchtower_bullet2["x"] = watchtower_bullet2["start_x"] + (watchtower_bullet2["target_x"] - watchtower_bullet2["start_x"]) * t
                    watchtower_bullet2["y"] = watchtower_bullet2["start_y"] + (watchtower_bullet2["target_y"] - watchtower_bullet2["start_y"]) * t
                    watchtower_bullet2["z"] = watchtower_bullet2["start_z"] + (watchtower_bullet2["target_z"] - watchtower_bullet2["start_z"]) * t
                else:
                    hit_distance = math.sqrt(
                        (watchtower_bullet2["target_x"] - defender["pos"][0])**2 +
                        (watchtower_bullet2["target_y"] - defender["pos"][1])**2
                    )

                    if hit_distance < 50:
                        defender["hp"] = max(0, defender["hp"] - 10)
                        print(f"Watchtower hit! Damage: 10, HP: {defender['hp']}")
                    else:
                        print(f"Watchtower shot missed! Distance: {hit_distance:.1f}")

                    watchtower_bullet2 = None

            # Finish sequence only after both tower shots are done
            if watchtower_sequence_active and watchtower_next_index >= 2 and watchtower_bullet is None and watchtower_bullet2 is None and active_attack is None:
                watchtower_sequence_active = False
                switch_turn()
        
        # Check danger zone (medium difficulty)
        if level == "medium" and game_state == "playing":
            half_width = danger_zone_width / 2
            in_danger_zone = (danger_zone_x - half_width <= defender["pos"][0] <= danger_zone_x + half_width)
            
            if in_danger_zone:
                # Apply speed reduction (70% slower)
                base_speed = 40
                if defender["status"] == "FRIZ":
                    defender["move_speed"] = int(base_speed * 0.4 * 0.1)  # Combine with freeze
                else:
                    defender["move_speed"] = int(base_speed * 0.1)  # 70% reduction
                
                # Track time in danger zone and drain HP
                global danger_zone_timer
                danger_zone_timer += dt
                
                if danger_zone_timer >= 1.0:
                    defender["hp"] = max(0, defender["hp"] - 1)
                    danger_zone_timer -= 1.0  # Subtract 1 second instead of reset to accumulate remainder
                    print(f"Danger zone damage! HP: {defender['hp']}")
            else:
                # Reset timer and speed when outside danger zone
                danger_zone_timer = 0
                # Restore speed based on status effects only
                base_speed = 40
                if defender["status"] == "FRIZ":
                    defender["move_speed"] = int(base_speed * 0.4)
                elif defender["status"] == "STUN":
                    defender["move_speed"] = int(base_speed * 0.7)
                elif defender["status"] is None:
                    defender["move_speed"] = base_speed
    
    glutPostRedisplay()

def showScreen():
    """Render the scene"""
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)
    
    if game_state == "menu":
        # Render 3D background with AI vs AI battle
        glClearColor(0.0, 0.0, 0.0, 1)
        
        # Setup orbiting camera for menu background
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60, 1.25, 0.1, 2500)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        # Orbiting camera around the arena
        radius = 700
        cam_x = radius * math.sin(math.radians(menu_camera_angle))
        cam_y = radius * math.cos(math.radians(menu_camera_angle))
        cam_z = 250
        gluLookAt(cam_x, cam_y, cam_z,
                  0, 0, 50,
                  0, 0, 1)
        
        # Draw 3D arena and menu background fighters
        draw_arena()
        draw_player(menu_bg_player1)
        draw_player(menu_bg_player2)
        
        # Draw attack if active
        if menu_bg_attack:
            draw_attack(menu_bg_attack)
        
        # Disable depth testing for 2D overlay and text
        glDisable(GL_DEPTH_TEST)
        
        # Draw semi-transparent overlay for text readability
        draw_dimming_overlay()
        
        # Draw menu text on top
        draw_text(435, 450, "POSITRON 3D", GLUT_BITMAP_TIMES_ROMAN_24)
        draw_text(420, 360, "3D Turn-Based Battle", GLUT_BITMAP_HELVETICA_18)
        draw_text(420, 320, "Press ENTER to Start", GLUT_BITMAP_HELVETICA_18)
        draw_text(300, 200, "Player 1: A/D-Move  1/2/3-Attack  SPACE-Fire  Q-Parry  W-Jump", GLUT_BITMAP_HELVETICA_12)
        draw_text(300, 180, "Player 2: Arrows-Move/Jump  1/2/3-Attack  SPACE-Fire  DEL-Parry", GLUT_BITMAP_HELVETICA_12)
        
        # Re-enable depth testing for next frame
        glEnable(GL_DEPTH_TEST)
    
    elif game_state == "mode_select":
        glClearColor(0.0, 0.0, 0.0, 1)  # Black background
        draw_text(360, 700, "SELECT GAME MODE", GLUT_BITMAP_TIMES_ROMAN_24)
        
        glColor3f(0.5, 0.8, 1.0)  # Light blue
        draw_text(360, 550, "1 - PLAYER VS PLAYER", GLUT_BITMAP_HELVETICA_18)
        draw_text(350, 510, "Two players battle against each other", GLUT_BITMAP_HELVETICA_12)
        
        glColor3f(1.0, 0.7, 0.3)  # Orange
        draw_text(360, 430, "2 - PLAYER VS AI", GLUT_BITMAP_HELVETICA_18)
        draw_text(350, 390, "Battle against computer-controlled opponent", GLUT_BITMAP_HELVETICA_12)
        
        glColor3f(0.3, 1.0, 0.3)  # Green
        draw_text(360, 310, "3 - HOW TO PLAY", GLUT_BITMAP_HELVETICA_18)
        draw_text(350, 270, "Learn the controls and game mechanics", GLUT_BITMAP_HELVETICA_12)
    
    elif game_state == "how_to_play":
        glClearColor(0.0, 0.0, 0.0, 1)  # Black background
        draw_text(380, 750, "HOW TO PLAY", GLUT_BITMAP_TIMES_ROMAN_24)
        
        # Controls Section
        glColor3f(0.5, 0.8, 1.0)  # Light blue
        draw_text(100, 680, "PLAYER 1 CONTROLS:", GLUT_BITMAP_HELVETICA_18)
        glColor3f(1, 1, 1)
        draw_text(120, 650, "A / D - Move left/right", GLUT_BITMAP_HELVETICA_12)
        draw_text(120, 630, "W - Jump to dodge", GLUT_BITMAP_HELVETICA_12)
        draw_text(120, 610, "Q - Parry incoming attack", GLUT_BITMAP_HELVETICA_12)
        draw_text(120, 590, "1 - Basic Attack (no stamina cost)", GLUT_BITMAP_HELVETICA_12)
        draw_text(120, 570, "2 - Signature Attack (costs 20 ST)", GLUT_BITMAP_HELVETICA_12)
        draw_text(120, 550, "3 - Ultimate Attack (costs 100 ST)", GLUT_BITMAP_HELVETICA_12)
        draw_text(120, 530, "SPACE - Fire selected attack", GLUT_BITMAP_HELVETICA_12)
        draw_text(120, 510, "P - Pause game", GLUT_BITMAP_HELVETICA_12)
        
        glColor3f(1.0, 0.7, 0.3)  # Orange
        draw_text(100, 470, "PLAYER 2 CONTROLS:", GLUT_BITMAP_HELVETICA_18)
        glColor3f(1, 1, 1)
        draw_text(120, 440, "Arrow Keys - Move left/right", GLUT_BITMAP_HELVETICA_12)
        draw_text(120, 420, "Up Arrow - Jump to dodge", GLUT_BITMAP_HELVETICA_12)
        draw_text(120, 400, "DEL - Parry incoming attack", GLUT_BITMAP_HELVETICA_12)
        draw_text(120, 380, "1/2/3 + SPACE - Same as Player 1", GLUT_BITMAP_HELVETICA_12)
        
        # Objective Section
        glColor3f(0.3, 1.0, 0.3)  # Green
        draw_text(100, 340, "OBJECTIVE:", GLUT_BITMAP_HELVETICA_18)
        glColor3f(1, 1, 1)
        draw_text(120, 310, "Reduce your opponent's HP to 0 to win!", GLUT_BITMAP_HELVETICA_12)
        draw_text(120, 290, "Aim carefully using the moving crosshair.", GLUT_BITMAP_HELVETICA_12)
        
        # Mechanics Section
        glColor3f(1.0, 0.7, 0.3)  # Orange
        draw_text(100, 240, "MECHANICS:", GLUT_BITMAP_HELVETICA_18)
        glColor3f(1, 1, 1)
        draw_text(120, 210, "ST BAR (Stamina): Build up by landing hits or dodging.", GLUT_BITMAP_HELVETICA_12)
        draw_text(120, 190, "- Basic attacks don't cost stamina", GLUT_BITMAP_HELVETICA_12)
        draw_text(120, 170, "- Signature attacks cost 20 ST and apply status effects", GLUT_BITMAP_HELVETICA_12)
        draw_text(120, 150, "- Ultimate attacks cost 100 ST and deal massive damage", GLUT_BITMAP_HELVETICA_12)
        
        draw_text(120, 120, "ELEMENTS: Each element has unique status effects when using", GLUT_BITMAP_HELVETICA_12)
        draw_text(120, 100, "Signature or Ultimate attacks.", GLUT_BITMAP_HELVETICA_12)
        
        # Status Effects Section (Right side)
        glColor3f(1.0, 0.5, 1.0)  # Magenta
        draw_text(550, 680, "STATUS EFFECTS:", GLUT_BITMAP_HELVETICA_18)
        
        glColor3f(1, 0, 0)  # Red
        draw_text(570, 650, "BURN (Fire):", GLUT_BITMAP_HELVETICA_12)
        glColor3f(1, 1, 1)
        draw_text(570, 630, "Deals 5 damage per round", GLUT_BITMAP_HELVETICA_12)
        
        glColor3f(1, 1, 0)  # Yellow
        draw_text(570, 600, "STUN (Electric):", GLUT_BITMAP_HELVETICA_12)
        glColor3f(1, 1, 1)
        draw_text(570, 580, "Reduces HP to 10 for 2 rounds", GLUT_BITMAP_HELVETICA_12)
        
        glColor3f(0, 1, 1)  # Cyan
        draw_text(570, 550, "FREEZE (Ice):", GLUT_BITMAP_HELVETICA_12)
        glColor3f(1, 1, 1)
        draw_text(570, 530, "Reduces speed by 60%", GLUT_BITMAP_HELVETICA_12)
        
        glColor3f(0.6, 0.2, 0.8)  # Purple
        draw_text(570, 500, "CRIPPLE (Earth):", GLUT_BITMAP_HELVETICA_12)
        glColor3f(1, 1, 1)
        draw_text(570, 480, "Take 50% more damage", GLUT_BITMAP_HELVETICA_12)
        
        glColor3f(0.5, 0.5, 0.5)  # Gray
        draw_text(570, 450, "WEAK (Water):", GLUT_BITMAP_HELVETICA_12)
        glColor3f(1, 1, 1)
        draw_text(570, 430, "Deal 80% less damage", GLUT_BITMAP_HELVETICA_12)
        
        glColor3f(0.8, 0.8, 0.8)  # Light gray
        draw_text(570, 400, "IMBALANCE (Wind):", GLUT_BITMAP_HELVETICA_12)
        glColor3f(1, 1, 1)
        draw_text(570, 380, "50% accuracy reduction", GLUT_BITMAP_HELVETICA_12)
        
        # Back option
        glColor3f(1.0, 1.0, 0.5)  # Yellow
        draw_text(350, 50, "Press BACKSPACE to return", GLUT_BITMAP_HELVETICA_18)
    
    elif game_state == "element_select":
        glClearColor(0.0, 0.0, 0.0, 1)  # Black background
        
        # Determine which player is selecting
        if player1["element"] is None:
            glColor3f(1, 0.5, 0.5)  # Light red for Player 1
            draw_text(350, 700, "PLAYER 1: SELECT ELEMENT", GLUT_BITMAP_TIMES_ROMAN_24)
        elif player2["element"] is None and game_mode == "pvp":
            glColor3f(0.5, 0.5, 1)  # Light blue for Player 2
            draw_text(350, 700, "PLAYER 2: SELECT ELEMENT", GLUT_BITMAP_TIMES_ROMAN_24)
        else:
            glColor3f(1, 1, 1)
            draw_text(380, 700, "SELECT YOUR ELEMENT", GLUT_BITMAP_TIMES_ROMAN_24)
        
        glColor3f(1, 1, 1)
        draw_text(290, 600, "1 - Fire (Red)     2 - Water (Blue)     3 - Electric (Yellow)", GLUT_BITMAP_HELVETICA_18)
        draw_text(300, 550, "4 - Earth (Green)  5 - Wind (Grey)      6 - Ice (Cyan)", GLUT_BITMAP_HELVETICA_18)
        
        y_pos = 400
        if player1["element"]:
            glColor3f(player1["color"][0], player1["color"][1], player1["color"][2])
            draw_text(300, y_pos, f"Player 1: {element_names[player1['element']]}", GLUT_BITMAP_HELVETICA_18)
            y_pos -= 50
        
        if player2["element"]:
            glColor3f(player2["color"][0], player2["color"][1], player2["color"][2])
            if game_mode == "pvai":
                draw_text(300, y_pos, f"AI: {element_names[player2['element']]}", GLUT_BITMAP_HELVETICA_18)
            else:
                draw_text(300, y_pos, f"Player 2: {element_names[player2['element']]}", GLUT_BITMAP_HELVETICA_18)
    
    elif game_state == "level_select":
        glClearColor(0.0, 0.0, 0.0, 1)  # Black background
        draw_text(380, 700, "SELECT DIFFICULTY", GLUT_BITMAP_TIMES_ROMAN_24)
        
        if game_mode == "pvai":
            # AI mode: Easy and Hard only
            glColor3f(0.5, 1.0, 0.5)  # Light green
            draw_text(300, 550, "1 - EASY ", GLUT_BITMAP_HELVETICA_18)
            
            glColor3f(1.0, 0.3, 0.3)  # Red
            draw_text(300, 500, "3 - HARD ", GLUT_BITMAP_HELVETICA_18)
            
            glColor3f(1, 1, 1)
            draw_text(300, 350, "Easy: AI has low accuracy and slow reactions.", GLUT_BITMAP_HELVETICA_12)
            draw_text(300, 325, "Hard: AI has improved accuracy and faster reactions.", GLUT_BITMAP_HELVETICA_12)
        else:
            # PvP mode: Easy, Medium, Hard
            glColor3f(0.5, 1.0, 0.5)  # Light green
            draw_text(300, 550, "1 - EASY (Normal mode)", GLUT_BITMAP_HELVETICA_18)
            
            glColor3f(1.0, 1.0, 0.5)  # Yellow
            draw_text(300, 500, "2 - MEDIUM (Danger zones)", GLUT_BITMAP_HELVETICA_18)
            
            glColor3f(1.0, 0.3, 0.3)  # Red
            draw_text(300, 450, "3 - HARD (Watchtower snipers)", GLUT_BITMAP_HELVETICA_18)
            
            glColor3f(1, 1, 1)
            draw_text(280, 350, "Medium: White danger zones appear during defense.", GLUT_BITMAP_HELVETICA_12)
            draw_text(290, 325, "           Standing inside reduces speed by 70% and drains 1 HP/sec.", GLUT_BITMAP_HELVETICA_12)
            draw_text(280, 300, "Hard: Watchtowers shoot at defender. Each hit deals 10 damage.", GLUT_BITMAP_HELVETICA_12)
    
    elif game_state == "playing":
        glClearColor(0.0, 0.0, 0.0, 1)  # Black background
        setupCamera()
        
        draw_arena()
        draw_danger_zone()
        draw_watchtowers()
        draw_player(player1)
        draw_player(player2)
        
        if phase == "attack":
            draw_crosshair()
        
        if active_attack:
            draw_attack(active_attack)
        
        if watchtower_bullet:
            draw_watchtower_bullet(watchtower_bullet)
        
        if watchtower_bullet2:
            draw_watchtower_bullet(watchtower_bullet2)
        
        # Left panel - Player 1 (Red side)
        glColor3f(1, 0, 0)  # Red border
        draw_text(5, 785, "|", GLUT_BITMAP_TIMES_ROMAN_24)
        
        glColor3f(1, 1, 1)
        draw_text(10, 785, "PLAYER RED", GLUT_BITMAP_HELVETICA_12)
        draw_text(10, 765, f"TYPE: {element_names.get(player1['element'], 'NONE').upper()}", GLUT_BITMAP_HELVETICA_12)
        draw_text(10, 735, f"HP: {player1['hp']}/100", GLUT_BITMAP_HELVETICA_12)
        
        # HP Bar for Player 1
        hp_percentage = player1['hp'] / 100.0
        draw_bar(10, 720, 100, 8, hp_percentage, [1, 0, 0])
        
        draw_text(10, 705, f"ST: {player1['st']}/100", GLUT_BITMAP_HELVETICA_12)
        
        # ST Bar for Player 1
        st_percentage = player1['st'] / 100.0
        draw_bar(10, 690, 100, 8, st_percentage, [0, 0.5, 1])
        
        # Status effect with color coding
        if player1["status"]:
            status_colors = {
                "BURN": [1, 0, 0],      # Red
                "STUN": [1, 1, 0],      # Yellow
                "FRIZ": [0, 1, 1],      # Cyan
                "CRPL": [0.6, 0.2, 0.8],  # Purple
                "WEAK": [0.5, 0.5, 0.5],  # Gray
                "IMBL": [0.8, 0.8, 0.8]   # Light gray
            }
            status_color = status_colors.get(player1["status"], [1, 1, 1])
            glColor3f(status_color[0], status_color[1], status_color[2])
            draw_text(10, 670, f"STATUS: {player1['status']}", GLUT_BITMAP_HELVETICA_12)
        else:
            glColor3f(1, 1, 1)
            draw_text(10, 670, "STATUS: NONE", GLUT_BITMAP_HELVETICA_12)
        
        # Right panel - Player 2 (Blue side)
        glColor3f(0, 0, 1)  # Blue border
        draw_text(990, 785, "|", GLUT_BITMAP_TIMES_ROMAN_24)
        
        glColor3f(1, 1, 1)
        if game_mode == "pvai":
            draw_text(900, 785, "AI BLUE", GLUT_BITMAP_HELVETICA_12)
        else:
            draw_text(900, 785, "PLAYER BLUE", GLUT_BITMAP_HELVETICA_12)
        draw_text(900, 765, f"TYPE: {element_names.get(player2['element'], 'NONE').upper()}", GLUT_BITMAP_HELVETICA_12)
        draw_text(900, 735, f"HP: {player2['hp']}/100", GLUT_BITMAP_HELVETICA_12)
        
        # HP Bar for Player 2
        hp_percentage = player2['hp'] / 100.0
        draw_bar(900, 720, 100, 8, hp_percentage, [0, 0, 1])
        
        draw_text(900, 705, f"ST: {player2['st']}/100", GLUT_BITMAP_HELVETICA_12)
        
        # ST Bar for Player 2
        st_percentage = player2['st'] / 100.0
        draw_bar(900, 690, 100, 8, st_percentage, [0, 0.5, 1])
        
        # Status effect with color coding
        if player2["status"]:
            status_colors = {
                "BURN": [1, 0, 0],      # Red
                "STUN": [1, 1, 0],      # Yellow
                "FRIZ": [0, 1, 1],      # Cyan
                "CRPL": [0.6, 0.2, 0.8],  # Purple
                "WEAK": [0.5, 0.5, 0.5],  # Gray
                "IMBL": [0.8, 0.8, 0.8]   # Light gray
            }
            status_color = status_colors.get(player2["status"], [1, 1, 1])
            glColor3f(status_color[0], status_color[1], status_color[2])
            draw_text(900, 670, f"STATUS: {player2['status']}", GLUT_BITMAP_HELVETICA_12)
        else:
            glColor3f(1, 1, 1)
            draw_text(900, 670, "STATUS: NONE", GLUT_BITMAP_HELVETICA_12)
        
        # Bottom center - Round and phase info
        glColor3f(1, 1, 1)
        draw_text(320, 50, f"ROUND {round_number}:", GLUT_BITMAP_HELVETICA_18)
        
        if phase == "attack":
            if game_mode == "pvai" and current_turn == 2:
                glColor3f(1.0, 0.7, 0.3)  # Orange for AI
                draw_text(460, 50, "AI IS ATTACKING", GLUT_BITMAP_HELVETICA_18)
            else:
                color_name = "RED" if current_turn == 1 else "BLUE"
                glColor3f(1, 0, 0) if current_turn == 1 else glColor3f(0, 0.5, 1)
                draw_text(460, 50, f"{color_name} IS ATTACKING", GLUT_BITMAP_HELVETICA_18)
        else:
            if game_mode == "pvai" and current_turn == 1:
                glColor3f(1.0, 0.7, 0.3)  # Orange for AI
                draw_text(460, 50, "AI IS DEFENDING", GLUT_BITMAP_HELVETICA_18)
            else:
                color_name = "BLUE" if current_turn == 1 else "RED"
                glColor3f(0, 0.5, 1) if current_turn == 1 else glColor3f(1, 0, 0)
                draw_text(460, 50, f"{color_name} IS DEFENDING", GLUT_BITMAP_HELVETICA_18)
        
        # Draw popup message if active
        draw_popup()
        
        # Draw pause overlay if game is paused
        if pause:
            # Dim the entire screen
            draw_dimming_overlay()
            
            # Switch to 2D mode for pause menu text
            glMatrixMode(GL_PROJECTION)
            glPushMatrix()
            glLoadIdentity()
            gluOrtho2D(0, 1000, 0, 800)
            glMatrixMode(GL_MODELVIEW)
            glPushMatrix()
            glLoadIdentity()
            glDisable(GL_DEPTH_TEST)
            
            # Draw "GAME PAUSED" text in center (yellow)
            glColor4f(1, 1, 0, 1)  # Yellow, fully opaque
            draw_text(400, 420, "GAME PAUSED", GLUT_BITMAP_TIMES_ROMAN_24)
            
            glColor4f(1, 1, 1, 1)  # White, fully opaque
            draw_text(405, 370, "Press P to Resume", GLUT_BITMAP_HELVETICA_18)
            draw_text(360, 340, "Press BACKSPACE to return to main menu", GLUT_BITMAP_HELVETICA_12)
            
            # Restore 3D mode
            glEnable(GL_DEPTH_TEST)
            glPopMatrix()
            glMatrixMode(GL_PROJECTION)
            glPopMatrix()
            glMatrixMode(GL_MODELVIEW)
    
    elif game_state == "game_over":
        # Always show 3D scene with celebrating winner and fallen loser
        glClearColor(0.0, 0.0, 0.0, 1)  # Black background
        setupCamera()
        
        draw_arena()
        draw_danger_zone()
        draw_watchtowers()
        draw_player(player1)
        draw_player(player2)
        
        # Apply dimming overlay for better text visibility
        draw_dimming_overlay()
        
        if game_over_animation:
            # During animation, show YOU WIN popup
            draw_popup()
        else:
            # After animation, show game over text with 3D background
            # Switch to 2D mode for text overlay
            glMatrixMode(GL_PROJECTION)
            glPushMatrix()
            glLoadIdentity()
            gluOrtho2D(0, 1000, 0, 800)
            glMatrixMode(GL_MODELVIEW)
            glPushMatrix()
            glLoadIdentity()
            glDisable(GL_DEPTH_TEST)
            
            winner_player = player1 if winner == 1 else player2
            glColor4f(winner_player["color"][0], winner_player["color"][1], winner_player["color"][2], 1)
            draw_text(410, 450, "GAME OVER", GLUT_BITMAP_TIMES_ROMAN_24)
            
            if game_mode == "pvai":
                if winner == 1:
                    draw_text(405, 380, f"You Win! ({element_names[winner_player['element']]})", GLUT_BITMAP_HELVETICA_18)
                else:
                    draw_text(405, 380, f"AI Wins! ({element_names[winner_player['element']]})", GLUT_BITMAP_HELVETICA_18)
            else:
                draw_text(405, 380, f"Player {winner} ({element_names[winner_player['element']]}) Wins!", GLUT_BITMAP_HELVETICA_18)
            
            glColor4f(1, 1, 1, 1)
            draw_text(400, 320, "Press R to Return to Main Menu", GLUT_BITMAP_HELVETICA_18)
            
            # Restore 3D mode
            glEnable(GL_DEPTH_TEST)
            glPopMatrix()
            glMatrixMode(GL_PROJECTION)
            glPopMatrix()
            glMatrixMode(GL_MODELVIEW)
    
    glutSwapBuffers()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"Positron - 3D Turn-Based Battle")
    
    glEnable(GL_DEPTH_TEST)
  
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    
    glutMainLoop()

if __name__ == "__main__":
    main()