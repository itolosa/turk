# -*- coding: utf-8 -*-

"""
Created by Rodrigo Fuentealba
Please, read the file "/LICENSE.md" for licensing information.
"""

__author__="Rodrigo Fuentealba <rfuentealbac.83@gmail.com>"
__version__="1.0"
__copyright__="Copyright (c) Rodrigo Fuentealba <rfuentealbac.83@gmail.com>"
__license__="MIT"

import os
import sys
import time
import signal
import atexit
import logging


class daemon(object):
    """
    Basic functionality to daemonize a function.
    """
    
    turk_state = {
        "pidfile" : "/var/run/turkmenbashi.pid",
        "tempdir" : "/",
        "userlog" : logging.getLogger("Turkmenbashi"),
        "waitfor" : 10,
        "debugit" : True,
        "working" : True,
    }

    def __init__(self):
        """
        Signal handling declaration.
        """
        for sig in (signal.SIGHUP, signal.SIGINT, signal.SIGQUIT):
            signal.signal(sig, lambda * args: self.turk_quit)
    
    def turk_start(self, function):
        """
        Daemonizes a function by double forking.
        """
        if self.turk_state["userlog"] is None:
            hdl = logging.StreamHandler()
            fmt = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s")
            hdl.setFormatter(fmt)
            self.turk_state["userlog"] = logging.getLogger("Turkmenbashi")
            self.turk_state["userlog"].addHandler(hdl)
            self.turk_state["userlog"].setLevel(logging.DEBUG)
            message = """
Your daemon is using the default logger. To avoid this, define a logger
and pass it to the state as follows:

    self.turk_state["userlog"] = logging.Logger()

Feel free to change the logger for something useful for you.
"""
            self.turk_state["userlog"].warning(message)

        pid = None
        
        try:
            pf = open(self.turk_state["pidfile"], "rb")
            pid = int(pf.read().strip())
            pf.close()
        except Exception:
            if self.turk_state["debugit"] == True:
                self.turk_state["userlog"].debug("No running instances. OK.")
        
        if pid is not None:
            self.turk_state["userlog"].critical("Another instance is running.")
            sys.exit(1)

        try:
            pid = os.fork()
            if pid > 0:
                if self.turk_state["debugit"] is True:
                    self.turk_state["userlog"].debug("Close parent fork.")
                sys.exit(0)

            pid = os.fork()
            if pid > 0:
                sys.exit(0)

            if not os.path.exists(self.turk_state["tempdir"]):
                os.mkdir(self.turk_state["tempdir"])
            os.chdir(self.turk_state["tempdir"])

        except (IOError, OSError), e:
            self.turk_state["userlog"].critical("Can't create daemon: %s" % \
                ", ".join(e.args)
            )
            sys.exit(1)

        os.setsid()
        os.umask(int('007', 8))

        if self.turk_state["debugit"] is False:
            null_value = "/dev/null"
            if hasattr(os, "devnull"):
                null_value = os.devnull

            null_descriptor = open(null_value, "rw")
            for stdall in (sys.stdin, sys.stdout, sys.stderr):
                stdall.close()
                stdall = null_descriptor

        atexit.register(self.turk_quit)
        pid = str(os.getpid())
        pidfile = open(self.turk_state["pidfile"], 'w+').write("%s" % pid)

        while self.turk_state["working"] is True:
            function()
            time.sleep(self.turk_state["waitfor"])
        
    def turk_quit(self):
        """
        Removes the PID file and launches the query stop.
        """
        self.turk_state["working"] = False

        try:
            os.remove(self.turk_state["pidfile"])
        except Exception:
            pass

    def turk_stop(self):
        """
        Send SIGTERM to the registered PID and remove it.
        """
        pid = None

        try:
            pf = open(self.turk_state["pidfile"], "rb")
            pid = int(pf.read().strip())
            pf.close()
        except (IOError, OSError):
            pass

        if pid is not None:
            try:
                for i in range(1, 10):
                    os.kill(pid, signal.SIGTERM)
                    time.sleep(5)
            except Exception, e:
                if "No such process" in e.args:
                    if os.path.exists(self.turk_state["pidfile"]):
                        os.remove(self.turk_state["pidfile"])
                else:
                    self.turk_state["userlog"].critical("There is an error: %s" % e)
                    sys.exit(1)
