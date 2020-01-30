FROM ubuntu:18.04 as builder
ENV TERM linux
ENV DEBIAN_FRONTEND noninteractive
COPY . /opt/mycroft/mycroft-core
# Install Server Dependencies for Mycroft
RUN set -x \
	&& sed -i 's/# \(.*multiverse$\)/\1/g' /etc/apt/sources.list \
	&& apt-get update \
    && apt-get -y install locales sudo\
	&& mkdir /opt/mycroft/skills \
	&& CI=true bash -x /opt/mycroft/mycroft-core/dev_setup.sh --allow-root -sm \
	&& apt-get -y autoremove \
	&& apt-get clean \
	&& rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
# Set the locale
RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8
WORKDIR /opt/mycroft/mycroft-core
RUN mkdir ~/.mycroft \
        && /opt/mycroft/mycroft-core/.venv/bin/msm -p mycroft_mark_1 default
EXPOSE 8181

# Integration Test Suite
FROM builder as voight_kampff
# Activate the virtual environment for Mycroft Core.
RUN source /opt/mycroft/mycroft-core/.venv/bin/activate
# Start the Mycroft Core proceses
RUN /opt/mycroft/mycroft-core/start-mycroft.sh all > /dev/null
# Setup the integration tests
RUN python -m test.integrationtests.voigt_kampff.test_setup -c ~/.mycroft/test.yml
    && cd test/integrationtests/voigt_kampff/
# Run the integration tests
ENTRYPOINT "behave -f behave_html_formatter:HTMLFormatter > ~/.mycroft/behave.html"
