import hashlib
import os
import time

from util.config import EnvConfig


# ISAS平台签名
def isas_sign():
    token, app_secret = EnvConfig.isas()
    # 获取当前时间戳
    timestamp = str(int(time.time()))
    # 拼接字符串：token + AppSecret + timestamp
    raw_string = token + app_secret + str(timestamp)

    # 使用sha256加密
    hash_object = hashlib.sha256(raw_string.encode('utf-8'))
    sign = hash_object.hexdigest()

    return sign,timestamp


def test_isas_sign():
    token = "kHDWCttQBVRojsfuLpzgbnVGumJmBkhaNxWTTtGjkBykWiuoscKrPBulPVoMZrQj"
    app_secret = ""  # 根据实际情况可能需要填入AppSecret
    result = isas_sign(token, app_secret)
    print("生成的Sign:", result)
