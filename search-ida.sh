#!/bin/bash

#caffeinate -i watch -n 600 ./app/dist/flysave SAO BEL 2026-01-24 400
caffeinate -i watch -n 600 python3 ./app/main.py SAO BEL 2026-01-24 400
