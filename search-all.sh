#!/bin/bash

#caffeinate -i watch -n 900 python3 ./app/main.py SAO BEL 2026-01-23 500 &
#caffeinate -i watch -n 900 python3 ./app/main.py SAO BEL 2026-01-24 500 &
#caffeinate -i watch -n 900 python3 ./app/main.py BEL SAO 2026-01-30 500 &

caffeinate -i watch -n 900 sh _search-all.sh
