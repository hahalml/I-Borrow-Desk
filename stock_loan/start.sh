#!/bin/bash
pid=$(pgrep -f twitter.py)
echo $pid
kill $pid
pid=$(pgrep -f manager.py)
echo $pid
kill $pid
nohup python -u twitter.py > twitter.out 2> twitter1.out < /dev/null &
nohup python -u manager.py > manager.out 2> manager2.out < /dev/null &
echo Complete