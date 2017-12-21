# Keepsafe Password Manager

## Registration

1. User sends initial request to /captcha

2. Server generates captcha and stores captcha answer, uuid and creation date in database, then returns the following JSON data: 

   ``` json
    {
        "uuid": "3123bc1e-a192-4e35-9080-f96c7fdae6d7",
        "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAKAAAAA8[...]ZCAAAiWElEQVR4nO=="
    }
   ```

3. The User sends a request to /register :

   1. User solves captcha and choses a username and passphrase
   2. Client derives the **encryption keypair** (private/public keypair for encryption) from the username and passphrase using Scrypt and the username as a SALT, preventing easy bruteforcing. => `public_key`
   3. Client sends the result to the server :

   ``` json
   {	
    	"public_key":"Rf5YElNrwMD7SNcNBPh9Iw6xBJmKxsNy4DoDT5oEDw8=",
      "captcha": {
          "uuid": "3123bc1e-a192-4e35-9080-f96c7fdae6d7",
          "encrypted_answer": "r+0xHxHYjtMGiPROjVK+9nWZZrEzdQ==",
          "nonce": "zIkmsndBdrR7UooDdoTJ/404dH1RZDAJ"
      }
   }
   ```

   ​

4. The server checks the captcha, then checks if the username is taken, if not and all is a-ok : 

   ``` json
   200 OK
   ```

   But if the public key is already in the database or the got the shitty captcha wrong : 

   ```json
   409 CONFLICT "ACCOUNT_EXISTS" / 418 I'M A TEAPOT "CAPTCHA_WRONG"
   ```

   ​

## Login

1. The user sends a request to /getChallenge

   1. The request contains the users public key.

      ```json
      "6auYQU8XhrUkiryxwcBWvUficKOUrGLif1ghDBOAijc="	
      ```


   2. The server then finds the public key in the database and its associated userID.

   3. It generates a UUID and some random data which it inserts into the challenges table in the database along with the userID connected to the public key and current datetime, from this point onwards the client has a fixed amount of time to solve the challenge before it expires. ==> `challengeUuid`

   4. The Server then encrypts this data with the users public key.==> `challenge`. 

   5. The server replies:

      ```json
      {
        challenge_uuid:"692b034e-f05a-47ba-8c52-e92406f20b81",
        challenge:"Zm9lemhvZ2ZpemVob2ZpaGFlb2loZmFva2VucGZzb2Jpc2hkb3A="
        nonce:"dhzdn729pemVob2ZpaGFlb2loZmFva2VucGZzb2df798dhdz0="
      }
      ```

6. The user sends a request to /Login

   1. The user enters their username and passphrase, the client derives the private and public key as during registration ==> `publicKey`

   2. Using the private key, the client decrypts the previously obtained challenge ==> `answer`

   3. The Client the generates a device keypair (public and private) => `devicePublicKey`

   4. The Client asks for a deviceName (defaults to browser on OS) => `deviceName`

   5. The client optionally allows the user to create expiring devices and add an expirydatetime => `expiryDateTime` (format to be decided)

   6. In Keepsafe Enterprise™ the Client also sends the level of access it wishes for this device to have ([ŧrue,true,true,true] for read, write,delete,manageDevices) => `accessLevel`

      ```json
      {
      public_key:"6auYQU8XhrUkiryxwcBWvUficKOUrGLif1ghDBOAijc=",
      challenge_uuid:"692b034e-f05a-47ba-8c52-e92406f20b81"
      answer:"ZnplaG90aWdmaGFwZWZvYWliZm9haWZwb2FpaHpyb2lhemhnb2ZpYXo=",
      device_name:"Internet Explorer 4 on Windows Vista",
      device_key:"GF928UD029Y972Y029EU0972G08ER",
      expiryDateTime:"2017-07-26-10:30",
      accessLevel:[true,true,true,true]
      }
      ```

   7. When the server recieves the request it checks the following conditions : 

      * Is the the userID of the given publickey the same as that of the challenge?
      * Has the challenge expired?
      * Is the answer given correct?

   8. If those conditions are met the server then replies with the newly added devices UUID :

      ```json
      200 OK "2ddd2634-0048-4c71-b847-2033a821dced"
      ```

   9. if it fails :

      ```json
      403 Forbidden "WRONG_UUID_FOR_CHALLENGE"/"CHALLENGE_EXPIRED"/"INCORRECT_ANSWER"
      ```



* After this, all requests to the server from the device are signed by the devices private key and verified serverside by the devices public key. The device uuid is included in all subsequent requests.

## Requesting/Modifying data (passwords):

1. The Client sends a request /getPasswords containing the deviceUUID and the current unix timestamp encrypted with the devices private key :

   ```json
   [
   	deviceUUID:"b74e3416-79ea-4338-9e26-0aa15e69c230"
   	encryptedRequest: encrypted(
   		timestamp
   	)
   ]
   ```

   ​

2. The server gets the request and replies

   1. The server gets the device public key connected to that UUID

   2. It attempts to decrypt the message, if it succeeds this means the user has the deviceprivatekey and is authenticated

   3. it then checks if the user is authorised to read data from the server

   4. if so it gets the userID related to the device in question and gets all their passwords.

   5. It then encrypts them with the device public key and replies :

      ``` json
      200 OK "encryptedData"
      ```

   6. In the event of an error the device replies as previously noted

3. The Client receives the reply :

   1. It decrypts the data with the device key
   2. It decrypts the passwords with the master key
   3. all done here

* A similar system is used when the user wishes to update or add a password

## Tables :

### users

|  id  | public_key |
| :--: | :--------: |
|  0   |    key     |
|  1   |    key     |

### devices

|      uuid      | userID |       name       |       device_key       |  expires   | permissions |
| :------------: | :----: | :--------------: | :--------------------: | :--------: | ----------- |
| uuid goes here |   0    | firefox on linux | ofnoaeifhoaeihfoaeihoa | 2018-04-06 | 1111        |
|   other uuid   |   1    | netscape on OS/2 | djazpejazpfjaezofho_gr |            | 1110        |

### captchas

|   uuid    | answer |     created      |
| :-------: | :----: | :--------------: |
| uuid here | jd6zk  | 2017-07-23-10:20 |

### passwords

| uuid | userID | data | nonce | created | modified |
| :--: | :----: | :--: | :---: | :-----: | :------: |
|      |        |      |       |         |          |
|      |        |      |       |         |          |
|      |        |      |       |         |          |

### challenges

| uuid | userID | answer | created |
| :--: | :----: | :----: | :-----: |
|      |        |        |         |
|      |        |        |         |
|      |        |        |         |