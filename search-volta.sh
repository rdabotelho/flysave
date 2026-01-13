#!/bin/bash

#caffeinate -i watch -n 900 ./app/dist/flysave BEL SAO 2026-01-30 400
caffeinate -i watch -n 900 python3 ./app/main.py BEL SAO 2026-01-30 500
