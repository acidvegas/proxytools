#!/bin/bash
cd "$(dirname "$0")"
KEY="$(<dronebl.key)"

(
        echo "<?xml version=\"1.0\"?><request key=\"$KEY\">"
        while [ -n "$1" ] ; do
                echo "<lookup ip=\"$1\" />"
                shift
        done
        echo "</request>"
) \
|       curl -s --data @- https://dronebl.org/RPC2  \
|       (xmllint --xpath '/response/result/@id' - 2>/dev/null | sed -n -e 's, id="\([^"]*\)",\1\n,gp') \
|(
        echo "<?xml version=\"1.0\"?><request key=\"$KEY\">"
        while read ID ; do
                echo "Remove ID $ID" >&2
                echo "<remove id=\"$ID\" />"
        done
        echo "</request>"
) \
|       tee -a dronebl-remove.log \
|       curl -s --data @- https://dronebl.org/RPC2 | tee -a dronebl-remove.log | grep -q "\"success\""
if [ $? -eq 0 ] ; then
        echo "DRONEBL: successfully removed $@"
else
        echo "DRONEBL: error removing $@"
fi
