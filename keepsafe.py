import db, falcon, json, uuid, random, string, base64, datetime, nacl.utils
from captcha.image import ImageCaptcha
from nacl.public import PrivateKey, SealedBox, Box
import nacl.encoding, nacl.hash
class UserResource(object):
    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200
        resp.body = 'db.User::Get'

    def on_post(self, req, resp):
        resp.status = falcon.HTTP_200
        resp.body = 'db.User::Post'

class CaptchaResource(object):
    def on_get(self, req, resp):
        # Generate a new captcha

        image = ImageCaptcha()

        captcha_uuid = str(uuid.uuid4())
        captcha_answer = ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for _ in range(6))
        captcha_image = 'data:image/png;base64,' + str(base64.b64encode(image.generate(captcha_answer).getvalue())).split("'")[1]

        # The answer should be case insensitive, the caps are just there for the bots
        captcha_answer = captcha_answer.lower()

        # Hash the user's IP address with the captcha UUID as salt
        captcha_ip_address_hash = nacl.hash.sha256(str.encode(captcha_uuid + req.remote_addr), encoder = nacl.encoding.Base64Encoder).decode('utf-8')

        captcha = db.Captcha(
            uuid = captcha_uuid,
            answer = captcha_answer,
            ip_address_hash = captcha_ip_address_hash
        )

        session = req.context['session']

        session.add(captcha)
        session.commit()

        resp.status = falcon.HTTP_200
        resp.body = json.dumps({
            'uuid': captcha_uuid,
            'image': captcha_image
        })

class ChallengeResource():
        def on_post(self, req, resp):
                challenge_publicKey = json.load(req.stream)
                session = req.context['session']
                challenge_userID = session.query(db.User).filter(db.User.publicKey == challenge_publicKey).first().id
                # ! get the userID related to the public key => challenge_userID
                challenge_answer = nacl.utils.random(Box.NONCE_SIZE)
                challenge_uuid = str(uuid.uuid4())
                challengedata = SealedBox(nacl.public.PublicKey(challenge_publicKey, nacl.encoding.Base64Encoder)).encrypt(challenge_answer)
                challenge=db.Challenge(
                        uuid = challenge_uuid,
                        userID = challenge_userID,
                        answer = str(base64.b64encode(challenge_answer))
                )
                session.add(challenge)
                session.commit()
                resp.status = falcon.HTTP_200
                resp.body = json.dumps({
                        'uuid' : challenge_uuid,
                        'challenge' : str(base64.b64encode(challengedata))
                })               
                
                
