# Quick PyGame Example...
# Initialise SDL, display an image...

import sys

# For handling filenames...
import os

# The pygame module itself...
import pygame

# The image handling...
import pygame.image

# Important constant definitions for Pygame,
# in this example: used to setup the "Double
# Buffered" Display...
from pygame.locals import *

# Get the image from: ./images/sprite1.gif
sprite_file = os.path.join('images', 'uvd.png')
dolphin_sound_file = os.path.join('sound', 'dolphin.wav')

# Open up a display, draw our loaded image onto it
# -- check for ESC; if pressed, exit...
#
def main():
  # Initialise SDL environment
  pygame.init()  
  pygame.mixer.init()

  dolphin_sound = pygame.mixer.Sound(dolphin_sound_file)

  j = None

  if not pygame.joystick.get_count() == 1:
      print "please connect a joystick"
      sys.exit()

  j = pygame.joystick.Joystick(0)

  j.init()

  # Setup a 640x480 screen...
  screen = pygame.display.set_mode((640,480), HWSURFACE|DOUBLEBUF)
  
  # Make a "surface" which is the same size as our screen...
  background = pygame.Surface(screen.get_size())

  # Make this background surface a white colour
  # (note: R,G,B tuple):
  background.fill((255,255,255))

  # Load our sprite:
  sprite = pygame.image.load(sprite_file)
    
  # Get the initial position of the sprite,
  sprite_position = sprite.get_rect()

  # Set it's position to the middle of our display...
  sprite_position.bottom = (480 / 2)
  sprite_position.left = (640 / 2) - 100

  # Now "blit" the background and our sprite
  # onto the screen...
  screen.blit(background, (0,0))
  screen.blit(sprite, sprite_position)

  # Now display the screen buffer we've been
  # blitting things to...
  pygame.display.flip()
  

  # Infinite loop to keep the window open until
  # ESC or "Close Window" widget
  # is pressed...
  while 1:
      event = pygame.event.poll()

      if event.type == pygame.NOEVENT:
          # print "no event"
          pass
      elif event.type == pygame.QUIT:
          print "quit"
      elif event.type == pygame.JOYBUTTONDOWN:
          print "DOWN", event.button
      elif event.type == pygame.JOYBUTTONUP:
          print "UP", event.button
          axis = event.button
          if axis < 0 or axis > 3: continue
          botoff = [-10, 10, 0, 0][axis]
          leftoff = [0, 0, -10, 10][axis]
          sprite_position.bottom += botoff
          sprite_position.left += leftoff

          print 'sprite_position = [', sprite_position.bottom, sprite_position.left, ']'
          
          # Now "blit" the background and our sprite
          # onto the screen...
          screen.blit(background, (0,0))
          screen.blit(sprite, sprite_position)

          # Now display the screen buffer we've been
          # blitting things to...
          pygame.display.flip()
          dolphin_sound.play()
          print "flip!!!"

      elif event.type == pygame.JOYAXISMOTION:
          print "AXIS", event.joy, ",", event.axis, ",", event.value
          
# So we can run straight from the CLI...
if __name__ == '__main__':
    main()
