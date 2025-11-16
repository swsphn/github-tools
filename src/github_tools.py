#!/usr/bin/env python3

"""GitHub Tools – Helper tools for working with GitHub Apps."""

import base64
import hashlib
import json
import time
import sys

import requests
import typer

from azure.identity import DefaultAzureCredential
from azure.keyvault.keys import KeyClient
from azure.keyvault.keys.crypto import CryptographyClient, SignatureAlgorithm

app = typer.Typer(rich_markup_mode="rich", name="ght", add_completion=False)


def jwt_encode(msg: bytes):
    return base64.urlsafe_b64encode(msg).rstrip(b"=")


def jwt_hmac(header: bytes, payload: bytes, secret: bytes):
    header_b64 = jwt_encode(header)
    payload_b64 = jwt_encode(payload)
    msg = b"%b.%b" % (header_b64, payload_b64)
    signature = jwt_encode(hmac.digest(secret, msg, "sha256"))

    return b"%b.%b.%b" % (header_b64, payload_b64, signature)


def jwt_rsa(payload: bytes, crypto_client: CryptographyClient):
    header = b'{"alg":"RS256","typ":"JWT"}'
    header_b64 = jwt_encode(header)
    payload_b64 = jwt_encode(payload)
    msg = b"%b.%b" % (header_b64, payload_b64)
    digest = hashlib.sha256(msg).digest()
    result = crypto_client.sign(SignatureAlgorithm.rs256, digest)
    signature = jwt_encode(result.signature)
    jwt_bytes = b"%b.%b.%b" % (header_b64, payload_b64, signature)
    return bytes.decode(jwt_bytes, encoding="utf-8")


def github_app_installation_id(app_id: int, jwt: str):
    """Get GitHub App installation ID for current organisation.
    (Organisation is determined automatically from valid JWT.)

    For more details see:
    https://docs.github.com/en/rest/apps/apps?apiVersion=2022-11-28#list-installations-for-the-authenticated-app
    """

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {jwt}",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    r = requests.get("https://api.github.com/app/installations", headers=headers)

    response = r.json()
    # Should only be one installation ID per app per organisation.
    app_installation_id = response[0]["id"]

    return app_installation_id


def github_app_installation_access_token(
    app_id: int, jwt: str, repositories: list = None, permissions: dict = None
) -> dict:
    """Generate a GitHub App installation access token for a given App
    id.

    For more details see:
    https://docs.github.com/en/rest/apps/apps?apiVersion=2022-11-28#create-an-installation-access-token-for-an-app

    https://docs.github.com/en/authentication/connecting-to-github-with-ssh/managing-deploy-keys#set-up-installation-access-tokens

    Args:
        app_id: The GitHub App ID for the app used to generate the
            tokens. If your organisation name is 'your_org', you will
            find your organisation's apps here:
            https://github.com/organizations/your_org/settings/apps/
            Click 'Edit' to view the App ID.
        jwt: A JSON Web Token (JWT) created with the private key of the
            app, signed using the RS256 algorithm.

            For more details see:
            https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/generating-a-json-web-token-jwt-for-a-github-app

            If you have a local copy of the private key, use the PyJWT
            library to create the JWT. If the private key is stored in
            Azure KeyVault, you can use the jwt_rsa() function defined
            in this module. In either case, the JWT payload should be:

            >>> payload = {
            ...     # Issued at time
            ...     'iat': int(time.time()),
            ...     # JWT expiration time (10 minutes maximum)
            ...     'exp': int(time.time()) + 600,
            ...     # GitHub App's identifier
            ...     'iss': app_id
            ... }

            To learn more about JWTs, see: https://jwt.io/
        repositories: A list of repositories. The generated token will
            be restricted to just these repositories. Note that you
            cannot generate a token with access to repositories outside
            those specified for the given GitHub app. (Default: None.
            By default, all available repositories are selected.)
        permissions: Dictionary of permission properties and values.
            For example: {"contents": "read"}
            The generated token will be restricted to just these
            permissions. (Default: None. By default, all available
            permissions are selected.)

            For available parameters, see the GitHub API docs:
            https://docs.github.com/en/rest/apps/apps?apiVersion=2022-11-28#create-an-installation-access-token-for-an-app

            Note that this will be limited by the permissions given to
            the app on GitHub. To review the permissions available on
            GitHub. See:
            https://github.com/organizations/YOUR_ORG/settings/apps/YOUR_APP

        Returns: Dict of token information, including token, expiry,
            permissions, repositories.
    """

    installation_id = github_app_installation_id(app_id, jwt)
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {jwt}",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    payload = {}
    payload |= {"repositories": repositories} if repositories else {}
    payload |= {"permissions": permissions} if permissions else {}

    r = requests.post(
        f"https://api.github.com/app/installations/{installation_id}/access_tokens",
        headers=headers,
        json=payload,
    )

    return r.json()


@app.command()
def app_token(app_id: str, vault_url: str, key_name: str, verbose: bool = False):
    """Generate a GitHub app installation token.

    WARNING: Do not expose the generated token. Treat it like a
    password.

    Args:
        app_id: GitHub App ID (or Client ID)
        vault_url: Azure Key Vault URL. e.g.
            https://example.vault.azure.net/
        key_name: Name of key in Azure key vault. e.g.
            example-key
    """
    credential = DefaultAzureCredential()
    key_client = KeyClient(vault_url=vault_url, credential=credential)

    key = key_client.get_key(key_name)
    crypto_client = CryptographyClient(key, credential)

    # 1 minute in the past, to allow for clock drift
    now = int(time.time() - 60)
    payload_json = json.dumps(
        {
            # Issued at time
            "iat": now,
            # JWT expiration time (10 minutes maximum)
            "exp": now + 600,
            # GitHub App's identifier
            "iss": app_id,
        }
    )
    payload = bytes(payload_json, encoding="utf-8")

    jwt = jwt_rsa(payload, crypto_client)
    app_installation_access_token = github_app_installation_access_token(app_id, jwt)

    if verbose:
        print("GitHub App Installation Token Generated")
        print(f"Expires: {app_installation_access_token['expires_at']}")
        print("\nPermissions:")
        for k, v in app_installation_access_token["permissions"].items():
            print(f"\t{k}: {v}")

        if repositories := app_installation_access_token.get("repositories"):
            print("\nRepositories:")
            for repository in repositories:
                print(f"\t{repository['full_name']}")
        print("\nToken:")
    print(app_installation_access_token["token"])


# Force app_token to be a sub-command to make it easier to add more
# sub-commands in future
# https://typer.tiangolo.com/tutorial/commands/one-or-multiple/
@app.callback()
def callback():
    """Collection of GitHub helper tools"""


if __name__ == "__main__":
    app()
