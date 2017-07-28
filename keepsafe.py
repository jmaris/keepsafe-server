import pymysql,captcha,base64,random,string, uuid, datetime, nacl.utils base64
from nacl.public import PrivateKey, SealedBox
from io import BytesIO
from captcha.image import ImageCaptcha
image = ImageCaptcha()

# Connects directly to the MySQL database
try:
	db=pymysql.connect("localhost","keepsafe","testingkeepsafe","keepsafe", autocommit=True)
	c=db.cursor()
except:
	print("Error : Connection to the Database Failed")

# Base Functions - These functions are not directly exposed by the API
def genUUID():
	return uuid.uuid4().hex

def addAccount(publicKey):
	c.execute("""INSERT INTO `users` (`publicKey`) VALUES (%s);""",(publicKey))
	
def deleteAccount(publicKey):
	# delete passwords from the database
	try:
		c.execute("""DELETE from `users` WHERE `publicKey` = %s;""", (publicKey,))
		return true
	except:	return false

def testCaptcha(captchaUUID, captchaAnswer):
	try:
		c.execute("""SELECT `captcha`,`created` FROM `captchas` WHERE `uuid` = %s;""",(captchaUUID))
	except:
		return "CAPTCHA_NOTFOUND"
	if str(c.fetchone()[0])==captchaguess:
		if: c.fetchone()[1].strftime('%Y-%m-%d %H:%M:%S') > datetime.now()-datetime.timedelta(minutes=5)
			return true
		else:
			return "CAPTCHA_EXPIRED"
	else:
		return "CAPTCHA_WRONG"

def generateChallenge(publicKey):
	try:
		c.execute("""SELECT `id` FROM `users` WHERE `publicKey` = %s;""",(publicKey))
		userID=c.fetchone()[0]
		challengeUUID=genUUID()
		challengebin=nacl.utils.random(Box.NONCE_SIZE)
		c.execute("""INSERT INTO `challenges` (`uuid`,`userID`,`data`) VALUES (%s, %s, %s);""",(challengeUuid, userID, base64.b64encode(challengebin))
		challenge=SealedBox(nacl.public.PublicKey(publicKey, nacl.encoding.Base64Encoder)).encrypt(challengebin)
		return {'challenge':challenge.encode(encoder=nacl.encoding.Base64Encoder) 'challengeUUID':challengeUUID}
		
def checkChallenge(challengeUUID, answer):
	

# User Interaction functions - These functions should be directly exposed to the API and have return values in the predefined format.
# the format is an array, first object is true or false, indicates if the request succeeded, second is either reply or error
# goal : replace errors by error codes for translation

def register(username, publicKey, captchaUUID, captchaAnswer):
	captchaResult=testCaptcha(captchaUUID, captchaAnswer)
	if captchaResult==true:
		try:
			addAccount(username, publicKey)
		except:
			return "USERNAME_TAKEN"
	else:
		return captchaResult
	
def generateCaptcha():
	captchatext=''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(5))
	uuid=genUUID()
	c.execute("""INSERT INTO `captcha` (`uuid`, `captcha`) VALUES (%s, %s);""",(uuid, captchatext))
	captchaimage=str(base64.b64encode(image.generate(captchatext).getvalue())).split("'")[1]
	return({'captchaUUID':uuid, 'captchaimage':captchaimage})


