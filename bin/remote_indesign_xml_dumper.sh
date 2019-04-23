#!/bin/bash
cat /root/.args | xargs python /var/www/slavdict/bin/indesign_xml_dumper.py
exit 0
