#!/usr/bin/env python3
"""
生产环境邮件连接测试脚本
用于诊断邮件服务器连接问题
"""

import os
import sys
import socket
import smtplib
import ssl
import time
from datetime import datetime

def print_section(title):
    """打印分隔标题"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def test_dns_resolution(host):
    """测试DNS解析"""
    print_section("🔍 DNS解析测试")
    try:
        print(f"🔄 解析域名: {host}")
        ip = socket.gethostbyname(host)
        print(f"✅ DNS解析成功: {host} -> {ip}")
        return ip
    except socket.gaierror as e:
        print(f"❌ DNS解析失败: {e}")
        return None

def test_port_connectivity(host, port, timeout=10):
    """测试端口连接性"""
    print_section(f"🔌 端口连接测试 {host}:{port}")
    try:
        print(f"🔄 尝试连接 {host}:{port} (超时: {timeout}秒)...")
        start_time = time.time()
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        end_time = time.time()
        
        if result == 0:
            print(f"✅ 端口连接成功! 耗时: {end_time - start_time:.2f}秒")
            sock.close()
            return True
        else:
            print(f"❌ 端口连接失败，错误码: {result}")
            sock.close()
            return False
            
    except socket.timeout:
        print(f"❌ 连接超时 ({timeout}秒)")
        return False
    except Exception as e:
        print(f"❌ 连接异常: {e}")
        return False

def test_smtp_connection_detailed(host, port, username, password, use_ssl=True):
    """详细的SMTP连接测试"""
    print_section("📧 详细SMTP连接测试")
    
    try:
        print(f"🔄 开始SMTP连接测试...")
        print(f"  服务器: {host}:{port}")
        print(f"  用户名: {username}")
        print(f"  使用SSL: {use_ssl}")
        print(f"  时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        start_time = time.time()
        
        if use_ssl:
            print("🔄 创建SMTP_SSL连接...")
            server = smtplib.SMTP_SSL(host, port, timeout=30)
        else:
            print("🔄 创建SMTP连接...")
            server = smtplib.SMTP(host, port, timeout=30)
        
        print("✅ SMTP连接创建成功")
        
        # 启用调试
        server.set_debuglevel(1)
        
        print("🔄 发送EHLO命令...")
        server.ehlo()
        print("✅ EHLO命令成功")
        
        print("🔄 尝试登录...")
        server.login(username, password)
        print("✅ 登录成功")
        
        end_time = time.time()
        print(f"✅ 完整SMTP测试成功! 总耗时: {end_time - start_time:.2f}秒")
        
        server.quit()
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ 认证失败: {e}")
        return False
    except smtplib.SMTPConnectError as e:
        print(f"❌ 连接失败: {e}")
        return False
    except smtplib.SMTPException as e:
        print(f"❌ SMTP错误: {e}")
        return False
    except socket.timeout as e:
        print(f"❌ 连接超时: {e}")
        return False
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        print(f"错误类型: {type(e).__name__}")
        return False

def test_fastapi_mail_connection(host, port, username, password):
    """测试FastAPI-Mail连接"""
    print_section("🚀 FastAPI-Mail连接测试")
    
    try:
        # 尝试导入fastapi-mail
        from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
        
        print("✅ fastapi-mail模块导入成功")
        
        # 创建配置
        conf = ConnectionConfig(
            MAIL_USERNAME=username,
            MAIL_PASSWORD=password,
            MAIL_FROM=username,
            MAIL_PORT=port,
            MAIL_SERVER=host,
            MAIL_FROM_NAME="WorkLog Pro",
            MAIL_STARTTLS=False,
            MAIL_SSL_TLS=True,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True
        )
        
        print("✅ ConnectionConfig创建成功")
        print(f"配置详情: {conf}")
        
        # 创建FastMail实例
        fm = FastMail(conf)
        print("✅ FastMail实例创建成功")
        
        return True
        
    except ImportError as e:
        print(f"❌ 无法导入fastapi-mail: {e}")
        return False
    except Exception as e:
        print(f"❌ FastAPI-Mail测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🔧 生产环境邮件连接诊断工具")
    print("=" * 60)
    
    # 从环境变量获取配置
    smtp_host = os.getenv("SMTP_HOST", "smtp.163.com")
    smtp_port = int(os.getenv("SMTP_PORT", "465"))
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_password = os.getenv("SMTP_PASSWORD", "")
    
    print(f"📧 当前邮件配置:")
    print(f"  SMTP_HOST: {smtp_host}")
    print(f"  SMTP_PORT: {smtp_port}")
    print(f"  SMTP_USER: {smtp_user}")
    print(f"  SMTP_PASSWORD: {'*' * len(smtp_password) if smtp_password else 'None'}")
    
    if not smtp_user or not smtp_password:
        print("❌ 邮件配置不完整，请检查环境变量")
        return 1
    
    # 1. DNS解析测试
    ip = test_dns_resolution(smtp_host)
    if not ip:
        print("❌ DNS解析失败，无法继续测试")
        return 1
    
    # 2. 端口连接测试
    if not test_port_connectivity(smtp_host, smtp_port):
        print("❌ 端口连接失败，可能是防火墙或网络问题")
        return 1
    
    # 3. 详细SMTP测试
    if not test_smtp_connection_detailed(smtp_host, smtp_port, smtp_user, smtp_password):
        print("❌ SMTP连接测试失败")
        return 1
    
    # 4. FastAPI-Mail测试
    if not test_fastapi_mail_connection(smtp_host, smtp_port, smtp_user, smtp_password):
        print("❌ FastAPI-Mail测试失败")
        return 1
    
    print_section("✅ 所有测试通过")
    print("邮件服务器连接正常，FastAPI-Mail配置正确")
    print("如果应用仍然无法发送邮件，请检查应用日志中的具体错误信息")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
