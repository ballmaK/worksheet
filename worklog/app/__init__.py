# 修复 fastapi-mail 与 pydantic v2 的兼容性问题（fastapi_mail.config 使用 SecretStr 但未 import）
import builtins
import pydantic
from pydantic import SecretStr
if not hasattr(pydantic, "SecretStr"):
    pydantic.SecretStr = SecretStr
builtins.SecretStr = SecretStr
