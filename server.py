import falcon
import keepsafe

from nacl.public import PrivateKey, Box

class App(falcon.API):
    def __init__(self, *args, **kwargs):
        super(App, self).__init__(*args, **kwargs)

        self.add_route('/configuration', keepsafe.ConfigurationResource())
        self.add_route('/users', keepsafe.UserResource())
        self.add_route('/captcha', keepsafe.CaptchaResource())
        self.add_route('/challenges', keepsafe.ChallengesResource())
        self.add_route('/register', keepsafe.RegisterResource())
        self.add_route('/challenges/{challengeUuid}', keepsafe.ChallengeResource())

server_key_pair = PrivateKey.generate()

app = App(middleware = [
    keepsafe.db.CorsMiddleware(),
    keepsafe.db.DatabaseSessionMiddleware(keepsafe.db.session),
    keepsafe.db.ConfigurationMiddleware(server_key_pair)
])
