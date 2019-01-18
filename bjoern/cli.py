import sys
import argparse

import email.utils
import errno
import fcntl
import html
import inspect
import io
import logging
import os
import pwd
import random
import re
import socket
import sys
import textwrap
import time
import traceback
import warnings

import pkg_resources

import urllib.parse

class AppImportError(ImportError):
    pass


def import_app(module):
    parts = module.split(":", 1)
    if len(parts) == 1:
        module, obj = module, "application"
    else:
        module, obj = parts[0], parts[1]

    try:
        import ipdb; ipdb.set_trace()
        __import__(module)
    except ImportError:
        if module.endswith(".py") and os.path.exists(module):
            msg = "Failed to find application, did you mean '%s:%s'?"
            raise ImportError(msg % (module.rsplit(".", 1)[0], obj))
        else:
            raise

    mod = sys.modules[module]

    is_debug = logging.root.level == logging.DEBUG
    try:
        app = eval(obj, vars(mod))
    except NameError:
        if is_debug:
            traceback.print_exception(*sys.exc_info())
        raise AppImportError("Failed to find application object %r in %r" % (obj, module))

    if app is None:
        raise AppImportError("Failed to find application object: %r" % obj)

    if not callable(app):
        raise AppImportError("Application object must be callable.")
    return app


def run_from_cli():
    import bjoern
    parser = argparse.ArgumentParser(description='Bjoern WSGI server')
    parser.add_argument('--host', type=str, help='host')
    parser.add_argument('--port', type=int, help='port')
    parser.add_argument('app', type=str, help='app module', nargs='*')
    args = parser.parse_args()
    parsed_args = vars(args)
    app = import_app(parsed_args['app'][0])
    host = parsed_args['host']
    port = parsed_args['port']
    bjoern.run(app, host, port)
