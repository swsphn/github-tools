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
