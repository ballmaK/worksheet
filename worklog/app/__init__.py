# 修复 fastapi-mail 与 pydantic v2 的兼容性问题
# 必须在任何导入 fastapi_mail 之前执行
import pydantic
from pydantic import SecretStr
# 将 SecretStr 添加到 pydantic 模块的命名空间（fastapi_mail 需要）
if not hasattr(pydantic, 'SecretStr'):
    pydantic.SecretStr = SecretStr
