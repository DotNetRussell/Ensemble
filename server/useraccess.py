import common.database_access as database_access
import hashlib
import base64
import crypt

def get_salt():
    return crypt.mksalt(crypt.METHOD_SHA512)

def salt_password(password,salt):
    return hashlib.sha512(base64.b64encode((password + salt).encode("ascii"))).hexdigest()

def admin_user_exists():
    return database_access.admin_user_check()

def log_user_in(username, password):

    if admin_user_exists():
        user = database_access.get_user_by_username(username)

        if not user:
            return 0
        
        test_password_hash = salt_password(password,user["Salt"])
        passwords_match = test_password_hash == user["PasswordHash"]
        return int(passwords_match)
    else:
        salt = get_salt()
        password_hash = salt_password(password, salt)
        database_access.add_admin_user(username, password_hash, salt)
        return 0
    