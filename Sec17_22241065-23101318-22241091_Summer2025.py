from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18
import random
import math
import time

screenX, screenY = 1400, 900
fovY = 110  # Field of view
height = 1400

# Globals
globalTime = 0
lastTime = time.time()
deltaTime = 0  # New: for frame rate independent movement
targetFPS = 60  # Target frame rate
health = 5
totalScore = 0  # New global for score that persists across levels
bulletsMissed = 0 # No longer used for game over, but kept for historical purposes.
startX, startY = 100,100
grid = 13
floorLength = 250
wave = 1
step = 0.01
midpoint = (startX + grid*(floorLength) + startX) / 2
spawn_margin = 300
spawn_min_x = startX + spawn_margin
spawn_max_x = (startX + grid * floorLength) - spawn_margin
spawn_min_y = startY + spawn_margin  
spawn_max_y = (startY + grid * floorLength) - spawn_margin
victory = False 
a = random.randint(spawn_min_x, spawn_max_x)
b = random.randint(spawn_min_y, spawn_max_y)
playerPos = [a, b, 0]
turnAngle = 0
cameraAngle = 90
pov = "third"
bulletFired = False
bulletRadius = 20
enemyRadius = 100
gameOver = False
enemyList = []
bullets = []
sv_cheats = False
cheatAngle = 0
fire_man_active = False # New cheat variable
bulletSpeed = 50
bulletDamage = 1 # Initial bullet damage

keys_pressed = {}
move_speed = 15
player_on_ground = True
speedBoostTimer = 0
maxSpeedBoostTime = 300  # 5 seconds at 60 FPS
speedPowerupCount = 0

is_reloading = False
reload_timer = 0
reload_time = 90  
gun_ammo = 30
gun_max_ammo = 30
status_message = ""

# --- WEAPON VARIABLES ---
current_weapon = "default" # Can be "default" or "shotgun"

# Shotgun Stats
shotgun_ammo = 10
shotgun_max_ammo = 10
shotgun_pellets = 6 # Number of pellets per shot
shotgun_spread = 25 # Angle of the cone of fire in degrees
shotgun_pellet_radius = 15

# --- BOSS VARIABLES ---
boss_active = False
boss_health = 100
boss_max_health = 100
boss_radius = 250
boss_pos = [midpoint, midpoint, 0]
boss_bullets = []
boss_attack_cooldown = 240 # Cooldown timer in frames
boss_attack_timer = 0

# --- ARMOR VARIABLES ---
kill_streak = 0
armor_active = False
armor_health = 5
armor_max_health = 5

# --- DRONE VARIABLES ---
drone_pos = [playerPos[0] + 60, playerPos[1] - 60, 100]
drone_speed = 8
drone_bullets = []
drone_bullet_radius = 15
drone_shoot_cooldown = 300 # 5 seconds at approx 60fps
drone_shoot_timer = 0

# --- LAVA PIT VARIABLES ---
lava_patches = []
lava_damage_cooldown = 60 # 1 second at 60fps
lava_damage_timer = 0

level = 1
killsInLevel = 0
kills_required_for_level_up = 10
if level == 2:
    kills_required_for_level_up = 20
can_enter_portal = False
Epressed = False
lastHealthIncreaseTime = time.time() # New global to track health increases
enemyHealthIncrement = 5 # New global for enemy health increment

# New globals for powerups, destructible objects, enemy health, and bombs
healthPowerups = []
speedPowerups = []
damagePowerups = []
bombPowerups = []
destructiveObjects = []
trees = []
rocks = []
bombCount = 0
bomb_explosion = None # New variable to store bomb explosion info
bomb_explosion_duration = 30 # Number of frames for explosion animation
bomb_explosion_radius = 1000 # NEW: Larger radius for bomb explosion
bulletPowerupCount = 0

# Level configurations with portal coordinates
levels = [
    {"portal": (500, 500, 0)},
    {"portal": (2000, 2000, 0)},
    {"portal": (1000, 200, 0)},
]
portalC = levels[level-1]["portal"]

floorPatches = []
# Colors for each level
level_colors = {
    1: {'walls': [229/255, 207/255, 190/255], 'floor_base': [92/255, 69/255, 64/255]},
    2: {'walls': [140/255, 140/255, 140/255], 'floor_base': [50/255, 50/255, 50/255]},
    3: {'walls': [100/255, 0/255, 0/255], 'floor_base': [30/255, 0/255, 0/255]},
}

# Initialize bounds
xbound = (startX, (startX + (grid * floorLength)))
ybound = (startY, (startY + (grid * floorLength)))
zbound = (0, 300)

# Initialize cooldown
cooldown = 0

def render_tree(x, y, z):
    glPushMatrix()
    glTranslatef(x, y, z)
    
    # Tree trunk
    glColor3f(101/255, 67/255, 33/255)  # Brown
    gluCylinder(gluNewQuadric(), 40, 30, 200, 10, 10)
    
    # Pine cone tree (3 stacked cones for fuller look)
    glTranslatef(0, 0, 150)
    
    # Bottom cone layer
    glColor3f(34/255, 139/255, 34/255)  # Forest green
    glutSolidCone(200, 150, 15, 15)
    
    # Middle cone layer
    glTranslatef(0, 0, 100)
    glColor3f(46/255, 125/255, 50/255)  # Slightly different green
    glutSolidCone(160, 120, 15, 15)
    
    # Top cone layer
    glTranslatef(0, 0, 80)
    glColor3f(60/255, 179/255, 113/255)  # Medium sea green
    glutSolidCone(120, 100, 15, 15)
    
    glPopMatrix()

def checkPortal():
    global level, playerPos, can_enter_portal

    if level > len(levels):
        return

    px, py, _ = playerPos
    portal = levels[level-1]["portal"]

    minX = portal[0] - 100
    maxX = portal[0] + 100
    minY = portal[1] - 100
    maxY = portal[1] + 100

    if minX <= px <= maxX and minY <= py <= maxY and killsInLevel >= kills_required_for_level_up:
        can_enter_portal = True
        draw_text(screenX//2 - 200, screenY - 50, "Press E to enter the portal!", font=GLUT_BITMAP_HELVETICA_18)
    else:
        can_enter_portal = False

def enterPortal():
    global level, playerPos, can_enter_portal, Epressed, levels, killsInLevel, totalScore, gameOver, enemyList, boss_active

    if can_enter_portal and Epressed:
        if level < len(levels):
            level += 1
            print(f"Entered portal! Now on Level {level}")
            playerPos = [random.randint(spawn_min_x, spawn_max_x), random.randint(spawn_min_y, spawn_max_y), 0]
            killsInLevel = 0
            # Reset the game state for the new level
            enemyList.clear()
            healthPowerups.clear()
            speedPowerups.clear()
            damagePowerups.clear()
            destructiveObjects.clear()
            bombPowerups.clear()
            
            if level == 3:
                #generate_boss()
                boss_active = True
            else:
                boss_active = False
                for _ in range(5):
                    generate_enemy()
            
            for _ in range(3):
                generate_health_powerup()
            for _ in range(2):
                generate_speed_powerup()
            for _ in range(2):
                generate_damage_powerup()
            for _ in range(5):
                generate_destructive_object()
            for _ in range(2):
                generate_bomb_powerup()

        else:
            print("You have completed all levels!")
            gameOver = True
            
        can_enter_portal = False
        Epressed = False

# def use_bomb():
#     global bombCount, enemyList, destructiveObjects, totalScore, killsInLevel, bomb_explosion
#     if bombCount > 0:
#         bombCount -= 1
#         print(f"Bomb used! Enemies and rocks cleared.")
        
#         # Add score for all enemies killed by the bomb
#         totalScore += len(enemyList)
        
#         # Clear enemies and some rocks
#         enemyList.clear()
        
#         # Remove a random number of destructive objects, but not all of them
#         num_to_remove = len(destructiveObjects) // 2
#         for _ in range(num_to_remove):
#             if destructiveObjects:
#                 destructiveObjects.pop(random.randint(0, len(destructiveObjects) - 1))
        
#         bomb_explosion = {'pos': list(playerPos), 'timer': bomb_explosion_duration}

def use_bomb():
    global bombCount, enemyList, destructiveObjects, totalScore, killsInLevel, bomb_explosion
    if bombCount > 0:
        bombCount -= 1
        print(f"Bomb used!")
        
        bomb_pos = list(playerPos)
        enemies_killed = 0
        
        # Check each enemy to see if it's within bomb radius
        for i in range(len(enemyList) - 1, -1, -1):
            enemy_pos = enemyList[i]
            dx = enemy_pos[0] - bomb_pos[0]
            dy = enemy_pos[1] - bomb_pos[1]
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance <= bomb_explosion_radius:
                enemyList.pop(i)
                enemies_killed += 1
                totalScore += 1
                killsInLevel += 1
        
        # Remove destructive objects within radius
        objects_destroyed = 0
        for i in range(len(destructiveObjects) - 1, -1, -1):
            obj_pos = destructiveObjects[i]
            dx = obj_pos[0] - bomb_pos[0]
            dy = obj_pos[1] - bomb_pos[1]
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance <= bomb_explosion_radius:
                destructiveObjects.pop(i)
                objects_destroyed += 1
        
        
        for i in range(len(trees) - 1, -1, -1):
            tree_pos = trees[i]
            dx = tree_pos[0] - bomb_pos[0]
            dy = tree_pos[1] - bomb_pos[1]
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance <= bomb_explosion_radius:
                trees.pop(i)
        
        print(f"Bomb killed {enemies_killed} enemies and destroyed {objects_destroyed} objects!")
        bomb_explosion = {'pos': bomb_pos, 'timer': bomb_explosion_duration}


def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1,1,1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    
    # Set up an orthographic projection that matches window coordinates
    gluOrtho2D(0, screenX, 0, screenY)  # left, right, bottom, top
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Draw text at (x, y) in screen coordinates
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    
    # Restore original projection and modelview matrices
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def reload_gun():
    global is_reloading, reload_timer, current_weapon
    if not is_reloading:
        if current_weapon == "shotgun" and shotgun_ammo < shotgun_max_ammo:
            is_reloading = True
            reload_timer = reload_time
        elif current_weapon == "default" and gun_ammo < gun_max_ammo:
            is_reloading = True
            reload_timer = reload_time

def updateVariables():
    global playerPos, turnAngle, xbound, ybound, player_on_ground, is_reloading, reload_timer, gun_ammo, status_message, move_speed, speedBoostTimer
    global destructiveObjects, current_weapon, shotgun_ammo
    
    if gameOver:
        return
        
    if current_weapon == "default" and gun_ammo <= 0 and not is_reloading:
        status_message = "Out of ammo! Press T to reload."
    elif current_weapon == "shotgun" and shotgun_ammo <= 0 and not is_reloading:
        status_message = "Out of ammo! Press T to reload."
    elif is_reloading:
        status_message = "RELOADING..."
    else:
        status_message = ""

    if is_reloading:
        reload_timer -= 1
        if reload_timer <= 0:
            is_reloading = False
            if current_weapon == "shotgun":
                shotgun_ammo = shotgun_max_ammo
            else:
                gun_ammo = gun_max_ammo
            status_message = ""
        
    # # Handle horizontal movement continuously
    # dx, dy = 0, 0
    # current_speed = move_speed
    # if speedBoostTimer > 0:
    #     current_speed *= 1.5
    #     speedBoostTimer -= 1
        
    # if keys_pressed.get(b'w', False):
    #     theta = math.radians(turnAngle-90)
    #     dx += current_speed * math.cos(theta)
    #     dy += current_speed * math.sin(theta)
    
    # if keys_pressed.get(b's', False):
    #     theta = math.radians(turnAngle-90)
    #     dx -= current_speed * math.cos(theta)
    #     dy -= current_speed * math.sin(theta)
    
    # if keys_pressed.get(b'd', False):
    #     turnAngle -= 5
    
    # if keys_pressed.get(b'a', False):
    #     turnAngle += 5

    # newx = playerPos[0] + dx
    # newy = playerPos[1] + dy
    
    # can_move = True

    # if playerPos[2] <= 0.1:
    #     for obj in destructiveObjects:
    #         if checkCollision([newx, newy, playerPos[2]], obj, 50, 50):
    #             can_move = False
    #             break

    # xmin, xmax = xbound[0], xbound[1]
    # ymin, ymax = ybound[0], ybound[1]
    # if can_move and (newx >= xmin and newx <= xmax and newy >= ymin and newy <= ymax):
    #     playerPos[0] += dx
    #     playerPos[1] += dy
def grab_powerup():
    global health, healthPowerups, speedBoostTimer, bulletDamage, speedPowerups, damagePowerups, bombCount, bombPowerups, speedPowerupCount, bulletPowerupCount
    
    # Check for health powerup
    for i in range(len(healthPowerups) - 1, -1, -1):
        pu_pos = healthPowerups[i]
        if checkCollision(playerPos, pu_pos, 100, 50):
            healthPowerups.pop(i)
            health = min(health + 2, 5)
            print(f"Health powerup grabbed! Health is now {health}")
            return
            
    # Check for movement speed powerup - now gives permanent boost
    for i in range(len(speedPowerups) - 1, -1, -1):
        pu_pos = speedPowerups[i]
        if checkCollision(playerPos, pu_pos, 100, 50):
            speedPowerups.pop(i)
            speedPowerupCount += 1
            print(f"Permanent speed boost acquired! Speed boosts: {speedPowerupCount}")
            return

    # Check for bullet damage powerup
    for i in range(len(damagePowerups) - 1, -1, -1):
        pu_pos = damagePowerups[i]
        if checkCollision(playerPos, pu_pos, 100, 50):
            damagePowerups.pop(i)
            bulletDamage += 2 # Stackable
            bulletPowerupCount += 1
            print(f"Bullet damage increased! Current damage: {bulletDamage}")
            return

    # Check for bomb powerup
    for i in range(len(bombPowerups) - 1, -1, -1):
        pu_pos = bombPowerups[i]
        if checkCollision(playerPos, pu_pos, 100, 50):
            bombPowerups.pop(i)
            bombCount += 1
            print(f"Bomb powerup grabbed! You now have {bombCount} bombs.")
            return

def updateCameraPosition():
    global cameraPos, cameraLookAt, cameraAngle, cheatAngle, turnAngle
    
    midpoint = startX + (grid * floorLength) / 2
    cameraLookAt = [midpoint, midpoint, 0]

    distance = 1600
    
    theta = math.radians(cameraAngle)
    camera_x = midpoint + distance * math.cos(theta)
    camera_y = midpoint + distance * math.sin(theta)
    camera_z = height
    
    cameraPos = [camera_x, camera_y, camera_z]

def setupCamera():
    global cameraPos, cameraLookAt, playerPos, turnAngle, pov, height
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, screenX/screenY, 0.1, 6500)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if pov == "first":
        camera_x = playerPos[0]
        camera_y = playerPos[1] 
        camera_z = playerPos[2] + 250

        theta = math.radians(turnAngle-90)
        look_x = playerPos[0] + (math.cos(theta) * 100)
        look_y = playerPos[1] + (math.sin(theta) * 100)
        look_z = playerPos[2] + 250 
        
        gluLookAt(camera_x, camera_y, camera_z,    # Camera position
                look_x, look_y, look_z,          # Look-at target
                0, 0, 1)                         # Up vector

    elif pov == "third":
        updateCameraPosition()
        
        gluLookAt(cameraPos[0], cameraPos[1], cameraPos[2],      # Camera position
                cameraLookAt[0], cameraLookAt[1], cameraLookAt[2], # Look-at target
                0, 0, 1)
        
    elif pov == "firstcheat":
        camera_x = playerPos[0]
        camera_y = playerPos[1] 
        camera_z = playerPos[2] + 250

        theta = math.radians(cheatAngle-90)
        look_x = playerPos[0] + (math.cos(theta) * 100)
        look_y = playerPos[1] + (math.sin(theta) * 100)
        look_z = playerPos[2] + 250 
        
        gluLookAt(camera_x, camera_y, camera_z,    # Camera position
                look_x, look_y, look_z,          # Look-at target
                0, 0, 1)                         # Up vector

def keyboardListener(key, x, y):
    global turnAngle, xbound, ybound, gameOver, sv_cheats, pov, keys_pressed, status_message, player_on_ground, current_weapon, fire_man_active, Epressed, speedPowerupCount, speedBoostTimer
    
    if key == b'1':
        current_weapon = "shotgun"
        print("Switched to Shotgun")
        return
    if key == b'2':
        current_weapon = "default"
        print("Switched to Default Gun")
        return
    

    if not gameOver:
        # move_distance = 50
        # if speedBoostTimer > 0:
        #     move_distance = int(move_distance * 1.25)  
        #     speedBoostTimer -= 1
        
        # if key == b'w':
        #     theta = math.radians(turnAngle-90)
        #     xmin, xmax = xbound[0], xbound[1]
        #     ymin, ymax = ybound[0], ybound[1]
        #     newx = playerPos[0] + move_distance*math.cos(theta)
        #     newy = playerPos[1] + move_distance*math.sin(theta)
            
        #     # Check collision with trees and destructible objects
        #     can_move = True
        #     for obj in destructiveObjects:
        #         if checkCollision([newx, newy, playerPos[2]], obj, 100, 100):
        #             can_move = False
        #             break
            
        #     if can_move:
        #         for tree in trees:
        #             if checkCollision([newx, newy, playerPos[2]], tree, 80, 60):
        #                 can_move = False
        #                 break
            
        #     # Check boundaries and move if allowed
        #     if can_move and (newx - 100 >= xmin and newx + 100 <= xmax and newy - 100 >= ymin and newy + 100 <= ymax):
        #         playerPos[0] += move_distance*math.cos(theta)
        #         playerPos[1] += move_distance*math.sin(theta)
            
        # # Move backward (S key)
        # if key == b's':
        #     theta = math.radians(turnAngle-90)
        #     xmin, xmax = xbound[0], xbound[1]
        #     ymin, ymax = ybound[0], ybound[1]
        #     newx = playerPos[0] - move_distance*math.cos(theta)
        #     newy = playerPos[1] - move_distance*math.sin(theta)
            
        #     can_move = True
        #     for obj in destructiveObjects:
        #         if checkCollision([newx, newy, playerPos[2]], obj, 100, 100):
        #             can_move = False
        #             break
            
        #     if can_move:
        #         for tree in trees:
        #             if checkCollision([newx, newy, playerPos[2]], tree, 80, 60):
        #                 can_move = False
        #                 break
            
           
        #     if can_move and (newx - 100 >= xmin and newx + 100 <= xmax and newy - 100 >= ymin and newy + 100 <= ymax):
        #         playerPos[0] -= move_distance*math.cos(theta)
        #         playerPos[1] -= move_distance*math.sin(theta)
        
        base_move_distance = 50
        speed_multiplier = 1.0 + (speedPowerupCount * 0.1)  # 10% increase per powerup
        move_distance = int(base_move_distance * speed_multiplier)
        
        if key == b'w':
            theta = math.radians(turnAngle-90)
            xmin, xmax = xbound[0], xbound[1]
            ymin, ymax = ybound[0], ybound[1]
            newx = playerPos[0] + move_distance*math.cos(theta)
            newy = playerPos[1] + move_distance*math.sin(theta)
            
            # Check collision with trees and destructible objects
            can_move = True
            for obj in destructiveObjects:
                if checkCollision([newx, newy, playerPos[2]], obj, 100, 100):
                    can_move = False
                    break
            
            if can_move:
                for tree in trees:
                    if checkCollision([newx, newy, playerPos[2]], tree, 80, 60):
                        can_move = False
                        break
            
            # Check boundaries and move if allowed
            if can_move and (newx - 100 >= xmin and newx + 100 <= xmax and newy - 100 >= ymin and newy + 100 <= ymax):
                playerPos[0] += move_distance*math.cos(theta)
                playerPos[1] += move_distance*math.sin(theta)
            
        # Move backward (S key)
        if key == b's':
            theta = math.radians(turnAngle-90)
            xmin, xmax = xbound[0], xbound[1]
            ymin, ymax = ybound[0], ybound[1]
            newx = playerPos[0] - move_distance*math.cos(theta)
            newy = playerPos[1] - move_distance*math.sin(theta)
            
            can_move = True
            for obj in destructiveObjects:
                if checkCollision([newx, newy, playerPos[2]], obj, 100, 100):
                    can_move = False
                    break
            
            if can_move:
                for tree in trees:
                    if checkCollision([newx, newy, playerPos[2]], tree, 80, 60):
                        can_move = False
                        break
            
           
            if can_move and (newx - 100 >= xmin and newx + 100 <= xmax and newy - 100 >= ymin and newy + 100 <= ymax):
                playerPos[0] -= move_distance*math.cos(theta)
                playerPos[1] -= move_distance*math.sin(theta)

        # Rotate gun left (A key)
        if key == b'a':
            turnAngle += 8

        # Rotate gun right (D key)
        if key == b'd':
            turnAngle -= 8
        
        # Toggle cheat mode (C key)
        if key == b'y':
            drone_shoot()
        if key == b'c':
            sv_cheats = not sv_cheats
            if not sv_cheats:
                fire_man_active = False # Disable fire man if cheats are off
            print(f"sv_cheats {1 if sv_cheats else 0}")
        if key == b'i' and sv_cheats:
            fire_man_active = not fire_man_active
            print(f"Fire Man mode {'ACTIVATED' if fire_man_active else 'DEACTIVATED'}")
        if key == b'v' and sv_cheats:
            pov = "firstcheat" if pov == "first" else "first"
        if key == b't':
            reload_gun()
        if key == b'b':
            use_bomb()
        if key == b'e':
            Epressed = True
            enterPortal()

    # Reset the game if R key is pressed
    if key == b'r':
        if gameOver:
            gameOver = False
            reinitialize()

def specialKeyListener(key, x, y):
    global cameraPos, cameraLookAt, cameraAngle, height
    
    if key == GLUT_KEY_LEFT:
        cameraAngle -= 2
        
    elif key == GLUT_KEY_RIGHT:
        cameraAngle += 2 
        
    elif key == GLUT_KEY_UP:
        height += 50
    
    elif key == GLUT_KEY_DOWN:
        if height <= 50:
            return
        height -= 50
    
    glutPostRedisplay()

def mouseListener(button, state, x, y):
    global pov, bulletFired, gameOver, gun_ammo, is_reloading
    global current_weapon, shotgun_ammo, bullets, fire_man_active

    if not gameOver:
        if not fire_man_active: # Player cannot shoot when in fire man mode
            if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
                if current_weapon == "default":
                    if gun_ammo > 0 and not is_reloading:
                        bulletFired = True
                        coords = [playerPos[0], playerPos[1], turnAngle, bulletRadius]
                        bullets.append(coords)
                        gun_ammo -= 1

                elif current_weapon == "shotgun":
                    if shotgun_ammo > 0 and not is_reloading:
                        bulletFired = True
                        for _ in range(shotgun_pellets):
                            spread = random.uniform(-shotgun_spread / 2, shotgun_spread / 2)
                            pellet_angle = turnAngle + spread
                            coords = [playerPos[0], playerPos[1], pellet_angle, shotgun_pellet_radius]
                            bullets.append(coords)
                        shotgun_ammo -= 1

        if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
            pov = "first" if pov == "third" else "third"

    glutPostRedisplay()

def raycast():
    global cheatAngle, playerPos, enemyList, enemyRadius, bulletFired, wave, cooldown, fire_man_active

    if cooldown > 0 or fire_man_active: # Aimbot doesn't shoot in fire man mode
        return

    startX_ray, startY_ray, startZ = playerPos[0], playerPos[1], 100
    theta = math.radians(cheatAngle-90)
    rayDirection = [math.cos(theta), math.sin(theta), 0]

    maxDistance = 2000
    for i in range(0, maxDistance, 10):
        rayX = startX_ray + (i * rayDirection[0])
        rayY = startY_ray + (i * rayDirection[1])

        for j in range(len(enemyList)):
            ex, ey, ez = enemyList[j][0], enemyList[j][1], enemyList[j][2]
            dx, dy = rayX - ex, rayY - ey
            distance = math.sqrt((dx*dx) + (dy*dy))
            if distance - (enemyRadius * wave) <= 0:
                bulletFired = True
                coords = [playerPos[0], playerPos[1], cheatAngle, bulletRadius]
                bullets.append(coords)
                cooldown = 5
                return

def cheatMode():
    global sv_cheats, cheatAngle, cooldown
    if cooldown > 0:
        cooldown -= 1
    cheatAngle += 10
    raycast()

def reinitialize():
    global health, totalScore, bulletsMissed, wave, playerPos, turnAngle, pov, gameOver, enemyList, bullets
    global sv_cheats, drone_pos, is_reloading, reload_timer, gun_ammo, status_message, speedBoostTimer, bulletSpeed
    global globalTime, lastTime, bombCount, bulletDamage, current_weapon, shotgun_ammo, boss_active, boss_bullets
    global kill_streak, armor_active, armor_health, fire_man_active, drone_bullets, drone_shoot_timer
    global lava_patches, lava_damage_timer, healthPowerups, speedPowerups, damagePowerups, destructiveObjects, bombPowerups
    global level, killsInLevel, can_enter_portal, Epressed, portalC, lastHealthIncreaseTime, speedPowerupCount, bulletPowerupCount
    global victory, trees, rocks, floorPatches, boss_health, boss_attack_timer, enemyHealthIncrement
    
    globalTime = 0
    victory = False
    trees = []
    rocks = []
    lastTime = time.time()
    lastHealthIncreaseTime = time.time()
    health = 5
    totalScore = 0
    bulletsMissed = 0
    wave = 1
    step = 0.01
    playerPos = [random.randint(spawn_min_x, spawn_max_x), random.randint(spawn_min_y, spawn_max_y), 0]
    turnAngle = 0
    pov = "third"
    bulletFired = False
    gameOver = False
    enemyList = []
    bullets = []
    sv_cheats = False
    drone_pos = [playerPos[0] + 60, playerPos[1] - 60, 100]
    
    is_reloading = False
    reload_timer = 0
    gun_ammo = gun_max_ammo
    shotgun_ammo = shotgun_max_ammo
    current_weapon = "default"
    status_message = ""
    
    speedBoostTimer = 0
    bulletSpeed = 50
    bulletDamage = 1
    speedPowerupCount = 0
    bulletPowerupCount = 0
    enemyHealthIncrement = 2
    
    healthPowerups = []
    speedPowerups = []
    damagePowerups = []
    bombPowerups = []
    destructiveObjects = []
    bombCount = 0
    
    level = 1
    killsInLevel = 0
    can_enter_portal = False
    Epressed = False
    portalC = levels[level-1]["portal"]
    
    boss_active = False
    boss_health = boss_max_health
    boss_bullets = []
    boss_attack_timer = 0

    kill_streak = 0
    armor_active = False
    armor_health = armor_max_health
    fire_man_active = False
    drone_bullets = []
    drone_shoot_timer = 0

    lava_damage_timer = 0
    
    for _ in range(5):
        generate_enemy()
    for _ in range(3):
        generate_health_powerup()
    for _ in range(2):
        generate_speed_powerup()
    for _ in range(2):
        generate_damage_powerup()
    for _ in range(5):
        generate_destructive_object()
    for _ in range(2):
        generate_bomb_powerup()
    for _ in range(10): 
        trees.append([random.randrange(200, 2600), random.randrange(200, 2600), 0])
    
    generate_floorPatches()

def generate_floorPatches():
    global floorPatches, grid, lava_patches
    floorPatches = []
    lava_patches = []

    patch_colors = [
        [160/255, 82/255, 45/255], [139/255, 69/255, 19/255], [105/255, 105/255, 105/255],
        [85/255, 107/255, 47/255], [46/255, 125/255, 50/255],
    ]

    num_patches = random.randint(3, 8)
    num_lava_patches = 2

    for i in range(num_patches + num_lava_patches):
        patch_size = random.choice([2, 3])

        start_x_idx = random.randint(0, grid - patch_size)
        start_y_idx = random.randint(0, grid - patch_size)

        patch_type = 'lava' if i >= num_patches else 'normal'

        patch = {
            'start_x': start_x_idx,
            'start_y': start_y_idx,
            'size': patch_size,
            'color': random.choice(patch_colors) if patch_type == 'normal' else None,
            'type': patch_type
        }
        floorPatches.append(patch)

        if patch_type == 'lava':
            lava_patches.append(patch)

def floor():
    global startX, startY, grid, floorLength, floorPatches, globalTime, level_colors, level
    z = 0

    if not floorPatches:
        generate_floorPatches()

    patch_grid = [[None for _ in range(grid)] for _ in range(grid)]

    for patch in floorPatches:
        for i in range(patch['size']):
            for j in range(patch['size']):
                patch_x = patch['start_x'] + j
                patch_y = patch['start_y'] + i
                if patch_x < grid and patch_y < grid:
                    patch_grid[patch_y][patch_x] = patch

    glBegin(GL_QUADS)

    for i in range(grid):
        for j in range(grid):
            cell_patch = patch_grid[i][j]
            if cell_patch and cell_patch['type'] == 'lava':
                pulse = 0.75 + 0.25 * math.sin(globalTime * 3)
                glColor3f(1.0 * pulse, 0.2 * pulse, 0.0)
            elif cell_patch:
                color = cell_patch['color']
                glColor3f(color[0], color[1], color[2])
            else:
                floor_base_color = level_colors[level]['floor_base']
                glColor3f(floor_base_color[0], floor_base_color[1], floor_base_color[2])

            x = startX + j * floorLength
            y = startY + i * floorLength

            glVertex3f(x, y, z)
            glVertex3f(x + floorLength, y, z)
            glVertex3f(x + floorLength, y + floorLength, z)
            glVertex3f(x, y + floorLength, z)
    glEnd()

def walls():
    global startX, startY, floorLength, grid, level_colors, level
    glBegin(GL_QUADS)
    z = 400
    
    wall_color = level_colors[level]['walls']
    glColor3f(wall_color[0], wall_color[1], wall_color[2])
    
    glVertex3f(startX,startY,0)
    glVertex3f(startX+(grid*floorLength),startY,0)
    glVertex3f(startX+(grid*floorLength),startY,z)
    glVertex3f(startX,startY,z)
    
    glVertex3f(startX,startY,0)
    glVertex3f(startX,startY+(grid*floorLength),0)
    glVertex3f(startX,startY+(grid*floorLength),z)
    glVertex3f(startX,startY,z)
    
    glVertex3f(startX+(grid*floorLength),startY,0)
    glVertex3f(startX+(grid*floorLength),startY+(grid*floorLength),0)
    glVertex3f(startX+(grid*floorLength),startY+(grid*floorLength),z)
    glVertex3f(startX+(grid*floorLength),startY,z)
    
    glVertex3f(startX,startY+(grid*floorLength),0)
    glVertex3f(startX+(grid*floorLength),startY+(grid*floorLength),0)
    glVertex3f(startX+(grid*floorLength),startY+(grid*floorLength),z)
    glVertex3f(startX,startY+(grid*floorLength),z)

    glEnd()

def render_armor():
    if not armor_active:
        return

    glPushMatrix()
    glTranslatef(playerPos[0], playerPos[1], playerPos[2] + 100)

    size_pulse = 1 + 0.05 * math.sin(globalTime * 5)
    radius = 120 * size_pulse

    glColor3f(0.0, 1.0, 1.0)  # Solid cyan color without alpha
    gluSphere(gluNewQuadric(), radius, 30, 30)

    glPopMatrix()

def player():
    global playerPos, turnAngle, gameOver, cheatAngle, sv_cheats, current_weapon, fire_man_active

    x,y,z = playerPos
    glPushMatrix()
    glTranslatef(x, y, z)

    if not gameOver:
        glRotatef(cheatAngle if sv_cheats else turnAngle, 0, 0, 1)
    else:
        glRotatef(90, 1, 0, 0)
        glRotatef(180, 0, 0, 1)

    if fire_man_active:
        glPushMatrix()
        glTranslatef(0, 0, 100)
        pulse = 1 + 0.1 * math.sin(globalTime * 10)
        glColor3f(1.0, 0.5, 0.0)
        gluSphere(gluNewQuadric(), 100 * pulse, 20, 20)
        glPopMatrix()

    # Set leg color
    if fire_man_active: 
        glColor3f(1.0, 0.2, 0.0)
    else: 
        glColor3f(0, 0, 1)

    glPushMatrix()
    glTranslatef(-30, 0, 0)
    gluCylinder(gluNewQuadric(), 10, 20, 80, 20, 20)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(30, 0, 0)
    gluCylinder(gluNewQuadric(), 10, 20, 80, 20, 20)
    glPopMatrix()

    # Set body color
    if fire_man_active: 
        glColor3f(1.0, 0.5, 0.0)
    else: 
        glColor3f(85/255, 107/255, 47/255)

    glPushMatrix()
    glTranslatef(0,0,120)
    glScalef(1,0.6,1.4)
    glutSolidCube(80)
    glPopMatrix()

    glTranslatef(0,0,130)
    glRotatef(90,1,0,0)

    if current_weapon == "shotgun":
        glColor3f(0.2, 0.2, 0.2)
        gluCylinder(gluNewQuadric(), 25, 20, 70, 20, 20)
    else:
        glColor3f(190/255, 190/255, 190/255)
        gluCylinder(gluNewQuadric(), 15, 8, 100, 20, 20)

    # Set arm color
    if fire_man_active: 
        glColor3f(1.0, 0.2, 0.0)
    else: 
        glColor3f(255/255, 220/255, 185/255)

    glTranslatef(-50,0,0)
    gluCylinder(gluNewQuadric(), 15, 8, 70, 20, 20)
    glTranslatef(100,0,0)
    gluCylinder(gluNewQuadric(), 15, 8, 70, 20, 20)

    # Set head color
    if fire_man_active: 
        glColor3f(1.0, 1.0, 0.0)
    else: 
        glColor3f(0,0,0)

    glPushMatrix()
    glRotatef(-90,1,0,0)
    glTranslatef(-50,0,40)
    gluSphere(gluNewQuadric(), 30, 20, 20)
    glPopMatrix()

    glPopMatrix()

    render_armor()

def renderPortal(x,y,z):
    glPushMatrix()
    glTranslatef(x,y,z)
    glColor3f(0.7, 0.7, 0.8)
    radius = 250
    gluCylinder(gluNewQuadric(), radius, radius, 10, 40, 40)  
    glColor3f(0.5, 0.5, 0.6)
    glTranslatef(0, 0, 10) 
    gluCylinder(gluNewQuadric(), radius-50, radius-50, 10, 40, 40)  
    glPopMatrix()

# def enemy(x,y,z,sf,currentHealth,maxHealth):
#     glPushMatrix()
#     glColor3f(1,0,0)
#     radius = 100
#     glTranslatef(x,y,0)
#     glScalef(wave, wave, wave)
#     gluSphere(gluNewQuadric(), radius, 10, 10)
#     glColor3f(0,0,0)
#     glTranslatef(0,0,radius)
#     radius = 50
#     gluSphere(gluNewQuadric(), radius, 10, 10)

#     # Health bar
#     glPushMatrix()
#     glTranslatef(-40, 0, radius + 20)
#     glRotatef(90, 1, 0, 0)
#     #glScalef(1.0 / wave, 1.0 / wave, 1.0 / wave)

#     # glColor3f(1, 0, 0)
#     # glBegin(GL_QUADS)
#     # glVertex3f(0, 0, 0); glVertex3f(80, 0, 0); glVertex3f(80, 10, 0); glVertex3f(0, 10, 0)
#     # glEnd()

#     health_ratio = max(0.0, min(1.0, currentHealth / maxHealth))
#     glColor3f(0, 1, 1)
#     glBegin(GL_QUADS)
#     glVertex3f(0, 0, 0)
#     glVertex3f(80 * health_ratio, 0, 0)
#     glVertex3f(80 * health_ratio, 10, 0)
#     glVertex3f(0, 10, 0)
#     glEnd()
#     glPopMatrix()
#     glPopMatrix()

def enemy(x,y,z,sf,currentHealth,maxHealth):
    glPushMatrix()
    glColor3f(1,0,0)
    radius = 70
    glTranslatef(x,y,z + radius)  # Add radius to z to lift enemy above ground
    glScalef(wave, wave, wave)
    
    # Main body - make it more cylindrical
    gluCylinder(gluNewQuadric(), radius, radius * 0.8, radius * 1.5, 20, 20)
    
    # Head on top
    glColor3f(0.8,0,0)
    glTranslatef(0,0,radius * 1.5)
    gluSphere(gluNewQuadric(), radius * 0.6, 15, 15)
    
    # Eyes
    glColor3f(1,1,0)
    glPushMatrix()
    glTranslatef(-radius * 0.3, radius * 0.4, 0)
    gluSphere(gluNewQuadric(), radius * 0.1, 10, 10)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(radius * 0.3, radius * 0.4, 0)
    gluSphere(gluNewQuadric(), radius * 0.1, 10, 10)
    glPopMatrix()

    # Health bar (move it up since enemy is now higher)
    glPushMatrix()
    glTranslatef(-40, 0, radius * 0.8)
    glRotatef(90, 1, 0, 0)

    health_ratio = max(0.0, min(1.0, currentHealth / maxHealth))
    glColor3f(0, 1, 1)
    glBegin(GL_QUADS)
    glVertex3f(0, 0, 0)
    glVertex3f(80 * health_ratio, 0, 0)
    glVertex3f(80 * health_ratio, 10, 0)
    glVertex3f(0, 10, 0)
    glEnd()
    glPopMatrix()
    glPopMatrix()

def final_boss(x,y,z,sf, currentHealth, maxHealth):
    glPushMatrix()
    
    # Boss is bigger and has a different color
    glColor3f(0.8, 0.2, 0.8)  # Purple color
    radius = 300  # Much larger
    glTranslatef(x,y,0)
    glScalef(sf, sf, sf)
    gluSphere(gluNewQuadric(), radius, 20, 20)
    
    # A single, ominous eye
    glColor3f(1, 1, 0)  # Yellow
    glPushMatrix()
    glTranslatef(0, radius, radius/2)
    gluSphere(gluNewQuadric(), 50, 10, 10)
    glPopMatrix()
    
    # Health bar above boss
    glPushMatrix()
    glTranslatef(-150, 0, radius + 50)
    glRotatef(90, 1, 0, 0)
    
    # # Background (red)
    # glColor3f(1, 0, 0)
    # glBegin(GL_QUADS)
    # glVertex3f(0, 0, 0); glVertex3f(300, 0, 0); glVertex3f(300, 20, 0); glVertex3f(0, 20, 0)
    # glEnd()
    
    # Foreground (green)
    health_ratio = max(0.0, min(1.0, currentHealth / maxHealth))
    glColor3f(0, 1, 0)
    glBegin(GL_QUADS)
    glVertex3f(0, 0, 0); glVertex3f(300 * health_ratio, 0, 0); glVertex3f(300 * health_ratio, 20, 0); glVertex3f(0, 20, 0)
    glEnd()
    glPopMatrix()
    
    glPopMatrix()

# Powerups
def generate_health_powerup():
    coord = [random.randrange(200, 2600), random.randrange(200, 2600), 0]
    healthPowerups.append(coord)

# def render_health_powerup(x, y, z):
#     glPushMatrix()
#     glTranslatef(x, y, z + 50)
#     #glRotatef(45, 0, 0, 1)  # Rotate the powerup for better visibility
    
#     # White box for the first aid kit
#     glColor3f(1, 1, 1)
#     glutSolidCube(50)
    
#     # Red cross
#     glColor3f(1, 0, 0)
    
#     # Horizontal part of the cross
#     glPushMatrix()
#     glScalef(1.0, 0.2, 0.2)
#     glutSolidCube(50)
#     glPopMatrix()
    
#     # Vertical part of the cross
#     glPushMatrix()
#     glScalef(0.2, 1.0, 0.2)
#     glutSolidCube(50)
#     glPopMatrix()
#     glPopMatrix()

def render_health_powerup(x, y, z):
    glPushMatrix()
    glTranslatef(x, y, z + 50)
    glRotatef(90,1,0,0)
    
    # White background/base
    glColor3f(1, 1, 1)
    glutSolidCube(60)
    
    # Red cross made of two cubes - positioned slightly forward to avoid clipping
    glColor3f(1, 0, 0)
    
    # Horizontal bar of the cross
    glPushMatrix()
    glTranslatef(0, 0, 32)  # Move forward to sit on top of the white cube
    glScalef(1.0, 0.2, 0.2)  # Make it longer horizontally, thinner in other dimensions
    glutSolidCube(70)
    glPopMatrix()
    
    # Vertical bar of the cross
    glPushMatrix()
    glTranslatef(0, 0, 32)  # Move forward to sit on top of the white cube
    glScalef(0.2, 1.0, 0.2)  # Make it longer vertically, thinner in other dimensions
    glutSolidCube(70)
    glPopMatrix()
    
    glPopMatrix()

def generate_speed_powerup():
    coord = [random.randrange(200, 2600), random.randrange(200, 2600), 0]
    speedPowerups.append(coord)

def render_speed_powerup(x, y, z):
    glPushMatrix()
    glTranslatef(x, y, z + 50)
    glColor3f(0.2, 0.2, 0.8)
    glutSolidCube(50)
    glColor3f(1, 1, 1)
    glutSolidCone(20, 30, 10, 10)
    glPopMatrix()

def generate_damage_powerup():
    coord = [random.randrange(200, 2600), random.randrange(200, 2600), 0]
    damagePowerups.append(coord)

def render_damage_powerup(x, y, z):
    glPushMatrix()
    glTranslatef(x, y, z + 50)
    
    glColor3f(0.8, 0.2, 0.2)
    gluCylinder(gluNewQuadric(), 15, 15, 40, 20, 20)  # radius, radius, height, slices, stacks
    
    glPushMatrix()
    glTranslatef(0, 0, 40)  
    glColor3f(0.8, 0.2, 0.2)
    glutSolidCone(35, 50, 20, 20)  # base radius, height, slices, stacks
    glPopMatrix()
    
    glPopMatrix()

def generate_bomb_powerup():
    coord = [random.randrange(200, 2600), random.randrange(200, 2600), 0]
    bombPowerups.append(coord)

def render_bomb_powerup(x, y, z):
    glPushMatrix()
    glTranslatef(x, y, z + 30)
    
    
    glColor3f(0, 0, 0)
    glutSolidSphere(50, 20, 20)
    

    glPushMatrix()
    glTranslatef(0, 0, 60)
    glRotatef(37, 1,0,0)
    glColor3f(1, 0, 0)
    glScalef(0.5, 0.5, 1.5) 
    glutSolidCube(30)
    glPopMatrix()
    
    glPopMatrix()

def render_bomb_explosion():
    global bomb_explosion, bomb_explosion_radius
    if bomb_explosion:
        x, y, z = bomb_explosion['pos']
        timer = bomb_explosion['timer']
        
        glPushMatrix()
        glTranslatef(x, y, z)
        # Use timer to change size and color for explosion animation
        size = bomb_explosion_radius * (1 - timer / bomb_explosion_duration)
        alpha = timer / bomb_explosion_duration
        glColor3f(1.0, 0.0, 0.0) # Red color
        glutSolidSphere(size, 20, 20)
        glPopMatrix()
        
        bomb_explosion['timer'] -= deltaTime * targetFPS
        if bomb_explosion['timer'] <= 0:
            bomb_explosion = None

# Destructible Objects (Rocks)
def generate_destructive_object():
    coord = [random.randrange(200, 2600), random.randrange(200, 2600), 0]
    destructiveObjects.append(coord)

def render_destructive_object(x, y, z):
    glPushMatrix()
    glTranslatef(x, y, z)
    
    # Rock
    glColor3f(105/255, 105/255, 105/255)  
    glScalef(1.2, 0.8, 0.6) 
    gluSphere(gluNewQuadric(), 100, 5, 5)  # parameters are: quadric, radius, slices, stacks
    
    glPopMatrix()

#Generation
def generate_enemy():
    global enemyList
    # enemies now have a health attribute
    max_health = random.randint(5, 7)
    coord = [random.randrange(200,2600), random.randrange(200,2600), 0, max_health, max_health]
    enemyList.append(coord)
    
# def generate_boss():
#     global enemyList, boss_active, boss_health, boss_max_health
#     # Boss has a massive health pool
#     boss_active = True
#     boss_health = boss_max_health
#     max_health = 200
#     coord = [1000, 1000, 0, max_health, max_health]
#     enemyList.append(coord)

# def moveEnemy():
#     step = 1.5
#     global playerPos, enemyList
#     for i in range(len(enemyList)):
#         ex, ey, ez, cur_health, max_health = enemyList[i]
#         dx, dy = playerPos[0] - ex, playerPos[1] - ey
#         distance = math.sqrt((dx*dx) + (dy*dy))
#         if distance >= 180:
#             dx = (dx/distance) * step
#             dy = (dy/distance) * step
#             enemyList[i][0] = ex + dx
#             enemyList[i][1] = ey + dy

def moveEnemy():
    step = 1.5 * deltaTime * targetFPS  # Frame rate independent movement
    global playerPos, enemyList
    for i in range(len(enemyList)):
        ex, ey, ez, cur_health, max_health = enemyList[i]
        dx, dy = playerPos[0] - ex, playerPos[1] - ey
        distance = math.sqrt((dx*dx) + (dy*dy))
        if distance >= 180:
            dx = (dx/distance) * step
            dy = (dy/distance) * step
            enemyList[i][0] = ex + dx
            enemyList[i][1] = ey + dy

def renderBullet(i):
    global playerPos, bullets, bulletRadius
    glPushMatrix()
    x,y,angle,radius = bullets[i]
    glColor3f(1,1,0)
    glTranslatef(x,y,100)
    glRotatef(angle, 0,0,1)
    glutSolidCube(radius)
    glPopMatrix()

def moveDrone():
    global drone_pos, drone_speed
    target_x = playerPos[0] + 60
    target_y = playerPos[1] - 60
    target_z = playerPos[2] + 100
    dx = target_x - drone_pos[0]
    dy = target_y - drone_pos[1]
    dz = target_z - drone_pos[2]
    dist = math.sqrt((dx*dx) + (dy*dy) + (dz*dz))
    if dist > 100:
        drone_pos[0] += (dx / dist) * drone_speed
        drone_pos[1] += (dy / dist) * drone_speed
        drone_pos[2] += (dz / dist) * drone_speed

def render_drone():
    glPushMatrix()
    glTranslatef(drone_pos[0], drone_pos[1], drone_pos[2])
    glColor3f(0.2, 0.6, 0.8)
    glutSolidCube(30)
    glPushMatrix()
    glColor3f(0.8, 0.8, 0.8)
    glTranslatef(0, 0, 20)
    glScalef(1, 0.1, 1)
    glutSolidSphere(20, 10, 10)
    glPopMatrix()
    glPopMatrix()

def render_health_bar():
    global health
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, screenX, 0, screenY)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    bar_width, bar_height = 300, 20
    health_ratio = max(0.0, min(1.0, health / 5))
    
    # Background (always dark red/gray)
    # health_width = 80 * health_ratio
    # glVertex3f(0, 0, 0); 
    # glVertex3f(health_width, 0, 0); 
    # glVertex3f(health_width, 10, 0); 
    # glVertex3f(0, 10, 0)
    
    # Foreground color changes based on health level
    if health_ratio > 0.6:  # High health (green)
        glColor3f(0, 1, 0)
    elif health_ratio > 0.3:  # Medium health (yellow)
        glColor3f(1, 1, 0)
    else:  # Low health (red)
        glColor3f(1, 0, 0)
    
    glBegin(GL_QUADS)
    glVertex2f(10, 50)
    glVertex2f(10 + bar_width * health_ratio, 50)
    glVertex2f(10 + bar_width * health_ratio, 50 + bar_height)
    glVertex2f(10, 50 + bar_height)
    glEnd()

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

# distance-based collision checking
def checkCollision(A, B, radiusA, radiusB, flag=0):
    global wave
    distX = A[0] - B[0]
    distY = A[1] - B[1]
    
    if flag == 0:
        distance = math.sqrt( (distX*distX) + (distY*distY) )
        return distance <= (radiusA + radiusB)
    else:
        eradius = radiusB * wave
        distance = math.sqrt( (distX*distX) + (distY*distY) )
        return distance <= (radiusA + eradius)

def render_boss():
    if not boss_active: return
    x, y, z = boss_pos
    glPushMatrix()
    glTranslatef(x, y, z + 150)
    glColor3f(0.8, 0.1, 0.1)
    gluSphere(gluNewQuadric(), boss_radius, 30, 30)
    glPushMatrix()
    glRotatef(globalTime * 30, 0, 0, 1)
    glColor3f(0.3, 0.3, 0.3)
    glutSolidTorus(40, boss_radius + 50, 10, 30)
    glPopMatrix()
    glPushMatrix()
    glRotatef(globalTime * -20, 1, 1, 0)
    glColor3f(0.3, 0.3, 0.3)
    glutSolidTorus(30, boss_radius + 20, 10, 30)
    glPopMatrix()
    glColor3f(1, 1, 0)
    glTranslatef(0, boss_radius - 20, 0)
    gluSphere(gluNewQuadric(), 50, 20, 20)
    glPopMatrix()

def render_boss_health_bar():
    if not boss_active: 
        return
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, screenX, 0, screenY)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    bar_width, bar_height = 600, 25
    bar_x = (screenX - bar_width) / 2
    bar_y = screenY - 50
    
    # Background
    # glColor3f(0.5, 0, 0)
    # glBegin(GL_QUADS)
    # glVertex2f(bar_x, bar_y)
    # glVertex2f(bar_x + bar_width, bar_y)
    # glVertex2f(bar_x + bar_width, bar_y + bar_height)
    # glVertex2f(bar_x, bar_y + bar_height)
    # glEnd()
    
    # Health bar
    health_ratio = max(0.0, min(1.0, boss_health / boss_max_health))
    glColor3f(1, 0, 0)
    glBegin(GL_QUADS)
    glVertex2f(bar_x, bar_y)
    glVertex2f(bar_x + (bar_width * health_ratio), bar_y)
    glVertex2f(bar_x + (bar_width * health_ratio), bar_y + bar_height)
    glVertex2f(bar_x, bar_y + bar_height)
    glEnd()
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    
def move_boss():
    angle = globalTime * 0.2
    radius = 400
    boss_pos[0] = midpoint + math.cos(angle) * radius
    boss_pos[1] = midpoint + math.sin(angle) * radius

def boss_attack():
    global boss_attack_timer, boss_bullets
    boss_attack_timer -= deltaTime * targetFPS
    if boss_attack_timer <= 0:
        dx, dy = playerPos[0] - boss_pos[0], playerPos[1] - boss_pos[1]
        dist = math.sqrt(dx*dx + dy*dy) if (dx*dx + dy*dy) > 0 else 1
        dir_x, dir_y = dx / dist, dy / dist
        boss_bullets.append({'pos': [boss_pos[0], boss_pos[1], 150], 'dir': [dir_x, dir_y]})
        boss_attack_timer = boss_attack_cooldown

def render_boss_bullets():
    for bullet in boss_bullets:
        x, y, z = bullet['pos']
        glPushMatrix()
        glTranslatef(x, y, z)
        glColor3f(1, 0.5, 0)
        glutSolidSphere(30, 10, 10)
        glPopMatrix()

def drone_shoot():
    global drone_shoot_timer, enemyList, drone_bullets, drone_pos
    if drone_shoot_timer <= 0 and enemyList:
        closest_enemy = None
        min_dist = float('inf')
        for enemy_pos in enemyList:
            dx = enemy_pos[0] - drone_pos[0]
            dy = enemy_pos[1] - drone_pos[1]
            dist = math.sqrt(dx*dx + dy*dy)
            if dist < min_dist:
                min_dist = dist
                closest_enemy = enemy_pos

        if closest_enemy:
            dx = closest_enemy[0] - drone_pos[0]
            dy = closest_enemy[1] - drone_pos[1]
            dist = math.sqrt(dx*dx + dy*dy) if (dx*dx + dy*dy) > 0 else 1
            dir_x = dx / dist
            dir_y = dy / dist

            drone_bullets.append({
                'pos': list(drone_pos),
                'dir': [dir_x, dir_y]
            })

            drone_shoot_timer = drone_shoot_cooldown
            print("Drone Fired!")

def update_drone_logic():
    global drone_shoot_timer, drone_bullets, totalScore
    if drone_shoot_timer > 0:
        drone_shoot_timer -= deltaTime * targetFPS

    for i in range(len(drone_bullets) - 1, -1, -1):
        bullet = drone_bullets[i]
        bullet['pos'][0] += bullet['dir'][0] * 40
        bullet['pos'][1] += bullet['dir'][1] * 40

        hit = False
        for j in range(len(enemyList) - 1, -1, -1):
            if checkCollision(bullet['pos'], enemyList[j], drone_bullet_radius, enemyRadius, 1):
                drone_bullets.pop(i)
                enemyList.pop(j)
                totalScore += 1
                hit = True
                break

        if hit: continue

        if not (xbound[0] < bullet['pos'][0] < xbound[1] and ybound[0] < bullet['pos'][1] < ybound[1]):
            drone_bullets.pop(i)

def render_drone_bullets():
    for bullet in drone_bullets:
        glPushMatrix()
        glTranslatef(bullet['pos'][0], bullet['pos'][1], bullet['pos'][2])
        glColor3f(0.0, 1.0, 0.0)
        glutSolidSphere(drone_bullet_radius, 10, 10)
        glPopMatrix()

def check_lava_damage():
    global playerPos, lava_patches, health, lava_damage_timer

    if lava_damage_timer > 0:
        lava_damage_timer -= deltaTime * targetFPS
        return

    on_lava = False
    for patch in lava_patches:
        min_x = startX + patch['start_x'] * floorLength
        max_x = min_x + patch['size'] * floorLength
        min_y = startY + patch['start_y'] * floorLength
        max_y = min_y + patch['size'] * floorLength

        if min_x < playerPos[0] < max_x and min_y < playerPos[1] < max_y:
            on_lava = True
            break

    if on_lava and playerPos[2] <= 0.1:
        health -= 1
        lava_damage_timer = lava_damage_cooldown
        print(f"Player took lava damage! Health: {health}")

def idle():
    global wave, step, playerPos, xbound, ybound, zbound, bullets, bulletsMissed, enemyList, bulletRadius, enemyRadius
    global totalScore, health, gameOver, pov, sv_cheats, globalTime, lastTime, bulletSpeed, destructiveObjects, bulletDamage
    global killsInLevel, lastHealthIncreaseTime, enemyHealthIncrement, level, victory
    global boss_active, boss_health, kill_streak, armor_active, armor_health, fire_man_active, deltaTime

    currentTime = time.time()
    deltaTime = currentTime - lastTime
    globalTime += deltaTime
    
    # Increase enemy health every 30 seconds
    if currentTime - lastHealthIncreaseTime >= 30:
        print("Enemy health increased!")
        enemyHealthIncrement += 2
        for enemy in enemyList:
            enemy[3] += enemyHealthIncrement # Increase current health
            enemy[4] += enemyHealthIncrement # Increase max health
        lastHealthIncreaseTime = currentTime

    lastTime = currentTime

    updateVariables()

    if gameOver or victory:
        pov = "third"
        return
    else:
        wave = (0.25 * math.sin(step) + 1) # oscillates between 0.75, 1.25 {Starts at 1.0}
        step += 0.025 * deltaTime * targetFPS
        
        if boss_active:
            move_boss()
            boss_attack()
            for i in range(len(boss_bullets) - 1, -1, -1):
                bullet = boss_bullets[i]
                bullet['pos'][0] += bullet['dir'][0] * 30 * deltaTime * targetFPS
                bullet['pos'][1] += bullet['dir'][1] * 30 * deltaTime * targetFPS
                if checkCollision(bullet['pos'], playerPos, 30, 100):
                    if armor_active:
                        armor_health -= 1
                        print(f"Armor took a hit! Durability: {armor_health}/{armor_max_health}")
                        if armor_health <= 0:
                            armor_active = False
                            print("Armor shattered!")
                    else:
                        health -= 1
                    boss_bullets.pop(i)
                    continue
                if not (xbound[0] < bullet['pos'][0] < xbound[1] and ybound[0] < bullet['pos'][1] < ybound[1]):
                    boss_bullets.pop(i)
            if boss_health <= 0:
                boss_active = False
                totalScore += 100
                victory = True
                gameOver = True
                print("BOSS DEFEATED!")
        else:
            moveEnemy()
            for i in range(len(enemyList) - 1, -1, -1):
                if playerPos[2] <= 0.1 and checkCollision(playerPos, enemyList[i], 100, enemyRadius):
                    if fire_man_active:
                        enemyList.pop(i)
                        totalScore += 1
                        killsInLevel += 1
                    elif armor_active:
                        enemyList.pop(i)
                        armor_health -= 1
                        print(f"Armor took a hit! Durability: {armor_health}/{armor_max_health}")
                        if armor_health <= 0:
                            armor_active = False
                            print("Armor shattered!")
                    else:
                        enemyList.pop(i)
                        health -= 1
        
        # Handle bullet movement and collisions
        for i in range(len(bullets) - 1, -1, -1):
            if i >= len(bullets):  # Safety check
                continue
                
            angle = bullets[i][2]
            theta = math.radians(angle-90)
            bullets[i][0] += bulletSpeed*math.cos(theta) * deltaTime * targetFPS
            bullets[i][1] += bulletSpeed*math.sin(theta) * deltaTime * targetFPS
            
            hit = False

            # Check collision with boss if active
            if boss_active:
                if checkCollision(bullets[i], boss_pos, bullets[i][3], boss_radius):
                    bullets.pop(i)
                    boss_health -= bulletDamage
                    totalScore += 5
                    hit = True
                    continue
            
            # Check collision with enemies
            if not hit:
                for j in range(len(enemyList) - 1, -1, -1):
                    if checkCollision(bullets[i], enemyList[j], bullets[i][3], enemyRadius, 1):
                        bullets.pop(i)
                        enemyList[j][3] -= bulletDamage  # Decrease enemy health by bulletDamage
                        if enemyList[j][3] <= 0:
                            enemyList.pop(j)
                            totalScore += 1
                            killsInLevel += 1
                            if not armor_active:
                                kill_streak += 1
                                if kill_streak >= 10:
                                    armor_active = True
                                    armor_health = armor_max_health
                                    kill_streak = 0
                                    print("SPECIAL ARMOR ACTIVATED!")
                            if level == 3 and not enemyList:
                                victory = True
                                gameOver = True
                                print("Congratulations! You have defeated the final boss!")
                        hit = True
                        break
            
            # Check collision with trees
            # if not hit:
            #     for j in range(len(trees) - 1, -1, -1):
            #         if checkCollision(bullets[i], trees[j], bullets[i][3], 100):
            #             bullets.pop(i)
            #             trees.pop(j)
            #             print("Tree destroyed!")
            #             hit = True
            #             break

            # Check collision with rocks
            if not hit:
                for j in range(len(rocks) - 1, -1, -1):
                    if checkCollision(bullets[i], rocks[j], bullets[i][3], 100):
                        bullets.pop(i)
                        rocks.pop(j)
                        print("Rock destroyed!")
                        hit = True
                        break
            
            # Check for collision with destructive objects
            if not hit:
                for j in range(len(destructiveObjects) - 1, -1, -1):
                    if checkCollision(bullets[i], destructiveObjects[j], bullets[i][3], 50):
                        bullets.pop(i)
                        destructiveObjects.pop(j)
                        print("Obstacle destroyed!")
                        hit = True
                        break
            
            # Remove bullets that go out of bounds
            if not hit:
                bx, by = bullets[i][0], bullets[i][1]
                if not (xbound[0] <= bx <= xbound[1] and ybound[0] <= by <= ybound[1]):
                    bullets.pop(i)
        
        grab_powerup()
        check_lava_damage()
        moveDrone()
        update_drone_logic()

        # The game now only ends when health is 0 or less
        if health <= 0:
            midpoint_calc = (startX + grid*floorLength + startX) / 2
            playerPos = [midpoint_calc, midpoint_calc, 0]
            pov = "third"
            gameOver = True
            bullets = []
        
        # Don't spawn new enemies on level 3
        if level != 3 and not boss_active:
            if len(enemyList) < 7:
                generate_enemy()

    if sv_cheats:
        cheatMode()
    
    glutPostRedisplay()

def showScreen():
    global enemyList, bulletFired, bullets, gameOver, globalTime, level, killsInLevel, kills_required_for_level_up
    global portalC, healthPowerups, speedPowerups, damagePowerups, destructiveObjects, bombPowerups, bombCount, bomb_explosion
    global bulletPowerupCount, speedPowerupCount, bulletDamage, enemyHealthIncrement, trees, rocks, victory
    global current_weapon, shotgun_ammo
    
    # Clear color and depth buffers
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()  # Reset modelview matrix
    glViewport(0, 0, screenX, screenY)  # Set viewport size

    setupCamera()  # Configure camera perspective

    floor()
    walls()
    player()
    render_drone()
    
    if level <= len(levels):
        renderPortal(levels[level-1]["portal"][0], levels[level-1]["portal"][1], levels[level-1]["portal"][2])
    
    if boss_active:
        render_boss()
        render_boss_health_bar()
        render_boss_bullets()

    if not gameOver and not victory:
        # Spawn powerups and objects continuously
        if len(healthPowerups) < 3:
            generate_health_powerup()
        if len(speedPowerups) < 2:
            generate_speed_powerup()
        if len(damagePowerups) < 2:
            generate_damage_powerup()
        if len(bombPowerups) < 2:
            generate_bomb_powerup()
        if len(destructiveObjects) < 5:
            generate_destructive_object()
        if len(trees) < 10:
            trees.append([random.randrange(200, 2600), random.randrange(200, 2600), 0])
        
        for i in range(len(enemyList)):
            x,y,z, cur_health, max_health = enemyList[i]
            if level == 3:
                final_boss(x,y,z, wave, cur_health, max_health)
            else:
                enemy(x,y,z, wave, cur_health, max_health)

        for i in range(len(bullets)):
            renderBullet(i)
        
        for pu in healthPowerups:
            render_health_powerup(pu[0], pu[1], pu[2])
        for pu in speedPowerups:
            render_speed_powerup(pu[0], pu[1], pu[2])
        for pu in damagePowerups:
            render_damage_powerup(pu[0], pu[1], pu[2])
        for pu in bombPowerups:
            render_bomb_powerup(pu[0], pu[1], pu[2])
        for obj in destructiveObjects:
            render_destructive_object(obj[0], obj[1], obj[2])
        for tree_pos in trees:
            render_tree(tree_pos[0], tree_pos[1], tree_pos[2])

        render_bomb_explosion()
        render_drone_bullets()
        draw_text(10, 870, f"Player Life Remaining: {health}")
        render_health_bar()
        draw_text(10, 840, f"Total Score: {totalScore}")
        if level == 2:
            kills_required_for_level_up = 20
        draw_text(10, 810, f"Kills this Level: {killsInLevel}/{kills_required_for_level_up}")
        
        # Display appropriate ammo count based on current weapon
        if current_weapon == "shotgun":
            draw_text(10, 780, f"Ammo: {shotgun_ammo}/{shotgun_max_ammo}")
        else:
            draw_text(10, 780, f"Ammo: {gun_ammo}/{gun_max_ammo}")
            
        draw_text(10, 750, f"Bombs: {bombCount}")
        if status_message:
            draw_text(10, 720, status_message)
        
        draw_text(1050, 870, f"Level : {level}")
        draw_text(1050, 840, f"Time: {int(globalTime)} s")
        draw_text(1050, 810, f"Enemies Health Increment: {enemyHealthIncrement}")
        draw_text(1050, 780, f"Bullet Damage: {bulletDamage}")
        draw_text(1050, 750, f"Speed Powerups Grabbed: {speedPowerupCount}")
        draw_text(1050, 720, f"Bullet Powerups Grabbed: {bulletPowerupCount}")
        checkPortal()
    elif victory:
        draw_text(screenX//2 - 150, screenY//2, "VICTORY!", font=GLUT_BITMAP_HELVETICA_18)
        draw_text(screenX//2 - 200, screenY//2 - 50, f"Your Final Score is {totalScore}.", font=GLUT_BITMAP_HELVETICA_18)
        draw_text(screenX//2 - 200, screenY//2 - 100, f'Press "R" to RESTART the Game.', font=GLUT_BITMAP_HELVETICA_18)
    else:
        draw_text(screenX//2 - 150, screenY//2, "GAME OVER", font=GLUT_BITMAP_HELVETICA_18)
        draw_text(10, 870, f"Game is Over. Your score is {totalScore}.")
        draw_text(10, 840, f'Press "R" to RESTART the Game.')

    glutSwapBuffers()

# Initialize the game
for _ in range(5):
    generate_enemy()
for _ in range(3):
    generate_health_powerup()
for _ in range(2):
    generate_speed_powerup()
for _ in range(2):
    generate_damage_powerup()
for _ in range(5):
    generate_destructive_object()
for _ in range(2):
    generate_bomb_powerup()
for _ in range(10): 
    trees.append([random.randrange(200, 2600), random.randrange(200, 2600), 0])

generate_floorPatches()


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH) 
    glutInitWindowSize(screenX, screenY) 
    glutInitWindowPosition(250, 50)
    wind = glutCreateWindow(b"Portal Escape")

    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)

    glEnable(GL_DEPTH_TEST)  # Enable depth testing
    glClearColor(0.5, 0.8, 1.0, 1.0)  # Sky blue background

    glutMainLoop() 

if __name__ == "__main__":
    main()