#!/bin/bash

# Script to start mycroft core services and run the integration tests.
source /opt/mycroft/mycroft-core/.venv/bin/activate
/opt/mycroft/mycroft-core/start-mycroft.sh all > /dev/null
behave -f behave_html_formatter:HTMLFormatter > ~/.mycroft/behave.html
RESULT=$?

# Remove temporary skill files
rm -rf ~/.mycroft/skills
# Remove intent cache
rm -rf ~/.mycroft/intent_cache

exit $RESULT

#TODO Export logs
