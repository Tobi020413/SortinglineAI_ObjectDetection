import logging
import os
import threading

from lib.controller import *
from lib.display import *
from lib.machine_learning import *
from lib.node_red import *
from lib.sorting_line import *

import lib.ki_integration as ki


controllerid = None
client = None


controllerid = os.uname()[1]
logging.basicConfig(level=logging.ERROR, format="%(asctime)s %(levelname)-10s %(funcName)3s %(message)s   #%(filename)3s:%(lineno)d")
display.set_attr("part_pass_fail.text", str(''.join([str(x) for x in ['<h4>UI at: http://', controllerid, '.local:1880/ui</h4>']])))

# <<< HIER: init_model aufrufen, BEVOR der Thread losläuft
ki.init_model()

threading.Thread(target=thread_SLD, daemon=True).start()
client = mqtt_client_forever()
