#!/bin/bash
source /opt/mycroft/mycroft-core/.venv/bin/activate
/opt/mycroft/mycroft-core/start-mycroft.sh all
python -m test.integrationtests.voigt_kampff.test_setup -c ~/.mycroft/test.yml
cd test/integrationtests/voigt_kampff/
behave
#TODO Export logs
