#!/bin/sh

[ -z "$GIMP" ] && GIMP=gimp

for basename in Blackboard_DidIkillthem Blackboard_whoisboters Blackboard_YouAreBeingWatched
do
	${GIMP} --no-interface --batch '(python-fu-miasmata-to-dds-jpg RUN-NONINTERACTIVE "'${basename}.ora'" "'${basename}'")' --batch '(gimp-quit 1)'
done
