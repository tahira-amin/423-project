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
attack_travel_time = 0
attack_progress = 0
last_time = 0

# Timing variables
defend_timer = 0
attack_timer = 0
pause = False
cheat_mode = False

# Popup message variables
popup_message = ""
popup_timer = 0
popup_duration = 2.0  # Display for 2 seconds

# Game over animation variables
game_over_animation = False
game_over_timer = 0
game_over_duration = 3.0  # 3 seconds of animation before showing final screen
loser_rotation = 0  # Rotation angle for falling animation

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
danger_zone_direction = 1  # Direction of movement: 1 for right, -1 for left
danger_zone_speed = 100  # Movement speed in units per second
danger_zone_element = "WTR"  # Danger zone represents Water element

# Watchtower (hard difficulty)
active_watchtower = None  # "left" or "right"
watchtower_bullet = None  # Active bullet from watchtower
watchtower_bullet_progress = 0
watchtower_bullet2 = None  # Second bullet from non-active watchtower
watchtower_bullet2_progress = 0
watchtower_cooldown = 0  # Cooldown between shots

def initialize_game():
    """Reset game to initial state"""
    global player1, player2, game_state, current_turn, active_attack, winner
    global round_number, phase, danger_zone_timer, danger_zone_direction
    global active_watchtower, watchtower_bullet, watchtower_bullet2, watchtower_cooldown
    global ai_decision_timer, ai_executing
    global game_over_animation, game_over_timer, loser_rotation
    
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
    danger_zone_direction = 1  # Reset direction
    active_watchtower = None
    watchtower_bullet = None
    watchtower_bullet2 = None
    watchtower_cooldown = 0
    ai_decision_timer = 0
    ai_executing = False
    game_over_animation = False
    game_over_timer = 0
    loser_rotation = 0
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
    glTranslatef(player["pos"][0], player["pos"][1], player["pos"][2] + player["jump_height"])
    
    # Apply rotation if this is the loser during game over animation
    if game_state == "game_over" and game_over_animation:
        loser = player2 if winner == 1 else player1
        if player == loser:
            glRotatef(loser_rotation, 0, 1, 0)  # Rotate around Y-axis to fall sideways
    
    # Main body sphere
    glColor3f(player["color"][0], player["color"][1], player["color"][2])
    gluSphere(gluNewQuadric(), 30, 32, 32)
    
    # Lighter top hemisphere for detail
    glColor3f(
        min(1, player["color"][0] + 0.3),
        min(1, player["color"][1] + 0.3),
        min(1, player["color"][2] + 0.3)
    )
    glPushMatrix()
    glTranslatef(0, 0, 40)
    gluSphere(gluNewQuadric(), 18, 32, 32)
    glPopMatrix()
    
    glPopMatrix()

def draw_crosshair():
    """Draw aiming crosshair on opponent's side"""
    if not crosshair_visible and not cheat_mode:
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
    Calculates Yaw (Z-rotation) and Pitch (Y-rotation) to align 
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
    
    # Calculate Yaw (Angle on ground)
    # math.atan2(y, x) gives angle from X-axis. 
    # We convert to degrees.
    yaw = math.degrees(math.atan2(dy, dx))
    
    # Calculate Pitch (Angle from ground up/down)
    # We need the horizontal magnitude to compare Z against.
    horiz_dist = math.sqrt(dx*dx + dy*dy)
    pitch = math.degrees(math.atan2(dz, horiz_dist))
    
    return yaw, pitch

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
    yaw, pitch = get_projectile_angles(attack, t)
    
    glPushMatrix()
    glTranslatef(attack["x"], attack["y"], attack["z"])
    
    # --- APPLY NEW PROJECTION ---
    glRotatef(yaw, 0, 0, 1)      # Face target
    glRotatef(-pitch, 0, 1, 0)   # Face up/down along arc
    
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
    target_x = crosshair_pos if not cheat_mode else defender["pos"][0]
    target_y = defender["pos"][1]
    
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
    
    active_attack = {
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
        "speed": 0.8 if attacker["attack_type"] == "ultimate" else 1.2
    }
    
    print(f"Attack fired! Type: {attacker['attack_type']}, From: ({start_x:.1f}, {start_y:.1f}), To: ({target_x}, {target_y})")
    
    # Reset timers
    attack_travel_time = 0
    attack_progress = 0
    
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
        global active_watchtower, watchtower_cooldown
        active_watchtower = random.choice(["left", "right"])
        watchtower_cooldown = 1.5  # 1.5 second delay before first shot
        print(f"Watchtower activated: {active_watchtower}")

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

def ai_make_attack_decision():
    """AI decides which attack type to use and fires at player 1"""
    global ai_executing
    
    ai_player = player2
    target_player = player1
    
    # AI decision logic for attack type (easy difficulty)
    # 70% basic, 20% signature, 10% ultimate (if enough stamina)
    attack_choice = random.random()
    
    if ai_player["st"] >= 100 and attack_choice > 0.9:
        ai_player["attack_type"] = "ultimate"
        print("AI chose ULTIMATE attack")
    elif ai_player["st"] >= 20 and attack_choice > 0.7:
        ai_player["attack_type"] = "signature"
        print("AI chose SIGNATURE attack")
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
    global active_attack, phase, attack_travel_time, attack_progress
    
    if active_attack is None:
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
    
    # Check if defender jumped (for ultimate)
    jumped = defender["jump_height"] > 50 and attack["type"] == "ultimate"
    
    damage = 0
    hit = False
    damage_multiplier = 1.0
    
    # Apply Cripple effect (defender takes more damage)
    if defender["status"] == "CRPL":
        damage_multiplier = 1.3
    
    # Apply Weaken effect (deal less damage)
    if attacker["status"] == "WEAK":
        damage_multiplier *= 0.7
    
    if jumped:
        # Successful jump dodge
        defender["st"] = min(100, defender["st"] + 30)
    elif attack["type"] == "basic":
        if hit_distance < 60:
            damage = int(10 * damage_multiplier)
            hit = True
        elif hit_distance < 100:
            damage = int(6 * damage_multiplier)
            hit = True
            
    elif attack["type"] == "signature":
        if hit_distance < 70:
            damage = int(20 * damage_multiplier)
            hit = True
            apply_status_effect(defender, attack["element"])
        elif hit_distance < 110:
            damage = int(12 * damage_multiplier)
            hit = True
            
    elif attack["type"] == "ultimate":
        if hit_distance < 120:
            damage = int(40 * damage_multiplier)
            hit = True
            apply_status_effect(defender, attack["element"])
        elif hit_distance < 120:
            damage = int(24 * damage_multiplier)
            hit = True
    
    if hit:
        defender["hp"] = max(0, defender["hp"] - damage)
        attacker["st"] = min(100, attacker["st"] + 10)
        print(f"HIT! Damage: {damage}, Defender HP: {defender['hp']}")
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
        player["status"] = status_name
        player["status_rounds"] = 3
        print(f"Applied status: {status_name} for 3 rounds")

def apply_status_damage(player, decrement_rounds=False):
    """Apply damage/effects from status"""
    if player["status"] == "BURN" and player["status_rounds"] > 0:
        player["hp"] = max(0, player["hp"] - 5)
        print(f"BURN damage: -5 HP")
    
    if player["status"] == "STUN" and player["status_rounds"] > 0:
        player["st"] = max(0, player["st"] - 10)  # Increased from 5 to 10
        print(f"STUN drain: -10 ST")
    
    # Update move speed based on status
    base_speed = 40
    if player["status"] == "FRIZ":
        player["move_speed"] = int(base_speed * 0.4)  # Increased from 0.6 to 0.4 (-60% speed)
        print(f"FREEZE slow: {player['move_speed']} speed")
    elif player["status"] == "STUN":
        player["move_speed"] = int(base_speed * 0.7)  # Increased from 0.9 to 0.7 (-30% speed)
    # Note: Don't reset to base_speed here - let danger zone or other mechanics handle it
    
    # Only decrement rounds when specified (at start of new round)
    if decrement_rounds and player["status_rounds"] > 0:
        player["status_rounds"] -= 1
        if player["status_rounds"] == 0:
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
    """Attempt to parry incoming attack"""
    global active_attack, defend_timer, popup_message, popup_timer, attack_travel_time
    
    if active_attack and active_attack["type"] != "ultimate":
        defender = player2 if current_turn == 1 else player1
        
        # Check if attack is close enough to parry (proximity check)
        attack_distance = math.sqrt(
            (active_attack["x"] - defender["pos"][0])**2 +
            (active_attack["y"] - defender["pos"][1])**2
        )
        
        # Only allow parry if attack is within 150 units
        if attack_distance > 150:
            print(f"Parry failed - attack too far ({attack_distance:.1f} units)")
            return
        
        # Check timing window (0.7 to 0.9 seconds into travel)
        if 0.7 < attack_travel_time < 0.9:
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
    global pause, cheat_mode, game_state, camera_mode, current_turn, level, game_mode
    
    if key == b'p':
        pause = not pause
        return
    
    if key == b'r':
        if game_state == "game_over":
            game_state = "mode_select"
            player1["element"] = None
            player2["element"] = None
        return
    
    if key == b'c':
        cheat_mode = not cheat_mode
        return
    
    if pause:
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
    
    # Attack phase controls
    if phase == "attack":
        # Movement - adjust direction based on which player is attacking
        if key == b'a':
            # Player 1 moves left (negative X), Player 2 moves right (positive X) from their perspective
            if current_turn == 1:
                attacker["pos"][0] = max(-ARENA_WIDTH + 50, 
                                         attacker["pos"][0] - attacker["move_speed"])
            else:  # Player 2
                attacker["pos"][0] = min(ARENA_WIDTH - 50, 
                                         attacker["pos"][0] + attacker["move_speed"])
        elif key == b'd':
            # Player 1 moves right (positive X), Player 2 moves left (negative X) from their perspective
            if current_turn == 1:
                attacker["pos"][0] = min(ARENA_WIDTH - 50, 
                                         attacker["pos"][0] + attacker["move_speed"])
            else:  # Player 2
                attacker["pos"][0] = max(-ARENA_WIDTH + 50, 
                                         attacker["pos"][0] - attacker["move_speed"])
        
        # Attack type selection
        elif key == b'1':
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
        
        # Fire attack
        elif key == b' ':
            fire_attack()
    
    # Defend phase controls
    elif phase == "defend":
        # In AI mode, only allow player 1 to defend when it's their turn
        if game_mode == "pvai" and current_turn == 1:
            # AI is defending, player can't control
            return
        
        # Movement - adjust direction based on which player is defending
        if key == b'a':
            # Player 1 moves left (negative X), Player 2 moves right (positive X) from their perspective
            if current_turn == 2:  # Player 1 is defending
                defender["pos"][0] = max(-ARENA_WIDTH + 50, 
                                         defender["pos"][0] - defender["move_speed"])
            else:  # Player 2 is defending
                defender["pos"][0] = min(ARENA_WIDTH - 50, 
                                         defender["pos"][0] + defender["move_speed"])
        elif key == b'd':
            # Player 1 moves right (positive X), Player 2 moves left (negative X) from their perspective
            if current_turn == 2:  # Player 1 is defending
                defender["pos"][0] = min(ARENA_WIDTH - 50, 
                                         defender["pos"][0] + defender["move_speed"])
            else:  # Player 2 is defending
                defender["pos"][0] = max(-ARENA_WIDTH + 50, 
                                         defender["pos"][0] - defender["move_speed"])
        elif key == b'e':  # Jump key changed to 'e'
            # Jump
            if defender["jump_height"] == 0:
                defender["vel"] = 600
        elif key == b'q':
            # Parry
            parry_attack()

def specialKeyListener(key, x, y):
    """Handle arrow keys for camera"""
    global camera_pos, camera_angle, camera_mode, camera_distance
    
    if camera_mode != "free":
        return
    
    if key == GLUT_KEY_UP:
        camera_pos[2] += 30
    elif key == GLUT_KEY_DOWN:
        camera_pos[2] = max(100, camera_pos[2] - 30)
    elif key == GLUT_KEY_LEFT:
        camera_angle = (camera_angle - 10) % 360
    elif key == GLUT_KEY_RIGHT:
        camera_angle = (camera_angle + 10) % 360

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
    
    # Game over: camera behind winner
    if game_state == "game_over" and game_over_animation:
        if winner == 1:
            gluLookAt(0, -700, 250,
                      0, 200, 60,
                      0, 0, 1)
        else:
            gluLookAt(0, 700, 250,
                      0, -200, 60,
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
    global game_over_timer, loser_rotation, game_over_animation
    
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
    
    # Update popup timer
    if popup_message:
        popup_timer += dt
        if popup_timer >= popup_duration:
            popup_message = ""
            popup_timer = 0
    
    # Game over animation
    if game_state == "game_over" and game_over_animation:
        game_over_timer += dt
        
        # Animate loser falling (rotate from 0 to 90 degrees over 1.5 seconds)
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
            global watchtower_cooldown, watchtower_bullet, watchtower_bullet_progress, watchtower_bullet2, watchtower_bullet2_progress
            
            # Cooldown before shooting
            if watchtower_cooldown > 0:
                watchtower_cooldown -= dt
                if watchtower_cooldown <= 0 and watchtower_bullet is None:
                    fire_watchtower_bullet()
            
            # Update bullet 1 movement (active tower - targets defender)
            if watchtower_bullet is not None:
                watchtower_bullet_progress += dt * watchtower_bullet["speed"]
                
                if watchtower_bullet_progress < 1.0:
                    # Interpolate position
                    t = watchtower_bullet_progress
                    watchtower_bullet["x"] = watchtower_bullet["start_x"] + (watchtower_bullet["target_x"] - watchtower_bullet["start_x"]) * t
                    watchtower_bullet["y"] = watchtower_bullet["start_y"] + (watchtower_bullet["target_y"] - watchtower_bullet["start_y"]) * t
                    watchtower_bullet["z"] = watchtower_bullet["start_z"] + (watchtower_bullet["target_z"] - watchtower_bullet["start_z"]) * t
                else:
                    # Bullet reached target - check hit
                    hit_distance = math.sqrt(
                        (watchtower_bullet["target_x"] - defender["pos"][0])**2 +
                        (watchtower_bullet["target_y"] - defender["pos"][1])**2
                    )
                    
                    if hit_distance < 50:  # Hit if within 50 units
                        defender["hp"] = max(0, defender["hp"] - 10)
                        print(f"Active watchtower hit! Damage: 10, HP: {defender['hp']}")
                    else:
                        print(f"Active watchtower missed! Distance: {hit_distance:.1f}")
                    
                    watchtower_bullet = None
                    watchtower_cooldown = 1.5  # 1.5 second cooldown before next shot
            
            # Update bullet 2 movement (non-active tower - random direction)
            if watchtower_bullet2 is not None:
                watchtower_bullet2_progress += dt * watchtower_bullet2["speed"]
                
                if watchtower_bullet2_progress < 1.0:
                    # Interpolate position
                    t = watchtower_bullet2_progress
                    watchtower_bullet2["x"] = watchtower_bullet2["start_x"] + (watchtower_bullet2["target_x"] - watchtower_bullet2["start_x"]) * t
                    watchtower_bullet2["y"] = watchtower_bullet2["start_y"] + (watchtower_bullet2["target_y"] - watchtower_bullet2["start_y"]) * t
                    watchtower_bullet2["z"] = watchtower_bullet2["start_z"] + (watchtower_bullet2["target_z"] - watchtower_bullet2["start_z"]) * t
                else:
                    # Bullet reached target - check if it hit defender by chance
                    hit_distance = math.sqrt(
                        (watchtower_bullet2["target_x"] - defender["pos"][0])**2 +
                        (watchtower_bullet2["target_y"] - defender["pos"][1])**2
                    )
                    
                    if hit_distance < 50:  # Lucky hit if within 50 units
                        defender["hp"] = max(0, defender["hp"] - 10)
                        print(f"Non-active watchtower lucky hit! Damage: 10, HP: {defender['hp']}")
                    else:
                        print(f"Non-active watchtower missed (as expected).")
                    
                    watchtower_bullet2 = None
        
        # Check danger zone (medium difficulty)
        if level == "medium" and game_state == "playing":
            # Update danger zone position (move back and forth)
            global danger_zone_x, danger_zone_direction
            danger_zone_x += danger_zone_direction * danger_zone_speed * dt
            
            # Bounce at arena boundaries
            half_width = danger_zone_width / 2
            max_x = ARENA_WIDTH - half_width - 30
            min_x = -ARENA_WIDTH + half_width + 30
            
            if danger_zone_x >= max_x:
                danger_zone_x = max_x
                danger_zone_direction = -1
            elif danger_zone_x <= min_x:
                danger_zone_x = min_x
                danger_zone_direction = 1
            
            # Check if defender is in danger zone
            in_danger_zone = (danger_zone_x - half_width <= defender["pos"][0] <= danger_zone_x + half_width)
            
            if in_danger_zone:
                # Element-reactive zone effects
                defender_element = defender["element"]
                damage_multiplier = 1.0
                
                # Fire player in Water zone: double damage
                if defender_element == "FIR" and danger_zone_element == "WTR":
                    damage_multiplier = 2.0
                    print("Fire player in Water zone - double damage!")
                
                # Air/Wind player: push instead of slow
                if defender_element == "WND":
                    # Push player away from center of danger zone
                    push_force = 150 * dt  # Push speed
                    if defender["pos"][0] < danger_zone_x:
                        # Push left
                        defender["pos"][0] = max(-ARENA_WIDTH + 50, defender["pos"][0] - push_force)
                    else:
                        # Push right
                        defender["pos"][0] = min(ARENA_WIDTH - 50, defender["pos"][0] + push_force)
                    print("Wind player pushed by danger zone!")
                else:
                    # Apply speed reduction (70% slower) for non-Wind players
                    base_speed = 40
                    if defender["status"] == "FRIZ":
                        defender["move_speed"] = int(base_speed * 0.4 * 0.1)  # Combine with freeze
                    elif defender["status"] == "STUN":
                        defender["move_speed"] = int(base_speed * 0.7 * 0.1)  # Combine with stun
                    else:
                        defender["move_speed"] = int(base_speed * 0.1)  # 70% reduction
                
                # Track time in danger zone and drain HP
                global danger_zone_timer
                danger_zone_timer += dt
                
                if danger_zone_timer >= 1.0:
                    damage = int(1 * damage_multiplier)
                    defender["hp"] = max(0, defender["hp"] - damage)
                    danger_zone_timer -= 1.0  # Subtract 1 second instead of reset to accumulate remainder
                    print(f"Danger zone damage! Damage: {damage}, HP: {defender['hp']}")
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
        glClearColor(0.0, 0.0, 0.0, 1)  # Black background
        draw_text(450, 450, "POSITRON", GLUT_BITMAP_TIMES_ROMAN_24)
        draw_text(420, 360, "3D Turn-Based Battle", GLUT_BITMAP_HELVETICA_18)
        draw_text(420, 320, "Press ENTER to Start", GLUT_BITMAP_HELVETICA_18)
        draw_text(300, 200, "Controls: A/D-Move  1/2/3-Attack  SPACE-Fire  Q-Parry  E-Jump", GLUT_BITMAP_HELVETICA_12)
    
    elif game_state == "mode_select":
        glClearColor(0.0, 0.0, 0.0, 1)  # Black background
        draw_text(360, 700, "SELECT GAME MODE", GLUT_BITMAP_TIMES_ROMAN_24)
        
        glColor3f(0.5, 0.8, 1.0)  # Light blue
        draw_text(360, 550, "1 - PLAYER VS PLAYER", GLUT_BITMAP_HELVETICA_18)
        draw_text(350, 510, "Two players battle against each other", GLUT_BITMAP_HELVETICA_12)
        
        glColor3f(1.0, 0.7, 0.3)  # Orange
        draw_text(360, 430, "2 - PLAYER VS AI", GLUT_BITMAP_HELVETICA_18)
        draw_text(350, 390, "Battle against computer-controlled opponent", GLUT_BITMAP_HELVETICA_12)
    
    elif game_state == "element_select":
        glClearColor(0.0, 0.0, 0.0, 1)  # Black background
        draw_text(380, 700, "SELECT YOUR ELEMENT", GLUT_BITMAP_TIMES_ROMAN_24)
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
        draw_text(10, 715, f"ST: {player1['st']}/100", GLUT_BITMAP_HELVETICA_12)
        
        if player1["status"]:
            draw_text(10, 695, f"SP: {player1['status']}", GLUT_BITMAP_HELVETICA_12)
        else:
            draw_text(10, 695, "SP: NONE", GLUT_BITMAP_HELVETICA_12)
        
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
        draw_text(900, 715, f"ST: {player2['st']}/100", GLUT_BITMAP_HELVETICA_12)
        
        if player2["status"]:
            draw_text(900, 695, f"SP: {player2['status']}", GLUT_BITMAP_HELVETICA_12)
        else:
            draw_text(900, 695, "SP: NONE", GLUT_BITMAP_HELVETICA_12)
        
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
        
        if cheat_mode:
            glColor3f(1, 0, 0)
            draw_text(400, 20, "CHEAT MODE", GLUT_BITMAP_HELVETICA_12)
        
        # Draw popup message if active
        draw_popup()
    
    elif game_state == "game_over":
        # During animation, show 3D scene with camera behind winner
        if game_over_animation:
            glClearColor(0.0, 0.0, 0.0, 1)  # Black background
            setupCamera()
            
            draw_arena()
            draw_danger_zone()
            draw_watchtowers()
            draw_player(player1)
            draw_player(player2)
            
            # Draw YOU WIN popup
            draw_popup()
        else:
            # After animation, show traditional game over screen
            glClearColor(0.0, 0.0, 0.0, 1)  # Black background
            winner_player = player1 if winner == 1 else player2
            glColor3f(winner_player["color"][0], winner_player["color"][1], winner_player["color"][2])
            draw_text(400, 450, "GAME OVER", GLUT_BITMAP_TIMES_ROMAN_24)
            
            if game_mode == "pvai":
                if winner == 1:
                    draw_text(400, 380, f"You Win! ({element_names[winner_player['element']]})", GLUT_BITMAP_HELVETICA_18)
                else:
                    draw_text(400, 380, f"AI Wins! ({element_names[winner_player['element']]})", GLUT_BITMAP_HELVETICA_18)
            else:
                draw_text(400, 380, f"Player {winner} ({element_names[winner_player['element']]}) Wins!", GLUT_BITMAP_HELVETICA_18)
            
            glColor3f(1, 1, 1)
            draw_text(400, 320, "Press R to Restart", GLUT_BITMAP_HELVETICA_18)
    
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