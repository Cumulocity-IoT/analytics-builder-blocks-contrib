ARG APAMA_VERSION
ARG APAMA_IMAGE
FROM ${APAMA_IMAGE}:${APAMA_VERSION}

ARG USERNAME=apama
ARG USER_UID=1000
ARG USER_GID=${USER_UID}

USER root
RUN apt update && apt install git tar -y

# The mount location.
RUN mkdir "/workspaces"
RUN mkdir "/home/${USERNAME}"

RUN groupmod --gid ${USER_GID} ${USERNAME} \
    && usermod --uid ${USER_UID} --gid ${USER_GID} ${USERNAME} -d "/home/${USERNAME}" \
    && chown -R ${USER_UID}:${USER_GID} /workspaces \
    && chown -R ${USER_UID}:${USER_GID} /home/${USERNAME}

USER ${USERNAME}
WORKDIR "/workspaces"

# Check out Block SDK at the mount location.
RUN git clone https://github.com/Cumulocity-IoT/apama-analytics-builder-block-sdk.git
ARG APAMA_ANALYTICS_BUILDER_SDK_BRANCH
WORKDIR "/workspaces/apama-analytics-builder-block-sdk"
RUN git checkout ${APAMA_ANALYTICS_BUILDER_SDK_BRANCH}

WORKDIR "/workspaces"

# Check out EPLApps Tools at the mount location.
RUN git clone https://github.com/Cumulocity-IoT/apama-eplapps-tools.git 
ARG APAMA_EPLAPPS_TOOLS_BRANCH
WORKDIR "/workspaces/apama-eplapps-tools"
RUN git checkout ${APAMA_EPLAPPS_TOOLS_BRANCH}
ENV ANALYTICS_BUILDER_SDK=/workspaces/apama-analytics-builder-block-sdk
ENV SHELL=/bin/bash