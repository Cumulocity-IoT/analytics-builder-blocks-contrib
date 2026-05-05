# analytics-builder-blocks-contrib
This repository contains non-productized blocks for Apama Analytics Builder that have been contributed by the community.

## Installation
Working with this repository requires either a local installation of the dependencies and tools or the usage of a Development Container.

### Local installation
To add these blocks to a tenant, you will require:

* A copy of the [block-sdk](https://github.com/Cumulocity-IoT/apama-analytics-builder-block-sdk) github repo
* A local install of the Apama Full Edition from https://download.cumulocity.com/Apama/
* A Cumulocity tenant with a suitable apama-ctrl microservice subscribed (custom blocks are not supported with apama-ctrl-starter).

Installation Steps:

```
. /opt/cumulocity/Apama/bin/apama_env
git clone https://github.com/Cumulocity-IoT/apama-analytics-builder-block-sdk.git
git clone https://github.com/Cumulocity-IoT/analytics-builder-blocks-contrib.git
./apama-analytics-builder-block-sdk/analytics_builder build extension \
      --input analytics-builder-blocks-contrib/blocks/  --name contrib-blocks\
      --cumulocity_url https://$TENANT/ \
      --username $USERNAME --password $PASSWORD --restart
```

### Development Containers
The repository contains a Development Container setup that starts a container with all dependencies and tools already installed. If you use Visual Studio Code, it will detect the presence of the Development Container setup and ask if it should restart in a container.

* When using the default Dockerfile, the latest versions of Apama, the Block SDK and the EPL Apps Tools will be installed by default. This is the recommended setup but if you require a specific version of each, you can overwrite the APAMA_VERSION, APAMA_ANALYTICS_BUILDER_SDK_BRANCH, and APAMA_EPLAPPS_TOOLS_BRANCH variables in devcontainer.json.
* If you are using a computer running macOS on Apple silicon, it is recommended to replace the Dockerfile in devcontainer.json with Dockerfile.apple which uses an ARM64 base image yielding significantly better performance. This Dockerfile will currently always use Apama 27.

## Licensing

Copyright (c) 2019-present Cumulocity GmbH

This project is licensed under the Apache 2.0 license - see <https://www.apache.org/licenses/LICENSE-2.0>

______________________
These tools are provided as-is and without warranty or support. They do not constitute part of the Cumulocity products. Users are free to use, fork and modify them, subject to the license agreement. While Cumulocity welcomes contributions, we cannot guarantee to include every contribution in the master project.

Contact us at https://apamacommunity.com if you have any questions.
______________________

