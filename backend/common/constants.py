LOGIN_NOTIFY = """
<h3>Hi {name},</h3>
<p>This email address was used to access the your {app_name} dashboard :</p>
<p>------------------------------------------</p>
<p>Email Address: {email}</p>
<p>Time: {time}</p>
<p>IP address: {ip}</p>
<p>Browser :{user_agent}</p>
<p>------------------------------------------</p>
<p>If this was you, you can ignore this alert. If you suspect any suspicious activity on your account kindly change your password.</p>
"""

FORGOT_PWD = """
<h3>Hi, {name}</h3>
<p>You requested to change your password, click on this link to begin the process: <a href='{url}'>CLICK HERE</a></p>
"""
CONFIRM_ACC = """
<h3>Hi {name},</h3>
<p>Your account activation link <a href='{url}'> Click here</a></p>
"""

CHANGE_EMAIL = """
<h3>Hi {name},</h3>
<p>You request to change your email, please use this link to change your mail <a href="{url}">Change Your Email</a></p>
"""

NEW_ACC = """
<p>Your Account has been created.</p>
<p>Your Username is : {username}.</p> 
<p>Your Password is : {password}.</p> 
<h4>Welcome To Ngsapps.
"""
