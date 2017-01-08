#!/bin/bash

username=$1
tag=$2
level=$3
winrate=$4
rank=$5

#while getopts ":w:r:" opt; do
#	case $opt in
#		w) winrate=$OPTARG
#			;;
#		r) rank=$OPTARG
#			;;
#		s) stars=$OPTARG
#			;;
#	esac
#done

convert avatar.png \( -size 128x128 xc:none -fill white -draw "circle 64,64 64,9" \) -compose copy_opacity -composite avatar.png
composite -compose atop -geometry +32+40 avatar.png background.png out.png
composite -compose atop -geometry -32-24 frame.png out.png out.png
convert -font Iosevka-bold -fill "#d0d0e0" -pointsize 25 -draw "text 250,65 '$username'" out.png out.png;
offset=$((${#username}* 13 + 250));
convert -font Iosevka -fill "#606060" -pointsize 25 -draw "text $offset,65 '#$tag'" out.png out.png;
convert -font Iosevka-bold -fill "#30c030" -pointsize 18 -draw "text 256,90 'level $level'" out.png out.png;

if [ -a stars.png ]; then
	composite -compose atop -geometry -32+110 stars.png out.png out.png
fi

if [ ${#4} -gt 0 ]; then
	convert rank.png -geometry 50 rank.png;
	composite -compose atop -geometry +200+32 rank.png out.png out.png;
	convert -font Iosevka -fill "#c0c0d0" -pointsize 18 -draw "text 256,135 'winrate: $winrate%'" out.png out.png;
	convert -font Iosevka -fill "#c0c0d0" -pointsize 18 -draw " text 256,165 'rank: $rank'" out.png out.png;
fi
mv out.png ../ow_rank.png
rm ./*
