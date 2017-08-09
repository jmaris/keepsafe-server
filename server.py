import falcon
import keepsafe
class App(falcon.API):
    def __init__(self, *args, **kwargs):
        super(App, self).__init__(*args, **kwargs)

        self.add_route('/users', keepsafe.UserResource())
        self.add_route('/captcha', keepsafe.CaptchaResource())
        self.add_route('/challenge', keepsafe.ChallengeResource())

app = App(middleware = [keepsafe.db.CorsMiddleware(), keepsafe.db.DatabaseSessionMiddleware(keepsafe.db.session)])
