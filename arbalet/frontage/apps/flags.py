import time

from apps.fap import Fap
from utils.colors import name_to_rgb
from json import loads
from scheduler_state import SchedulerState


class Flags(Fap):
    PLAYABLE = False
    ACTIVATED = True

    PARAMS_LIST = {'uapp': ['french',
                            'italy',
                            'spain',
                            'germany',
                            'algeria',
                            'saudi',
                            'argentina',
                            'armenia',
                            'australia',
                            'austria',
                            'belgium',
                            'brazil',
                            'burkina',
                            'cameroon',
                            'canada',
                            'chile',
                            'china',
                            'colombia',
                            'ivory',
                            'denmark',
                            'emirates',
                            'usa',
                            'finland',
                            'greece',
                            'india',
                            'indonesia',
                            'ireland',
                            'iceland',
                            'japan',
                            'latvia',
                            'lebanon',
                            'lgbtq',
                            'libya',
                            'liechtenstein',
                            'lituania',
                            'luxembourg',
                            'mali',
                            'malta',
                            'morocco',
                            'mexico',
                            'monaco',
                            'nigeria',
                            'norway',
                            'newzealand',
                            'netherlands',
                            'pakistan',
                            'paraguay',
                            'peru',
                            'poland',
                            'portugal',
                            'qatar',
                            'romania',
                            'uk',
                            'russia',
                            'sweden',
                            'swiss',
                            'syria',
                            'czech',
                            'tunisia',
                            'turkey',
                            'ukraine',
                            'uruguay',
                            'venezuela',
                            'vietnam',
                            'yemen']}

    def french(self):
        cols = SchedulerState.get_cols()
        b1 = cols // 3
        b2 = cols - b1
        for i in range(0, b1):
            self.model.set_column(i, name_to_rgb('navy'))
        for i in range(b1, b2):
            self.model.set_column(i, name_to_rgb('white'))
        for i in range(b2, cols):
            self.model.set_column(i, name_to_rgb('red'))

    def italy(self):
        cols = SchedulerState.get_cols()
        b1 = cols // 3
        b2 = cols - b1
        for i in range(0, b1):
            self.model.set_column(i, name_to_rgb('green'))
        for i in range(b1, b2):
            self.model.set_column(i, name_to_rgb('white'))
        for i in range(b3, cols):
            self.model.set_column(i, name_to_rgb('firebrick'))

    def spain(self):
        r = name_to_rgb('red')
        y = name_to_rgb('yellow')
        rows = SchedulerState.get_rows()
        b1 = rows // 4
        b2 = rows - b1
        for i in range(0, b1) :
            self.model.set_line(i, r)
        for i in range(b1, b2) :
            self.model.set_line(i, y)
        for i in range(b2, rows) :
            self.model.set_line(i, r)

    def germany(self):
        d = name_to_rgb('black')
        r = name_to_rgb('red')
        y = name_to_rgb('yellow')
        rows = SchedulerState.get_rows()
        b1 = rows // 3
        b2 = rows - b1
        for i in range(0, b1) :
            self.model.set_line(i, d)
        for i in range(b1, b2) :
            self.model.set_line(i, r)
        for i in range(b2, rows) :
            self.model.set_line(i, y)

    def algeria(self):
        for i in range(0, 9):
            self.model.set_column(i, name_to_rgb('darkgreen'))
        for i in range(9, 18):
            self.model.set_column(i, name_to_rgb('white'))
        self.model.set_pixel(1, 8, name_to_rgb('red'))
        self.model.set_pixel(2, 8, name_to_rgb('red'))
        self.model.set_pixel(2, 9, name_to_rgb('red'))

    def saudi(self):
        self.model.set_all('darkgreen')
        for i in range(5, 14):
            self.model.set_pixel(1, i, name_to_rgb('white'))
        for i in range(7, 12):
            self.model.set_pixel(2, i, name_to_rgb('white'))

    def argentina(self):
        self.model.set_line(0, name_to_rgb('skyblue'))
        self.model.set_line(1, name_to_rgb('white'))
        self.model.set_line(2, name_to_rgb('skyblue'))
        self.model.set_line(3, name_to_rgb('skyblue'))
        for c in range(8, 11):
            self.model.set_pixel(1, c, name_to_rgb('yellow'))

    def armenia(self):
        self.model.set_line(0, name_to_rgb('darkred'))
        self.model.set_line(1, name_to_rgb('navy'))
        self.model.set_line(2, name_to_rgb('yellow'))
        self.model.set_line(3, name_to_rgb('black'))

    def australia(self):
        self.model.set_all('navy')
        self.model.set_pixel(1, i, name_to_rgb('red'))
        self.model.set_pixel(0, 4, name_to_rgb('red'))
        self.model.set_pixel(2, 4, name_to_rgb('red'))
        for r, c in [(0, 14), (1, 11), (1, 16), (2, 13), (3, 12), (0, 3), (2, 3), (0, 5), (2, 5), (3, 4)]:
            self.model.set_pixel(r, c, name_to_rgb('white'))

    def austria(self):
        self.model.set_line(0, (0.75, 0.25, 0.25))
        self.model.set_line(1, name_to_rgb('white'))
        self.model.set_line(2, (0.75, 0.25, 0.25))
        self.model.set_line(3, name_to_rgb('black'))

    def belgium(self):
        a = name_to_rgb('black')
        b = name_to_rgb('yellow')
        c = name_to_rgb('red')
        cols = SchedulerState.get_cols()
        b1 = cols // 3
        b2 = cols - b1
        for i in range(0, b1):
            self.model.set_column(i, a)
        for i in range(b1, b2):
            self.model.set_column(i, b)
        for i in range(b2, cols):
            self.model.set_column(i, c)

    def brazil(self):
        y = name_to_rgb('yellow')
        self.model.set_all('green')
        for i in range(7, 11):
            self.model.set_pixel(0, i, y)
        for i in range(4, 14):
            self.model.set_pixel(1, i, y)
        for i in range(1, 17):
            self.model.set_pixel(2, i, y)
        for i in range(6, 12):
            self.model.set_pixel(3, i, y)
        for r, c in [(2, 8), (2, 9), (1, 8), (1, 9)]:
            self.model.set_pixel(r, c, name_to_rgb('darkblue'))
        self.model.set_column(18, (0, 0, 0))

    def burkina(self):
        self.model.set_line(0, (0.75, 0.25, 0.25))
        self.model.set_line(1, (0.75, 0.25, 0.25))
        self.model.set_line(2, (0, 0.62, 0.27))
        self.model.set_line(3, (0, 0.62, 0.27))
        for r in range(1, 3):
            for c in range(8, 11):
                self.model.set_pixel(r, c, name_to_rgb('yellow'))

    def cameroon(self):
        a = (0, 0.62, 0.27)
        b = (0.75, 0.25, 0.25)
        y = name_to_rgb('yellow')
        cols = SchedulerState.get_cols()
        rows = SchedulerState.get_rows()
        b1 = cols // 3
        b2 = cols - b1
        for i in range(0, b1):
            self.model.set_column(i, a)
        for i in range(b1, b2):
            self.model.set_column(i, b)
        for i in range(b2, cols):
            self.model.set_column(i, y)
        b3 = rows // 3
        b4 = rows - b3
        for r in range(b3, b4):
            for c in range(b1+(b1//3), b2-(b1//3)):
                self.model.set_pixel(r, c, name_to_rgb('yellow'))

    def canada(self):
        a = (0.83, 0.17, 0.12)
        b = (1, 1, 1)
        for i in range(0, 5):
            self.model.set_column(i, a)
        for i in range(5, 14):
            self.model.set_column(i, b)
        for i in range(14, 19):
            self.model.set_column(i, a)
        for c in range(7, 12):
            self.model.set_pixel(1, c, a)
        for c in range(8, 11):
            self.model.set_pixel(2, c, a)
        self.model.set_pixel(0, 9, a)

    def chile(self):
        for i in range(0, 6):
            self.model.set_column(i, name_to_rgb('navy'))
        for i in range(6, 19):
            self.model.set_column(i, name_to_rgb('white'))
        self.model.set_line(2, (0.75, 0.25, 0.25))
        self.model.set_line(3, (0.75, 0.25, 0.25))

    def china(self):
        self.model.set_all('red')
        for r in range(0, 2):
            for c in [1, 2, 4]:
                self.model.set_pixel(r, c, name_to_rgb('yellow'))

    def colombia(self):
        self.model.set_line(0, name_to_rgb('yellow'))
        self.model.set_line(1, name_to_rgb('yellow'))
        self.model.set_line(2, name_to_rgb('navy'))
        self.model.set_line(3, name_to_rgb('red'))

    def ivory(self):
        cols = SchedulerState.get_cols()
        b1 = cols // 3
        b2 = cols - b1
        for i in range(0, b1):
            self.model.set_column(i, (0.96, 0.5, 0))
        for i in range(b1, b2):
            self.model.set_column(i, (1, 1, 1))
        for i in range(b2, cols):
            self.model.set_column(i, (0, 0.62, 0.38))

    def denmark(self):
        rows = SchedulerState.get_rows()
        cols = SchedulerState.get_cols()
        self.model.set_all((0.78, 0, 0.17))
        self.model.set_line(rows//2, (1, 1, 1))
        self.model.set_column(cols//3, (1, 1, 1))

    def emirates(self):
        self.model.set_line(0, (0, 0.45, 0.18))
        self.model.set_line(1, (1, 1, 1))
        for c in range(6):
            self.model.set_column(c, (1, 0, 0))

    def usa(self):
        self.model.set_line(0, (0.73, 0.04, 0.23))
        self.model.set_line(1, (1, 1, 1))
        self.model.set_line(2, (0.73, 0.04, 0.23))
        self.model.set_line(3, (1, 1, 1))
        for r in range(2):
            for c in range(8):
                self.model.set_pixel(r, c, (0, 0.13, 0.4) if r % 2 == c % 2 else (1, 1, 1))

    def finland(self):
        self.model.set_all((1, 1, 1))
        self.model.set_line(1, (0, 0.2, 0.5))
        self.model.set_line(2, (0, 0.2, 0.5))
        self.model.set_column(6, (0, 0.2, 0.5))
        self.model.set_column(7, (0, 0.2, 0.5))

    def greece(self):
        self.model.set_line(0, (0, 0.4, 0.7))
        self.model.set_line(1, (1, 1, 1))
        self.model.set_line(2, (0, 0.4, 0.7))
        self.model.set_line(3, (1, 1, 1))
        for r in (1, 3):
            for c in range(5):
                self.model.set_pixel(r, c, (0, 0.4, 0.7))
        for c in range(5):
            self.model.set_pixel(2, c, (1, 1, 1))
        self.model.set_column(2, (1, 1, 1))

    def india(self):
        self.model.set_line(0, (1, 0.6, 0.18))
        self.model.set_line(1, (1, 1, 1))
        self.model.set_line(2, (1, 1, 1))
        self.model.set_line(3, (0, 0.6, 0))

    def indonesia(self):
        self.model.set_line(0, name_to_rgb('red'))
        self.model.set_line(1, name_to_rgb('red'))
        self.model.set_line(2, name_to_rgb('white'))
        self.model.set_line(3, name_to_rgb('white'))

    def ireland(self):
        cols = SchedulerState.get_cols()
        b1 = cols // 3
        b2 = cols - b1
        for i in range(0, b1):
            self.model.set_column(i, (0, 0.62, 0.38))
        for i in range(b1, b2):
            self.model.set_column(i, (1, 1, 1))
        for i in range(b2, cols):
            self.model.set_column(i, (0.96, 0.5, 0))

    def iceland(self):
        self.model.set_all((0, 0.31, 0.63))
        self.model.set_line(1, (0.86, 0.1, 0.2))
        self.model.set_column(6, (0.86, 0.1, 0.2))

    def japan(self):
        self.model.set_all((1, 1, 1))
        for r in range(1, 3):
            for c in range(8, 11):
                self.model.set_pixel(r, c, name_to_rgb('red'))

    def latvia(self):
        self.model.set_all((0.62, 0.18, 0.21))
        self.model.set_line(2, (1, 1, 1))

    def lebanon(self):
        self.model.set_all((1, 1, 1))
        self.model.set_line(0, (1, 0, 0))
        self.model.set_line(3, (1, 0, 0))
        for c in range(8, 11):
            self.model.set_pixel(1, c, name_to_rgb('darkgreen'))
            self.model.set_pixel(2, c, name_to_rgb('darkgreen'))

    def lgbtq(self):
        self.model.set_column(0, (0.46, 0., 0.52))
        self.model.set_column(1, (0.46, 0., 0.52))
        self.model.set_column(2, (0.46, 0., 0.52))
        self.model.set_column(3, (0., 0.3, 1.))
        self.model.set_column(4, (0., 0.3, 1.))
        self.model.set_column(5, (0., 0.3, 1.))
        self.model.set_column(6, (0., 0.5, 0.16))
        self.model.set_column(7, (0., 0.5, 0.16))
        self.model.set_column(8, (0., 0.5, 0.16))
        self.model.set_column(9, (1, 1, 0))
        self.model.set_column(10, (1, 1, 0))
        self.model.set_column(11, (1, 1, 0))
        self.model.set_column(12, (1, 0.54, 0))
        self.model.set_column(13, (1, 0.54, 0))
        self.model.set_column(14, (1, 0.54, 0))
        self.model.set_column(15, (1, 0, 0))
        self.model.set_column(16, (1, 0, 0))
        self.model.set_column(17, (1, 0, 0))
        self.model.set_column(18, (0, 0, 0))


    def libya(self):
        self.model.set_line(0, (1, 0, 0))
        self.model.set_line(3, name_to_rgb('darkgreen'))

    def liechtenstein(self):
        self.model.set_line(0, (0, 0.16, 0.5))
        self.model.set_line(1, (0, 0.16, 0.5))
        self.model.set_line(2, (0.8, 0.05, 0.13))
        self.model.set_line(3, (0.8, 0.05, 0.13))

    def lituania(self):
        self.model.set_line(0, name_to_rgb('yellow'))
        self.model.set_line(1, name_to_rgb('darkgreen'))
        self.model.set_line(2, name_to_rgb('red'))

    def luxembourg(self):
        self.model.set_line(0, name_to_rgb('red'))
        self.model.set_line(1, name_to_rgb('white'))
        self.model.set_line(2, name_to_rgb('skyblue'))

    def mali(self):
        cols = SchedulerState.get_cols()
        b1 = cols // 3
        b2 = cols - b1
        for i in range(0, b1):
            self.model.set_column(i, name_to_rgb('green'))
        for i in range(b1, b2):
            self.model.set_column(i, name_to_rgb('yellow'))
        for i in range(b2, rows):
            self.model.set_column(i, name_to_rgb('red'))

    def malta(self):
        cols = SchedulerState.get_cols()
        b1 = cols // 2
        for i in range(0, b2):
            self.model.set_column(i, name_to_rgb('white'))
        for i in range(b2, cols):
            self.model.set_column(i, name_to_rgb('red'))

    def morocco(self):
        self.model.set_all((0.73, 0.13, 0.16))
        for c in range(8, 11):
            self.model.set_pixel(1, c, (0, 0.4, 0.2))
            self.model.set_pixel(2, c, (0, 0.4, 0.2))

    def mexico(self):
        return self.italy()

    def monaco(self):
        return self.indonesia()

    def nigeria(self):
        cols = SchedulerState.get_cols()
        b1 = cols // 3
        b2 = cols - b1
        for i in range(0, b1):
            self.model.set_column(i, (0, 0.53, 0.31))
        for i in range(b1, b2):
            self.model.set_column(i, name_to_rgb('white'))
        for i in range(b2, cols):
            self.model.set_column(i, (0, 0.53, 0.31))

    def norway(self):
        self.model.set_all((0.86, 0.1, 0.2))
        self.model.set_line(1, (0, 0.31, 0.63))
        self.model.set_column(6, (0, 0.31, 0.63))

    def newzealand(self):
        self.model.set_all('navy')
        for i in range(0, 9):
            self.model.set_pixel(1, i, name_to_rgb('firebrick'))
        self.model.set_pixel(0, 4, name_to_rgb('firebrick'))
        self.model.set_pixel(2, 4, name_to_rgb('firebrick'))
        for r, c in [(0, 14), (1, 11), (1, 16), (2, 13), (0, 3), (2, 3), (0, 5), (2, 5)]:
            self.model.set_pixel(r, c, name_to_rgb('firebrick'))

    def netherlands(self):
        self.model.set_line(0, name_to_rgb('firebrick'))
        self.model.set_line(1, name_to_rgb('white'))
        self.model.set_line(2, name_to_rgb('navy'))

    def pakistan(self):
        self.model.set_all((0, 0.25, 0.1))
        for c in range(6):
            self.model.set_column(c, (1, 1, 1))

    def paraguay(self):
        return self.netherlands()

    def peru(self):
        cols = SchedulerState.get_cols()
        b1 = cols // 3
        b2 = cols - b1
        for i in range(0, b1):
            self.model.set_column(i, name_to_rgb('red'))
        for i in range(b1, b2):
            self.model.set_column(i, name_to_rgb('white'))
        for i in range(b2, cols):
            self.model.set_column(i, name_to_rgb('red'))

    def poland(self):
        self.model.set_line(3, name_to_rgb('red'))
        self.model.set_line(2, name_to_rgb('red'))
        self.model.set_line(1, name_to_rgb('white'))
        self.model.set_line(0, name_to_rgb('white'))

    def portugal(self):
        self.model.set_all((1, 0, 0))
        for i in range(0, 6):
            self.model.set_column(i, (0, 1, 0))

    def qatar(self):
        self.model.set_all((0.57, 0.08, 0.23))
        for i in range(0, 6):
            self.model.set_column(i, (1, 1, 1))

    def romania(self):
        cols = SchedulerState.get_cols()
        b1 = cols // 3
        b2 = cols - b1
        for i in range(0, b1):
            self.model.set_column(i, name_to_rgb('navy'))
        for i in range(b1, b2):
            self.model.set_column(i, name_to_rgb('yellow'))
        for i in range(b2, cols):
            self.model.set_column(i, name_to_rgb('firebrick'))

    def uk(self):
        self.model.set_all(name_to_rgb('navy'))
        self.model.set_line(1, (0.81, 0.05, 0.16))
        self.model.set_line(2, (0.81, 0.05, 0.16))
        self.model.set_column(9, (0.81, 0.05, 0.16))
        self.model.set_column(10, (0.81, 0.05, 0.16))
        for c in range(0, 5):
            self.model.set_pixel(0, c, (0.81, 0.05, 0.16))
            self.model.set_pixel(1, c, name_to_rgb('navy'))
            self.model.set_pixel(3, c, (0.81, 0.05, 0.16))
            self.model.set_pixel(2, c, name_to_rgb('navy'))
            self.model.set_pixel(0, 18 - c, (0.81, 0.05, 0.16))
            self.model.set_pixel(1, 18 - c, name_to_rgb('navy'))
            self.model.set_pixel(3, 18 - c, (0.81, 0.05, 0.16))
            self.model.set_pixel(2, 18 - c, name_to_rgb('navy'))

    def russia(self):
        cols = SchedulerState.get_cols()
        b1 = cols // 3
        b2 = cols - b1
        for i in range(0, b1):
            self.model.set_column(i, name_to_rgb('white'))
        for i in range(b1, b2):
            self.model.set_column(i, name_to_rgb('navy'))
        for i in range(b2, cols):
            self.model.set_column(i, name_to_rgb('firebrick'))

    def sweden(self):
        self.model.set_all((0, 0.41, 0.66))
        self.model.set_line(1, name_to_rgb('yellow'))
        self.model.set_line(2, name_to_rgb('yellow'))
        self.model.set_column(6, name_to_rgb('yellow'))
        self.model.set_column(7, name_to_rgb('yellow'))

    def swiss(self):
        self.model.set_all((1, 0, 0))
        self.model.set_line(1, name_to_rgb('white'))
        self.model.set_line(2, name_to_rgb('white'))
        self.model.set_column(9, name_to_rgb('white'))
        self.model.set_column(10, name_to_rgb('white'))

    def syria(self):
        self.model.set_all((1, 1, 1))
        self.model.set_line(0, name_to_rgb('red'))
        self.model.set_line(1, name_to_rgb('red'))
        for r in [2, 3]:
            for c in [4, 5, 13, 14]:
                self.model.set_pixel(r, c, name_to_rgb('darkgreen'))

    def czech(self):
        self.model.set_line(0, name_to_rgb('white'))
        self.model.set_line(1, name_to_rgb('white'))
        self.model.set_line(2, name_to_rgb('red'))
        self.model.set_line(3, name_to_rgb('red'))
        self.model.set_column(0, name_to_rgb('navy'))
        self.model.set_column(1, name_to_rgb('navy'))
        self.model.set_column(2, name_to_rgb('navy'))
        for r, c in [(1, 6), (1, 5), (2, 6), (2, 5), (1, 4), (1, 3), (2, 4), (2, 3), (2, 2), (2, 1)]:
            self.model.set_pixel(r, c, name_to_rgb('navy'))

    def tunisia(self):
        self.model.set_all('red')
        for c in range(8, 11):
            self.model.set_pixel(1, c, (1, 1, 1))
            self.model.set_pixel(2, c, (1, 1, 1))

    def turkey(self):
        return self.tunisia()

    def ukraine(self):
        self.model.set_line(3, (1, 0.83, 0))
        self.model.set_line(2, (1, 0.83, 0))
        self.model.set_line(1, (0, 0.35, 0.74))
        self.model.set_line(0, (0, 0.35, 0.74))

    def uruguay(self):
        self.model.set_line(0, name_to_rgb('navy'))
        self.model.set_line(1, (1, 1, 1))
        self.model.set_line(2, name_to_rgb('navy'))
        self.model.set_line(3, (1, 1, 1))
        for r in range(0, 2):
            for c in [0, 1, 2]:
                self.model.set_pixel(r, c, name_to_rgb('yellow'))

    def venezuela(self):
        self.model.set_line(0, name_to_rgb('yellow'))
        self.model.set_line(1, name_to_rgb('navy'))
        self.model.set_line(2, name_to_rgb('firebrick'))
        for c in [8, 9, 10]:
            self.model.set_pixel(1, c, name_to_rgb('white'))

    def vietnam(self):
        self.model.set_all('red')
        for c in range(8, 11):
            self.model.set_pixel(1, c, name_to_rgb('yellow'))
            self.model.set_pixel(2, c, name_to_rgb('yellow'))

    def yemen(self):
        self.model.set_line(0, name_to_rgb('red'))
        self.model.set_line(1, name_to_rgb('white'))

    def handle_message(self, data, path=None):  # noqa
        if data is not None:
            flag = loads(data)['flag']
            if flag in self.PARAMS_LIST['uapp']:
                self.model.set_all('black')
                getattr(self, flag)()
            self.send_model()

    def run(self, params, expires_at=None):
        self.start_socket()
        self.params = params
        if params and params.get('uapp', False) in self.PARAMS_LIST['uapp']:
            getattr(self, params.get('uapp'))()
        else:
            self.french()

        # count = 0
        while True:
            self.send_model()
            time.sleep(1)
