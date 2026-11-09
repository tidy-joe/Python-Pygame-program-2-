import sys # 退出游戏时使用

import pygame #开发游戏

from time import sleep

from game_states import GameStats
from settings import Settings
from ship import Ship
from bullet import Bullet
from alien import Alien
from button import Button
from scoreboard import Scoredboard

class AlienInvasion:
    """管理游戏资源和行为的类"""
    def __init__(self):
        """初始化游戏并创建游戏资源"""
        pygame.init()  # 初始化背景
        self.clock = pygame.time.Clock() #时钟用来控制帧率,为了保证实现画面的循环进度相似,这里调用pygame中的time中的Clock类,创建了一个实例
        self.settings = Settings()

        # self.screen = pygame.display.set_mode((0,0),pygame.FULLSCREEN)
        # self.settings.screen_width = self.screen.get_rect().width
        # self.settings.screen_height = self.screen.get_rect().height
        self.screen = pygame.display.set_mode((self.settings.screen_width,self.settings.screen_height))  # 创建显示窗口,规定大小,同时赋值给srlf.screen.  there the type is surface, wwhich will be realize on the screen.通过不断打印来作为游戏窗口,这里改成设置中的变量,通过改变设置中的变量可以改变
        pygame.display.set_caption("被前凸后翘的妖精包围了")#框图标题
        self.stats = GameStats(self) #创建一个用于存储游戏统计信息的实例
        self.sb = Scoredboard(self)
        self.ship = Ship(self) #这句1话很关键,让我理解了为什么ship不用import settings却加了这个属性.  ai = AlienInvasion时self(括号中)顶成了ai,再在ship中传递给ai_game,这时实参ai包括了__init__中生成的settings属性,可以赋给里面的self.settings..所以这里self.ship中的ship有一个包含多属性的ai实例,就是与AlienInvasion互指了,代表一条路可以前进也可以后退,所以不用再额外索引settings
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()

        self._create_fleet()

        # 设置背景色
        self.bg_color = (230,230,230) # 通过0~255的红绿蓝三色来调制,这里是灰色  这一段后面可以删除,因为用Setting中的变量替代了

        # 游戏启动后处于非活动状态
        self.game_active = False

        # 创建play按钮
        self.play_button = Button(self,"Play")

    def run_game(self):  # 控制方法
        """开始游戏的主循环"""
        while True:
            self._check_events() # 侦听键盘和鼠标事件
            if self.game_active:
                self.ship.update() #移动标志
                self._update_bullets() #移动子弹
                self._update_aliens() #更新外星人
            # 每次循环时都重绘屏幕
            self._update_screen()

            # 让最近绘制的屏幕可见
            pygame.display.flip()  #  这个函数负责不断更新屏幕,里面肯定有一个while循环
            self.clock.tick(60)  #调用了Clock类中的tick()函数(计时函数,循环超过帧率时会计算误差并停留)
    
    #通过辅助方法来分割run_game方法中的不同方法,辅助方法一般用_打头
    def _check_events(self):
        """响应按键和鼠标事件"""
        # 侦听键盘和鼠标事件
        for event in pygame.event.get():   #一个事件循环,侦听事件并作出反应  这里有get的函数会return一个列表,包括鼠标和键盘行为,然后通过if语句一一作出响应
            if event.type == pygame.QUIT:  #这个.type类似于字典里的Key  QUIT指窗口的X关闭窗口作为事件来提示终止while循环
                sys.exit()
            elif event.type == pygame.KEYDOWN:       # 通过KEYDOWN和KEYUP将事件编码分类,再聚焦具体按键
                self._check_keydown_events(event)
            elif event.type ==  pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)

    def _check_play_button(self, mouse_pos):
        """在玩家单击Play按钮时开始新游戏"""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.game_active:
            # 还原游戏设置
            self.settings.initialize_dynamic_settings() # 单独把变化的速度拿出来,方便这里重置
            # 重置游戏的统计信息
            self.stats.reset_stats()
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()
            self.game_active = True

            #清空外星人列表和子弹列表
            self.bullets.empty()
            self.aliens.empty()

            #创建一个外星舰队,并将飞船放在屏幕底部的中央
            self._create_fleet()
            self.ship.center_ship()

            #隐藏光标
            pygame.mouse.set_visible(False)

    def _check_keydown_events(self,event):
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()


    def _check_keyup_events(self,event):
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False
        
    def _fire_bullet(self):
            """创建一颗子弹,并将其加入编组bullets"""
            if len(self.bullets) < self.settings.bullets_allowed:
                new_bullet = Bullet(self)
                self.bullets.add(new_bullet)

    def _update_bullets(self):
        """更新子弹的位置并删除已消失的子弹"""
        # 更新子弹的位置
        self.bullets.update()

        # 删除已消失的子弹
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)

        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        """响应子弹和外星人的碰撞"""
        #检查是否有子弹击中了外星人
        #如果是就删除相应的子弹和外星人
        collisions = pygame.sprite.groupcollide(self.bullets,self.aliens,True,True)

        if collisions:
            for aliens_hit in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens_hit) # 通过这个操作使外星人正确计分
            self.sb.prep_score()
            self.sb.check_high_score()

        
        
        if not self.aliens:
            #删除现有的子弹并创建一个新的外星人舰队
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()

            # 升级
            self.stats.level += 1
            self.sb.prep_level()

    def _update_aliens(self):
        """更新外星舰队中所有外星人的位置"""
        self._check_fleet_edges()
        self.aliens.update()

        #检测飞船和外星人之间的碰撞
        if pygame.sprite.spritecollideany(self.ship,self.aliens):
            self._ship_hit()

        #检查外星人是否触底
        self._check_aliens_bottom()



    def _check_fleet_edges(self):
        """在有外星人到达边缘时采取相应的措施"""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_driction()
                break

    def _change_fleet_driction(self):
        """将整个外星人舰队向下移动,并改变它们的方向"""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1


    def _update_screen(self):
        """更新屏幕上的图像,并更新到新图像"""
        # 每次循环时都重绘屏幕
        self.screen.fill(self.settings.bg_color)  # fill方法把screen填满
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()  # 放在绘制飞船之前,防止出现在飞船里
        self.ship.blitme()
        self.aliens.draw(self.screen)

        #显示得分
        self.sb.show_score()

        # 如果游戏处于非活动状态,就绘制Play按钮
        if not self.game_active:
            self.play_button.draw_button()  #绘制的前后关系会影响上下覆盖.

    def _create_fleet(self):
        """创建一个外星舰队"""
        #创建一个外星人,再不断添加,直到没有空间添加外星人为止
        #外星人的间距为外星恶人的宽度
        alien = Alien(self)
        alien_width,alien_height = alien.rect.size# .size是一个元组,包含宽和高

        current_x, current_y = alien_width, alien_height
        while current_y < (self.settings.screen_height - 3 * alien_height):
            while current_x < (self.settings.screen_width - 2 * alien_width):
                self._create_alien(current_x,current_y)
                current_x += 2 * alien_width
            current_x = alien_width
            current_y += 3 * alien_height# xy的迭代增加在不同循环中

    def _create_alien(self,x_position,y_position):
        new_alien = Alien(self)
        new_alien.x = x_position
        new_alien.rect.x = x_position
        new_alien.rect.y = y_position
        self.aliens.add(new_alien)

    def _ship_hit(self):
        """响应飞船和外星人的碰撞"""
        if self.stats.ships_left > 0:

        #将ship_left减一
            self.stats.ships_left -= 1
            self.sb.prep_ships()

        #清空外星人列表和子弹列表
            self.bullets.empty()
            self.aliens.empty()

        # 创建一个新的外星人列表和子弹列表,并将飞船放在屏幕底部的中央
            self._create_fleet()
            self.ship.center_ship()

        # 暂停
            sleep(0.5)
        else:
            self.game_active = False
            pygame.mouse.set_visible(True)

    def _check_aliens_bottom(self):
        """检查是否有外星人到达了屏幕的下边缘"""
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= self.settings.screen_height:
                #像撞到飞船一样处理
                self._ship_hit()
                break # 防止多个外星人同时触发这个循环

    
if __name__ == '__main__':  #类只是一个打包,要用实例来调用它.  这里__name__ is what python give to the file  就是说本地运行时__name__自动dengyu__main__,导入时叫文件名本身,防止调用时自动出现黑框创建实例 
    # 创建游戏实例并运行游戏
    ai = AlienInvasion()  #创建实例的瞬间__init__被python瞬间调用
    ai.run_game()

































































































































































































































































































































































