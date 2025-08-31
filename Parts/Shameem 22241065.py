
# Globals
globalTime = 0
lastTime = time.time()
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

level = 1
killsInLevel = 0
kills_required_for_level_up = 10
can_enter_portal = False
Epressed = False
lastHealthIncreaseTime = time.time() # New global to track health increases
enemyHealthIncrement = 2 # New global for enemy health increment

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

def use_bomb():
    global bombCount, enemyList, destructiveObjects, totalScore, killsInLevel, bomb_explosion
    if bombCount > 0:
        bombCount -= 1
        print(f"Bomb used! Enemies and rocks cleared.")
        
        # Add score for all enemies killed by the bomb
        totalScore += len(enemyList)
        
        # Clear enemies and some rocks
        enemyList.clear()
        
        # Remove a random number of destructive objects, but not all of them
        num_to_remove = len(destructiveObjects) // 2
        for _ in range(num_to_remove):
            if destructiveObjects:
                destructiveObjects.pop(random.randint(0, len(destructiveObjects) - 1))
        
        bomb_explosion = {'pos': list(playerPos), 'timer': bomb_explosion_duration}


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
            
    # Check for movement speed powerup
    for i in range(len(speedPowerups) - 1, -1, -1):
        pu_pos = speedPowerups[i]
        if checkCollision(playerPos, pu_pos, 100, 50):
            speedPowerups.pop(i)
            speedBoostTimer += maxSpeedBoostTime
            speedPowerupCount += 1
            print("Movement speed boost active!")
            return

    # Check for bullet damage powerup (NEW)
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

def enemy(x,y,z,sf,currentHealth,maxHealth):
    glPushMatrix()
    glColor3f(1,0,0)
    radius = 100
    glTranslatef(x,y,0)
    glScalef(wave, wave, wave)
    gluSphere(gluNewQuadric(), radius, 10, 10)
    glColor3f(0,0,0)
    glTranslatef(0,0,radius)
    radius = 50
    gluSphere(gluNewQuadric(), radius, 10, 10)

    # Health bar
    glPushMatrix()
    glTranslatef(-40, 0, radius + 20)
    glRotatef(90, 1, 0, 0)
    #glScalef(1.0 / wave, 1.0 / wave, 1.0 / wave)

    # glColor3f(1, 0, 0)
    # glBegin(GL_QUADS)
    # glVertex3f(0, 0, 0); glVertex3f(80, 0, 0); glVertex3f(80, 10, 0); glVertex3f(0, 10, 0)
    # glEnd()

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

def render_health_powerup(x, y, z):
    glPushMatrix()
    glTranslatef(x, y, z + 50)
    glRotatef(45, 0, 0, 1)  # Rotate the powerup for better visibility
    
    # White box for the first aid kit
    glColor3f(1, 1, 1)
    glutSolidCube(50)
    
    # Red cross
    glColor3f(1, 0, 0)
    
    # Horizontal part of the cross
    glPushMatrix()
    glScalef(1.0, 0.2, 0.2)
    glutSolidCube(50)
    glPopMatrix()
    
    # Vertical part of the cross
    glPushMatrix()
    glScalef(0.2, 1.0, 0.2)
    glutSolidCube(50)
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
    glutSolidSphere(50, 20, 20)
    glColor3f(1, 1, 1)
    glutSolidCube(10)
    glPopMatrix()

def generate_bomb_powerup():
    coord = [random.randrange(200, 2600), random.randrange(200, 2600), 0]
    bombPowerups.append(coord)

def render_bomb_powerup(x, y, z):
    glPushMatrix()
    glTranslatef(x, y, z + 50)
    glColor3f(0, 0, 0)
    glutSolidSphere(50, 20, 20)
    glColor3f(1, 0, 0)
    glutSolidCube(20)
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
        
        bomb_explosion['timer'] -= 1
        if bomb_explosion['timer'] <= 0:
            bomb_explosion = None
            
def render_health_bar():
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
    health_width = 80 * health_ratio
    glVertex3f(0, 0, 0); 
    glVertex3f(health_width, 0, 0); 
    glVertex3f(health_width, 10, 0); 
    glVertex3f(0, 10, 0)
    
    # Foreground color changes based on health level
    if health_ratio > 0.6:  # High health (green)
        glColor3f(0, 1, 0)
    elif health_ratio > 0.3:  # Medium health (yellow)
        glColor3f(1, 1, 0)
    else:  # Low health (red)
        glColor3f(1, 0, 0)
    
    glBegin(GL_QUADS)
    glVertex2f(10, 50); glVertex2f(10 + bar_width * health_ratio, 50); glVertex2f(10 + bar_width * health_ratio, 50 + bar_height); glVertex2f(10, 50 + bar_height)
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
    boss_attack_timer -= 1
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
    
    def idle():
    global wave, step, playerPos, xbound, ybound, zbound, bullets, bulletsMissed, enemyList, bulletRadius, enemyRadius
    global totalScore, health, gameOver, pov, sv_cheats, globalTime, lastTime, bulletSpeed, destructiveObjects, bulletDamage
    global killsInLevel, lastHealthIncreaseTime, enemyHealthIncrement, level, victory
    global boss_active, boss_health, kill_streak, armor_active, armor_health, fire_man_active

    currentTime = time.time()
    globalTime += currentTime - lastTime
    
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
        step += 0.025
        
        if boss_active:
            move_boss()
            boss_attack()
            for i in range(len(boss_bullets) - 1, -1, -1):
                bullet = boss_bullets[i]
                bullet['pos'][0] += bullet['dir'][0] * 30
                bullet['pos'][1] += bullet['dir'][1] * 30
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
            bullets[i][0] += bulletSpeed*math.cos(theta)
            bullets[i][1] += bulletSpeed*math.sin(theta)
            
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
            if not hit:
                for j in range(len(trees) - 1, -1, -1):
                    if checkCollision(bullets[i], trees[j], bullets[i][3], 100):
                        bullets.pop(i)
                        trees.pop(j)
                        print("Tree destroyed!")
                        hit = True
                        break

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
