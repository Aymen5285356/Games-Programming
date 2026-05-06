import pygame
from settings import GREEN

def fight(player, enemy):
    if player.rect.colliderect(enemy.rect):
        if player.attack():
            if enemy.take_damage(player.attack_damage):
                return "enemy_died"

        if enemy.attack():
            player.take_damage(enemy.attack_damage)
            if player.hp <= 0:
                return "player_died"

    return "fighting"


def check_death(player, enemy, screen, font):
    if enemy.hp <= 0:
        player.gain_exp(50)
        return "enemy_defeated"
    elif player.hp <= 0:
        return "game_over"
    return None