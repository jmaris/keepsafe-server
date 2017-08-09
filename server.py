import falcon
import keepsafe
class App(falcon.API):
    def __init__(self, *args, **kwargs):
        super(App, self).__init__(*args, **kwargs)

        userResource = keepsafe.UserResource()
        captchaResource = keepsafe.CaptchaResource()

        self.add_route('/users', userResource)
        self.add_route('/captcha', captchaResource)

app = App(middleware = [keepsafe.db.CorsMiddleware(), keepsafe.db.DatabaseSessionMiddleware(keepsafe.db.session)])
