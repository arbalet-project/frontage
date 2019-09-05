import time, sys, socket, logging, threading, itertools
logging.basicConfig()

from artnet import STANDARD_PORT, OPCODES, packet, daemon

log = logging.getLogger(__name__)

class Frame(list):
    def __init__(self, channels=None):
        super(Frame, self).__init__((channels[i] if channels else None for i in range(512)))
    
    def __setitem__(self, index, value):
        if not(isinstance(index, int)):
            raise TypeError("Invalid channel index: %r" % index)
        if not(0 <= index < 512):
            raise ValueError("Invalid channel index: %r" % index)
        if not(isinstance(value, int)):
            raise TypeError("Invalid value type: %r" % value)
        if not(0 <= value < 256):
            raise ValueError("Invalid value index: %r" % value)
        super(Frame, self).__setitem__(index, value)
    
    def merge(self, frame):
        result = Frame()
        for i in range(512):
            value = self[i] if frame[i] is None else frame[i]
            if(value is not None):
                result[i] = value
        return result

class AutoCycler(object):
    def __init__(self, controller):
        self.controller = controller
        self.enabled = False
    
    def __enter__(self):
        self.enabled = True
    
    def __exit__(self, etype, e, trace):
        self.enabled = False
        return False

class Universe(object):
    def __init__(self, id=0, fps=40.0, bpm=240.0, measure=4):
        self.id = id
        self.fps = fps
        self.bpm = bpm
        self.measure = measure
        self.fpb = (fps * 60) / bpm
        self.last_frame = Frame()
        self.generators = []
        self.access_lock = threading.Lock()
        self.frameindex = 0
        self.beatindex = 0
        self.beat = 0
        self.autocycle = AutoCycler(self)

    def add(self, generator):
        try:
            self.access_lock.acquire()
            if(self.autocycle.enabled):
                self.generators.append(itertools.cycle(generator))
            else:
                self.generators.append(generator)
        finally:
            self.access_lock.release()
    
    def iterate(self):
        f = self.last_frame
        for g in self.generators:
            try:
                n = next(g)
                f = f.merge(n) if f else n
            except StopIteration:
                self.generators.remove(g)
        
        self.frameindex = self.frameindex + 1 if self.frameindex < self.fps - 1 else 0
        self.beatindex = self.beatindex + 1 if self.beatindex < self.fpb - 1 else 0
        if self.beatindex < self.fpb - 1:
            self.beatindex += 1
        else:
            self.beatindex = 0
            self.beat = self.beat + 1 if self.beat < self.measure - 1 else 0
        
        self.last_frame = f

    def get_clock(self):
        def _clock():
            return dict(
                beat = self.beat,
                measure = self.measure,
                frameindex = self.frameindex,
                fps = self.fps,
                beatindex = self.beatindex,
                fpb = self.fpb,
                last = self.last_frame
            )
        return _clock

class Controller(daemon.Poller):
    def __init__(self, address, nodaemon=False, runout=False, fps=40.0, bpm=240.0, measure=4, universes=(0,)):
        super(Controller, self).__init__(address, nodaemon=nodaemon, runout=runout)
        self.fps = float(fps)
        self.runout = runout
        self.access_lock = threading.Lock()
        universes = range(universes) if isinstance(universes, int) else universes
        self.universes = {universe:Universe(universe, self.fps, bpm, measure) for universe in universes}

    def stop(self):
        try:
            self.access_lock.acquire()
            if(self.running):
                self.running = False
        finally:
            self.access_lock.release()

    def add(self, generator, universe=0):
        return self.universes[universe].add(generator)
    
    def iterate(self, universe=0):
        return self.universes[universe].iterate()

    def get_clock(self, universe=0):
        return self.universes[universe].get_clock().update({"running": self.running})

    def run(self):
        now = time.time()
        while(self.running):
            drift = now - time.time()
            
            # do anything potentially framerate-affecting here
            self.handle_artnet()
            for universe in self.universes:
                self.universes[universe].iterate()
                self.send_dmx(self.universes[universe].last_frame, universe)
            if(self.runout and len(self.generators) == 0):
                self.running = False
            # end framerate-affecting code
            
            elapsed = time.time() - now
            excess = (1 / self.fps) - elapsed
            if(excess > 0):
                time.sleep(excess - drift if self.running else 0)
            else:
                log.warning("Frame rate loss; generators took %sms too long" % round(abs(excess * 1000)))
            now = time.time()

