import pygame


import sys
from alien_invasion import AlienInvasion
AlienInvasion.__init__()
for event in pygame.event.get():
    print(event.type)

for event in pygame.event.get():
    print(event.type)  # 你会看到 256、768 等数字
    if event.type == 256:  # 完全等价于 pygame.QUIT
        sys.exit()





