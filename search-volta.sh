#!/bin/bash

#caffeinate -i watch -n 600 ./app/dist/flysave BEL SAO 2026-01-30 400
caffeinate -i watch -n 600 python3 ./app/main.py BEL SAO 2026-01-30 400
