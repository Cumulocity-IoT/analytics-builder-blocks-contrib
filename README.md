# analytics-builder-blocks-contrib
This repository contains non-productized blocks for Apaam Analytics Builder that have been contributed by the community.

## Installation
To add these blocks to a tenant, you will require:

* A copy of the [block-sdk](https://github.com/Cumulocity-IoT/apama-analytics-builder-block-sdk) github repo
* A local install of the Apama Full Edition from https://download.cumulocity.com/Apama/
* A Cumulocity tenant with a suitable apama-ctrl microservice subscribed (custom blocks are not supported with apama-ctrl-starter).

Installation Steps:

```
. $SAG_INSTALL/Apama/bin/apama_env
git clone https://github.com/Cumulocity-IoT/apama-analytics-builder-block-sdk.git
git clone https://github.com/Cumulocity-IoT/analytics-builder-blocks-contrib.git
./apama-analytics-builder-block-sdk/analytics_builder build extension \
      --input analytics-builder-blocks-contrib/blocks/  --name contrib-blocks\
      --cumulocity_url https://$TENANT/ \
      --username $USERNAME --password $PASSWORD --restart
```



## Licensing

Copyright (c) 2019-present Cumulocity GmbH

This project is licensed under the Apache 2.0 license - see <https://www.apache.org/licenses/LICENSE-2.0>

______________________
These tools are provided as-is and without warranty or support. They do not constitute part of the Cumulocity products. Users are free to use, fork and modify them, subject to the license agreement. While Cumulocity welcomes contributions, we cannot guarantee to include every contribution in the master project.

Contact us at https://apamacommunity.com if you have any questions.
______________________

