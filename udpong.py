import pygame
import os
import random
import sys
import math
import pygame.image
from pygame.locals import *

WINSCORE = 4

def load_png(name):
    """ Load image and return image object"""
    fullname = os.path.join('images', name)
    try:
        image = pygame.image.load(fullname)
        if image.get_alpha() is None:
            image = image.convert()
        else:
            image = image.convert_alpha()
    except pygame.error, message:
        print 'Cannot load image:', fullname
        raise SystemExit, message
    return image, image.get_rect()

def load_snd(name):
    """ Load sound and return sound object"""
    fullname = os.path.join('sounds', name)
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error, message:
        print 'Cannot load sound:', fullname
        raise SystemExit, message
    return sound

class Court(pygame.Surface):
    def __init__(self, (width, height)):
        pygame.Surface.__init__(self, (width, height))

    def collide_top(self, obj):
        return obj.top < 0

    def collide_bottom(self, obj):
        return obj.bottom > self.get_height()

    def collide_player(self, ball, player):
        return player.collide_ball(ball)

    def update_ball(self, ball, players):
       if self.collide_top(ball.rect) or self.collide_bottom(ball.rect):
           ball.vector = (ball.vector[0], ball.vector[1] * -1)

       for player in players:
           if self.collide_player(ball, player):
               player.play_hit_sound()
               if ball.vector[0] < 0:
                   ball.rect.left = player.rect.right + 1
               else:
                   ball.rect.right = player.rect.left - 1
               ball.vector = player.ball_vector(ball)
               player.reset_sauce()
       ball.update()


class Ball(pygame.sprite.Sprite):
    def __init__(self, vector):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_png('ball.png')
        self.vector = vector

    def update(self):
        self.rect.left += self.vector[0]
        self.rect.top += self.vector[1]

    def draw(self, surface):
        surface.blit(self.image, (self.rect.left, self.rect.top))

def vector_function(angle):
    return (math.cos(math.pi/2 * angle/90), -math.sin(math.pi/2 * angle/90))

class Player(pygame.sprite.Sprite):
    MOVEDIST = 5
    SAUCELEFT = 0
    SAUCERIGHT = 1
    MAXSAUCE = 30
    MINSAUCE = 5
    SAUCEINC = 3
    SAUCEDEC = 1
    vector_list = [vector_function(75.0),
                   vector_function(60.0),
                   vector_function(50.0),
                   vector_function(40.0),
                   vector_function(30.0),
                   vector_function(20.0),
                   vector_function(10.0),
                   vector_function(0.0),
                   vector_function(-10.0),
                   vector_function(-20.0),
                   vector_function(-30.0),
                   vector_function(-40.0),
                   vector_function(-50.0),
                   vector_function(-60.0),
                   vector_function(-75.0)]
    def __init__(self, court):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_png(self.image_file)
        self.hit_sound = load_snd(self.hit_sound_file)
        self.sauce = self.MINSAUCE
        self.last_sauce = self.SAUCELEFT
        self.topmost = 0
        self.bottommost = court.get_rect().height
        self.up = None
        self.down = None

    def __str__(self):
        return self.name

    def ball_vector(self, ball):
        vector = None
        ball_middle = ball.rect.bottom - (ball.rect.height / 2)
        hit_spot = ball_middle - self.rect.top

        hit_idx = math.floor((float(hit_spot) / self.rect.height) * (len(self.vector_list) - 2))
        
        try:
            vector = self.vector_list[int(hit_idx)]
        except IndexError:
            if hit_spot >= self.rect.height:
                vector = self.vector_list[-1]
            else:
                vector = self.vector_list[0]
        return (vector[0] * self.sauce * self.side_factor, vector[1] * self.sauce)

    def play_hit_sound(self):
        self.hit_sound.play()

    def up_on(self):
        self.up = True

    def up_off(self):
        self.up = False

    def down_on(self):
        self.down = True

    def down_off(self):
        self.down = False

    def update_pos(self):
        if self.up == True:
            self.move_up()
        elif self.down == True:
            self.move_down()

    def move_up(self):
        self.rect.top -= self.MOVEDIST
        if self.rect.bottom < self.topmost:
            self.rect.bottom = self.topmost
        self.dec_sauce()

    def move_down(self):
        self.rect.top += self.MOVEDIST
        if self.rect.top > self.bottommost:
            self.rect.top = self.bottommost
        self.dec_sauce()

    def sauce_left(self):
        if self.last_sauce == self.SAUCERIGHT:
            self.last_sauce = self.SAUCELEFT

    def sauce_right(self):
        if self.last_sauce == self.SAUCELEFT:
            self.last_sauce = self.SAUCERIGHT
            self.inc_sauce()

    def inc_sauce(self):
        if self.sauce < self.MAXSAUCE:
            self.sauce += self.SAUCEINC

    def dec_sauce(self):
        if self.sauce > self.MINSAUCE:
            self.sauce -= self.SAUCEDEC

    def reset_sauce(self):
        self.sauce = self.MINSAUCE

    def collide_ball(self, ball):
        return self.rect.colliderect(ball.rect) == 1

    def draw(self, surface):
        surface.blit(self.image, (self.rect.left, self.rect.top))

class Unicorn(Player):
    image_file = 'unicorn.png'
    hit_sound_file = 'unicorn_hit.wav'
    side_factor = 1
    name = 'unicorn'
    def __init__(self, court):
        Player.__init__(self, court)

    def lost_point(self, ball):
        return self.rect.left > ball.rect.right

    def collide_ball(self, ball):
        return (self.rect.colliderect(ball.rect) == 1) and (self.rect.right <= (ball.rect.left - ball.vector[0]))

class Dolphin(Player):
    image_file = 'dolphin.png'
    hit_sound_file = 'dolphin_hit.wav'
    side_factor = -1
    name = 'dolphin'
    def __init__(self, court):
        Player.__init__(self, court)

    def lost_point(self, ball):
        return self.rect.right < ball.rect.left

    def collide_ball(self, ball):
        return (self.rect.colliderect(ball.rect) == 1) and (self.rect.left >= (ball.rect.right - ball.vector[0]))

class RoboUnicorn(Unicorn):
    def __init__(self, court):
        Unicorn.__init__(self, court)
    def ball_vector(self, ball):
        vec = random.choice(self.vector_list)
        sauce = random.randint(5,20)
        return (vec[0] * sauce * self.side_factor, vec[1] * sauce)
    def collide_ball(self, ball):
        return ball.rect.left < self.rect.right

def start_point(court, ball, dir):
    ball.vector = (5 * dir, 0)
    ball.rect.top = court.get_rect().height / 2 - ball.rect.height / 2
    ball.rect.left = court.get_rect().width / 2 - ball.rect.width / 2

class JoystickButtonTranslator:
    def __init__(self):
        self.button_up_map = {0:{}, 1:{}}
        self.button_down_map = {0:{}, 1:{}}

    def add_button_up(self, joystick_id, button, handler):
        self.button_up_map[joystick_id][button] = handler

    def add_button_down(self, joystick_id, button, handler):
        self.button_down_map[joystick_id][button] = handler

    def process_event(self, event):
        if event.type == pygame.JOYBUTTONUP or event.type == pygame.JOYBUTTONDOWN:
            try:
                {pygame.JOYBUTTONUP:self.button_up_map,
                 pygame.JOYBUTTONDOWN:self.button_down_map}[event.type][event.joy][event.button]()
            except KeyError:
                pass

class Score:
    def __init__(self, players):
        self.scores = {}
        for p in players:
            self.scores[p] = 0
        self.rendered_score = []
        font = pygame.font.Font(None, 20)
        for i in range(0,10):
            self.rendered_score.append(font.render('%d'%i, 1, (0, 0, 0), (255,255,255)))

    def reset(self):
        for p in self.scores.keys():
            self.scores[p] = 0

    def point(self, player):
        self.scores[player] += 1

    def get_score(self, player):
        return self.scores[player]

    def get_rendered_score(self, player):
        return self.rendered_score[self.get_score(player)]

def main_game(court_size, robo_unicorn):
    pygame.init()
    pygame.mixer.init()
    pygame.joystick.init()

    if not pygame.joystick.get_count() == 2:
        print 'Please plug in two joysticks.'
        raise SystemExit

    js = []
    js.append(pygame.joystick.Joystick(0))
    js.append(pygame.joystick.Joystick(1))

    for j in js:
        j.init()

    unicorn_wins_snd = load_snd('unicorn_wins.wav')
    dolphin_wins_snd = load_snd('dolphin_wins.wav')

    screen = pygame.display.set_mode(court_size, HWSURFACE|DOUBLEBUF|FULLSCREEN)

    clock = pygame.time.Clock()

    court = Court((court_size[0], court_size[1] - 20))
    court.fill((255,255,0))


    background = pygame.Surface((screen.get_size()[0], 20))
    background.fill((255,255,255))
    # background.blit(get_score_text((0,0)), (320, 0))

    ball = Ball((0, 0))
    start_point(court, ball, random.choice([-1,1]))

    dolphin = Dolphin(court)
    dolphin.rect.top = 0
    dolphin.rect.right = court.get_rect().width

    unicorn = None
    if robo_unicorn:
        unicorn = RoboUnicorn(court)
    else:
        unicorn = Unicorn(court)
    unicorn.rect.top = 0
    unicorn.rect.left = 0

    screen.blit(background, (0,0))
    
    ball.draw(court)

    unicorn.draw(court)
    dolphin.draw(court)

    screen.blit(court, (0,20))
    
    pygame.display.flip()

    jbt = JoystickButtonTranslator()

    for (i, p) in enumerate([unicorn, dolphin]):
        jbt.add_button_down(i, 0, p.up_on)
        jbt.add_button_down(i, 1, p.down_on)

        jbt.add_button_up(i, 0, p.up_off)
        jbt.add_button_up(i, 1, p.down_off)
        
        jbt.add_button_down(i, 2, p.sauce_left)
        jbt.add_button_down(i, 3, p.sauce_right)

    score = Score((unicorn, dolphin))

    game_on_dolphin = False
    game_on_unicorn = False

    while True:
        clock.tick(100)
        events = pygame.event.get()

        for e in events:
            if hasattr(e, 'key') and e.key == pygame.K_ESCAPE:
                raise SystemExit
            if hasattr(e, 'key') and e.key == pygame.K_SPACE:
                pygame.image.save(screen, "uvd.bmp")

        if game_on_unicorn and game_on_dolphin:
            for e in events:
                jbt.process_event(e)

            for p in (unicorn, dolphin):
                p.update_pos()

            court.update_ball(ball, (unicorn, dolphin))

            if unicorn.lost_point(ball):
                score.point(dolphin)
                start_point(court, ball, 1)
                for p in (dolphin, unicorn):
                    p.reset_sauce()

            if dolphin.lost_point(ball):
                score.point(unicorn)
                start_point(court, ball, -1)
                for p in (dolphin, unicorn):
                    p.reset_sauce()

            if score.get_score(unicorn) >= WINSCORE or score.get_score(dolphin) >= WINSCORE:
                game_on_dolphin = False
                game_on_unicorn = False

                score_file = open('score.txt', 'a')

                if score.get_score(unicorn) >= WINSCORE:
                    unicorn_wins_snd.play()
                    score_file.write('unicorn %d\n'%score.get_score(dolphin))
                if score.get_score(dolphin) >= WINSCORE:
                    dolphin_wins_snd.play()
                    score_file.write('dolphin %d\n'%score.get_score(unicorn))

                score_file.close()

                score.reset()

        else:
            start_point(court, ball, random.choice([-1,1]))
            for p in (dolphin, unicorn):
                p.reset_sauce()
            for e in events:
                if e.type == pygame.JOYBUTTONDOWN:
                    if e.joy == 0:
                        game_on_unicorn = True
                    if e.joy == 1:
                        game_on_dolphin = True

        court.fill((255,255,0))

        ball.draw(court)
        unicorn.draw(court)
        dolphin.draw(court)
        screen.blit(background, (0,0))
        screen.blit(court, (0,20))

        screen.blit(score.get_rendered_score(unicorn), (court_size[0] / 2 - 40,0))
        screen.blit(score.get_rendered_score(dolphin), (court_size[0] / 2 + 40,0))
        pygame.display.flip()

if __name__ == '__main__':
    args = sys.argv[:]
    args.reverse()

    court_size = (800, 600)
    robo_unicorn = False

    while args:
        arg = args.pop()
        if arg == '--court_size':
            court_size = (int(args.pop()), int(args.pop()))
        elif arg == '--robo':
            robo_unicorn = True
    main_game(court_size, robo_unicorn)
