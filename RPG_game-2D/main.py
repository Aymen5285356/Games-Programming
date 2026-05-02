import pygame
from settings import *
from player import Player
from enemy import Enemy
from map import Map
from combat import fight

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("RPG Game")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

player = Player(100, 100)
enemy = Enemy(400, 300)
game_map = Map()

running = True
game_state = "playing"  # playing, game_over, victory
attack_cooldown_player = 0
attack_cooldown_enemy = 0


def draw_health_bars():
    bar_width = 40
    bar_height = 6
    player_health_width = (player.hp / player.max_hp) * bar_width
    pygame.draw.rect(screen, RED, (player.rect.x, player.rect.y - 10, bar_width, bar_height))
    pygame.draw.rect(screen, GREEN, (player.rect.x, player.rect.y - 10, player_health_width, bar_height))

    enemy_health_width = (enemy.hp / enemy.max_hp) * bar_width
    pygame.draw.rect(screen, RED, (enemy.rect.x, enemy.rect.y - 10, bar_width, bar_height))
    pygame.draw.rect(screen, GREEN, (enemy.rect.x, enemy.rect.y - 10, enemy_health_width, bar_height))


def draw_ui():
    level_text = font.render(f"Level: {player.level}", True, WHITE)
    exp_text = font.render(f"EXP: {player.exp}/{player.level * 100}", True, WHITE)
    hp_text = font.render(f"HP: {player.hp}/{player.max_hp}", True, WHITE)

    screen.blit(level_text, (10, 10))
    screen.blit(exp_text, (10, 40))
    screen.blit(hp_text, (10, 70))

    if player.rect.colliderect(enemy.rect):
        attack_text = font.render("Press SPACE to attack!", True, YELLOW)
        text_rect = attack_text.get_rect(center=(WIDTH // 2, HEIGHT - 50))
        screen.blit(attack_text, text_rect)

    controls_text = font.render("Arrow Keys/ZQSD: Move | SPACE: Attack | ESC: Exit", True, WHITE)
    controls_rect = controls_text.get_rect(center=(WIDTH // 2, HEIGHT - 20))
    screen.blit(controls_text, controls_rect)

while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    if game_state == "playing":
        keys = pygame.key.get_pressed()

        player.move(keys, game_map.walls)
        enemy.update(player, game_map.walls)

        if player.rect.colliderect(enemy.rect):
            if keys[pygame.K_SPACE] and attack_cooldown_player == 0:
                enemy.hp -= player.attack_damage
                attack_cooldown_player = 30
                print(f"You attacked! Enemy HP: {enemy.hp}")

            if attack_cooldown_enemy == 0:
                player.hp -= enemy.attack_damage
                attack_cooldown_enemy = 40
                print(f"Enemy attacked! Your HP: {player.hp}")

        if attack_cooldown_player > 0:
            attack_cooldown_player -= 1
        if attack_cooldown_enemy > 0:
            attack_cooldown_enemy -= 1

        if enemy.hp <= 0:
            game_state = "victory"
            print("You defeated the enemy!")
        elif player.hp <= 0:
            game_state = "game_over"
            print("You died!")

    screen.fill(BLACK)

    game_map.draw(screen)

    player.draw(screen)
    enemy.draw(screen)

    draw_health_bars()

    draw_ui()

    if game_state == "game_over":
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))

        game_over_text = font.render("GAME OVER!", True, RED)
        restart_text = font.render("Close the window to exit", True, WHITE)

        game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))

        screen.blit(game_over_text, game_over_rect)
        screen.blit(restart_text, restart_rect)

    elif game_state == "victory":
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))

        victory_text = font.render("VICTORY!", True, GREEN)
        exp_text = font.render(f"You gained 50 EXP!", True, YELLOW)
        restart_text = font.render("Close the window to exit", True, WHITE)

        victory_rect = victory_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        exp_rect = exp_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))

        screen.blit(victory_text, victory_rect)
        screen.blit(exp_text, exp_rect)
        screen.blit(restart_text, restart_rect)

    pygame.display.flip()

pygame.quit()
print("Game closed!")