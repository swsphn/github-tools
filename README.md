# GitHub Tools

Helper tools for GitHub.

Included tools:

- Generate an RS256 signed JWT token from a private key stored in Azure
  Key Vault
- Use the JWT token and a GitHub App ID to generate a GitHub App
  Installation Token, which can be used to authenticate to GitHub as an
  app rather than a human user. (Useful for deployment scripts.)

## Disclaimer
- This tool is not an officially supported or production-grade product.
- The content does not necessarily reflect the views or policies of South Western Sydney Primary Health Network (SWSPHN).
- Use at your own discretion and risk.

## Install

Install with the following pip command:

``` sh
pip install github-tools@git+https://github.com/swsphn/github-tools.git
# OR with SSH authentication
# (ensure your ssh-agent is running and has your ssh key added!)
pip install github-tools@git+ssh://git@github.com/swsphn/github-tools.git
```

This should also work with `pipx` or Poetry.

## Usage

Run the following for a list of included sub-commands:

``` sh
ght --help
```

You can also get help for specific sub-commands. For example:

``` sh
ght app-token --help
```

## Examples

Generate a GitHub App Installation Token using a private key stored in
Azure Key Vault.

``` sh
GITHUB_APP_ID=123456
KEYVAULT_URL=https://example.vault.azure.net/
KEYVAULT_KEY=example-key-name
GITHUB_TOKEN=$(ght app-token $GITHUB_APP_ID $KEYVAULT_URL $KEYVAULT_KEY)
```

You can use the generated token to authenticate to GitHub, using the
permissions assigned to the GitHub App as follows:

``` sh
git clone https://x-access-token:${GITHUB_TOKEN}@github.com/org/example.git
```

You can also use it to install Python packages from private GitHub
repositories for which the GitHub app has been granted access as
follows:

``` sh
pipx install git+https://x-access-token:${GITHUB_TOKEN}@github.com/org/example.git
```

However, note that this will not work for private Python packages which
depend on other private Python packages. In this case, you will need to
set some additional git config environment variables to ensure that all
subsequent git processes use the `GITHUB_TOKEN`:

``` sh
# Assuming GITHUB_TOKEN is already defined as above
export GITHUB_TOKEN
export GIT_CONFIG_COUNT=2
export GIT_CONFIG_KEY_0='credential.https://github.com.username'
export GIT_CONFIG_VALUE_0=x-access-token
export GIT_CONFIG_KEY_1='credential.https://github.com.helper'
export GIT_CONFIG_VALUE_1='!f() { test "$1" = get && echo "password=${GITHUB_TOKEN}"; }; f'
```

Now, regular git clones and pip install commands should automatically
use the GITHUB_TOKEN to authenticate to private repositories.

See [this answer on StackOverflow](https://stackoverflow.com/a/78064753)
for details.

## Security note
This tool generates GitHub App installation tokens. These tokens grant
access to GitHub repositories and should be handled as securely as 
passwords or SSH keys. Do not share them or expose them in logs.

## License
This project is licensed under the [MIT license](LICENSE).

## Maintainers
Developed by David Wales  
Digital Health & Data Team  
South Western Sydney Primary Health Network (SWSPHN)
