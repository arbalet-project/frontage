import time

from apps.fap import Fap
from utils.colors import name_to_rgb
from json import loads
from scheduler_state import SchedulerState
from server.flaskutils import print_flush

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
                            'netherlands',
                            'pakistan',
                            'paraguay',
                            'peru',
                            'poland',
                            'portugal',
                            'qatar',
                            'romania',
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

    def french(self): # scalable
        cols = SchedulerState.get_cols()
        b1 = cols // 3
        b2 = cols - b1
        for i in range(0, b1):
            self.model.set_column(i, name_to_rgb('navy'))
        for i in range(b1, b2):
            self.model.set_column(i, name_to_rgb('white'))
        for i in range(b2, cols):
            self.model.set_column(i, name_to_rgb('red'))

    def italy(self): # scalable
        cols = SchedulerState.get_cols()
        b1 = cols // 3
        b2 = cols - b1
        for i in range(0, b1):
            self.model.set_column(i, name_to_rgb('green'))
        for i in range(b1, b2):
            self.model.set_column(i, name_to_rgb('white'))
        for i in range(b2, cols):
            self.model.set_column(i, name_to_rgb('firebrick'))

    def spain(self): # scalable
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

    def germany(self): # scalable
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

    def algeria(self): # scalable
        cols = SchedulerState.get_cols()
        rows = SchedulerState.get_rows()
        midc = cols // 2
        midr = rows // 2
        croissant = [(-1,0), (0,-1), (1,0)]
        for i in range(0, midc):
            self.model.set_column(i, name_to_rgb('darkgreen'))
        for i in range(midc, cols):
            self.model.set_column(i, name_to_rgb('white'))
        if (rows > 2 and cols > 2):
            for pix in croissant:
                self.model.set_pixel(midr + pix[0], midc + pix[1], name_to_rgb('red'))

    def saudi(self): # scalable
        cols = SchedulerState.get_cols()
        rows = SchedulerState.get_rows()
        quarc = cols / 4
        midr = rows // 2
        self.model.set_all('darkgreen')
        for i in range(int(quarc), int(quarc*3)+1):
            self.model.set_pixel(midr-1, i, name_to_rgb('white'))
        if (int(quarc) + 2 >= int(quarc -1)*2):
            self.model.set_pixel(midr+1, int(quarc*2), name_to_rgb('white'))
        else:
            for i in range(int(quarc) + 2, int(quarc*2)-2):
                self.model.set_pixel(midr+1, i, name_to_rgb('white'))

    def argentina(self): # scalable
        cols = SchedulerState.get_cols()
        rows = SchedulerState.get_rows()
        midc = cols // 2
        midr = rows // 2
        tierr = rows / 3
        if (cols < 3 or rows < 3):
            self.model.set_all((0,0,0))
        else :
            self.model.set_all('skyblue')
            for i in range(max(int(tierr), 1), max(int(tierr*2), 2)):
                self.model.set_line(i, name_to_rgb('white'))
            for c in range(max(midc -1, 1), max(midc+2, 2)):
                self.model.set_pixel(midr, c, name_to_rgb('yellow'))

    def armenia(self): # scalable
        rows = SchedulerState.get_rows()
        tierr = rows / 3
        if (rows < 3):
            self.model.set_all('darked')
        else :
            for i in range(0, max(int(tierr), 1)):
                self.model.set_line(i, name_to_rgb('red'))
            for i in range(int(tierr), max(int(tierr*2), 2)):
                self.model.set_line(i, name_to_rgb('navy'))
            for i in range(max(int(tierr*2), 2), rows):
                self.model.set_line(i, name_to_rgb('yellow'))

    def austria(self): # scalable
        rows = SchedulerState.get_rows()
        tierr = rows / 3
        if (rows < 3):
            self.model.set_all('darked')
        else:
            print_flush("a row tier is {}, 2 tier are {}".format(int(tierr), int(tierr*2)))
            for i in range(0, int(tierr )):
                self.model.set_line(i, (0.75, 0.25, 0.25))
            for i in range(int(tierr ), int(2*tierr)):
                self.model.set_line(i, name_to_rgb('white'))
            for i in range(int(2*tierr), rows):
                self.model.set_line(i, (0.75, 0.25, 0.25))


    def belgium(self): # scalable
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

    def brazil(self): # scalable
        cols = SchedulerState.get_cols()
        rows = SchedulerState.get_rows()
        midr = rows / 2
        midc = cols /2
        y = name_to_rgb('yellow')
        self.model.set_all(name_to_rgb('green'))
        if (rows %2 == 0):
            cinf = int(midc)-1
            csup = int(midc)+1
        else :
            cinf = int(midc)
            csup = int(midc)+1
        for r in range(1, int(midr)):
            for c in range(cinf, csup):
                self.model.set_pixel(r,c, y)
            if (midc > midr):
                cinf = max(cinf -2,1)
                csup = min(csup +2, cols-1)
            else :
                cinf = max(cinf -1,1)
                csup = min(csup +1, cols-1)
        if (rows %2 == 0):
            cinf = int(midc)-1
            csup = int(midc)+1
        else :
            cinf = int(midc)
            csup = int(midc)+1
        for r in range(rows-2, int(midr)-1, -1):
            for c in range(cinf, csup):
                self.model.set_pixel(r,c, y)
            if (midc > midr):
                cinf = max(cinf -2,1)
                csup = min(csup +2, cols-1)
            else :
                cinf = max(cinf -1,1)
                csup = min(csup +1, cols-1)
        quarr = rows / 4
        quarc = cols / 4
        rank = min(quarc, quarr)
        for i in range(int(midr-rank), int(midr+rank)):
            for j in range(int(midc-rank), int(midc+rank)):
                self.model.set_pixel(i,j, name_to_rgb('navy'))

    def burkina(self): # scalable
        rows = SchedulerState.get_rows()
        cols = SchedulerState.get_cols()
        if (rows < 2 or cols < 2):
            self.model.set_all((0,0,0))
            return
        midc = cols // 2
        midr = rows // 2
        if (midr * 2 != rows):
            rows = rows -1
        self.model.set_all((0,0,0))
        for i in range(0, midr):
            self.model.set_line(i, (0.75, 0.25, 0.25))
        for i in range(midr, rows):
            self.model.set_line(i, (0, 0.62, 0.27))
        for r in range(max(0,midr-1), max(midr+1,2)):
            for c in range(max(0,midc-1), max(2,midc+1)):
                self.model.set_pixel(r, c, name_to_rgb('yellow'))

    def cameroon(self): # scalable
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

    def canada(self): # scalable
        cols = SchedulerState.get_cols()
        rows = SchedulerState.get_rows()
        quarc = cols / 4
        tierr = rows / 3
        a = (0.83, 0.17, 0.12)
        b = (1, 1, 1)
        self.model.set_all(b)
        for i in range(0, int(quarc)):
            self.model.set_column(i, a)
        for i in range(int(cols-quarc), cols):
            self.model.set_column(i, a)
        for c in range(1, rows-1):
            self.model.set_pixel(c, cols//2, a)
        for c in range(2, rows-2):
            self.model.set_pixel(c, cols//2-1, a)
        for c in range(2, rows-2):
            self.model.set_pixel(c, cols//2+1, a)

    def chile(self): # scalable
        rows = SchedulerState.get_rows()
        cols = SchedulerState.get_cols()
        midr = rows // 2
        tierc = cols // 3
        for i in range(0, midr):
            self.model.set_line(i, name_to_rgb('white'))
        for i in range(0, tierc):
            self.model.set_column(i, name_to_rgb('navy'))
        for i in range(midr, rows):
            self.model.set_line(i, (0.75, 0.25, 0.25))
        self.model.set_pixel((rows // 4), 1, name_to_rgb('white'))

    def china(self): # scalable
        self.model.set_all('red')
        for r in range(0, 2):
            for c in [1, 2, 4]:
                self.model.set_pixel(r, c, name_to_rgb('yellow'))

    def colombia(self): # scalable
        rows = SchedulerState.get_rows()
        quarr = rows // 4
        for i in range(0, rows // 2):
            self.model.set_line(i, name_to_rgb('yellow'))
        for i in range(rows //2, 3*quarr):
            self.model.set_line(i, name_to_rgb('navy'))
        for i in range(3* quarr, rows):
            self.model.set_line(i, name_to_rgb('red'))

    def ivory(self): # scalable
        cols = SchedulerState.get_cols()
        b1 = cols // 3
        b2 = cols - b1
        for i in range(0, b1):
            self.model.set_column(i, (0.96, 0.5, 0))
        for i in range(b1, b2):
            self.model.set_column(i, (1, 1, 1))
        for i in range(b2, cols):
            self.model.set_column(i, (0, 0.62, 0.38))

    def denmark(self): # scalable
        rows = SchedulerState.get_rows()
        cols = SchedulerState.get_cols()
        self.model.set_all((0.78, 0, 0.17))
        self.model.set_line(rows//2, (1, 1, 1))
        self.model.set_column(cols//3, (1, 1, 1))

    def emirates(self): # scalable
        cols = SchedulerState.get_cols()
        rows = SchedulerState.get_rows()
        tierr = rows / 3
        self.model.set_all((0,0,0))
        for i in range(0, int(tierr)):
            self.model.set_line(i, (0, 0.45, 0.18))
        for i in range(int(tierr), int(2*tierr)):
            self.model.set_line(i, (1, 1, 1))
        for i in range(max(1,cols//3)):
            self.model.set_column(i, (1, 0, 0))

    def usa(self): # scalable
        rows = SchedulerState.get_rows()
        cols = SchedulerState.get_cols()
        for i in range(0, rows, 2):
            self.model.set_line(i, (0.73, 0.04, 0.23))
        for i in range(1, rows, 2):
            self.model.set_line(i, (1, 1, 1))
        for r in range(rows //2 +1):
            for c in range(cols //3 + 1):
                self.model.set_pixel(r, c, (0, 0.13, 0.4) if r % 2 == c % 2 else (1, 1, 1))

    def finland(self): # scalable
        rows = SchedulerState.get_rows()
        cols = SchedulerState.get_cols()
        midr = rows //2
        tierc = cols /3
        self.model.set_all((1, 1, 1))
        for i in range(min(1,midr-1), midr+1):
            self.model.set_line(i, (0, 0.2, 0.5))
        for i in range(min(int(tierc-1), 1), int(tierc+1)):
            self.model.set_column(i, (0, 0.2, 0.5))

    def greece(self): # scalable
        rows = SchedulerState.get_rows()
        cols = SchedulerState.get_cols()
        for i in range(0, rows, 2):
            self.model.set_line(i, (0, 0.4, 0.7))
        for i in range(1, rows, 2):
            self.model.set_line(i, (1, 1, 1))
        for j in range(cols//3):
            for i in range(rows // 2):
                if ( i != 2 and j != 2):
                    self.model.set_pixel(i,j, (1, 1, 1))
                else:
                    self.model.set_pixel(i,j, (0, 0.4, 0.7))

    def india(self): # scalable
        rows = SchedulerState.get_rows()
        for i in range(0, rows // 3):
            self.model.set_line(i, (1, 0.6, 0.18))
        for i in range(rows//3, int(rows/ 3 *2)):
            self.model.set_line(i, (1, 1, 1))
        for i in range(int(rows/ 3 *2), rows):
            self.model.set_line(i, (0, 0.6, 0))

    def indonesia(self): # scalable
        rows = SchedulerState.get_rows()
        for i in range(rows//2):
            self.model.set_line(i, name_to_rgb('red'))
        for i in range(rows//2, rows):
            self.model.set_line(i, name_to_rgb('white'))

    def ireland(self): # scalable
        cols = SchedulerState.get_cols()
        b1 = cols // 3
        b2 = cols - b1
        for i in range(0, b1):
            self.model.set_column(i, (0, 0.62, 0.38))
        for i in range(b1, b2):
            self.model.set_column(i, (1, 1, 1))
        for i in range(b2, cols):
            self.model.set_column(i, (0.96, 0.5, 0))

    def iceland(self): # scalable
        rows = SchedulerState.get_rows()
        cols = SchedulerState.get_cols()
        self.model.set_all((0, 0.31, 0.63))
        self.model.set_line(rows // 2, (0.86, 0.1, 0.2))
        self.model.set_column(cols//3, (0.86, 0.1, 0.2))

    def japan(self): # scalable
        rows = SchedulerState.get_rows()
        cols = SchedulerState.get_cols()
        self.model.set_all((1, 1, 1))
        for r in range(max(1, rows//4), max(3,int(rows/4*3))):
            for c in range(max(1,cols//3), max(3, int(cols/3 *2))):
                self.model.set_pixel(r, c, name_to_rgb('red'))

    def latvia(self): # scalable
        rows = SchedulerState.get_rows()
        self.model.set_all((0.62, 0.18, 0.21))
        self.model.set_line(rows //2, (1, 1, 1))

    def lebanon(self): # scalable
        rows = SchedulerState.get_rows()
        cols = SchedulerState.get_cols()
        self.model.set_all((1, 1, 1))
        for i in range(rows//3):
            self.model.set_line(i, (1, 0, 0))
        for i in range(int(rows/3*2), rows):
            self.model.set_line(i, (1, 0, 0))
        for c in range(cols//3, int(cols/3*2)):
            for r in range(rows //3 , int(rows/3*2)):
                self.model.set_pixel(r, c, name_to_rgb('darkgreen'))

    def lgbtq(self): # scalable above 6
        cols = SchedulerState.get_cols()
        widness = cols // 6
        colors = [(0.46, 0., 0.52),(0., 0.3, 1.),(0., 0.5, 0.16),(1, 1, 0),(1, 0.54, 0),(1, 0, 0)]
        self.model.set_all((0,0,0))
        if (cols >= 6):
            k = 0
            for i in range(0, cols-1, widness):
                for j in range(widness):
                    self.model.set_column(i+j, colors[k])
                k += 1


    def libya(self): # scalable
        rows = SchedulerState.get_rows()
        cols = SchedulerState.get_cols()
        self.model.set_all((0,0,0))
        for i in range(rows//3):
            self.model.set_line(i, (1, 0, 0))
        for i in range(int(rows/3*2), rows):
            self.model.set_line(i, name_to_rgb('darkgreen'))

    def liechtenstein(self): # scalable
        rows = SchedulerState.get_rows()
        cols = SchedulerState.get_cols()
        for i in range(0, rows//2):
            self.model.set_line(i, (0, 0.16, 0.5))
        for i in range(rows//2, rows):
            self.model.set_line(i, (0.8, 0.05, 0.13))

    def lituania(self): # scalable
        rows = SchedulerState.get_rows()
        cols = SchedulerState.get_cols()
        for i in range(rows//3):
            self.model.set_line(i, name_to_rgb('yellow'))
        for i in range(rows//3, int(rows/3*2)):
            self.model.set_line(i, name_to_rgb('darkgreen'))
        for i in range(int(rows/3*2), rows):
            self.model.set_line(i, name_to_rgb('red'))

    def luxembourg(self): # scalable
        rows = SchedulerState.get_rows()
        cols = SchedulerState.get_cols()
        for i in range(rows//3):
            self.model.set_line(i, name_to_rgb('red'))
        for i in range(rows//3, int(rows/3*2)):
            self.model.set_line(i, name_to_rgb('white'))
        for i in range(int(rows/3*2), rows):
            self.model.set_line(i, name_to_rgb('skyblue'))

    def mali(self): # scalable
        cols = SchedulerState.get_cols()
        b1 = cols // 3
        b2 = cols - b1
        for i in range(0, b1):
            self.model.set_column(i, name_to_rgb('green'))
        for i in range(b1, b2):
            self.model.set_column(i, name_to_rgb('yellow'))
        for i in range(b2, cols):
            self.model.set_column(i, name_to_rgb('red'))

    def malta(self): # scalable
        cols = SchedulerState.get_cols()
        b1 = cols // 2
        for i in range(0, b1):
            self.model.set_column(i, name_to_rgb('white'))
        for i in range(b1, cols):
            self.model.set_column(i, name_to_rgb('red'))

    def morocco(self): # scalable
        cols = SchedulerState.get_cols()
        rows = SchedulerState.get_rows()
        self.model.set_all((0.73, 0.13, 0.16))
        for c in range(int(cols/10*5),int(cols/10*6)):
            for r in range(int(rows/6*3),int(rows/6*4)):
                self.model.set_pixel(r, c, (0, 0.4, 0.2))

    def mexico(self): # scalable (bizzar)
        return self.italy()

    def monaco(self): # scalable (bizzar)
        return self.indonesia()

    def nigeria(self): # scalable
        cols = SchedulerState.get_cols()
        b1 = cols // 3
        b2 = cols - b1
        for i in range(0, b1):
            self.model.set_column(i, (0, 0.53, 0.31))
        for i in range(b1, b2):
            self.model.set_column(i, name_to_rgb('white'))
        for i in range(b2, cols):
            self.model.set_column(i, (0, 0.53, 0.31))

    def norway(self): # scalable
        cols = SchedulerState.get_cols()
        rows = SchedulerState.get_rows()
        self.model.set_all((0.86, 0.1, 0.2))
        self.model.set_line(int(rows/2), (0, 0.31, 0.63))
        self.model.set_column(int(cols/10*4) , (0, 0.31, 0.63))

    def netherlands(self): # scalable
        cols = SchedulerState.get_cols()
        rows = SchedulerState.get_rows()
        for i in range(0, rows//3):
            self.model.set_line(i, name_to_rgb('firebrick'))
        for i in range(rows//3, int(rows/3*2)):
            self.model.set_line(i, name_to_rgb('white'))
        for i in range(int(rows/3*2), rows):
            self.model.set_line(i, name_to_rgb('navy'))

    def pakistan(self): # scalable
        cols = SchedulerState.get_cols()
        rows = SchedulerState.get_rows()
        self.model.set_all((0, 0.25, 0.1))
        for c in range(cols//3):
            self.model.set_column(c, (1, 1, 1))

    def paraguay(self): # scalable (bizzar)
        return self.netherlands()

    def peru(self): # scalable
        cols = SchedulerState.get_cols()
        b1 = cols // 3
        b2 = cols - b1
        for i in range(0, b1):
            self.model.set_column(i, name_to_rgb('red'))
        for i in range(b1, b2):
            self.model.set_column(i, name_to_rgb('white'))
        for i in range(b2, cols):
            self.model.set_column(i, name_to_rgb('red'))

    def poland(self): # scalable
        cols = SchedulerState.get_cols()
        rows = SchedulerState.get_rows()
        for i in range(0, rows//2):
            self.model.set_line(0, name_to_rgb('white'))
        for i in range(rows//2, rows):
            self.model.set_line(i, name_to_rgb('red'))


    def portugal(self): # scalable
        cols = SchedulerState.get_cols()
        rows = SchedulerState.get_rows()
        self.model.set_all((1, 0, 0))
        for i in range(0, cols//3):
            self.model.set_column(i, (0, 1, 0))

    def qatar(self): # scalable
        cols = SchedulerState.get_cols()
        rows = SchedulerState.get_rows()
        self.model.set_all((0.57, 0.08, 0.23))
        for i in range(0, cols//3):
            self.model.set_column(i, (1, 1, 1))

    def romania(self): # scalable
        cols = SchedulerState.get_cols()
        b1 = cols // 3
        b2 = cols - b1
        for i in range(0, b1):
            self.model.set_column(i, name_to_rgb('navy'))
        for i in range(b1, b2):
            self.model.set_column(i, name_to_rgb('yellow'))
        for i in range(b2, cols):
            self.model.set_column(i, name_to_rgb('firebrick'))

    def russia(self): # scalable
        cols = SchedulerState.get_cols()
        b1 = cols // 3
        b2 = cols - b1
        for i in range(0, b1):
            self.model.set_column(i, name_to_rgb('white'))
        for i in range(b1, b2):
            self.model.set_column(i, name_to_rgb('navy'))
        for i in range(b2, cols):
            self.model.set_column(i, name_to_rgb('firebrick'))

    def sweden(self): # scalable
        cols = SchedulerState.get_cols()
        rows = SchedulerState.get_rows()
        self.model.set_all((0, 0.41, 0.66))
        for i in range(rows//2, rows//2+1):
            self.model.set_line(i, name_to_rgb('yellow'))
        for i in range(cols//3, cols//3 + 2):
            self.model.set_column(i, name_to_rgb('yellow'))

    def swiss(self): # scalable
        rows = SchedulerState.get_rows()
        cols = SchedulerState.get_cols()
        self.model.set_all((1, 0, 0))
        for i in range(int(rows/2 /5 *4), max(int(rows /2 /5 *6),int(rows/2 /5 *4)+2)):
            self.model.set_line(i, name_to_rgb('white'))
        for i in range(int(cols/2 /5 *4), int(cols /2 /5 *6)):
            self.model.set_column(i, name_to_rgb('white'))
        self.model.set_line(0, name_to_rgb('red'))
        self.model.set_line(rows-1, name_to_rgb('red'))
        self.model.set_column(0, name_to_rgb('red'))
        self.model.set_column(cols-1, name_to_rgb('red'))

    def syria(self): # scalable
        cols = SchedulerState.get_cols()
        rows = SchedulerState.get_rows()
        for i in range(0, max(1,rows // 3)):
            self.model.set_line(i, name_to_rgb('red'))
        for i in range(max(1, rows //3), max(2, int(rows/3*2))):
            self.model.set_line(i, (1, 1, 1))
        for i in range(max(2, int(rows/3*2)), rows):
            self.model.set_line(i, (0,0,0))
        for r in [rows //3, rows //3 +1 ]:
            for c in [cols//3, int(cols/3*2)]:
                self.model.set_pixel(r, c, name_to_rgb('darkgreen'))
                self.model.set_pixel(r, c+1, name_to_rgb('darkgreen'))

    def czech(self): # scalable
        cols = SchedulerState.get_cols()
        rows = SchedulerState.get_rows()
        for i in range(rows//2):
            self.model.set_line(i, name_to_rgb('white'))
        for i in range(rows//2, rows):
            self.model.set_line(i, name_to_rgb('red'))
        rinf= 0
        rsup = rows
        for c in range(0, cols //2+1):
            for r in range(rinf, rsup):
                self.model.set_pixel(r,c, name_to_rgb('navy'))
            rinf = min(rinf +1, rows//2)
            rsup = max (rsup -1, rows//2 )

    def tunisia(self): # scalable
        cols = SchedulerState.get_cols()
        rows = SchedulerState.get_rows()
        self.model.set_all('red')
        for c in range(int(cols/8*3), int(cols/8*6) ):
            self.model.set_pixel(rows//2, c, (1, 1, 1))
            self.model.set_pixel(rows//2+1, c, (1, 1, 1))

    def turkey(self): # scalable (bizzar)
        return self.tunisia()

    def ukraine(self): # scalable
        cols = SchedulerState.get_cols()
        rows = SchedulerState.get_rows()
        for i in range(0, rows//2):
            self.model.set_line(i, (1, 0.83, 0))
        for i in range(rows//2, rows):
            self.model.set_line(i, (0, 0.35, 0.74))

    def uruguay(self): # scalable
        rows = SchedulerState.get_rows()
        cols = SchedulerState.get_cols()
        for i in range(0, rows, 2):
            self.model.set_line(i, name_to_rgb('navy'))
        for i in range(1, rows, 2):
            self.model.set_line(i, (1, 1, 1))
        for r in range(0, 2):
            for c in [0, 1]:
                self.model.set_pixel(r, c, name_to_rgb('yellow'))

    def venezuela(self): # scalable
        cols = SchedulerState.get_cols()
        rows = SchedulerState.get_rows()
        for i in range(0, rows//3):
            self.model.set_line(i, name_to_rgb('yellow'))
        for i in range(rows//3, int(rows / 3*2)):
            self.model.set_line(i, name_to_rgb('navy'))
        for i in range(int(rows/3*2), rows):
            self.model.set_line(i, name_to_rgb('firebrick'))

    def vietnam(self): # scalable
        cols = SchedulerState.get_cols()
        rows = SchedulerState.get_rows()
        self.model.set_all('red')
        for c in range(cols//2, cols//2 + 2):
            self.model.set_pixel(rows//2, c, name_to_rgb('yellow'))
            self.model.set_pixel(rows//2 +1, c, name_to_rgb('yellow'))

    def yemen(self): # scalable
        cols = SchedulerState.get_cols()
        rows = SchedulerState.get_rows()
        for i in range(0, rows//3):
            self.model.set_line(i, name_to_rgb('red'))
        for i in range(rows//3, int(rows / 3*2)):
            self.model.set_line(i, name_to_rgb('white'))
        for i in range(int(rows/3*2), rows):
            self.model.set_line(i, (0,0,0))

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
