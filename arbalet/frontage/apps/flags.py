import time

from apps.fap import Fap
from utils.colors import name_to_rgb
from json import loads


class Flags(Fap):
    FRENCH = 'french'
    GERMANY = 'germany'
    SPAIN = 'spain'
    ITALY = 'italy'

    PLAYABLE = False
    ACTIVATED = True

    PARAMS_LIST = {'uapp': [FRENCH, GERMANY, SPAIN, ITALY]}

    def french(self):
        bleu = name_to_rgb('navy')
        blanc = name_to_rgb('white')
        rouge = name_to_rgb('red')
        for i in range(0, 6):
            self.model.set_column(i, bleu)
        for i in range(6, 13):
            self.model.set_column(i, blanc)
        for i in range(13, 19):
            self.model.set_column(i, rouge)
        self.send_model()

    def italy(self):
        g = name_to_rgb('green')
        w = name_to_rgb('white')
        r = name_to_rgb('firebrick')
        for i in range(0, 6):
            self.model.set_column(i, g)
        for i in range(6, 13):
            self.model.set_column(i, w)
        for i in range(13, 19):
            self.model.set_column(i, r)
        self.send_model()

    def spain(self):
        r = name_to_rgb('red')
        y = name_to_rgb('yellow')
        self.model.set_line(0, r)
        self.model.set_line(1, y)
        self.model.set_line(2, y)
        self.model.set_line(3, r)
        self.send_model()

    def germany(self):
        d = name_to_rgb('black')
        r = name_to_rgb('red')
        y = name_to_rgb('yellow')
        self.model.set_line(0, d)
        self.model.set_line(1, r)
        self.model.set_line(2, y)
        self.model.set_line(3, d)

        self.send_model()

    def handle_message(self, data, path=None): # noqa
        if data is not None:
            flag = loads(data)['flag']
            if flag in self.PARAMS_LIST['uapp']:
                getattr(self, flag)()

    def run(self, params, expires_at=None):
        print("=====> Start FAP")
        self.start_socket()
        self.params = params
        if params and params.get('uapp', False) in self.PARAMS_LIST['uapp']:
            getattr(self, params.get('uapp'))()
        else:
            self.french()

        count = 0
        while True:
            time.sleep(0.1)
            if count % 100 == 0:
                self.italy()
                print(" ========== Inside FAP ==========")
            if count % 100 == 50:
                self.germany()
                print(" ========== Inside FAP ==========")
            count += 1
