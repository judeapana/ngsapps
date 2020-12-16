LOGIN_NOTIFY = """
<!DOCTYPE html>
<html>
<head>
	<title></title>
</head>
<body>
    <h3>Hi {name},</h3>
    <p>This email address was used to access the your {app_name} dashboard :</p>
    <p>------------------------------------------</p>
    <p>Email Address: {email}</p>
    <p>time: {time}</p>
    <p>IP address: {ip}</p>
    <p>browser:{user_agent}</p>
    <p>------------------------------------------</p>
    <p>If this was you, you can ignore this alert. If you suspect any suspicious activity on your account kindly change your password.</p>
</body>
</html>
"""

FORGOT_PWD = """
<!DOCTYPE html>
<html>
<head>
	<title></title>
</head>
<body>
	<h3>Hi, {name}</h3>
<p>You requested to change your password, click on this link to begin the process: <a href='{url}'>CLICK HERE</a></p>
</body>
</html>
"""
CONFIRM_ACC = """
<!DOCTYPE html>
<html>
<head>
	<title></title>
</head>
<body>
<h3>Hi, {name},</h3>
<p>Your account activation link <a href='{url}'> Click here</a>
</p>
</body>
</html>
"""
