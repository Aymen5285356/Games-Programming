from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random
import math

app = Ursina()

# ─── COLOR HELPER ─────────────────────────────────────────────────────────────
def rgb(r, g, b):      return color.rgb(r/255, g/255, b/255)
def rgba(r, g, b, a):  return color.rgba(r/255, g/255, b/255, a/255)

# ─── LIGHTING ─────────────────────────────────────────────────────────────────
DirectionalLight(y=20, z=20, shadows=True)
AmbientLight(color=rgba(120,120,120,180))
window.color = rgb(100,160,210)

# ─── GAME STATE ───────────────────────────────────────────────────────────────
game_state   = "menu"
score        = 0
wave         = 0

mouse.visible = True
mouse.locked  = False

# ─── WEAPON DEFINITIONS ───────────────────────────────────────────────────────
WEAPONS = {
    "ak":     {"damage":12,  "spread":0.03,  "cooldown":0.10, "ammo":30, "max_ammo":30, "reserve":120, "reload_time":2.0, "auto":True,  "label":"AK-47   [1]"},
    "pistol": {"damage":28,  "spread":0.01,  "cooldown":0.40, "ammo":12, "max_ammo":12, "reserve":60,  "reload_time":1.2, "auto":False, "label":"Pistol  [2]"},
    "shotgun":{"damage":18,  "spread":0.08,  "cooldown":0.80, "ammo":6,  "max_ammo":6,  "reserve":36,  "reload_time":2.5, "auto":False, "label":"Shotgun [3]"},
    "sniper": {"damage":95,  "spread":0.002, "cooldown":1.20, "ammo":5,  "max_ammo":5,  "reserve":20,  "reload_time":3.0, "auto":False, "label":"Sniper  [4]"},
    "sword":  {"damage":60,  "spread":0,     "cooldown":0.60, "ammo":-1, "max_ammo":-1, "reserve":-1,  "reload_time":0,   "auto":False, "label":"Sword   [5]"},
}
weapon_states = {k: dict(v) for k, v in WEAPONS.items()}

# ─── PLAYER ───────────────────────────────────────────────────────────────────
class PlayerCharacter(FirstPersonController):

    def __init__(self):
        super().__init__(speed=8, position=(0,2,0))
        self.visible      = False
        self.weapon       = "ak"
        self.shoot_cd     = 0
        self.reload_cd    = 0
        self.reloading    = False
        self.health       = 100
        self.max_health   = 100
        self.invincible   = 0
        self.mouse_held   = False   # tracked manually via input events

    def update(self):
        if game_state != "game":
            return
        super().update()

        # tick timers
        if self.shoot_cd  > 0: self.shoot_cd  -= time.dt
        if self.invincible > 0: self.invincible -= time.dt

        # auto-fire: only when mouse is held AND cooldown expired
        if self.mouse_held and WEAPONS[self.weapon]["auto"] and self.shoot_cd <= 0 and not self.reloading:
            self._do_shoot()

        if self.reloading:
            self.reload_cd -= time.dt
            if self.reload_cd <= 0:
                self._finish_reload()

    # called on mouse-down for semi-auto / sword
    def attack(self):
        if self.reloading:
            return
        w = self.weapon
        if w == "sword":
            if self.shoot_cd <= 0:
                self.shoot_cd = WEAPONS[w]["cooldown"]
                _gun_kick()
                for e in list(enemies):
                    if distance(self.position, e.position) < 3:
                        e.take_damage(WEAPONS[w]["damage"])
            return
        if weapon_states[w]["ammo"] <= 0:
            self.start_reload()
            return
        # semi-auto: only fire once per click, guard with cooldown
        if self.shoot_cd <= 0:
            self._do_shoot()

    def _do_shoot(self):
        if self.reloading:
            return
        w  = self.weapon
        ws = weapon_states[w]
        cfg = WEAPONS[w]

        if ws["ammo"] <= 0:
            self.start_reload()
            return

        self.shoot_cd  = cfg["cooldown"]
        ws["ammo"]    -= 1
        _gun_kick()

        pellets = 6 if w == "shotgun" else 1
        for _ in range(pellets):
            shoot_ray(cfg["damage"], cfg["spread"])

        if w == "sniper":
            camera.fov = 20
            invoke(setattr, camera, 'fov', 90, delay=0.12)

        if ws["ammo"] == 0:
            self.start_reload()

    def start_reload(self):
        w  = self.weapon
        ws = weapon_states[w]
        if ws["ammo"] == ws["max_ammo"] or ws["reserve"] <= 0 or ws["reserve"] == -1:
            return
        self.reloading      = True
        self.reload_cd      = WEAPONS[w]["reload_time"]
        reload_text.text    = "RELOADING..."
        reload_text.enabled = True

    def _finish_reload(self):
        w  = self.weapon
        ws = weapon_states[w]
        needed        = ws["max_ammo"] - ws["ammo"]
        taken         = min(needed, ws["reserve"])
        ws["ammo"]   += taken
        ws["reserve"] -= taken
        self.reloading      = False
        reload_text.enabled = False

    def take_damage(self, dmg):
        if self.invincible > 0:
            return
        self.health    -= dmg
        self.invincible = 0.4
        _screen_flash(rgba(255,0,0,120))
        if self.health <= 0:
            self.health = 0
            trigger_game_over()


player = PlayerCharacter()
player.enabled = False

# ─── GUN MODEL ────────────────────────────────────────────────────────────────
gun_parent = Entity(parent=camera.ui)
gun = Entity(parent=gun_parent, model='cube', color=rgb(20,20,20),
             scale=(0.22,0.12,0.7), position=(0.72,-0.42), rotation=(0,-5,0))
Entity(parent=gun, model='cube', color=color.dark_gray,
       scale=(0.18,0.18,0.7), position=(0,0,0.55))
Entity(parent=gun, model='cube', color=color.black,
       scale=(0.12,0.3,0.12), position=(0,-0.18,-0.15), rotation=(20,0,0))
Entity(parent=gun, model='cube', color=color.gray,
       scale=(0.1,0.08,0.25), position=(0,0.1,0))

def _gun_kick():
    gun.position = (0.70,-0.44)
    invoke(setattr, gun, 'position', (0.72,-0.42), delay=0.05)

# ─── SCREEN FLASH ─────────────────────────────────────────────────────────────
flash_quad = Entity(parent=camera.ui, model='quad', color=color.clear, scale=(2,2), z=-1)

def _screen_flash(col):
    flash_quad.color = col
    flash_quad.animate_color(color.clear, duration=0.3)

# ─── SHOOT RAY ────────────────────────────────────────────────────────────────
def shoot_ray(damage, spread):
    direction = camera.forward + Vec3(
        random.uniform(-spread, spread),
        random.uniform(-spread, spread),
        random.uniform(-spread, spread)
    )
    hit = raycast(camera.world_position, direction, distance=150)
    camera.rotation_x -= random.uniform(0.4, 1.2)

    if not hit.hit:
        return

    # ── FIX 2: walk up the parent chain to find the Enemy root ──
    target = hit.entity
    checked = 0
    while target is not None and not isinstance(target, Enemy) and checked < 6:
        target = target.parent
        checked += 1

    if isinstance(target, Enemy):
        target.take_damage(damage)
        Entity(model='sphere', color=color.red,    scale=0.15, position=hit.point, lifetime=0.15)
    else:
        Entity(model='sphere', color=color.yellow, scale=0.08, position=hit.point, lifetime=0.3)

# ─── ENEMY ────────────────────────────────────────────────────────────────────
class Enemy(Entity):

    def __init__(self, position=(0,0,0), tier=1):
        # ── FIX 2: no collider on root; collider only on body so raycast finds it ──
        super().__init__(position=position, model='cube',
                         scale=(1,2,1), color=color.clear)
        self.tier = tier

        body_col = {1: rgb(35,35,35), 2: rgb(180,30,30), 3: rgb(80,0,120)}.get(tier, rgb(35,35,35))

        # body gets the collider so raycasts hit it, and its parent chain leads back to Enemy
        self.body = Entity(parent=self, model='cube', scale=(0.8,1.2,0.4),
                           y=0.6, color=body_col, collider='box')
        self.head = Entity(parent=self, model='sphere', scale=0.35, y=1.5,
                           color=rgb(255,220,190), collider='sphere')

        for side in (-1,1):
            Entity(parent=self, model='cube', scale=(0.18,0.9,0.18),
                   position=(side*0.55, 0.65, 0), color=color.black)
            Entity(parent=self, model='cube', scale=(0.22,1.0,0.22),
                   position=(side*0.2, -0.6, 0), color=color.black)

        self.max_health = 100 * tier
        self.health     = self.max_health
        self.speed      = random.uniform(1.8, 2.5) + (tier-1)*0.6
        self.attack_cd  = random.uniform(1.0, 2.0)
        self._base_col  = body_col

        self.hp_bg  = Entity(parent=self, model='quad', color=color.black,
                             scale=(1.2,0.12), position=(0,2.4,0), billboard=True)
        self.hp_bar = Entity(parent=self, model='quad', color=color.lime,
                             scale=(1.1,0.08), position=(0,2.4,-0.01), billboard=True)

    def update(self):
        if game_state != "game":
            return

        direction = player.position - self.position
        direction.y = 0
        dist = direction.length()

        ratio = max(0, self.health / self.max_health)
        self.hp_bar.scale_x = 1.1 * ratio
        self.hp_bar.color   = lerp(color.red, color.lime, ratio)

        if dist > 1.2:
            direction = direction.normalized()
            avoid = Vec3(0,0,0)
            for other in enemies:
                if other is not self:
                    d = distance_xz(self.position, other.position)
                    if d < 2.5:
                        push = self.position - other.position
                        push.y = 0
                        if push.length() > 0:
                            avoid += push.normalized() * (2.5 - d)
            fd = direction + avoid * 2
            if fd.length() > 0:
                fd = fd.normalized()
            self.position += fd * self.speed * time.dt
            self.look_at_2d(player.position, 'y')

        if dist < 2:
            self.attack_cd -= time.dt
            if self.attack_cd <= 0:
                player.take_damage(8 * self.tier)
                self.attack_cd = random.uniform(1.0, 2.0)

    def take_damage(self, dmg):
        global score
        self.health -= dmg
        self.body.color = color.white
        invoke(setattr, self.body, 'color', self._base_col, delay=0.1)
        if self.health <= 0:
            score += 10 * self.tier
            if self in enemies:
                enemies.remove(self)
            destroy(self)
            check_wave_clear()


enemies = []

def spawn_enemy(tier=1):
    angle = random.uniform(0, math.tau)
    r     = random.uniform(18, 30)
    e = Enemy(position=(math.cos(angle)*r, 0, math.sin(angle)*r), tier=tier)
    enemies.append(e)

# ─── WAVE SYSTEM ──────────────────────────────────────────────────────────────
def start_wave():
    global wave
    wave += 1
    count = 8 + wave * 3
    wave_text_popup(f"WAVE  {wave}")
    for i in range(count):
        tier = 1
        if wave >= 3 and i % 4 == 0: tier = 2
        if wave >= 6 and i % 8 == 0: tier = 3
        invoke(spawn_enemy, tier, delay=i*0.35)

def check_wave_clear():
    if len(enemies) == 0:
        for k, ws in weapon_states.items():
            if ws["reserve"] >= 0:
                ws["reserve"] = min(ws["reserve"]+20, WEAPONS[k]["reserve"]*2)
        wave_text_popup("WAVE CLEAR!  +AMMO")
        invoke(start_wave, delay=3.5)

def wave_text_popup(msg):
    t = Text(msg, scale=2.5, origin=(0,0), color=color.yellow)
    t.x = 0; t.y = 0.1
    t.parent = camera.ui
    t.animate_color(rgba(255,255,0,0), duration=3.0)
    destroy(t, delay=3.2)

# ─── PICKUPS ──────────────────────────────────────────────────────────────────
class Pickup(Entity):
    def __init__(self, kind, position):
        col = color.red if kind == "health" else color.cyan
        super().__init__(model='sphere', color=col, scale=0.6,
                         position=position, collider='sphere')
        self.kind     = kind
        self.t        = 0
        self.y_origin = position[1]

    def update(self):
        self.t += time.dt
        self.y = self.y_origin + math.sin(self.t*2)*0.18
        self.rotation_y += 60*time.dt
        if distance(self.position, player.position) < 1.5:
            self._collect()

    def _collect(self):
        if self.kind == "health":
            player.health = min(player.max_health, player.health+30)
            _screen_flash(rgba(0,200,0,80))
        else:
            for k, ws in weapon_states.items():
                if ws["reserve"] >= 0:
                    ws["reserve"] += WEAPONS[k]["max_ammo"]
            _screen_flash(rgba(0,150,255,80))
        if self in pickups:
            pickups.remove(self)
        destroy(self)

pickups      = []
pickup_timer = 0

def _maybe_spawn_pickups():
    global pickup_timer
    pickup_timer += time.dt
    if pickup_timer >= 12:
        pickup_timer = 0
        x = random.uniform(-20,20)
        z = random.uniform(-20,20)
        p = Pickup(random.choice(["health","ammo"]), position=(x,0.5,z))
        pickups.append(p)

# ─── ENVIRONMENT ──────────────────────────────────────────────────────────────
ground = Entity(model='plane', scale=120, texture='white_cube', texture_scale=(120,120),
                collider='box', color=rgb(55,130,55))
Sky(color=rgb(100,160,210))

for angle_deg in range(0,360,90):
    a = math.radians(angle_deg)
    Entity(model='cube', collider='box', scale=(120,8,2),
           position=(math.sin(a)*60, 3, math.cos(a)*60),
           rotation=(0,angle_deg,0), color=rgb(80,60,40))

for _ in range(80):
    x = random.uniform(-50,50); z = random.uniform(-50,50)
    if abs(x)<4 and abs(z)<4: continue
    Entity(model='cube', position=(x,2.5,z), scale=(1.2,5,1.2),
           color=rgb(110,65,15), collider='box')
    Entity(model='sphere', position=(x,6.5,z), scale=random.uniform(2.5,4),
           color=rgb(20+random.randint(0,30), 150+random.randint(0,40), 20))

for _ in range(30):
    x = random.uniform(-45,45); z = random.uniform(-45,45)
    Entity(model='cube', position=(x,0.5,z),
           scale=(random.uniform(1.5,3), random.uniform(0.8,2), random.uniform(1.5,3)),
           color=rgb(100,95,90), collider='box')

for _ in range(20):
    x = random.uniform(-40,40); z = random.uniform(-40,40)
    Entity(model='cube', position=(x,0.6,z), scale=1.2,
           color=rgb(160,110,40), collider='box', texture='white_cube')

# ─── HUD ──────────────────────────────────────────────────────────────────────
hud_parent = Entity(parent=camera.ui)
hud_parent.enabled = False

hp_bg  = Entity(parent=hud_parent, model='quad', color=color.black,
                scale=(0.32,0.034), position=(-0.72,-0.44))
hp_bar = Entity(parent=hud_parent, model='quad', color=color.lime,
                scale=(0.30,0.026), position=(-0.72,-0.44))

ammo_text   = Text(parent=hud_parent, position=( 0.52,-0.42), scale=1.4, color=color.white)
weapon_text = Text(parent=hud_parent, position=( 0.52,-0.36), scale=1.1, color=color.yellow)
score_text  = Text(parent=hud_parent, position=(-0.85, 0.46), scale=1.2, color=color.white)
wave_label  = Text(parent=hud_parent, position=(-0.85, 0.40), scale=1.2, color=color.cyan)
reload_text = Text("RELOADING...", parent=hud_parent, origin=(0,0),
                   scale=1.6, color=color.orange, y=-0.18)
reload_text.enabled = False

_cs = 0.007
crosshair_h = Entity(parent=camera.ui, model='quad', color=color.white, scale=(_cs*4,_cs))
crosshair_v = Entity(parent=camera.ui, model='quad', color=color.white, scale=(_cs,_cs*4))

def update_hud():
    w  = player.weapon
    ws = weapon_states[w]
    ratio          = max(0, player.health/player.max_health)
    hp_bar.scale_x = 0.30*ratio
    hp_bar.x       = -0.72-(0.30-0.30*ratio)/2
    hp_bar.color   = lerp(color.red, color.lime, ratio)
    ammo_text.text   = "INF" if ws["ammo"]<0 else f"{ws['ammo']} / {ws['reserve']}"
    weapon_text.text = WEAPONS[w]["label"]
    score_text.text  = f"Score: {score}"
    wave_label.text  = f"Wave:  {wave}"

# ─── PAUSE MENU ───────────────────────────────────────────────────────────────
pause_parent = Entity(parent=camera.ui)
pause_parent.enabled = False
Entity(parent=pause_parent, model='quad', color=rgba(0,0,0,160), scale=(1,0.7), z=1)
Text("PAUSED", parent=pause_parent, y=0.2, scale=2.5, color=color.white)

def _resume():
    global game_state
    game_state = "game"
    pause_parent.disable()
    mouse.visible = False
    mouse.locked  = True

Button(text="RESUME",       parent=pause_parent, y= 0.00, scale=(0.22,0.08), on_click=_resume)
Button(text="QUIT TO MENU", parent=pause_parent, y=-0.12, scale=(0.22,0.08), on_click=lambda: _go_to_menu())

# ─── GAME OVER ────────────────────────────────────────────────────────────────
go_parent = Entity(parent=camera.ui)
go_parent.enabled = False
Entity(parent=go_parent, model='quad', color=rgba(0,0,0,200), scale=(1,0.7), z=1)
go_title = Text("GAME OVER", parent=go_parent, y=0.20, scale=2.5, color=color.red)
go_score = Text("",          parent=go_parent, y=0.08, scale=1.4, color=color.white)

def trigger_game_over():
    global game_state
    game_state    = "gameover"
    go_score.text = f"Score: {score}   Wave: {wave}"
    go_parent.enable()
    for e in list(enemies): destroy(e)
    enemies.clear()
    mouse.visible  = True
    mouse.locked   = False
    player.enabled = False
    hud_parent.disable()

Button(text="PLAY AGAIN", parent=go_parent, y=-0.06, scale=(0.22,0.08), on_click=lambda: start_game())
Button(text="MAIN MENU",  parent=go_parent, y=-0.18, scale=(0.22,0.08), on_click=lambda: _go_to_menu())

# ─── MAIN MENU ────────────────────────────────────────────────────────────────
menu_parent = Entity(parent=camera.ui)
Entity(parent=menu_parent, model='quad', color=rgba(0,0,0,170), scale=(0.7,0.85), z=1)
Text("SURVIVAL FPS", parent=menu_parent, y=0.34, scale=2.2, color=color.yellow)
Text("WASD Move | Mouse Aim | LMB Shoot\nR Reload | RMB Zoom | 1-5 Weapons | ESC Pause",
     parent=menu_parent, y=0.16, scale=0.9, color=color.light_gray)

def start_game():
    global game_state, score, wave, pickup_timer
    score=0; wave=0; pickup_timer=0
    for k,v in WEAPONS.items(): weapon_states[k]=dict(v)
    player.health=player.max_health; player.weapon="ak"
    player.reloading=False; player.position=Vec3(0,2,0)
    for e in list(enemies): destroy(e)
    enemies.clear()
    for p in list(pickups): destroy(p)
    pickups.clear()
    game_state="game"
    menu_parent.disable(); go_parent.disable(); hud_parent.enable()
    player.enabled=True; mouse.visible=False; mouse.locked=True
    start_wave()

Button(text="START",      parent=menu_parent, y=-0.05, scale=(0.22,0.09), on_click=start_game)
Button(text="QUIT",       parent=menu_parent, y=-0.18, scale=(0.22,0.09), on_click=application.quit)
Button(text="FPS ON/OFF", parent=menu_parent, y=-0.30, scale=(0.22,0.09),
       on_click=lambda: setattr(window.fps_counter,'enabled', not window.fps_counter.enabled))

def _go_to_menu():
    global game_state
    game_state="menu"
    go_parent.disable(); pause_parent.disable(); hud_parent.disable(); menu_parent.enable()
    player.enabled=False; mouse.visible=True; mouse.locked=False
    for e in list(enemies): destroy(e)
    enemies.clear()

# ─── INPUT ────────────────────────────────────────────────────────────────────
def input(key):
    global game_state

    if game_state == "game":
        wmap = {'1':'ak','2':'pistol','3':'shotgun','4':'sniper','5':'sword'}
        if key in wmap:
            player.weapon=wmap[key]; player.reloading=False; reload_text.enabled=False

        if key == 'left mouse down':
            player.mouse_held = True
            if not WEAPONS[player.weapon]["auto"]:
                player.attack()
        if key == 'left mouse up':
            player.mouse_held = False

        if key == 'r': player.start_reload()
        if key == 'right mouse down': camera.fov=35
        if key == 'right mouse up':   camera.fov=90
        if key == 'escape':
            game_state="paused"; pause_parent.enable()
            mouse.visible=True; mouse.locked=False

    elif game_state == "paused":
        if key == 'escape': _resume()
    elif game_state == "menu":
        if key == 'escape': application.quit()
    elif game_state == "gameover":
        if key == 'escape': _go_to_menu()

# ─── MAIN UPDATE ──────────────────────────────────────────────────────────────
def update():
    if game_state != "game":
        return
    update_hud()
    _maybe_spawn_pickups()

app.run()
