from NekoBlog.NekoPack import NekoRedis
from jwt import jwk_from_pem, jwt

with open(r'NekoBlog/keys/rsa_private_key.pem', 'rb') as fh:
    rsa_private_key = jwk_from_pem(fh.read())
with open(r'NekoBlog/keys/rsa_public_key.pem', 'rb') as fh:
    rsa_public_key = jwk_from_pem(fh.read())


def gen_jwt(message: dict, token_type='access'):
    r = NekoRedis.Redis()
    instance = jwt.JWT()
    key = instance.encode(message, rsa_private_key, alg='RS256')
    r.set(f'token:{key}:uuid', message['info']['uuid'], message['exp'])
    r.set(f'token:{key}:type', token_type, message['exp'])
    return key


def dec_jwt(key: str):
    try:
        jwt_key = jwt.JWT().decode(key, rsa_public_key)
        return jwt_key
    except Exception as e:
        print(e)
        return False


def del_jwt(key: str):
    NekoRedis.Redis().delete(key)
