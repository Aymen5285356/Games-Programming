from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random
import math

app = Ursina()

game_state = "menu"

mouse.visible = True
mouse.locked = False

class PlayerCharacter(FirstPersonController):
    def __init__(self):
        super().__init__(speed=8, position=(0,2,0))
        self.visible = False

        self.weapon = "ak"
        self.shoot_cd = 0

    def update(self):
        if game_state != "game":
            return

        super().update()

        if self.shoot_cd > 0:
            self.shoot_cd -= time.dt

    def attack(self):
        if self.weapon == "sword":
            for e in enemies:
                if distance(self.position, e.position) < 3:
                    e.take_damage(25)

        elif self.weapon == "pistol":
            if self.shoot_cd <= 0:
                shoot_ray(25, 0.01)
                self.shoot_cd = 0.5

        elif self.weapon == "ak":
            if self.shoot_cd <= 0:
                shoot_ray(10, 0.03)
                self.shoot_cd = 0.1

player = PlayerCharacter()
player.enabled = False

class Enemy(Entity):
    def __init__(self, position=(0,0,0)):
        super().__init__(position=position)

        self.body = Entity(parent=self, model='cube', scale=(1,1.5,0.5), y=0.75, color=color.azure)
        self.head = Entity(parent=self, model='sphere', scale=0.5, y=1.75, color=color.peach)

        self.collider = BoxCollider(self, center=(0,0.75,0), size=(1,2,1))

        self.health = 60
        self.speed = 2

    def update(self):
        if game_state != "game":
            return

        self.look_at(player.position)
        self.position += self.forward * self.speed * time.dt

    def take_damage(self, dmg):
        self.health -= dmg

        # hit flash
        self.body.color = color.red
        invoke(setattr, self.body, 'color', color.azure, delay=0.1)

        if self.health <= 0:
            enemies.remove(self)
            destroy(self)

def shoot_ray(damage, spread):
    direction = camera.forward + Vec3(
        random.uniform(-spread, spread),
        random.uniform(-spread, spread),
        random.uniform(-spread, spread)
    )

    hit = raycast(camera.world_position, direction, distance=100)

    # recoil
    camera.rotation_x -= random.uniform(1,2)

    if hit.hit:
        target = hit.entity

        while target and not isinstance(target, Enemy):
            target = target.parent

        if isinstance(target, Enemy):
            target.take_damage(damage)

            Entity(model='sphere', color=color.red, scale=0.2, position=hit.point, lifetime=0.2)
        else:
            Entity(model='quad', color=color.gray, scale=0.2, position=hit.point, lifetime=0.3)

ground = Entity(model='plane', scale=100, collider='box', color=color.green)
Sky()

enemies = []

def spawn_enemy():
    e = Enemy(position=(random.uniform(-20,20),0,random.uniform(-20,20)))
    enemies.append(e)

# ================== MENU ==================
menu_parent = Entity(parent=camera.ui)

Text("REALISTIC FPS RPG", parent=menu_parent, y=0.3, scale=2)

def start_game():
    global game_state
    game_state = "game"

    menu_parent.disable()

    mouse.visible = False
    mouse.locked = True

    player.enabled = True

    for i in range(5):
        spawn_enemy()

Button(text="START", parent=menu_parent, y=0.1, scale=(0.2,0.1), on_click=start_game)
Button(text="QUIT", parent=menu_parent, y=-0.1, scale=(0.2,0.1), on_click=application.quit)

def toggle_fps():
    window.fps_counter.enabled = not window.fps_counter.enabled

Button(text="FPS ON/OFF", parent=menu_parent, y=-0.3, scale=(0.2,0.1), on_click=toggle_fps)

weapon_text = Text(position=(-0.85,0.45))

crosshair = Entity(parent=camera.ui, model='quad', color=color.white, scale=0.01)

def update_ui():
    weapon_text.text = f"Weapon: {player.weapon}"

    if player.weapon == "ak":
        crosshair.scale = 0.015
    elif player.weapon == "pistol":
        crosshair.scale = 0.01
    else:
        crosshair.scale = 0.02

def input(key):
    global game_state

    if game_state == "game":

        if key == '1':
            player.weapon = "ak"
        if key == '2':
            player.weapon = "pistol"
        if key == '3':
            player.weapon = "sword"

        if key == 'left mouse down':
            player.attack()

        if key == 'right mouse down':
            camera.fov = 40
        if key == 'right mouse up':
            camera.fov = 90

        if key == 'escape':
            game_state = "menu"
            menu_parent.enable()
            mouse.visible = True
            mouse.locked = False
            player.enabled = False

    elif game_state == "menu":
        if key == 'escape':
            application.quit()

def update():
    if game_state != "game":
        return

    for e in enemies:
        e.update()

    update_ui()

app.run()
