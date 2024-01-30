# GitHub Tools

Helper tools for GitHub.

Included tools:

- Generate an RS256 signed JWT token from a private key stored in Azure
  Key Vault
- Use the JWT token and a GitHub App ID to generate a GitHub App
  Installation Token, which can be used to authenticate to GitHub as an
  app rather than a human user. (Useful for deployment scripts.)

## Install

Install with the following pip command:

``` sh
pip install git+https://git@github.com/swsphn/github-tools.git
```

This should also work with `pipx` or Poetry.
