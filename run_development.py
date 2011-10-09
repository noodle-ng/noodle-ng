#!/usr/bin/env python
# -*- coding: utf-8 -*-

from paste.script.serve import ServeCommand
ServeCommand("serve").run(["--reload", "development.ini"])