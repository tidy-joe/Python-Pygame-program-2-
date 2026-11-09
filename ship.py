import pygame
from pygame.sprite import Sprite

class Ship(Sprite):
    """管理飞船的类"""
    def __init__(self,ai_game):  #这个形参指向主文件中的实例
        """初始化飞船并设置其初始位置"""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings #将self与实例名绑定,这里运用了添加属性的方法
        self.screen_rect = ai_game.screen.get_rect()#访问屏幕的rect attribution

        # 加载飞船图像并获取其外接图形
        self.image = pygame.image.load('images/lulu2.jpg')
        self.rect = self.image.get_rect()

        # 每艘飞船放在底部中央
        self.rect.midbottom = self.screen_rect.midbottom  # zscreen_rect代表整个窗口,这里将图形与窗口对齐

        #将ship的attribution变成一个float
        self.x = float(self.rect.x) #rect属性会要求保留整数,所以转移成新属性

        # 移动标志[飞船一开始不移动]
        self.moving_right = False
        self.moving_left = False
    def update(self):
        """根据移动标志调整飞船的位置"""
        # 设置self.x = float(self.rect.x)后,直接更改属性x而非其外界矩阵x的数据,这时将其转化成了浮点数
        if self.moving_right and self.rect.right < self.screen_rect.right:
            self.x += self.settings.ship_speed
        if self.moving_left and self.rect.left > 0:
            self.x -= self.settings.ship_speed

        #self.x不是一个关键量,要还给self.rect.x
        self.rect.x = self.x
        
    def blitme(self):
        """在指定位置绘制飞船"""
        self.screen.blit(self.image,self.rect) 

    def center_ship(self):
        """将飞船放在屏幕底部中央"""
        self.rect.midbottom = self.screen_rect.midbottom
        self.x = float(self.rect.x)
