from apps.fap import Fap
from utils.colors import name_to_rgb

class Flags(Fap):
    FRENCH = 'french'
    GERMANY = 'germany'
    SPAIN = 'spain'
    ITALY = 'italy'

    PLAYABLE = False
    ACTIVATED = True

    PARAMS_LIST = {'uapp' : [FRENCH, GERMANY, SPAIN, ITALY ]}

    def french(self):
        bleu = name_to_rgb('navy')
        blanc = name_to_rgb('white')
        rouge = name_to_rgb('red')
        for i in range(0, 5):
            self.model.set_column(i, bleu)
        for i in range(5, 12):
            self.model.set_column(i, blanc)
        for i in range(12, 19):
            self.model.set_column(i, rouge)
        self.send_model()

    def italy(self):
        g = name_to_rgb('green')
        w = name_to_rgb('white')
        r = name_to_rgb('firebrick')
        for i in range(0, 5):
            self.model.set_column(i, g)
        for i in range(5, 12):
            self.model.set_column(i, w)
        for i in range(12, 19):
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

    def run(self, params):
        self.params = params
        if params and params.get('uapp', False) in self.PARAMS_LIST['uapp']:
            getattr(self, params.get('uapp'))()