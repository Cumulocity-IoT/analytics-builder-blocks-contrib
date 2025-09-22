ARG APAMA_VERSION=latest
ARG APAMA_IMAGE=public.ecr.aws/apama/apama-builder
FROM ${APAMA_IMAGE}:${APAMA_VERSION}

USER root
ARG ADDITIONAL_PACKAGES=
RUN apt update && apt install git tar ${ADDITIONAL_PACKAGES} -y && apt clean

RUN mkdir "/workspaces" && chown -R apama.apama "/workspaces"

USER apama

# Clone the SDKs. We clone under the home dir because "/workspaces" gets overwritten by the mount
# (and devcontainer.json workspaceMount is not respected in many cases - https://github.com/microsoft/vscode-remote-release/issues/3034)
ARG APAMA_ANALYTICS_BUILDER_SDK_BRANCH=main
RUN git clone https://github.com/Cumulocity-IoT/apama-analytics-builder-block-sdk.git --branch ${APAMA_ANALYTICS_BUILDER_SDK_BRANCH} ${APAMA_WORK}/apama-analytics-builder-block-sdk

ARG APAMA_EPLAPPS_TOOLS_BRANCH=main
RUN git clone https://github.com/Cumulocity-IoT/apama-eplapps-tools.git ${APAMA_WORK}/apama-eplapps-tools --branch ${APAMA_EPLAPPS_TOOLS_BRANCH}

# Link the SDKs to the root dir so we can find them from /workspaces/projectdir using a relative path
USER root
RUN ln -s ${APAMA_WORK}/apama-analytics-builder-block-sdk /apama-analytics-builder-block-sdk \
  && ln -s ${APAMA_WORK}/apama-eplapps-tools /apama-eplapps-tools

USER apama
ENV ANALYTICS_BUILDER_SDK=${APAMA_WORK}/apama-analytics-builder-block-sdk
ENV EPL_TESTING_SDK=${APAMA_WORK}/apama-eplapps-tools
ENV PATH="${APAMA_WORK}/apama-eplapps-tools/scripts:${APAMA_WORK}/apama-analytics-builder-block-sdk:${PATH}"
WORKDIR "/workspaces"

ENV SHELL=/bin/bash