import pygame
import platform 
import os
import asyncio
import random
from math import ceil



# ------------------------------ PYGAME SETUP ---------------------------- #
pygame.init()

# Setting game caption 
pygame.display.set_caption(("FLAPPY BIRD"))

# Clock
clock = pygame.time.Clock()

# Initializing game-window resolution (fixed)
screen_width, screen_height = 1000, 600 # 1000, 600 earlier
game_window = pygame.display.set_mode((screen_width, screen_height))

# Hand-cursor for hovering usecases
hand = pygame.SYSTEM_CURSOR_HAND
# ------------------------------ PYGAME SETUP ---------------------------- #



# ---------------------------- GAME VARIABLES ---------------------------- #
top3PersonalHughscoreDict = fetchedTotalCoins = birdPrices = None
app_data_dict = {}
exit_game = game_over = False
fps = 60
# ---------------------------- GAME VARIABLES ---------------------------- #



# ----------------------- PLATFORM SPECIFIC FUNCTIONS -------------------- #
if __import__("sys").platform == "emscripten":
        from platform import window
        import json
        runningOn = "browser"
else:   
        import pickle
        runningOn = "localDevice"    

# Minimizing game window
def minimizeGameForBrowser(): 
    platform.window.canvas.style.width = f"{float(platform.window.myBackground.offsetWidth)*(408/900)}px"
    platform.window.canvas.style.height = f"{float(platform.window.myBackground.offsetWidth)*(304/900)}px"

# Maximizing game window
def maximizeGameForBrowser():
    platform.window.canvas.style.width = f"{float(platform.window.myBackground.offsetWidth)}px"
    platform.window.canvas.style.height = f"{float(platform.window.myBackground.offsetWidth)*(600/1000)}px"

# Presetting the window to minimized state
if runningOn == "browser":
    minimizeGameForBrowser()
    platform.window.myBackground.style.backgroundImage = "url(consoleImage.png)"

# Saving game-data
def saveGameData(runningPlatform=runningOn):
    if runningPlatform == "browser":
        window.localStorage.setItem("appData", json.dumps(app_data_dict))
    else:
        with open('appdata.dat', 'wb') as file_stream:
            pickle.dump(app_data_dict, file_stream)


# Loading game-data
def loadGameData(runningPlatform=runningOn):
    global top3PersonalHughscoreDict, fetchedTotalCoins, birdPrices, app_data_dict
    if runningPlatform == "browser":
        app_data_dict = window.localStorage.getItem("appData")
        # First time running
        if app_data_dict == None:
            app_data_dict = {"HighScore": {"#1":0, "#2":0, "#3":0}, "TotalCoins": 0, "BirdsStatus": {"BlueBird": "unlocked", "GreenBird": "locked", "DarkGreenBird": "locked", "PinkBird": "locked"}}
            window.localStorage.setItem("appData", json.dumps(app_data_dict))
        else:
            app_data_dict = json.loads(app_data_dict)
    else:
        if os.path.isfile("appdata.dat"):
            with open("appdata.dat", "rb") as file:
                data = file.read()
                app_data_dict = pickle.loads(data)
        else:
            # First time running
            app_data_dict = {"HighScore": {"#1":0, "#2":0, "#3":0}, "TotalCoins": 0, "BirdsStatus": {"BlueBird": "unlocked", "GreenBird": "locked", "DarkGreenBird": "locked", "PinkBird": "locked"}}
    
    top3PersonalHughscoreDict = app_data_dict["HighScore"]
    fetchedTotalCoins = app_data_dict["TotalCoins"]
    birdPrices = {"BlueBird":0, "GreenBird":100, "DarkGreenBird":150, "PinkBird":200}

# Erasing game-data -  NOT YET USED
def eraseGameData(runningPlatform=platform):
    if runningPlatform == "browser":
        keys = []
        for i in range(window.localStorage.length):
            keys.append(window.localStorage.key(i))
        while keys: window.localStorage.removeItem(keys.pop())
    else:
        os.unlink("appdata.dat")
# ----------------------- PLATFORM SPECIFIC FUNCTIONS -------------------- #





# ------------------------------- GAME ASSETS ---------------------------- #
# Fonts
font_color = (0, 0, 0)
font = pygame.font.Font('fonts/Clarine.otf', 28)
font2 = pygame.font.Font('fonts/TrendSlabFour.ttf', 16)

# Sounds
audioExtn = "ogg"
button_press_sound = pygame.mixer.Sound(os.path.join("audios", f"beepshort.{audioExtn}"))
wing_flap_sound = pygame.mixer.Sound(os.path.join("audios", f"flap.{audioExtn}"))
wall_hit_sound = pygame.mixer.Sound(os.path.join("audios", f"explosion.{audioExtn}"))
score_increase_sound = pygame.mixer.Sound(os.path.join("audios", f"point.{audioExtn}"))
start_music = pygame.mixer.Sound(os.path.join("audios", f"bgmusic.{audioExtn}"))
life_losing_beep = pygame.mixer.Sound(os.path.join("audios", f"lifelosing.{audioExtn}"))
lock_sound = pygame.mixer.Sound(os.path.join("audios", f"lock.{audioExtn}"))
unlock_sound = pygame.mixer.Sound(os.path.join("audios", f"unlock.{audioExtn}"))
sounds = [button_press_sound, wing_flap_sound, wall_hit_sound,
          score_increase_sound, start_music, life_losing_beep, lock_sound, unlock_sound]

# Background images
welcome_img = pygame.image.load(os.path.join("background", "welcomescreen.png"))
welcome_img = pygame.transform.scale(welcome_img, (screen_width, screen_height)).convert_alpha()
game_bgimg = pygame.image.load(os.path.join("background", "day.jpg"))
game_bgimg = pygame.transform.scale(game_bgimg, (screen_width, screen_height)).convert()
game_bgimg2 = pygame.image.load(os.path.join("background", "night.png"))
game_bgimg2 = pygame.transform.scale(game_bgimg2, (screen_width, screen_height)).convert()
background_image = game_bgimg
background_image_width, background_image_height = background_image.get_rect().size

# Bird images
BlueBird = [pygame.image.load(os.path.join("birds/BlueBird", "BlueBird1.png")),
            pygame.image.load(os.path.join("birds/BlueBird", "BlueBird2.png")),
            pygame.image.load(os.path.join("birds/BlueBird", "BlueBird3.png")),
            pygame.image.load(os.path.join("birds/BlueBird", "BlueBirdDie.png"))]
GreenBird = [pygame.image.load(os.path.join("birds/GreenBird", "GreenBird1.png")),
             pygame.image.load(os.path.join("birds/GreenBird", "GreenBird2.png")),
             pygame.image.load(os.path.join("birds/GreenBird", "GreenBird3.png")),
             pygame.image.load(os.path.join("birds/GreenBird", "GreenBirdDie.png"))]
PinkBird = [pygame.image.load(os.path.join("birds/PinkBird", "PinkBird1.png")),
            pygame.image.load(os.path.join("birds/PinkBird", "PinkBird2.png")),
            pygame.image.load(os.path.join("birds/PinkBird", "PinkBird3.png")),
            pygame.image.load(os.path.join("birds/PinkBird", "PinkBirdDie.png"))]
DarkGreenBird = [pygame.image.load(os.path.join("birds/DarkGreenBird", "DarkGreenBird1.png")),
                 pygame.image.load(os.path.join("birds/DarkGreenBird", "DarkGreenBird2.png")),
                 pygame.image.load(os.path.join("birds/DarkGreenBird", "DarkGreenBird3.png")),
                 pygame.image.load(os.path.join("birds/DarkGreenBird", "DarkGreenBirdDie.png"))]

# Other images
selection_box = pygame.image.load(os.path.join("others", 'selection_box2.png'))
arrows = [pygame.image.load(os.path.join("others", 'left_button.png')),
          pygame.image.load(os.path.join("others", 'right_button.png')),
          pygame.image.load(os.path.join("others", 'left_button_small.png')),
          pygame.image.load(os.path.join("others", 'right_button_small.png'))]
play_button_box = pygame.image.load(os.path.join("others", 'playbutton.png'))
shop_button_box = pygame.image.load(os.path.join("others", "shopbutton.png"))
menu_button_box = pygame.image.load(os.path.join("others", "menubutton.png"))
leaderboard_button_box = pygame.image.load(os.path.join("others", "leaderboardButton.png"))
speaker_images = [pygame.image.load(os.path.join("others", 'speaker_on.png')).convert_alpha(),
                  pygame.image.load(os.path.join("others", 'speaker_off.png')).convert_alpha()]
screen_resize_images = [pygame.image.load(os.path.join("others", 'fullscreen.png')).convert_alpha(),
                        pygame.image.load(os.path.join("others", 'shortscreen.png')).convert_alpha()]
heart = pygame.image.load(os.path.join("others", "heart.png"))
coin_image = pygame.image.load(os.path.join("others", "coin.png"))
lock_image = pygame.image.load(os.path.join("others", "lock.png"))
# ------------------------------- GAME ASSETS ---------------------------- #



# ------------------------------------------------------------------------ #
# Bird 
class Bird:
    X_POS = 50
    Y_POS = 200

    def __init__(self):
        self.fly_img = BlueBird
        self.fall_img = BlueBird[2]

        self.image = self.fall_img
        self.bird_fly = False
        self.bird_rect = self.image.get_rect()
        self.bird_rect.x = self.X_POS
        self.bird_rect.y = self.Y_POS
        self.step_index = 0  # this is for displaying the different Bird images

    def update(self, userInput):
        if self.bird_fly:
            self.Y_POS -= 4
            self.fly()
        if not self.bird_fly:
            self.Y_POS += 4
            self.fall()
        if self.step_index > 10:
            self.step_index = 0
        if userInput == 'bird_dead':
            self.image = self.fly_img[3]
            self.bird_rect = self.image.get_rect()
            self.bird_rect.x = self.X_POS
            self.bird_rect.y = self.Y_POS #+ -8
        elif userInput[pygame.K_UP] and not self.bird_fly:
            self.bird_fly = True
            wing_flap_sound.play()
        elif self.bird_fly and not userInput[pygame.K_UP]:
            self.bird_fly = False

    def fly(self):
        self.image = self.fly_img[self.step_index // 5]
        self.bird_rect = self.image.get_rect()
        self.bird_rect.x = self.X_POS
        self.bird_rect.y = self.Y_POS
        self.step_index += 1

    def fall(self):
        self.image = self.fall_img
        self.bird_rect = self.image.get_rect()
        self.bird_rect.x = self.X_POS
        self.bird_rect.y = self.Y_POS

    def draw(self, game_window):
        game_window.blit(self.image, (self.bird_rect.x, self.bird_rect.y))

# Pillar
class Obstacle:
    passage_length = 130

    def __init__(self, where_wall):
        self.i = random.randint(60, 320)
        self.where_wall = where_wall
        self.wall_speed = -4
        self.rect1 = pygame.Rect(self.where_wall, 0, 50, self.i)
        self.rect2 = pygame.Rect(
            self.where_wall, self.i+(self.passage_length+30), 50, 487-self.i-(self.passage_length+30))
        self.rect3 = pygame.Rect(self.where_wall - 5, self.i, 60, 15)
        self.rect4 = pygame.Rect(self.where_wall - 5, self.i+(self.passage_length+15), 60, 15)

    def update(self):
        self.rect1.x += self.wall_speed
        self.rect2.x += self.wall_speed
        self.rect3.x += self.wall_speed
        self.rect4.x += self.wall_speed

    def draw(self, game_window):

        self.rect2.y, self.rect2.h = self.i+(self.passage_length+30), 487-self.i-(self.passage_length+30)
        self.rect4.y, self.rect4.h = self.i+(self.passage_length+15), 15

        pygame.draw.rect(game_window, (211, 118, 118),
                         self.rect1)
        pygame.draw.rect(game_window, (211, 118, 118), self.rect2)
        pygame.draw.rect(game_window, (255, 202, 212),
                         self.rect3)
        pygame.draw.rect(game_window, (255, 202, 212),
                         self.rect4)
        
    def checkPillarOutOfScreen(obstacles):
        for wallWithPassage in obstacles:
            if wallWithPassage.rect1.x < -wallWithPassage.rect1.width:
                wallWithPassage.rect1.x += (screen_width + wallWithPassage.rect1.width)
                wallWithPassage.rect2.x += (screen_width + wallWithPassage.rect1.width)
                wallWithPassage.rect3.x += (screen_width + wallWithPassage.rect1.width)
                wallWithPassage.rect4.x += (screen_width + wallWithPassage.rect1.width)
                

# Coin
class Coin:
    def checkCoinOutOfScreen(coinsList):
        for coin in coinsList:
            if coin.image_rect.x < -coin.image_rect.width:
                coin.pushCoinAfterScreen()

    def pushCoinAfterScreen(self):
        self.image_rect.x += (screen_width + self.image_rect.width)
        self.where_coin += (screen_width + self.image_rect.width)
        self.i = random.randint(50, 450)
        self.image_rect.y = self.i

    def __init__(self, where_coin):
        self.i = random.randint(50, 450)
        self.where_coin = where_coin
        self.coin_speed = -4
        self.image = coin_image
        self.image_rect = self.image.get_rect()
        self.image_rect.x = self.where_coin
        self.image_rect.y = self.i

    def update(self):
        self.image_rect.x += self.coin_speed
        self.where_coin += self.coin_speed

    def draw(self, game_window, obstacles):
        for wall_with_passage in obstacles:
            collide_list = [wall_with_passage.rect1, wall_with_passage.rect2,
                            wall_with_passage.rect3, wall_with_passage.rect4]
            check_collision = self.image_rect.collidelist(collide_list)
            if check_collision >= 0:
                self.image_rect.x += (self.image_rect.width + collide_list[check_collision].width)
                self.where_coin += (self.image_rect.width + collide_list[check_collision].width)
        game_window.blit(self.image, (self.where_coin, self.i))
        

# Text animation
def display_text_animation(string, verticle_position):
    text = ''
    for i in range(len(string)):
        text += string[i]

        random_int = random.randint(0, 255)
        pulsating_text = font.render(
            text, True, (random_int, 255 - random_int, random_int))

        pulsation_factor = 0.5 + \
            abs((pygame.time.get_ticks() % 1000) - 500) / 500

        width = int(pulsating_text.get_width() * pulsation_factor)
        height = int(pulsating_text.get_height() * pulsation_factor)

        pulsating_text = pygame.transform.scale(
            pulsating_text,
            (width, height)
        )

        text_x = width // 2 - pulsating_text.get_width() // 2
        text_y = 200

        game_window.blit(pulsating_text, (250 + text_x, -120 + text_y))
# ------------------------------------------------------------------------ # 


async def main():

    loadGameData()
    
    # -------------- GENERAL VARIABLES --------------- # 
    # Others
    screen = "menuScreen"
    bird_list = [BlueBird, GreenBird, PinkBird, DarkGreenBird]
    sound_toggle_button = speaker_images[0]
    screen_resize_button = screen_resize_images[0]
    index = 0  # for switching birds
    step = 0  # for changing selected bird sprites
    sound_toggle_area = pygame.Rect(920, 80, 50, 40)
    screen_toggle_area = pygame.Rect(920, 30, 41, 40)
    enableFullscreen = False

    # Initializing Bird Object
    selected_bird = bird_list[index]
    flappy_bird_object = Bird()
    flappy_bird_object.fly_img = selected_bird
    flappy_bird_object.fall_img = selected_bird[2]
    # -------------- GENERAL VARIABLES --------------- #


    # ----------------- GAME SCREEN ------------------ #
    coins_list = [Coin(screen_width + (screen_width)/6), Coin(screen_width + 3*(screen_width)/6), Coin(screen_width + 5*(screen_width)/6)]
    obstacles = [Obstacle(screen_width), Obstacle(screen_width + (screen_width)/3), Obstacle(screen_width + 2*(screen_width)/3)]
    tiles = ceil(screen_width/background_image_width)+1
    scroll = 0
    coin_count = 0
    score = 0
    lives_count = 3
    lives_distance = [90, 130, 170]
    game_over =  False
    # ----------------- GAME SCREEN ------------------ #


    # ----------------- MENU SCREEN ------------------ #
    # Hover reader typewriter text config + event
    typewriter_event = pygame.USEREVENT+2
    pygame.time.set_timer(typewriter_event, 100)
    text = ''
    text_len = 0
    text_surf = None
    text_color = (1, 50, 32)

    # Start music loop event
    startMusicTimer = pygame.USEREVENT+1
    pygame.time.set_timer(startMusicTimer, 29000)
    start_music.play(maxtime=29000)

    # button images
    left_arrow = arrows[0]
    right_arrow = arrows[1]
    play_button = play_button_box

    # Interaction areas of welcome screen
    play_area = pygame.Rect(680, 230, 143, 50)
    shop_area = pygame.Rect(680, 290, 143, 56)
    right_button_area = pygame.Rect(300, 250, 30, 40)
    left_button_area = pygame.Rect(160, 250, 30, 40)

    # Other
    shop_button_display = False
    # ----------------- MENU SCREEN ------------------ #


    # _____________ HIGHSCORE SCREEN -------------- #
    # Typewriter text config + event
    text2 = 'Press Any Key To Restart'
    text_len2 = 0
    typewriter_event2 = pygame.USEREVENT+3
    pygame.time.set_timer(typewriter_event2, 100)
    text_surf2 = None
    text_color2 = font_color


    new_highscore = False
    STEP = 0
    flying_bird_x = 0
    flying_bird_y = screen_height // 2 - 140
    sign = +1
    menu_button_area = pygame.Rect(screen_width//2 - 90, screen_height//2 + 220, 98, 45)
    leaderboard_button_area = pygame.Rect(screen_width//2 + 40, screen_height//2 + 220, 47, 45)
    # _____________ HIGHSCORE SCREEN -------------- #


    def resetGameScreen():
        nonlocal score, scroll, obstacles, coins_list, coin_count, flappy_bird_object, tiles, lives_count,  game_over, screen, step, index, new_highscore

        game_over = False
        new_highscore = False

        flappy_bird_object.Y_POS = 200
        flappy_bird_object.bird_rect.y = 200
        pygame.display.update(flappy_bird_object.bird_rect)
        index = 0  # for switching birds
        step = 0  # for changing selected bird sprites
 
        coins_list = [Coin(screen_width + (screen_width)/6), Coin(screen_width + 3*(screen_width)/6), Coin(screen_width + 5*(screen_width)/6)]
        obstacles = [Obstacle(screen_width), Obstacle(screen_width + (screen_width)/3), Obstacle(screen_width + 2*(screen_width)/3)]
        tiles = ceil(screen_width/background_image_width)+1
        scroll = 0
        coin_count = 0
        score = 0
        lives_count = 3


    def menu_screen():
        global fetchedTotalCoins, birdPrices, app_data_dict, screen_resize_images
        nonlocal selected_bird, step, left_arrow, right_arrow, sound_toggle_button, screen_toggle_area,screen_resize_button, text_surf, shop_button_display, text_len, text, text_color, index, screen, enableFullscreen, sound_toggle_area
        
        # ----------------------------- BLITTING IMAGES --------------------------- #
        game_window.blit(welcome_img, (0, 0)) 
        game_window.blit(coin_image, (10, 70))
        game_window.blit(sound_toggle_button, (sound_toggle_area.x, sound_toggle_area.y))
        if runningOn == "browser": game_window.blit(screen_resize_button, (screen_toggle_area.x, screen_toggle_area.y))
        game_window.blit(selection_box, (200, 230))
        game_window.blit(left_arrow, (160, 250))
        game_window.blit(right_arrow, (300, 250))
        game_window.blit(selected_bird[step//10], (220, 250))
        game_window.blit(play_button, (680, 230))
        if shop_button_display: game_window.blit(shop_button_box, (680, 290))

    
        total_coins = font.render("Total Coins", True, (255, 255, 255))
        totalCoinsRect = total_coins.get_rect()
        totalCoinsRect.center = (70, 50)
        game_window.blit(total_coins, totalCoinsRect)

        total_coins_count = font.render(
            ": " + str(fetchedTotalCoins), True, (255, 255, 255))
        totalCoinsCountRect = total_coins_count.get_rect()
        totalCoinsCountRect.center = (85, 85)
        game_window.blit(total_coins_count, totalCoinsCountRect)
        # ----------------------------- BLITTING IMAGES --------------------------- #

        step += 1
        if step > 20:
            step = 0


        # ---------------------- TRACKING MOUSE HOVER POSITION -------------------- #
        # Mouse button pressed ?
        left, middle, right = pygame.mouse.get_pressed()

        # Mouse pointer not over any hoverable area
        if True:
            # Setting mouse pointer to default shape
            pygame.mouse.set_cursor()
            text = "FLAPPY BIRD GAME! LESS GOOOO"
            text_color = (1, 50, 32)

            if pygame.mixer.Sound.get_volume(sounds[0]) == 0.0:
                sound_toggle_button = speaker_images[1]
            else:
                sound_toggle_button = speaker_images[0]

        # Mouse pointer over speaker button
        if sound_toggle_area.collidepoint(pygame.mouse.get_pos()):
            # Setting mouse pointer to hand shape
            pygame.mouse.set_cursor(hand)
            text = "Turn Sound Off"
            text_color = (0, 0, 0)

            if left and sound_toggle_area.collidepoint(pygame.mouse.get_pos()):
                if pygame.mixer.Sound.get_volume(sounds[0]) == 0.0:
                    sound_toggle_button = speaker_images[1]
                else:
                    sound_toggle_button = speaker_images[0]
            else:
                if sound_toggle_button == speaker_images[0]:
                    text = "Turn-Off Sound"
                else:
                    text = "Turn-On Sound"

        # Mouse pointer over resize button
        if screen_toggle_area.collidepoint(pygame.mouse.get_pos()) and runningOn == "browser":
            # Setting mouse pointer to hand shape
            pygame.mouse.set_cursor(hand)
            text = "Fullscreen"
            text_color = (0, 0, 0)

            if left and screen_toggle_area.collidepoint(pygame.mouse.get_pos()):
                if enableFullscreen:
                    screen_resize_button = screen_resize_images[1]
                else:
                    screen_resize_button = screen_resize_images[0]
            else:
                if enableFullscreen:
                    text = "Minimize"
                else:
                    text = "Fullscreen"

        # Mouse pointer over play button
        if play_area.collidepoint(pygame.mouse.get_pos()):
            # Setting mouse pointer to hand shape
            pygame.mouse.set_cursor(hand)
            text_color = (0, 0, 0)

            if shop_button_display:
                text = "Bird Locked"
            else:
                text = "Start Game"

        # Mouse pointer over left button
        if left_button_area.collidepoint(pygame.mouse.get_pos()):
            # Setting mouse pointer to hand shape
            pygame.mouse.set_cursor(hand)
            text = "See Previous Bird"
            text_color = (0, 0, 0)

            if left and left_button_area.collidepoint(pygame.mouse.get_pos()):
                left_arrow = arrows[2]
            else:
                left_arrow = arrows[0]

        # Mouse pointer over right button
        if right_button_area.collidepoint(pygame.mouse.get_pos()):
            # Setting mouse pointer to hand shape
            pygame.mouse.set_cursor(hand)
            text = "See Next Bird"
            text_color = (0, 0, 0)

            if left and right_button_area.collidepoint(pygame.mouse.get_pos()):
                right_arrow = arrows[3]
            else:
                right_arrow = arrows[1]

        # Mouse pointer over shop button
        if shop_area.collidepoint(pygame.mouse.get_pos()) and shop_button_display:
            pygame.mouse.set_cursor(hand)
            text_color = (0, 0, 0)

            if fetchedTotalCoins >= birdPrices[[k for k, v in globals().items() if v == selected_bird][0]]:
                text = f"Spend {birdPrices[[k for k, v in globals().items() if v == selected_bird][0]]} Coins to Purchase Bird"
            else:
                text = "Not Enough Coins to Purchase Bird"
        # ---------------------- TRACKING MOUSE HOVER POSITION -------------------- #

        if text_surf:
            move_x = (screen_width//2) - (text_surf.get_width()//2)
            game_window.blit(text_surf, text_surf.get_rect(
                midleft=game_window.get_rect().midleft).move(move_x, 220))

        # -------------------- DISPLAYING STUFF FOR LOCKED BIRDS ------------------ #
        if app_data_dict["BirdsStatus"][[k for k, v in globals(
                            ).items() if v == selected_bird][0]] == "locked":
            # Creating a surface for veil
            veil = pygame.Surface((75, 60))
            veil.set_alpha(128)
            veil.fill((128, 128, 128))

            # Displaying veil
            game_window.blit(veil, (210, 240))

            # Displaying a little lock 
            game_window.blit(lock_image, (270, 280))

            # Displaying bird price
            game_window.blit(coin_image, (200, 310))
            reqPrice = birdPrices[[k for k, v in globals().items() if v == selected_bird][0]]
            req_coins = font2.render(f"x{reqPrice}", True, (255, 255, 255))
            reqCoinsRect = req_coins.get_rect()
            reqCoinsRect.center = (260, 330)
            game_window.blit(req_coins, reqCoinsRect)

            # Turn shop_button_display bool to True
            shop_button_display = True
        else:
            shop_button_display = False
        # -------------------- DISPLAYING STUFF FOR LOCKED BIRDS ------------------ #

        # --------------------------- LISTENING TO EVENTS ------------------------- #
        for event in pygame.event.get():
            # Close button pressed
            if event.type == pygame.QUIT:
                __import__("sys").exit()

            # Music timer event fired
            if event.type == startMusicTimer:
                start_music.play(maxtime=29000)

            # Hover typewriter text event fired
            if event.type == typewriter_event:
                text_len += 1
                if text_len > len(text):
                    text_len = 0
                text_surf = None if text_len == 0 else font.render(
                    text[:text_len], True, text_color)
                
            # Mouse button clicked
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Storing mouse coordinates
                mouse_x, mouse_y = pygame.mouse.get_pos()
            
                if play_area.collidepoint(mouse_x, mouse_y):
                    if not shop_button_display:
                        button_press_sound.play()
                        pygame.mixer.Sound.stop(start_music)
                        pygame.time.set_timer(startMusicTimer, 0)
                        flappy_bird_object.fly_img = selected_bird
                        flappy_bird_object.fall_img = selected_bird[2]
                        screen = "gameScreen"
                    else:
                        lock_sound.play()

                elif shop_area.collidepoint(mouse_x, mouse_y):
                    if shop_button_display:
                        if fetchedTotalCoins >= birdPrices[[k for k, v in globals().items() if v == selected_bird][0]]:
                            unlock_sound.play()
                            fetchedTotalCoins -= 100
                            app_data_dict["BirdsStatus"][[k for k, v in globals(
                            ).items() if v == selected_bird][0]] = "unlocked"
                            app_data_dict["TotalCoins"] -= 100
                            saveGameData()
                        else:
                            lock_sound.play()

                elif left_button_area.collidepoint(mouse_x, mouse_y):
                    button_press_sound.play()
                    if index == 0:
                        index = 3
                    else:
                        index -= 1
                    selected_bird = bird_list[index]

                elif right_button_area.collidepoint(mouse_x, mouse_y):
                    button_press_sound.play()
                    if index == 3:
                        index = 0
                    else:
                        index += 1
                    selected_bird = bird_list[index]

                elif sound_toggle_area.collidepoint(mouse_x, mouse_y):
                    # Sound On
                    if sound_toggle_button == speaker_images[0]:
                        for sound in sounds:
                            sound.set_volume(0)
                    # Sound Off
                    else:
                        for sound in sounds:
                            sound.set_volume(1)

                elif screen_toggle_area.collidepoint(mouse_x, mouse_y) and runningOn == "browser":
                    if screen_resize_button == screen_resize_images[0]:
                        enableFullscreen = True
                    else:
                        enableFullscreen = False
        # --------------------------- LISTENING TO EVENTS ------------------------- #

    def game_screen():

        global background_image, font_color, top3PersonalHughscoreDict, app_data_dict, fetchedTotalCoins
        nonlocal score, scroll, obstacles, coins_list, coin_count, score, flappy_bird_object, tiles, lives_count, lives_distance, game_over, screen, new_highscore, startMusicTimer, selected_bird

        # Silly little bird exhausted all its lives anddd DIEDDDD
        if game_over:
            wall_hit_sound.play()
            flappy_bird_object.update('bird_dead')
            game_window.blit(
                flappy_bird_object.image, (flappy_bird_object.bird_rect.x, flappy_bird_object.bird_rect.y))
            pygame.display.update()


            # fixing highscore, Total_Coins and BirdsStatus Value
            if score//100 > top3PersonalHughscoreDict['#1']:
                new_highscore = True
            top3PersonalHighscoreList = sorted(list(top3PersonalHughscoreDict.values()), reverse=True)
            for i in range(3):
                if score//100 > top3PersonalHighscoreList[i]:
                    top3PersonalHighscoreList.insert(i, score//100)
                    top3PersonalHighscoreList.pop()
                    top3PersonalHughscoreDict = dict(zip([f"#{j}" for j in range(1,4)],top3PersonalHighscoreList))
                    app_data_dict["HighScore"] = top3PersonalHughscoreDict
                    break
            fetchedTotalCoins += coin_count
            app_data_dict["TotalCoins"] += coin_count
            
            # Save game data
            saveGameData()

            # Changing to scoreScreen
            pygame.time.wait(2000)
            screen = "scoreScreen"
            start_music.play(maxtime=29000)
            pygame.time.set_timer(startMusicTimer, 29000)
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    __import__('sys').exit()


        # Updating the score board
        def score_board():
            nonlocal score
            score += 1

            # highscore area
            highscore = font.render(
                str("HighScore: ").rjust(11) + str(top3PersonalHughscoreDict['#1']).rjust(3), True, font_color)
            highscoreRect = highscore.get_rect()
            highscoreRect.center = (880, 40)

            # Points area
            points = font.render(str("Distance: ").rjust(11) + str(score//100).rjust(3), True, font_color)
            pointsRect = points.get_rect()
            pointsRect.center = (880, 70)

            game_window.blit(points, pointsRect)
            game_window.blit(highscore, highscoreRect)


        # ------------------------ ARENA BACKGROUND ------------------------ #
        # Adding background image at the last for creating endless arena effect
        for i in range(0, tiles):
            game_window.blit(background_image,
                            (i*background_image_width + scroll, 0))
            
        scroll -= 2
        
        # Resest the scroll
        if abs(scroll) > background_image_width:
            scroll = 0

        # Changing background image based on score
        if score//100 > 50:
            # Night background
            background_image = game_bgimg2
            font_color = (255, 202, 212)
        else:
            # Day background
            background_image = game_bgimg
            font_color = (0, 0, 0)
        # # Changing obstacle passage length based on score
        # if (score//100 >= 5) and (score//100 % 5 == 0):
        #     Obstacle.passage_length -= 1/50
        # print(Obstacle.passage_length)
        # # else:
        # #     Obstacle.passage_length = 130
        # ------------------------ ARENA BACKGROUND ------------------------ #


        # ------------------------ LIFE-LOSING CASES ----------------------- #
        def findRevivalPlace():
            closestPillar = min(obstacles, key = lambda obj: abs(flappy_bird_object.bird_rect.x-obj.rect1.x))
            return closestPillar.i+30
        
        # Collision detection function
        def check_collision():
            nonlocal game_over, lives_count
            for wall_with_passage in obstacles:
                collide_list = [wall_with_passage.rect1, wall_with_passage.rect2,
                                wall_with_passage.rect3, wall_with_passage.rect4]
                check_collision = flappy_bird_object.bird_rect.collidelist(
                    collide_list)
                if check_collision >= 0:
                    if lives_count > 0:
                        life_losing_beep.play()
                        lives_count -= 1
                        pygame.draw.rect(game_window, (255, 87, 51),
                                        collide_list[check_collision])
                        pygame.display.update(collide_list[check_collision])
                        flappy_bird_object.Y_POS = findRevivalPlace()
                        pygame.display.update(flappy_bird_object.bird_rect)
                        # pygame.time.wait(1000)

                    else:
                        pygame.draw.rect(game_window, (255, 87, 51),
                                        collide_list[check_collision])
                        game_over = True

        # bird hitting the wall or ground
        if flappy_bird_object.bird_rect.y > 440 or flappy_bird_object.bird_rect.y < 0:
            if lives_count > 0:
                life_losing_beep.play()
                lives_count -= 1
                flappy_bird_object.Y_POS = findRevivalPlace()
                pygame.display.update(flappy_bird_object.bird_rect)
                # pygame.time.wait(1000)
            else:
                game_over = True
        # ------------------------ LIFE-LOSING CASES ----------------------- #



        # ------------------- DISPLAYING COINS AND PILLARS ----------------- #     
        for coin in coins_list:
            coin.draw(game_window, obstacles)
            coin.update()
            Coin.checkCoinOutOfScreen(coins_list)

            if flappy_bird_object.bird_rect.colliderect(coin.image_rect):
                coin.pushCoinAfterScreen()
                score_increase_sound.play()
                coin_count += 1

        for wall_with_passage in obstacles:
            wall_with_passage.draw(game_window)
            wall_with_passage.update()
            Obstacle.checkPillarOutOfScreen(obstacles)
        # ------------------- DISPLAYING COINS AND PILLARS ----------------- # 


        # ---------------- LISTENING TO KEYBOARD USERINPUT ----------------- #
        userInput = pygame.key.get_pressed()
        flappy_bird_object.draw(game_window)
        flappy_bird_object.update(userInput)
        # ---------------- LISTENING TO KEYBOARD USERINPUT ----------------- #


        # ---------------- DISPLAYING STUFF ON GAME SCREEN ----------------- #
        # flappy_bird_object.draw(game_window)
        for i in range(0, lives_count): game_window.blit(heart, (lives_distance[i], 30))
        game_window.blit(coin_image, (30, 30))
        coin_points = font2.render("x"+str(coin_count), True, (255, 255, 255))
        coinRect = coin_points.get_rect()
        coinRect.center = (70, 60)
        game_window.blit(coin_points, coinRect)
        # ---------------- DISPLAYING STUFF ON GAME SCREEN ----------------- #

        check_collision()
        score_board()


    def score_screen():
        
        global top3PersonalHughscoreDict, background_image, font_color, fetchedTotalCoins, screen_resize_images
        nonlocal score, sound_toggle_button, STEP, flying_bird_x, flying_bird_y, sign, leaderboard_button_area, text2, text_len2, text_surf2, text_color2, typewriter_event2, menu_button_area, sound_toggle_area, new_highscore, screen, startMusicTimer, screen_resize_button, screen_toggle_area, enableFullscreen, selected_bird

        # -------------------- DISPLAYING STUFF ON SCREEN ----------------------- #
        game_window.blit(background_image, (0, 0))
        game_window.blit(sound_toggle_button, (sound_toggle_area.x, sound_toggle_area.y))
        if runningOn == "browser": game_window.blit(screen_resize_button, (screen_toggle_area.x, screen_toggle_area.y))
        game_window.blit(
            menu_button_box, (menu_button_area.x, menu_button_area.y))
        game_window.blit(
            leaderboard_button_box, (leaderboard_button_area.x, leaderboard_button_area.y))
        score_points = font.render(
            "Your Score: " + str(score//100), True, font_color)
        scoreRect = score_points.get_rect()
        scoreRect.center = (screen_width // 2, screen_height // 2 + 40)
        game_window.blit(score_points, scoreRect)
        game_window.blit(
            selected_bird[STEP//20], (flying_bird_x, flying_bird_y))
        # -------------------- DISPLAYING STUFF ON SCREEN ----------------------- #

        if STEP % 20 == 0:
            sign *= -1

        STEP += 2
        if STEP > 40:
            STEP = 0

        flying_bird_x += 8
        if flying_bird_x > screen_width:
            flying_bird_x = 0


        # ------------------- CHECKING FOR NEW HIGHSCORE ---------------------- #
        if new_highscore:
            oldScore = font.render(f"Your old persnonal best was: {top3PersonalHughscoreDict['#2']}", True, font_color)
            oldScoreRect = oldScore.get_rect()
            oldScoreRect.center = (screen_width // 2, screen_height // 2 + 160)
            game_window.blit(oldScore, oldScoreRect)
            display_text_animation("NEW HIGHSCORE REACHED !!!", 100)
        else:
            display_text_animation("GAME OVER !   TRY AGAIN !", 100)
        # ------------------- CHECKING FOR NEW HIGHSCORE ---------------------- #


        # ------------------------ TEXT ANIMATION ----------------------------- #
        if text_surf2:
            move_x = (screen_width//2) - (text_surf2.get_width()//2)
            game_window.blit(text_surf2, text_surf2.get_rect(
                midleft=game_window.get_rect().midleft).move(move_x, -50))
        pygame.display.update()
        # ------------------------ TEXT ANIMATION ----------------------------- #

        
        # --------------------- LISTENING TO EVENTS --------------------------- #
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == startMusicTimer:
                start_music.play(maxtime=29000)
            if event.type == typewriter_event2:
                text_len2 += 1
                if text_len2 > len(text2):
                    text_len2 = 0
                text_surf2 = None if text_len2 == 0 else font.render(
                    text2[:text_len2], True, text_color2)
            if event.type == pygame.KEYDOWN:
                pygame.mixer.Sound.stop(start_music)
                pygame.time.set_timer(startMusicTimer, 0)
                screen = "gameScreen"
                resetGameScreen()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if sound_toggle_area.collidepoint(mouse_x, mouse_y):
                    if sound_toggle_button == speaker_images[0]:
                        for sound in sounds:
                            sound.set_volume(0)
                    else:
                        for sound in sounds:
                            sound.set_volume(1)
                elif menu_button_area.collidepoint(mouse_x, mouse_y):
                    button_press_sound.play()
                    pygame.mixer.Sound.stop(start_music)
                    pygame.time.set_timer(startMusicTimer, 0)
                    pygame.time.set_timer(startMusicTimer, 29000)
                    start_music.play(maxtime=29000)
                    resetGameScreen()
                    selected_bird = bird_list[0]
                    screen = "menuScreen"
                elif leaderboard_button_area.collidepoint(mouse_x, mouse_y):
                    button_press_sound.play()
                    pygame.mixer.Sound.stop(start_music)
                    # screen = "leaderboardScreen"
                elif screen_toggle_area.collidepoint(mouse_x, mouse_y) and runningOn == "browser":
                    if screen_resize_button == screen_resize_images[0]:
                        enableFullscreen = True
                    else:
                        enableFullscreen = False
        # --------------------- LISTENING TO EVENTS --------------------------- #            


        # -------------- CHANGING CURSOR ON HOVERABLE BUTTONS ----------------- #
        left, middle, right = pygame.mouse.get_pressed()

        if True:
            # Setting cursor to default shape
            pygame.mouse.set_cursor()
            if pygame.mixer.Sound.get_volume(sounds[0]) == 0.0:
                sound_toggle_button = speaker_images[1]
            else:
                sound_toggle_button = speaker_images[0]
            text2 = "Press Any Key To Restart"
            text_color2 = (0, 0, 0)

        # Mouse pointer over resize button
        if screen_toggle_area.collidepoint(pygame.mouse.get_pos()) and runningOn == "browser":
            # Setting mouse pointer to hand shape
            pygame.mouse.set_cursor(hand)
            text2 = "Fullscreen"
            text_color2 = (0, 0, 0)

            if left and screen_toggle_area.collidepoint(pygame.mouse.get_pos()):
                if enableFullscreen:
                    screen_resize_button = screen_resize_images[1]
                else:
                    screen_resize_button = screen_resize_images[0]
            else:
                if enableFullscreen:
                    text2 = "Minimize"
                else:
                    text2 = "Fullscreen"

        if sound_toggle_area.collidepoint(pygame.mouse.get_pos()):
            pygame.mouse.set_cursor(hand)
            if left and sound_toggle_area.collidepoint(pygame.mouse.get_pos()):
                if pygame.mixer.Sound.get_volume(sounds[0]) == 0.0:
                    sound_toggle_button = speaker_images[1]
                else:
                    sound_toggle_button = speaker_images[0]
            
            if sound_toggle_button == speaker_images[0]:
                text2 = "Turn Speaker-Off"
                text_color2 = (0, 0, 0)
            else:
                text2 = "Turn Speaker-On"
                text_color2 = (0, 0, 0)
        
        if menu_button_area.collidepoint(pygame.mouse.get_pos()):
            pygame.mouse.set_cursor(hand)
            text2 = "Go Back to Main Menu"
            text_color2 = (0, 0, 0)
        
        if leaderboard_button_area.collidepoint(pygame.mouse.get_pos()):
            pygame.mouse.set_cursor(hand)
            text2 = "See Global Leaderboard"
            text_color2 = (0, 0, 0)
        # ____________________________________________________

    running = True
    while running: 
        if enableFullscreen and runningOn=="browser":
            maximizeGameForBrowser()
        elif not enableFullscreen and runningOn=="browser":
            minimizeGameForBrowser()

        if screen == "menuScreen":
            menu_screen()
        elif screen == "gameScreen":
            game_screen()
        elif screen == "scoreScreen":
            score_screen()
        
        clock.tick(fps)
        pygame.display.update()
        await asyncio.sleep(0)
    
    pygame.quit()

asyncio.run(main())
