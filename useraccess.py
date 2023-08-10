import database_access
import hashlib, uuid
import base64
import crypt

def get_salt():
    return crypt.mksalt(crypt.METHOD_SHA512)

def salt_password(password,salt):
    return hashlib.sha512(base64.b64encode((password + salt).encode("ascii"))).hexdigest()

def admin_user_exists():
    return database_access.admin_user_check() 

def log_user_in(username, password):

    if(admin_user_exists()):

        user = database_access.get_user_by_username(username)
        
        if(user == None):
            return 0
        else:
            testPasswordHash = salt_password(password,user["Salt"])
            passwordsMatch = testPasswordHash == user["PasswordHash"]
            if(passwordsMatch == True):
                return 1
            else:
                return 0
    else:
        salt = get_salt()
        passwordHashed = salt_password(password,salt)
        database_access.add_admin_user(username,passwordHashed,salt)
        return 0