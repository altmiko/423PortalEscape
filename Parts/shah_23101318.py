
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
    
    def cheatMode():
    global sv_cheats, cheatAngle, cooldown
    if cooldown > 0:
        cooldown -= 1
    cheatAngle += 10
    raycast()
    
    
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