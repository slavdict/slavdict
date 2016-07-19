#!/bin/bash
cat /root/.list | xargs python /var/www/slavdict/bin/indesign_xml_dumper.py >/root/slavdict-dump.xml
exit 0
