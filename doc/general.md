# General

The server creates a public / private key pair on startup. This keypair can be obtained, along with other server configuration parameters via the `GET /configuration` endpoint.

Example response:

```
{
    "server_public_key": "DR02DJnt6VAhFS18cT8zcjMpbVW0t+NWwgbhUisy/Tk="
}
```

This public key is used for encrypting challenge responses (CAPTCHA, authentication challenge...)

# Registration

Upon registration the user needs to solve a CAPTCHA to prove that they are indeed a human being and not a bot spamming the registration API.

To get a new CAPTCHA challenge use the `GET /captcha` endpoint.

Example response:

```
{
    "uuid": "627592c5-9bde-49ce-946b-a90eef914013",
    "image": "data:image/png;base64,iVBORw0[...]rkJggg=="
}
```

The `image` parameter is the base64 encoded image data, provided as a image URI to use directly as the `img` tag's `src` parameter.

The user inputs a username, and a passphrase. This passphrase is then derived using multiple rounds of scrypt, with the username as the salt, to become the user's master private key.

The client then encrypts the captcha answer for the server (using the server's public key obtained via `GET /configuration`), and authenticates the message using the user's master private key. This allows the client to only send the user's master public key, the captcha UUID, the encrypted captcha answer and the nonce. The username and passphrase, aswell as the derived master private key remain purely client side.

The captcha answer is encrypted so that the server can verify, server-side, that the client indeed has the private key associated with the public key that they are trying to create a new account with, preventing spam (trying to register random public keys) and user enumeration (trying to find if a given public key is registered).