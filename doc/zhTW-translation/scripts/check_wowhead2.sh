#!/bin/bash
# for a given quest id, print: id<TAB>http_status<TAB>slug
id="$1"
resp=$(curl -s -o /dev/null -D - --max-time 10 "https://www.wowhead.com/tw/quest=${id}" 2>/dev/null)
status=$(printf '%s\n' "$resp" | head -1 | grep -oE "[0-9]{3}")
loc=$(printf '%s\n' "$resp" | grep -i "^location:" | tail -1 | sed 's/^[Ll]ocation: *//;s/\r$//')
slug="${loc##*/}"
printf '%s\t%s\t%s\n' "$id" "$status" "$slug"
