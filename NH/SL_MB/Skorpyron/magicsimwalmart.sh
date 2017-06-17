#!/bin/bash

if [ "$1"="skorpyron" ]; then
	cp shadowbonobo_template.simc shadowbonobo_skorpyron.simc
	raidevents='enemy=enemy1
enemy=enemy2
raid_events+=/move_enemy,name=enemy2,cooldown=2000,duration=1000,x=-27,y=-27
raid_events+=/adds,count=3,first=45,cooldown=45,duration=10,distance=5'
	echo 'fight_style=patchwerk' >> shadowbonobo.simc
	echo 'max_time=250' >> shadowbonobo.simc
	echo raidevents >> shadowbonobo.simc
	simc shadowbonobo_skorpyron.simc | grep -E '^.*100\.0.*Shadowbonobo' | tr " " "\n" | head -n2 | tail -n1
fi
