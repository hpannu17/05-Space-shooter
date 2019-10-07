import sys, logging, open_color, arcade, math, random, os
'''
Derived from Arcade documentation at http://arcade.academy/examples/asteroid_smasher.html
'''
#check to make sure we are running the right version of Python
version = (3,7)
assert sys.version_info >= version, "This script requires at least Python {0}.{1}".format(version[0],version[1])

#turn on logging, in case we have to leave ourselves debugging messages
logging.basicConfig(format='[%(filename)s:%(lineno)d] %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

STARTING_ASTEROID_COUNT = 5
SCALE = 0.5
OFFSCREEN_SPACE = 300
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Space Shooter"

class TurningSprite(arcade.Sprite):
    def update(self):
        super().update()
        self.angle = math.degrees(math.atan2(self.change_y, self.change_x))


class UFOSprite(arcade.Sprite):

    def __init__(self, filename, scale):
        super().__init__(filename, scale)
        self.thrust = 0
        self.speed = 0
        self.max_speed = 4
        self.drag = 0.05
        self.respawning = 0

        self.respawn()

    def respawn(self):
        self.respawning = 1
        self.center_x = SCREEN_WIDTH / 2
        self.center_y = SCREEN_HEIGHT / 2
        self.angle = 0

    def update(self):

        if self.respawning:
            self.respawning += 1
            self.alpha = self.respawning
            if self.respawning > 250:
                self.respawning = 0
                self.alpha = 255
        if self.speed > 0:
            self.speed -= self.drag
            if self.speed < 0:
                self.speed = 0

        if self.speed < 0:
            self.speed += self.drag
            if self.speed > 0:
                self.speed = 0

        self.speed += self.thrust
        if self.speed > self.max_speed:
            self.speed = self.max_speed
        if self.speed < -self.max_speed:
            self.speed = -self.max_speed

        self.change_x = -math.sin(math.radians(self.angle)) * self.speed
        self.change_y = math.cos(math.radians(self.angle)) * self.speed

        self.center_x += self.change_x
        self.center_y += self.change_y
        super().update()


class AsteroidSprite(arcade.Sprite):

    def __init__(self, image_file_name, scale):
        super().__init__(image_file_name, scale=scale)
        self.size = 0

    def update(self):

        super().update()


class LaserSprite(TurningSprite):
    def update(self):
        super().update()
        if self.center_x < -100 or self.center_x > 1500 or \
                self.center_y > 1100 or self.center_y < -100:
            self.kill()


class MyGame(arcade.Window):

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        self.frame_count = 0

        self.game_over = False
        self.background = None
        self.all_sprites_list = None
        self.asteroid_list = None
        self.laser_list = None
        self.ship_life_list = None
        
        self.score = 0
        self.player_sprite = None
        self.lives = 1


    def start_new_game(self):

        self.frame_count = 0
        self.game_over = False
        self.all_sprites_list = arcade.SpriteList()
        self.asteroid_list = arcade.SpriteList()
        self.laser_list = arcade.SpriteList()
        self.ship_life_list = arcade.SpriteList()
        self.score = 0
        self.player_sprite = UFOSprite("images/spaceshooter/PNG/ufoYellow.png", SCALE)
        self.all_sprites_list.append(self.player_sprite)
        self.lives = 3

    
        image_list = ("images/spaceshooter/PNG/Meteors/meteorBrown_big1.png","images/spaceshooter/PNG/Meteors/meteorBrown_big3.png",)

        for i in range(STARTING_ASTEROID_COUNT):
            image_no = random.randrange(2)
            enemy_sprite = AsteroidSprite(image_list[image_no], SCALE)
            enemy_sprite.guid = "Asteroid"

            enemy_sprite.center_y = random.randrange(0, 800)
            enemy_sprite.center_x = random.randrange(0, 600)

            enemy_sprite.change_x = random.random() * 2 - 1
            enemy_sprite.change_y = random.random() * 2 - 1

            enemy_sprite.change_angle = (random.random() - 0.5) * 2
            enemy_sprite.size = 4
            self.all_sprites_list.append(enemy_sprite)
            self.asteroid_list.append(enemy_sprite)
        self.background = arcade.load_texture("images/spaceshooter/Backgrounds/blue.png") 

    def on_draw(self):
        arcade.start_render()
        arcade.draw_texture_rectangle(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT, self.background)
        self.all_sprites_list.draw()
        output = f"Score: {self.score}"
        arcade.draw_text(output, 10, 70, arcade.color.WHITE, 13)
        output = f"Lives: {self.lives}"
        arcade.draw_text(output, 10, 60, arcade.color.WHITE, 13)
        output = f"Asteroid Count: {len(self.asteroid_list)}"
        arcade.draw_text(output, 10, 50, arcade.color.WHITE, 13)
        


    def on_key_press(self, symbol, modifiers):
        if not self.player_sprite.respawning and symbol == arcade.key.SPACE:
            laser_sprite = LaserSprite("images/spaceshooter/PNG/Effects/fire05.png", SCALE)
            laser_sprite.guid = "Laser"

            laser_speed = 13
            laser_sprite.change_y = \
                math.cos(math.radians(self.player_sprite.angle)) * laser_speed
            laser_sprite.change_x = \
                -math.sin(math.radians(self.player_sprite.angle)) \
                * laser_speed

            laser_sprite.center_x = self.player_sprite.center_x
            laser_sprite.center_y = self.player_sprite.center_y
            laser_sprite.update()

            self.all_sprites_list.append(laser_sprite)
            self.laser_list.append(laser_sprite)

        if symbol == arcade.key.LEFT:
            self.player_sprite.change_angle = 3
        elif symbol == arcade.key.RIGHT:
            self.player_sprite.change_angle = -3
        elif symbol == arcade.key.UP:
            self.player_sprite.thrust = 0.15
        elif symbol == arcade.key.DOWN:
            self.player_sprite.thrust = -.2

    def on_key_release(self, symbol, modifiers):
        if symbol == arcade.key.LEFT:
            self.player_sprite.change_angle = 0
        elif symbol == arcade.key.RIGHT:
            self.player_sprite.change_angle = 0
        elif symbol == arcade.key.UP:
            self.player_sprite.thrust = 0
        elif symbol == arcade.key.DOWN:
            self.player_sprite.thrust = 0

    def kill_asteroid(self, asteroid: AsteroidSprite):
        self.score += 1
        for i in self.asteroid_list:
            asteroid.kill()
    def update(self, x):
        self.frame_count += 1

        if not self.game_over:
            self.all_sprites_list.update()

            for laser in self.laser_list:
                asteroids_plain = arcade.check_for_collision_with_list(laser, self.asteroid_list)
                asteroids_spatial = arcade.check_for_collision_with_list(laser, self.asteroid_list)
                asteroids = asteroids_spatial

                for asteroid in asteroids:
                    self.kill_asteroid(asteroid)
                    asteroid.kill()
                    laser.kill()

            if not self.player_sprite.respawning:
                asteroids = arcade.check_for_collision_with_list(self.player_sprite, self.asteroid_list)
                if len(asteroids) > 0:
                    if self.lives > 0:
                        self.lives -= 1
                        self.player_sprite.respawn()
                        self.kill_asteroid(asteroids)
                        asteroids.kill()
                        self.ship_life_list.pop().kill()
                        print("Crash")
                    else:
                        self.game_over = True
                        print("Game over")


def main():
    window = MyGame()
    window.start_new_game()
    arcade.run()


if __name__ == "__main__":
    main()