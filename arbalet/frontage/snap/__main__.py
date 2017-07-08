from .snap import SnapServer
from argparse import ArgumentParser

parser = ArgumentParser(description='Server for the Snap visual programming language. '
                                    'First start the server and keep it open, it runs in background. '
                                    'Open the online Snap environment in your web browser: http://snap.berkeley.edu/run '
                                    'then select File > Import and choose the file "xml/arbalet.xml" file on your local disk')

parser.add_argument('-w', '--hardware',
                    action='store_true',
                    help='The server must connect to Arbalet hardware ')

parser.add_argument('-n', '--no-simulation',
                    dest='simulation',
                    action='store_false',
                    help='Disable the LED/touch device simulation that is automatically started otherwise')

args = parser.parse_args()

SnapServer(33450, args.hardware, args.simulation).run()
