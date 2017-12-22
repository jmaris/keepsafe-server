import db, falcon, json, uuid, random, string, base64, datetime, nacl.utils
from captcha.image import ImageCaptcha
from nacl.public import PublicKey, PrivateKey, Box
import nacl.encoding, nacl.hash

class ConfigurationResource(object):
    def on_get(self, req, resp):
        configuration = req.context['configuration']

        data = {
            'server_public_key': configuration['server_key_pair'].public_key.encode(encoder = nacl.encoding.Base64Encoder).decode('utf-8')
        }

        resp.body = json.dumps(data)

class RegisterResource(object):
    def on_post(self, req, resp):
        configuration = req.context['configuration']

        if req.content_length:
            data = json.load(req.bounded_stream)
        else:
            raise Exception("No data.")

        if 'public_key' not in data:
            raise Exception("No public key.")

        if 'captcha' not in data:
            raise Exception("No captcha.")

        if 'uuid' not in data['captcha']:
            raise Exception("No captcha UUID.")

        if 'encrypted_answer' not in data['captcha']:
            raise Exception("No captcha encrypted answer.")

        if 'nonce' not in data['captcha']:
            raise Exception("No captcha nonce.")

        # Decrypt captcha answer

        user_public_key = PublicKey(data['public_key'].encode('utf-8'), encoder = nacl.encoding.Base64Encoder)

        captcha_encrypted_answer = base64.b64decode(data['captcha']['encrypted_answer'].encode('utf-8'))
        captcha_nonce = base64.b64decode(data['captcha']['nonce'].encode('utf-8'))

        box = Box(configuration['server_key_pair'], user_public_key)
        captcha_answer = box.decrypt(captcha_encrypted_answer, captcha_nonce).decode('utf-8').lower()

        # Get captcha from database

        db_session = req.context['db_session']
        captcha = db_session.query(db.Captcha).filter(db.Captcha.uuid == data['captcha']['uuid']).first()

        # Whatever happens, delete the captcha from database
        db_session.delete(captcha)
        db_session.commit()

        # Check the IP hash of the user who requested the captcha matches the current client's IP hash
        ip_address_hash = nacl.hash.sha256(str.encode(captcha.uuid + req.remote_addr), encoder = nacl.encoding.RawEncoder)
        user_agent_hash = nacl.hash.sha256(str.encode(captcha.uuid + req.user_agent), encoder = nacl.encoding.RawEncoder)
        answer_hash = nacl.hash.sha256(str.encode(captcha.uuid + captcha_answer), encoder = nacl.encoding.RawEncoder)

        if (ip_address_hash != captcha.ip_address_hash) or (user_agent_hash != captcha.user_agent_hash):
            raise Exception("Captcha answer incorrect.")

        # Check the captcha answer
        if captcha.answer_hash != answer_hash:
            raise Exception("Captcha answer incorrect.")

        # Create new user
        user = db.User(
            public_key = user_public_key.encode(nacl.encoding.RawEncoder)
        )

        db_session.add(user)
        db_session.commit()

        resp.status = falcon.HTTP_201
        resp.body = json.dumps({})

class DeviceResource(object):
    def on_post(self, req, resp):
        # Does Device registration
        if req.content_length:
            data = json.load(req.bounded_stream)
        else:
            raise Exception("No data.")

        if 'challenge_uuid' not in data:
            raise Exception("Challenge UUID missing.")

        if 'challenge_reply' not in data:
            raise Exception("Challenge Reply Missing")

        if 'public_key' not in data:
            raise Exception("User Public Key Missing.")

        if 'device_key' not in data:
            raise Exception("Device Key Missing.")

        if 'permissions' not in data:
            raise Exception("Permission Set Missing.")
 
 
class UserResource(object):
    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200
        resp.body = 'db.User::Get'

class CaptchaResource(object):
    def on_get(self, req, resp):
        # Generate a new captcha

        image = ImageCaptcha(fonts = ['fonts/UbuntuMono-R.ttf'])

        captcha_uuid = str(uuid.uuid4())
        captcha_answer = ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for _ in range(6))
        captcha_image = 'data:image/png;base64,' + str(base64.b64encode(image.generate(captcha_answer).getvalue())).split("'")[1]

        # The answer should be case insensitive, the caps are just there for the bots
        captcha_answer = captcha_answer.lower()

        captcha = db.Captcha(
            uuid = captcha_uuid,
            answer_hash = nacl.hash.sha256(str.encode(captcha_uuid + captcha_answer), encoder = nacl.encoding.RawEncoder),
            ip_address_hash = nacl.hash.sha256(str.encode(captcha_uuid + req.remote_addr), encoder = nacl.encoding.RawEncoder),
            user_agent_hash = nacl.hash.sha256(str.encode(captcha_uuid + req.user_agent), encoder = nacl.encoding.RawEncoder)
        )

        db_session = req.context['db_session']

        db_session.add(captcha)
        db_session.commit()

        resp.status = falcon.HTTP_200
        resp.body = json.dumps({
            'uuid': captcha_uuid,
            'image': captcha_image
        })

class ChallengesResource(object):
    def on_post(self, req, resp):
        configuration = req.context['configuration']

        if req.content_length:
            data = json.load(req.bounded_stream)
        else:
            raise Exception("No data.")

        if 'public_key' not in data:
            raise Exception("No public key.")

        db_session = req.context['db_session']

        user_public_key = PublicKey(data['public_key'].encode('utf-8'), encoder = nacl.encoding.Base64Encoder)

        user = db_session.query(db.User).filter(db.User.public_key == user_public_key.encode(nacl.encoding.RawEncoder)).first()

        if user is None:
            raise Exception("Public key unknown.")

        challenge_answer = nacl.utils.random(Box.NONCE_SIZE)
        challenge_uuid = str(uuid.uuid4())

        box = Box(configuration['server_key_pair'], user_public_key)

        challenge_box = box.encrypt(plaintext = challenge_answer, encoder = nacl.encoding.Base64Encoder)

        challenge = db.Challenge(
            uuid = challenge_uuid,
            user = user,
            answer_hash = nacl.hash.sha256(challenge_answer, encoder = nacl.encoding.RawEncoder)
        )

        db_session.add(challenge)
        db_session.commit()

        resp.status = falcon.HTTP_200
        resp.body = json.dumps({
            'uuid': challenge_uuid,
            'nonce': str(challenge_box.nonce.decode('utf-8')),
            'challenge': str(challenge_box.ciphertext.decode('utf-8'))
        })
                
class LoginResource(object):
    def on_post(self, req, resp):
        configuration = req.context['configuration']

        if req.content_length:
            data = json.load(req.bounded_stream)
        else:
            raise Exception("No data.")

        if 'challenge' not in data:
            raise Exception("No challenge.")

        if 'uuid' not in data['challenge']:
            raise Exception("No UUID.")

        if 'nonce' not in data['challenge']:
            raise Exception("No nonce.")

        if 'response' not in data['challenge']:
            raise Exception("No response")

        db_session = req.context['db_session']
        challenge = db_session.query(db.Challenge).filter(db.Challenge.uuid == data['challenge']['uuid']).first()
        user = challenge.user

        if challenge is None:
            raise Exception("Challenge unknown.")

        db_session.delete(challenge)
        db_session.commit()

        user_public_key = PublicKey(challenge.user.public_key, encoder = nacl.encoding.RawEncoder)

        box = Box(configuration['server_key_pair'], user_public_key)

        response = base64.b64decode(data['challenge']['response'].encode('utf-8'))

        nonce = base64.b64decode(data['challenge']['nonce'].encode('utf-8'))

        answer = box.decrypt(response, nonce, encoder = nacl.encoding.RawEncoder)
        answer_hash = nacl.hash.sha256(answer, encoder = nacl.encoding.RawEncoder)

        if answer_hash != challenge.answer_hash:
            raise Exception("Response incorrect.")

        user_session = db.UserSession(
            uuid = str(uuid.uuid4()),
            user = user,
            ip_address_hash = nacl.hash.sha256(req.remote_addr.encode('utf-8'), encoder = nacl.encoding.RawEncoder),
            user_agent_hash = nacl.hash.sha256(req.user_agent.encode('utf_8'), encoder = nacl.encoding.RawEncoder)
        )

        db_session.add(user_session)
        db_session.commit()

        resp.status = falcon.HTTP_200
        resp.body = json.dumps({
            'uuid': user_session.uuid
        })
