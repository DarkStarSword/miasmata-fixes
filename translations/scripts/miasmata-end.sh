#!/bin/sh

gimp --no-interface --batch '(python-fu-miasmata-end-slide RUN-NONINTERACTIVE)' --batch '(gimp-quit 1)'
