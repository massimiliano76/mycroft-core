#!/bin/bash
source /opt/mycroft/mycroft-core/.venv/bin/activate
/opt/mycroft/mycroft-core/start-mycroft.sh all
python -m test.integrationtests.voigt_kampff.test_setup -c ~/.mycroft/test.yml
cd test/integrationtests/voigt_kampff/
behave
RESULT=$?

# Remove temporary skill files
rm -rf ~/.mycroft/skills
# Remove intent cache
rm -rf ~/.mycroft/intent_cache

exit $RESULT

#TODO Export logs
