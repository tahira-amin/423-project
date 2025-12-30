from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math
import ctypes

# Define GLUT fonts using ctypes pointers
GLUT_BITMAP_HELVETICA_18 = ctypes.c_void_p(7)
GLUT_BITMAP_TIMES_ROMAN_24 = ctypes.c_void_p(6)
GLUT_BITMAP_HELVETICA_12 = ctypes.c_void_p(8)

# Camera variables
camera_pos = [0, -800, 400]
camera_angle = 0
camera_mode = "static"  # "static" or "free"
camera_distance = 600

# Game state
game_state = "menu"  # "menu", "element_select", "playing", "game_over"
current_turn = 1  # 1 or 2
phase = "attack"  # "attack", "defend", "resolution"
winner = 0
round_number = 1

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
    "jump_height": 0
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
    "jump_height": 0
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

def initialize_game():
    """Reset game to initial state"""
    global player1, player2, game_state, current_turn, active_attack, winner
    global round_number, phase
    
    player1["hp"] = 100
    player1["st"] = 0
    player1["pos"] = [0, -400, 30]
    player1["status"] = None
    player1["status_rounds"] = 0
    player1["attack_type"] = "basic"
    player1["move_speed"] = 40
    player1["jump_height"] = 0
    
    player2["hp"] = 100
    player2["st"] = 0
    player2["pos"] = [0, 400, 30]
    player2["status"] = None
    player2["status_rounds"] = 0
    player2["attack_type"] = "basic"
    player2["move_speed"] = 40
    player2["jump_height"] = 0
    
    current_turn = random.randint(1, 2)
    active_attack = None
    winner = 0
    round_number = 1
    phase = "attack"
    game_state = "playing"
    reset_crosshair()

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
    glTranslatef(0, 0, 15)
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

def draw_attack(attack):
    """Draw active attack projectile"""
    if attack is None:
        return
    
    element = attack["element"]
    color = element_colors.get(element, [1, 1, 1])
    
    glPushMatrix()
    glTranslatef(attack["x"], attack["y"], attack["z"])
    
    if attack["type"] == "basic":
        # Stacked horizontal rectangular layers (like reference image)
        num_layers = 5
        layer_height = 8
        layer_width = 50
        layer_depth = 45
        
        for i in range(num_layers):
            z_offset = i * layer_height
            brightness = 1.0 - (i * 0.15)  # Darker as we go up
            
            glPushMatrix()
            glTranslatef(0, 0, z_offset - (num_layers * layer_height / 2))
            
            # Draw rectangular layer
            glColor3f(color[0] * brightness, color[1] * brightness, color[2] * brightness)
            glBegin(GL_QUADS)
            
            # Top face
            glVertex3f(-layer_width/2, -layer_depth/2, layer_height/2)
            glVertex3f(layer_width/2, -layer_depth/2, layer_height/2)
            glVertex3f(layer_width/2, layer_depth/2, layer_height/2)
            glVertex3f(-layer_width/2, layer_depth/2, layer_height/2)
            
            # Bottom face
            glVertex3f(-layer_width/2, -layer_depth/2, -layer_height/2)
            glVertex3f(layer_width/2, -layer_depth/2, -layer_height/2)
            glVertex3f(layer_width/2, layer_depth/2, -layer_height/2)
            glVertex3f(-layer_width/2, layer_depth/2, -layer_height/2)
            
            # Front face
            glVertex3f(-layer_width/2, layer_depth/2, -layer_height/2)
            glVertex3f(layer_width/2, layer_depth/2, -layer_height/2)
            glVertex3f(layer_width/2, layer_depth/2, layer_height/2)
            glVertex3f(-layer_width/2, layer_depth/2, layer_height/2)
            
            # Back face
            glVertex3f(-layer_width/2, -layer_depth/2, -layer_height/2)
            glVertex3f(layer_width/2, -layer_depth/2, -layer_height/2)
            glVertex3f(layer_width/2, -layer_depth/2, layer_height/2)
            glVertex3f(-layer_width/2, -layer_depth/2, layer_height/2)
            
            # Left face
            glVertex3f(-layer_width/2, -layer_depth/2, -layer_height/2)
            glVertex3f(-layer_width/2, layer_depth/2, -layer_height/2)
            glVertex3f(-layer_width/2, layer_depth/2, layer_height/2)
            glVertex3f(-layer_width/2, -layer_depth/2, layer_height/2)
            
            # Right face
            glVertex3f(layer_width/2, -layer_depth/2, -layer_height/2)
            glVertex3f(layer_width/2, layer_depth/2, -layer_height/2)
            glVertex3f(layer_width/2, layer_depth/2, layer_height/2)
            glVertex3f(layer_width/2, -layer_depth/2, layer_height/2)
            
            glEnd()
            glPopMatrix()
        
    elif attack["type"] == "signature":
        # Stacked spheres forming a cone/tower (like reference image)
        num_spheres = 4
        base_radius = 32
        
        for i in range(num_spheres):
            z_offset = i * 18  # Vertical spacing
            radius = base_radius - (i * 4)  # Smaller as we go up
            brightness = 1.0 - (i * 0.1)
            
            glPushMatrix()
            glTranslatef(0, 0, z_offset - 20)
            glColor3f(color[0] * brightness, color[1] * brightness, color[2] * brightness)
            gluSphere(gluNewQuadric(), radius, 20, 20)
            glPopMatrix()
        
    elif attack["type"] == "ultimate":
        # Large expanding ground wave (trapezoid/triangle shape on ground)
        glTranslatef(0, 0, -attack["z"] + 5)
        
        # Calculate expansion based on progress
        expansion = 1.0 + (attack_progress * 0.5)  # Grows as it travels
        
        # Determine direction based on attack movement
        direction = 1 if attack["target_y"] > attack["start_y"] else -1
        
        # Main trapezoid body (stacked layers for depth)
        num_layers = 5
        layer_height = 6
        
        for layer in range(num_layers):
            z_offset = layer * layer_height
            brightness = 1.0 - (layer * 0.12)
            
            glPushMatrix()
            glTranslatef(0, 0, z_offset)
            
            glColor3f(color[0] * brightness, color[1] * brightness, color[2] * brightness)
            
            # Draw trapezoid shape
            glBegin(GL_QUADS)
            
            # Top face (trapezoid) - oriented correctly based on direction
            top_width = 80 * expansion
            bottom_width = 140 * expansion
            depth = 110 * expansion
            
            glVertex3f(-top_width, depth/2 * direction, layer_height)
            glVertex3f(top_width, depth/2 * direction, layer_height)
            glVertex3f(bottom_width, -depth/2 * direction, layer_height)
            glVertex3f(-bottom_width, -depth/2 * direction, layer_height)
            
            # Bottom face
            glVertex3f(-top_width, depth/2 * direction, 0)
            glVertex3f(top_width, depth/2 * direction, 0)
            glVertex3f(bottom_width, -depth/2 * direction, 0)
            glVertex3f(-bottom_width, -depth/2 * direction, 0)
            
            glEnd()
            
            # Side faces
            glBegin(GL_QUADS)
            
            # Front
            glVertex3f(-top_width, depth/2 * direction, 0)
            glVertex3f(top_width, depth/2 * direction, 0)
            glVertex3f(top_width, depth/2 * direction, layer_height)
            glVertex3f(-top_width, depth/2 * direction, layer_height)
            
            # Back
            glVertex3f(-bottom_width, -depth/2 * direction, 0)
            glVertex3f(bottom_width, -depth/2 * direction, 0)
            glVertex3f(bottom_width, -depth/2 * direction, layer_height)
            glVertex3f(-bottom_width, -depth/2 * direction, layer_height)
            
            # Left side
            glVertex3f(-bottom_width, -depth/2 * direction, 0)
            glVertex3f(-top_width, depth/2 * direction, 0)
            glVertex3f(-top_width, depth/2 * direction, layer_height)
            glVertex3f(-bottom_width, -depth/2 * direction, layer_height)
            
            # Right side
            glVertex3f(bottom_width, -depth/2 * direction, 0)
            glVertex3f(top_width, depth/2 * direction, 0)
            glVertex3f(top_width, depth/2 * direction, layer_height)
            glVertex3f(bottom_width, -depth/2 * direction, layer_height)
            
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
    
    # Create attack projectile
    active_attack = {
        "type": attacker["attack_type"],
        "x": float(attacker["pos"][0]),
        "y": float(attacker["pos"][1]),
        "z": 50.0,
        "start_x": float(attacker["pos"][0]),
        "start_y": float(attacker["pos"][1]),
        "target_x": float(target_x),
        "target_y": float(target_y),
        "element": attacker["element"],
        "speed": 0.8 if attacker["attack_type"] == "ultimate" else 1.2  # Slower for more reaction time
    }
    
    print(f"Attack fired! Type: {attacker['attack_type']}, From: ({attacker['pos'][0]}, {attacker['pos'][1]}), To: ({target_x}, {target_y})")
    
    # Reset timers
    attack_travel_time = 0
    attack_progress = 0
    
    # Start camera animation from attacker to defender
    global camera_animating, camera_anim_progress, camera_start_y, camera_target_y
    global camera_start_look_y, camera_target_look_y
    
    camera_animating = True
    camera_anim_progress = 0
    
    # Set camera start position (behind attacker)
    camera_start_y = -700 if current_turn == 1 else 700
    camera_start_look_y = 200 if current_turn == 1 else -200
    
    # Set camera target position (behind defender)
    camera_target_y = 700 if current_turn == 1 else -700
    camera_target_look_y = -200 if current_turn == 1 else 200
    
    # Switch to defend phase (but don't move attack yet - wait for animation)
    phase = "defend"
    defend_timer = 0

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
        # Interpolate position
        t = attack_progress
        attack["x"] = attack["start_x"] + (attack["target_x"] - attack["start_x"]) * t
        attack["y"] = attack["start_y"] + (attack["target_y"] - attack["start_y"]) * t
        
        # Arc trajectory for basic and signature attacks
        if attack["type"] != "ultimate":
            arc_height = 60 * math.sin(t * math.pi)
            attack["z"] = 50 + arc_height
        else:
            attack["z"] = 10  # Ground-level for ultimate
    else:
        # Attack reached target - resolve it
        resolve_attack()

def resolve_attack():
    """Calculate damage and effects when attack lands"""
    global active_attack, phase, current_turn, game_state, winner
    
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
        global popup_message, popup_timer
        popup_message = "DODGED!"
        popup_timer = 0
    
    # Check win condition first
    if defender["hp"] <= 0:
        game_state = "game_over"
        winner = current_turn
        active_attack = None
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
    else:
        player["move_speed"] = base_speed
    
    # Only decrement rounds when specified (at start of new round)
    if decrement_rounds and player["status_rounds"] > 0:
        player["status_rounds"] -= 1
        if player["status_rounds"] == 0:
            print(f"Status {player['status']} expired")
    
    if player["status_rounds"] <= 0:
        player["status"] = None
        player["move_speed"] = base_speed

def switch_turn():
    """Switch to other player's turn"""
    global current_turn, phase, attack_timer, round_number
    
    current_turn = 2 if current_turn == 1 else 1
    phase = "attack"
    attack_timer = 0
    
    # Track if this is the start of a new round
    is_new_round = False
    if current_turn == 1:
        round_number += 1
        is_new_round = True
    
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
    global pause, cheat_mode, game_state, camera_mode
    
    if key == b'p':
        pause = not pause
        return
    
    if key == b'l':
        if game_state == "game_over":
            game_state = "element_select"
            player1["element"] = None
            player2["element"] = None
        return
    
    if key == b'c':
        cheat_mode = not cheat_mode
        return
    
    if pause:
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
                initialize_game()
        return
    
    if game_state != "playing":
        if key == b'\r':  # Enter key
            game_state = "element_select"
        return
    
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
                defender["jump_height"] = 100
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
    
    if camera_mode == "static":
        # Handle camera animation
        if camera_animating:
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

def idle():
    """Update game state"""
    global defend_timer, attack_timer, last_time, popup_timer, popup_message
    global camera_animating, camera_anim_progress
    
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
        
        # Update jump animation
        defender = player2 if current_turn == 1 else player1
        if defender["jump_height"] > 0:
            defender["jump_height"] = max(0, defender["jump_height"] - 300 * dt)
    
    glutPostRedisplay()

def showScreen():
    """Render the scene"""
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)
    
    if game_state == "menu":
        glClearColor(0.0, 0.0, 0.0, 1)  # Black background
        draw_text(380, 450, "POSITRON", GLUT_BITMAP_TIMES_ROMAN_24)
        draw_text(300, 380, "3D Turn-Based Battle", GLUT_BITMAP_HELVETICA_18)
        draw_text(320, 320, "Press ENTER to Start", GLUT_BITMAP_HELVETICA_18)
        draw_text(200, 200, "Controls: A/D-Move  1/2/3-Attack  SPACE-Fire  Q-Parry  J-Jump", GLUT_BITMAP_HELVETICA_12)
    
    elif game_state == "element_select":
        glClearColor(0.0, 0.0, 0.0, 1)  # Black background
        draw_text(320, 700, "SELECT YOUR ELEMENT", GLUT_BITMAP_TIMES_ROMAN_24)
        draw_text(150, 600, "1 - Fire (Red)     2 - Water (Blue)     3 - Electric (Yellow)", GLUT_BITMAP_HELVETICA_18)
        draw_text(150, 550, "4 - Earth (Green)  5 - Wind (Grey)      6 - Ice (Cyan)", GLUT_BITMAP_HELVETICA_18)
        
        y_pos = 400
        if player1["element"]:
            glColor3f(player1["color"][0], player1["color"][1], player1["color"][2])
            draw_text(300, y_pos, f"Player 1: {element_names[player1['element']]}", GLUT_BITMAP_HELVETICA_18)
            y_pos -= 50
        
        if player2["element"]:
            glColor3f(player2["color"][0], player2["color"][1], player2["color"][2])
            draw_text(300, y_pos, f"Player 2: {element_names[player2['element']]}", GLUT_BITMAP_HELVETICA_18)
    
    elif game_state == "playing":
        glClearColor(0.0, 0.0, 0.0, 1)  # Black background
        setupCamera()
        
        draw_arena()
        draw_player(player1)
        draw_player(player2)
        
        if phase == "attack":
            draw_crosshair()
        
        if active_attack:
            draw_attack(active_attack)
        
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
        draw_text(685, 785, "PLAYER BLUE", GLUT_BITMAP_HELVETICA_12)
        draw_text(685, 765, f"TYPE: {element_names.get(player2['element'], 'NONE').upper()}", GLUT_BITMAP_HELVETICA_12)
        draw_text(685, 735, f"HP: {player2['hp']}/100", GLUT_BITMAP_HELVETICA_12)
        draw_text(685, 715, f"ST: {player2['st']}/100", GLUT_BITMAP_HELVETICA_12)
        
        if player2["status"]:
            draw_text(685, 695, f"SP: {player2['status']}", GLUT_BITMAP_HELVETICA_12)
        else:
            draw_text(685, 695, "SP: NONE", GLUT_BITMAP_HELVETICA_12)
        
        # Bottom center - Round and phase info
        glColor3f(1, 1, 1)
        draw_text(320, 50, f"ROUND {round_number}:", GLUT_BITMAP_HELVETICA_18)
        
        if phase == "attack":
            color_name = "RED" if current_turn == 1 else "BLUE"
            glColor3f(1, 0, 0) if current_turn == 1 else glColor3f(0, 0.5, 1)
            draw_text(460, 50, f"{color_name} IS ATTACKING", GLUT_BITMAP_HELVETICA_18)
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
        glClearColor(0.0, 0.0, 0.0, 1)  # Black background
        winner_player = player1 if winner == 1 else player2
        glColor3f(winner_player["color"][0], winner_player["color"][1], winner_player["color"][2])
        draw_text(350, 450, "GAME OVER", GLUT_BITMAP_TIMES_ROMAN_24)
        draw_text(250, 380, f"Player {winner} ({element_names[winner_player['element']]}) Wins!", GLUT_BITMAP_HELVETICA_18)
        glColor3f(1, 1, 1)
        draw_text(320, 320, "Press L to Restart", GLUT_BITMAP_HELVETICA_18)
    
    glutSwapBuffers()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"Positron - 3D Turn-Based Battle")
    
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    
    glutMainLoop()

if __name__ == "__main__":
    main()