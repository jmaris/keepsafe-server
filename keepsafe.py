import pymysql,captcha,base64,random,string, uuid, datetime
from io import BytesIO
from captcha.image import ImageCaptcha
from passlib.hash import pbkdf2_sha256
image = ImageCaptcha()

# Connects directly to the MySQL database
try:
	db=pymysql.connect("localhost","keepsafe","testingkeepsafe","keepsafe", autocommit=True)
	c=db.cursor()
except:
	print("Error : Connection to the Database Failed")

# Base Functions
def hash(password):
	return pbkdf2_sha256.hash(password)

def genUUID():
	return uuid.uuid4().hex

def checkHash(password, hash):
	return pbkdf2_sha256.verify(password, hash)

def checkPassword(username, password):
	c.execute("""SELECT user_pwhash FROM users WHERE user_name = %s;""", (username,))
	return checkHash(password, c.fetchone()[0])

def addAccount(username, password, privatekey=''):
	user_name=str(username)
	pwhash=str(hash(password))
	c.execute("""INSERT INTO `users` (`user_name`, `user_pwhash`, `user_privatekey`) VALUES (%s, %s, %s);""",(username, pwhash, privatekey))
	c.execute("""SELECT `user_id` FROM `users` WHERE `user_name` = %s;""",(username))
	user_id=c.fetchone()[0]
	c.execute("""INSERT INTO `vaults` (`user_ID`) VALUES (%s);""",(user_id))
	
def deleteAccount(username):
	c.execute("""DELETE from `users` WHERE `user_name` = %s;""", (username,))

def generateCaptcha():
	captchatext=''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(5))
	uuid=genUUID()
	c.execute("""INSERT INTO `captcha` (`uuid`, `captcha`) VALUES (%s, %s);""",(uuid, captchatext))
	captchaimage=str(base64.b64encode(image.generate(captchatext).getvalue())).split("'")[1]
	return({'uuid':uuid, 'captchaimage':captchaimage})

def testCaptcha(uuid, captchaguess):
	try:
		c.execute("""SELECT `captcha`,`added` FROM `captcha` WHERE `uuid` = %s;""",(uuid))
		print(c.fetchone())
	except:
		print("Error : Captcha not found")
	if str(c.fetchone()[0])==captchaguess:
	# ADD CHECK FOR TIME 
		return {"success":true}
	else:
		return {"success":false,"error":1}

# User Interaction functions.
def user_deleteAccount(username, password):
	if checkPassword(username, password):
		try:
			deleteAccount(username)
		except:
			return [false, "Error : Could not delete account, account does not exist"]
	else:
		return [false, "Error : Could not delete account, incorrect password"]
