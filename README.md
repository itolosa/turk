Turkmenbashi Daemon Creator
===========================

A Python library for UNIX daemon creation.

**Latest version: 1.0**

It provides functions to start and stop a daemon and a state manager
to control basic aspects on daemon execution.

How it works
------------

According to PEP 3143, an UNIX daemon process should close all open
file descriptors, change current working directory, reset file access
creation mask, detach itself from its control terminal, stop getting
I/O signals and create other processes when getting SIGCLD signals.
This piece of code does everything except for handling SIGCLD.

How to implement it
-------------------

Just create a class which extends turkmenbashi.daemon, and configure
the state manager (it's a dict, kept in self.turk_state).

This is a demo implementation that prints debug messages:

    import turkmenbashi
    
    class debugdaemon (turkmenbashi.daemon):
    
        def config(self):
            self.turk_state["debugit"] = True
            self.turk_state["pidfile"] = "/var/run/turkmenbashi.pid"
            self.turk_state["tempdir"] = "/"
            self.turk_state["waitfor"] = 10
            self.turk_state["userlog"] = logging.Logger()
        
        def code(self):
            print "This is a debug message"

Running it is as easy as creating a piece of code to start and stop the
daemon.

    daemon = debugdaemon()
    daemon.config()
    daemon.turk_start(daemon.code)
    daemon.turk_stop()

Source
------
The source can be browsed at "http://github.com/rfc83/python-turkmenbashi"


Contact me
----------
For any requests, please contact me at: <rfuentealbac.83@gmail.com>
