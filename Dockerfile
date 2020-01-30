FROM ubuntu:18.04
ENV TERM linux
ENV DEBIAN_FRONTEND noninteractive
COPY . /opt/mycroft/mycroft-core
# Install Server Dependencies for Mycroft
RUN set -x \
	&& sed -i 's/# \(.*multiverse$\)/\1/g' /etc/apt/sources.list \
	&& apt-get update \
	# TODO: add locales to dev_setup.sh
    && apt-get -y install locales \
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

ENTRYPOINT "/opt/mycroft/mycroft-core/test/integrationtests/voigt_kampff/startup.sh"
