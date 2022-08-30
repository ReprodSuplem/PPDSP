#!/bin/bash

for ((r=1; r<41; r++))
do
	for ((v=1; v<11; v++))
	do
		for ((c=10; c<11; c++))
		do
			python3 ../GenIns/genIns_ex.py ulysses22 $r $v $c
			python3 ../GenIns/genIns_p1.py ulysses22 $r $v $c
		done
	done
done

for ((r=1; r<41; r++))
do
	for ((v=1; v<11; v++))
	do
		for ((c=10; c<11; c++))
		do
			python3 ../GenIns/genIns_ex.py ulysses16 $r $v $c
			python3 ../GenIns/genIns_p1.py ulysses16 $r $v $c
		done
	done
done

for ((r=1; r<41; r++))
do
	for ((v=1; v<11; v++))
	do
		for ((c=10; c<11; c++))
		do
			python3 ../GenIns/genIns_ex.py burma14 $r $v $c
			python3 ../GenIns/genIns_p1.py burma14 $r $v $c
		done
	done
done



