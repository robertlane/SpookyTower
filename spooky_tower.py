import sys
import pygame
import random

GAME_FPS = 60 # Changed games fps from 150 to 60 - Scarlet
WIDTH, HEIGHT = 1000, 700
JUMPING_HEIGHT = 20
MAX_ACCELERATION = 13
VEL_X = 3  # Setting the moving speed.
VEL_Y = JUMPING_HEIGHT  # Setting the jumping height.
pygame.init()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
GAMEPLAY_SOUND_LENGTH = 31  # 31 seconds.
SHELVES_COUNT = 500  # Number of shelves in the game.
### New constant for music volume - Rob
MUSIC_VOLUME = 0.8 # Must be a float between 0.0 (off) and 1.0 (max volume)
### New constant for character animation - Rob
BODY_ANIMATION_SPEED = 0.05

# Images:
### Changing BODY_IMAGE to an array to allow for character animation - Rob
BODY_IMAGE = [pygame.image.load("Assets/body_01.png"),
              pygame.image.load("Assets/body_02.png"),
              pygame.image.load("Assets/body_03.png")]
body_index = 0
BACKGROUND = pygame.image.load("Assets/background.png")
BRICK_IMAGE = pygame.image.load("Assets/brick_block.png")
SHELF_BRICK_IMAGE = pygame.image.load("Assets/shelf_brick.png")

# Walls settings:
WALLS_Y = -128
WALL_WIDTH = 128
WALLS_ROLLING_SPEED = 2
RIGHT_WALL_BOUND = WIDTH - WALL_WIDTH
LEFT_WALL_BOUND = WALL_WIDTH

# Background settings:
BACKGROUND_WIDTH = WIDTH - 2 * WALL_WIDTH  # removed irrelevant comment - Scarlet
BACKGROUND_ROLLING_SPEED = 1
BACKGROUND_Y = HEIGHT - BACKGROUND.get_height()
background_y = BACKGROUND_Y

# Booleans:
jumping = False
falling = False
standing = False
rolling_down = False
new_movement = False
current_direction = None
current_standing_shelf = None

# Colors:
GRAY = (180, 180, 180)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


class Shelf:
    def __init__(self, number):
        self.number = number
        self.image = None
        self.width = random.randint(4, 7) * 32
        self.x = random.randint(LEFT_WALL_BOUND, RIGHT_WALL_BOUND - self.width)
        self.y = - number * 130 + HEIGHT - 25
        self.rect = pygame.Rect(self.x, self.y, self.width, 32)


class Body:
    def __init__(self):
        self.size = 64
        self.x = WIDTH / 2 - self.size / 2
        self.y = HEIGHT - 25 - self.size
        self.vel_y = 0
        self.acceleration = 0
        self.jumpable = self.vel_y <= 0  # If body is hitting a level, then it can jump only if the body is going down.



# Track the highest shelf/platform reached
highest_shelf_reached = 0 # added a variable to track the highest shelf reached - Scarlet
body = Body()

total_shelves_list = []
for num in range(0, SHELVES_COUNT + 1):  # Creating all the game shelves.
    new_shelf = Shelf(num)
    if num % 50 == 0:
        new_shelf.width = BACKGROUND_WIDTH
        new_shelf.rect.width = BACKGROUND_WIDTH
        new_shelf.x = WALL_WIDTH
        new_shelf.rect.x = WALL_WIDTH
    total_shelves_list.append(new_shelf)

# Sounds:
### Changing JUMPING_SOUND to an array to allow random jump sound to avoid audio fatigue - Rob
JUMPING_SOUND = [pygame.mixer.Sound("Assets/jump_01.ogg"),
                 pygame.mixer.Sound("Assets/jump_02.ogg"),
                 pygame.mixer.Sound("Assets/jump_03.ogg")]
HOORAY_SOUND = pygame.mixer.Sound("Assets/hooray_sound.wav")

### Changing GAMEPLAY_SOUND to use built in music handling - Rob
MUSIC_GAMEPLAY = "Assets/music_gameplay.ogg"
MUSIC_MENUS = "Assets/music_menus.ogg"



def Move(direction):  # Moving the body according to the wanted direction.
    if direction == "Left":
        if body.x - body.acceleration >= LEFT_WALL_BOUND:  # If the body isn't about to pass the left wall on the next step.
            body.x -= body.acceleration  # Take the step.
        else:  # If the body is about to pass the left wall on the next step.
            body.x = LEFT_WALL_BOUND  # Force it to stay inside.
    else:  # If direction is right
        if body.x + body.acceleration <= RIGHT_WALL_BOUND - body.size:  # If the body isn't about to pass the right wall on the next step.
            body.x += body.acceleration  # Take the step.
        else:  # If the body is about to pass the right wall on the next step.
            body.x = RIGHT_WALL_BOUND - body.size  # Force the body to stay inside.
    body.acceleration -= 1  # Decreasing body's movement speed.


def HandleMovement(keys_pressed):  # Handling the Left/Right buttons pressing.
    global body, new_movement, current_direction
    if keys_pressed[pygame.K_LEFT] and body.x > LEFT_WALL_BOUND:  # If pressed "Left", and body is inside the bounding.
        current_direction = "Left"
        if body.acceleration + 3 <= MAX_ACCELERATION:  # If body's movement speed isn't maxed.
            body.acceleration += 3  # Accelerating the body's movement speed.
        else:
            body.acceleration = MAX_ACCELERATION
    if keys_pressed[
        pygame.K_RIGHT] and body.x < RIGHT_WALL_BOUND:  # If pressed "Right", and body is inside the bounding.
        current_direction = "Right"
        if body.acceleration + 3 <= MAX_ACCELERATION:  # If body's movement speed isn't maxed.
            body.acceleration += 3  # Accelerating the body's movement speed.
        else:
            body.acceleration = MAX_ACCELERATION


def DrawWindow():  # Basically, drawing the screen.
    global WALLS_Y
    font = pygame.font.SysFont("Arial", 26)
    HandleBackground()
    for shelf in total_shelves_list:
        for x in range(shelf.rect.x, shelf.rect.x + shelf.width, 32):
            WIN.blit(SHELF_BRICK_IMAGE, (x, shelf.rect.y))  # Drawing the shelf.
            if shelf.number % 10 == 0 and shelf.number != 0:
                shelf_number = pygame.Rect(shelf.rect.x + shelf.rect.width / 2 - 16, shelf.rect.y,
                                           16 * len(str(shelf.number)), 25)
                pygame.draw.rect(WIN, GRAY, shelf_number)
                txt = font.render(str(shelf.number), True, BLACK)
                WIN.blit(txt,
                         (shelf.rect.x + shelf.rect.width / 2 - 16, shelf.rect.y))  # Drawing the number of the shelf.
    for y in range(WALLS_Y, HEIGHT, 108):  # Drawing the walls.
        WIN.blit(BRICK_IMAGE, (0, y))
        WIN.blit(BRICK_IMAGE, (WIDTH - WALL_WIDTH, y))
    WIN.blit(BODY_IMAGE[body_index], (body.x, body.y))  # Drawing the body.
    pygame.display.update()


def OnShelf():  # Checking whether the body is on a shelf, returning True/False.
    global jumping, standing, falling, BACKGROUND_ROLLING_SPEED, current_standing_shelf, highest_shelf_reached # Changed the global variables to include the new ones - Scarlet
    if body.vel_y <= 0:  # Means the body isn't moving upwards, so now it's landing.
        for shelf in total_shelves_list:
            if body.y <= shelf.rect.y - body.size <= body.y - body.vel_y:
                if body.x + body.size * 2 / 3 >= shelf.rect.x and body.x + body.size * 1 / 3 <= shelf.rect.x + shelf.width: # Checking if the body is on the shelf - Scarlet
                    body.y = shelf.rect.y - body.size
                    if shelf.number > highest_shelf_reached:
                        highest_shelf_reached = shelf.number # added a variable to track the highest shelf reached - Scarlet
                    if current_standing_shelf != shelf.number and shelf.number % 50 == 0 and shelf.number != 0:
                        BACKGROUND_ROLLING_SPEED += 1 # Increased the speed of the background rolling down when reaching a new shelf - Scarlet
                        current_standing_shelf = shelf.number
                    if shelf.number % 100 == 0 and shelf.number != 0:
                        HOORAY_SOUND.play()
                    if shelf.number == SHELVES_COUNT:
                        GameOver()
                    return True
    else:  # Means body in not on a shelf.
        jumping, standing, falling = False, False, True


def ScreenRollDown():  # Increasing the y values of all elements.
    global background_y, WALLS_Y
    for shelf in total_shelves_list:
        shelf.rect.y += 1
    body.y += 1
    background_y += 0.5
    if background_y == BACKGROUND_Y + 164:
        background_y = BACKGROUND_Y
    WALLS_Y += WALLS_ROLLING_SPEED
    if WALLS_Y == 0:
        WALLS_Y = -108


# End scene function - Scarlet
def show_end_scene():
    global highest_shelf_reached
    font_big = pygame.font.SysFont("Arial", 60)
    font_small = pygame.font.SysFont("Arial", 36)
    selected = 0
    options = ["Try again", "Exit"]
    clock = pygame.time.Clock()
    while True:
        # Draw the same background as the game
        WIN.blit(BACKGROUND, (32, BACKGROUND_Y))
        text1 = font_big.render("You died!", True, WHITE)
        WIN.blit(text1, (WIDTH // 2 - text1.get_width() // 2, HEIGHT // 3))
        msg = f"Highest level reached: {highest_shelf_reached}"
        text2 = font_small.render(msg, True, WHITE)
        WIN.blit(text2, (WIDTH // 2 - text2.get_width() // 2, HEIGHT // 3 + 80))
        for i, opt in enumerate(options):
            color = (255, 255, 0) if i == selected else WHITE
            opt_text = font_small.render(opt, True, color)
            WIN.blit(opt_text, (WIDTH // 2 - opt_text.get_width() // 2, HEIGHT // 2 + 60 + i * 60))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_UP, pygame.K_w]:
                    selected = (selected - 1) % len(options)
                if event.key in [pygame.K_DOWN, pygame.K_s]:
                    selected = (selected + 1) % len(options)
                if event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    if selected == 0:
                        restart_game()
                        return
                    elif selected == 1:
                        pygame.quit()
                        sys.exit(0)
        clock.tick(30)

def restart_game():
    global body, total_shelves_list, highest_shelf_reached, current_standing_shelf, BACKGROUND_ROLLING_SPEED, background_y, WALLS_Y, rolling_down
    body = Body()
    total_shelves_list.clear()
    for num in range(0, SHELVES_COUNT + 1):
        new_shelf = Shelf(num)
        if num % 50 == 0:
            new_shelf.width = BACKGROUND_WIDTH
            new_shelf.rect.width = BACKGROUND_WIDTH
            new_shelf.x = WALL_WIDTH
            new_shelf.rect.x = WALL_WIDTH
        total_shelves_list.append(new_shelf)
    highest_shelf_reached = 0
    current_standing_shelf = None
    BACKGROUND_ROLLING_SPEED = 1
    background_y = BACKGROUND_Y
    WALLS_Y = -128
    rolling_down = False

def GameOver():
    show_end_scene()


def CheckIfTouchingFloor():  # Checking if the body is still on the main ground.
    global standing, falling
    if body.y > HEIGHT - body.size:
        if not rolling_down:  # Still on the starting point of the game, can't lose yet.
            body.y = HEIGHT - body.size
            standing, falling = True, False
        else:  # In a more advanced part of the game, when can already lose.
            GameOver()


def HandleBackground(): # Drawing the background.
    if body.y >= total_shelves_list[500].rect.y:
        WIN.blit(BACKGROUND, (32, background_y))

### New method to wrap all of our music calls for reusability - Rob
def PlayMusic(music):
    global MUSIC_VOLUME
    pygame.mixer.music.unload()
    pygame.mixer.music.load(music)
    pygame.mixer.music.set_volume(MUSIC_VOLUME)
    pygame.mixer.music.play(loops=-1)
    if __debug__:
        print(f"Loaded {music} at volume {MUSIC_VOLUME}")


def main():  # Main function.
    ### Added body_index to global variables - Rob 
    global body, keys_pressed, total_shelves_list, jumping, standing, falling, rolling_down, new_movement, body_index
    game_running = True
    rolling_down = False
    paused = False
    body_timer = 0
    ### New call to play the loaded music - Rob
    PlayMusic(MUSIC_GAMEPLAY)
    while game_running:
        while game_running and not paused:
            on_ground = not rolling_down and body.y == HEIGHT - 25 - body.size
            if rolling_down:  # If screen should roll down.
                for _ in range(BACKGROUND_ROLLING_SPEED):
                    ScreenRollDown()
            DrawWindow()  # Draw shelves, body and background.
            keys_pressed = pygame.key.get_pressed()
            HandleMovement(keys_pressed)  # Moving according to the pressed buttons.
            if body.acceleration != 0:  # If there's any movement.
                Move(current_direction)
            if keys_pressed[pygame.K_SPACE] and (
                    standing or on_ground):  # If enter "Space" and currently not in mid-jump.
                body.vel_y = VEL_Y  # Resets the body's jumping velocity.
                jumping, standing, falling = True, False, False
            if jumping and body.vel_y >= 0:  # Jumping up.
                if body.vel_y == VEL_Y:  # First moment of the jump.
                    JUMPING_SOUND[random.randrange(0,2)].play()
                if __debug__:  ### Adding a debug check for console messages - Rob
                    print("Jumping...")
                body.y -= body.vel_y
                body.vel_y -= 1
                if body.y <= HEIGHT / 5:  # If the body get to the top quarter of the screen.
                    rolling_down = True  # Starts rolling down the screen.
                    for _ in range(10):  # Rolling 10 times -> Rolling faster, so he can't pass the top of the screen.
                        ScreenRollDown()
                if not body.vel_y:  # Standing in the air.
                    jumping, standing, falling = False, False, True
            if falling:  # Falling down.
                if OnShelf():  # Standing on a shelf.
                    if __debug__: ### Adding a debug check for console messages - Rob
                        print("Standing...")
                    jumping, standing, falling = False, True, False
                else:  # Not standing - keep falling down.
                    if __debug__: ### Adding a debug check for console messages - Rob
                        print("Falling...")
                    body.y -= body.vel_y
                    body.vel_y -= 1
            CheckIfTouchingFloor()
            if standing and not OnShelf() and not on_ground:  # If falling from a shelf.
                if __debug__: ### Adding a debug check for console messages - Rob
                    print("Falling from shelf...")
                body.vel_y = 0  # Falls slowly from the shelf and not as it falls at the end of a jumping.
                standing, falling = False, True
            if body.acceleration == MAX_ACCELERATION - 1:  # While on max acceleration, getting a jumping height boost.
                VEL_Y = JUMPING_HEIGHT + 5
            else:  # If not on max acceleration.
                VEL_Y = JUMPING_HEIGHT  # Back to normal jumping height.

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_running = False
            ### Small refactor so delta_time can be used for animation - Rob
            delta_time = pygame.time.Clock().tick(GAME_FPS) /1000.0

            ### Handle body_timer for character animation - Rob
            body_timer += delta_time
            if body_timer > BODY_ANIMATION_SPEED:
                body_timer = 0
                body_index += 1
                if body_index >= len(BODY_IMAGE):
                    body_index = 0


if __name__ == "__main__":
    main()
