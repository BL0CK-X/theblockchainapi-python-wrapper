# The Blockchain API

Submit issues and feature requests for our API on our <a href="https://github.com/BL0CK-X/the-blockchain-api">main GitHub repository</a>.

See <a href="https://docs.theblockchainapi.com">the docs</a> for more info.

## Python Quick Start

`pip install theblockchainapi`

Get an API key pair at <a href="https://dashboard.theblockchainapi.com">dashboard.theblockchainapi.com</a>.

`from theblockchainapi import TheBlockchainAPIResource`

`result = TheBlockchainAPIResource("APIKeyID", "APISecretKey").generate_secret_key()`

`print(result)`

There are many examples using this package <a href="https://github.com/BL0CK-X/the-blockchain-api/tree/main/examples">here</a>.

## Python Documentation

To get a list of available functions, run `help(TheBlockchainAPIResource)` after importing `TheBlockchainAPIResource` as shown above.

## Documentation

For full API documentation, check out <a href="https://docs.theblockchainapi.com">the docs</a>.
