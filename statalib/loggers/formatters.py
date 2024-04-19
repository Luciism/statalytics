import logging

import colorlog


UncoloredFormatter = logging.Formatter(
    fmt='%(asctime)s %(levelname)-8s %(name)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

ColoredStreamFormatter = colorlog.ColoredFormatter(
    fmt='%(bold_light_black)s%(asctime)s '                  # timestamp
        '%(levelname_log_color)s%(levelname)-8s%(reset)s '  # log level
        '%(purple)s%(name)s '                               # logger name
        '%(message_log_color)s%(message)s',                 # log message
    datefmt='%Y-%m-%d %H:%M:%S',
    secondary_log_colors={
        'message': {
            'DEBUG':    'white',
            'INFO':     'white',
            'WARNING':  'white',
            'ERROR':    'light_red',
            'CRITICAL': 'light_red'
        },
        'levelname': {
            'DEBUG':    'bold_white',
            'INFO':     'bold_light_purple',
            'WARNING':  'bold_yellow',
            'ERROR':    'bold_red',
            'CRITICAL': 'bold_black,bg_red'
        },
    }
)