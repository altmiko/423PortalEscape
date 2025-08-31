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

# --- DRONE VARIABLES ---
drone_pos = [playerPos[0] + 60, playerPos[1] - 60, 100]
drone_speed = 8
drone_bullets = []
drone_bullet_radius = 15
drone_shoot_cooldown = 300 # 5 seconds at approx 60fps
drone_shoot_timer = 0


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
        drone_shoot_timer -= 1

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
        lava_damage_timer -= 1
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