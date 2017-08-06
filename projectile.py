# ---- projectile.py ----
from math import sin, cos, radians

here = 0
ip = 0

class Projectile:
    # 根據給定的發射角度、初始速度和位置創建一個投射體 object 
    def __init__ (self, angle, velocity, height):
        self.xpos = 0.0 
        self.ypos = height 
        theta = radians(angle) 
        self.xvel = velocity * cos(theta) 
        self.yvel = velocity * sin(theta) 
    def update (self, time) : 
        # 更新投射體的狀態
        self.xpos = self.xpos + time * self.xvel 
        yvell = self.yvel - 9.8 * time 
        self.ypos = self.ypos + time * (self.yvel + yvell)/2.0
        self.yvel = yvell
    def getY(self): 
        #返回投射體的角度
        return self.ypos 
    def getX(self):
        #返回投射體的距離
        return self.xpos 
    def getHere(self):
        return here

def test(s):
    print(s, 'is your input and here is now :', here)
    
'''
    c:\ Users\hcche\Documents\GitHub\peforth>python
    Python 3.6.0 (v3.6.0:41df79263a11, Dec 23 2016, 08:06:12) [MSC v.1900 64 bit (AMD64)] on win32
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import projectile
    >>> dir(projectile)
    ['Projectile', '__builtins__', '__cached__', '__doc__', '__file__', '__loader__', '__name__', '__package__', '__spec__', 'cos', 'radians', 'sin', 'test']
    >>> show = projectile.Projectile(1,2,3)
    >>> show.getX()
    0.0
    >>> show.getY()
    3
    >>> projectile.test('hello')
    hello is your input
    >>>
'''