import math
import pgzrun
from pgzero.builtins import *
from random import randint
from enum import Enum

class LaserType(Enum):
  ALIEN = 0
  PLAYER = 1      
class LaserStatus(Enum):
  ACTIVE = 0
  INACTIVE = 1

level = 1

#region *** DRAW ***
def drawAliens():
  for alien in aliens: alien.draw()

def drawBases():
  for base in bases: base.drawClipped()

def drawLasers():
  for laser in lasers: laser.draw()

def drawLives():
  for l in range(player.lives):
    screen.blit('life', (10+(l*32), 10))

def draw():
  screen.blit('background',(0,0))
  player.draw()
  drawAliens()
  drawBases()
  drawLasers()
  drawLives()
  screen.draw.text(str(score), topright=(780,10), owidth=0.5, ocolor=(255,255,255), color=(0,64,255), fontsize=60)
  if player.status >= 30:
    if player.lives > 0: drawCentreText('YOU WERE HIT!\nPress Enter to re-spawnn')
    else: drawCentreText('GAME OVER\nPress Enter to continue')
  if len(aliens) == 0: drawCentreText('LEVEL CLEARED!\nPress Enter to go to the next level')

def drawCentreText(t):
  screen.draw.text(t, center=(400,300), owidth=0.5, ocolor=(255,255,255), color=(255,64,0), fontsize=60)


#endregion

#region *** UPDATE ***
def updateAliens():
  global moveSequence, moveDelay
  movex = movey = 0
  if moveSequence < 10 or moveSequence > 30: movex = -15
  if moveSequence == 10 or moveSequence == 30: movey = 40 + (5*level)
  if moveSequence > 10 and moveSequence < 30: movex = 15
  for alien in aliens:
    animate(alien, pos=(alien.x + movex, alien.y + movey), duration=0.5, tween='linear')
    alien.image = 'alien1' if randint(0, 1) == 0 else 'alien1b'
    if randint(0,math.floor(50/level)) == 0: 
      laser = Actor('laser1', (alien.x, alien.y))
      laser.type = LaserType.ALIEN
      lasers.append(laser)
    if alien.y > 500 and player.status == 0: player.status = 1
  moveSequence = 1 if moveSequence == 40 else moveSequence + 1

def updateLasers():
  global lasers, aliens
  for laser in lasers:
    if laser.type == LaserType.ALIEN:
      laser.y += 2
      hit = checkLaserHit(laser)
      if hit or laser.y > 600: 
        lasers.remove(laser)
    if laser.type == LaserType.PLAYER:
      laser.y -= 5
      hit = checkPlayerLaserHit(laser)
      if hit or laser.y < 10: 
        lasers.remove(laser)
  
def checkLaserHit(laser):
  global player
  if player.collidepoint((laser.x, laser.y)):
    player.status = 1
    return True
  for base in bases:
    if base.collideLaser(laser):
      base.height -= 10
      return True
  return False

def checkPlayerLaserHit(laser):
  global score
  for base in bases:
    if base.collideLaser(laser): return True
  for alien in aliens:
    if alien.collidepoint((laser.x, laser.y)): 
      aliens.remove(alien)
      score += 1000
      return True
  return False

def update():
  global moveCounter, player, lasers, level
  if player.status < 30 and len(aliens) > 0:
    checkKeys()
    updateLasers()
    moveCounter += 1
    if moveCounter == moveDelay:
      moveCounter = 0
      updateAliens()
    player.image = player.images[math.floor(player.status/len(player.images))]
    if player.status > 0: 
      player.status += 1
      if player.status == 30:
        player.lives -= 1
  elif keyboard.RETURN:
    if player.lives > 0:
      player.status = 0
      lasers = []
      if len(aliens) == 0:
        level += 1
        initAliens()
        initBases()
    else:
      init()

def checkKeys():
  global player, lasers
  if keyboard.left:
    player.x = player.x - 5 if player.x > 5 else 790
  if keyboard.right:
    player.x = player.x + 5 if player.x < 795 else 10
  if keyboard.space and player.laserActive:
    player.laserActive = False
    clock.schedule(makeLaserActive, 0.5)
    laser = Actor('laser2', (player.x, player.y-32))
    laser.type = LaserType.PLAYER
    lasers.append(laser)

def makeLaserActive():
  global player
  player.laserActive = True
#endregion

#region *** INIT ***
def initPlayer():
  global player
  player = Actor('player',(400,550))
  player.status = 0
  player.laserActive = True
  player.images = ['player', 'explosion1', 'explosion2', 'explosion3', 'explosion4', 'explosion5']
  player.lives = 3
  player.name = ''

def initAliens():
  global aliens
  aliens = []
  for a in range(18):
    aliens.append(Actor('alien1', (210 + (a % 6) * 80, 100 + (int(a/6) * 64))))

def drawClipped(self):
  screen.surface.blit(self._surf, (self.x-32, self.y-self.height+30), (0,0,64,self.height))

def collideLaser(self, other):
  return (
    self.x-20 < other.x+5 and
    self.y-self.height+30 < other.y and
    self.x+32 > other.x+5 and
    self.y-self.height+30 + self.height > other.y
  )

def initBases():
  global bases
  bases = []
  bc = 0
  for b in range(3):
    for p in range(3):
      bases.append(Actor('base1', midbottom = (150+(b*200)+(p*40),520)))
      bases[bc].drawClipped = drawClipped.__get__(bases[bc])
      bases[bc].collideLaser = collideLaser.__get__(bases[bc])
      bases[bc].height = 60
      bc += 1

def init():
  global moveSequence, moveDelay, moveCounter, lasers, score, level
  moveSequence = moveCounter = score = 0
  moveDelay = 30
  lasers = []
  level = 1
  initPlayer()
  initAliens()
  initBases()
#endregion

init()
pgzrun.go()