#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Just starts a paster server with the reload option
and development.ini"""

from paste.script.serve import ServeCommand
ServeCommand("serve").run(["--reload", "development.ini"])