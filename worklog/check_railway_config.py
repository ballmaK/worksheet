#!/usr/bin/env python3
"""
Railway配置文件检查脚本
检查railway.toml、railway.json、nixpacks.toml等配置文件
"""

import os
import sys
import json
from pathlib import Path

# 尝试导入toml，如果失败则跳过toml相关检查
try:
    import toml
    TOML_AVAILABLE = True
except ImportError:
    TOML_AVAILABLE = False
    print("⚠️  toml模块未安装，将跳过toml配置文件检查")

def print_section(title):
    """打印分隔标题"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def check_railway_toml():
    """检查railway.toml配置文件"""
    print_section("Railway.toml配置检查")
    
    if not TOML_AVAILABLE:
        print("❌ toml模块未安装，无法检查railway.toml")
        return False
    
    config_file = Path("railway.toml")
    if not config_file.exists():
        print("❌ railway.toml 文件不存在")
        return False
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = toml.load(f)
        
        print("✅ railway.toml 文件存在且格式正确")
        
        # 检查build配置
        if 'build' in config:
            print("📋 Build配置:")
            build_config = config['build']
            if 'builder' in build_config:
                print(f"  ✅ Builder: {build_config['builder']}")
            else:
                print("  ❌ Builder: 未设置")
        
        # 检查deploy配置
        if 'deploy' in config:
            print("📋 Deploy配置:")
            deploy_config = config['deploy']
            
            # 检查启动命令
            if 'startCommand' in deploy_config:
                print(f"  ✅ 启动命令: {deploy_config['startCommand']}")
            else:
                print("  ❌ 启动命令: 未设置")
            
            # 检查健康检查
            if 'healthcheckPath' in deploy_config:
                print(f"  ✅ 健康检查路径: {deploy_config['healthcheckPath']}")
            else:
                print("  ❌ 健康检查路径: 未设置")
            
            if 'healthcheckTimeout' in deploy_config:
                print(f"  ✅ 健康检查超时: {deploy_config['healthcheckTimeout']}秒")
            else:
                print("  ❌ 健康检查超时: 未设置")
            
            # 检查重启策略
            if 'restartPolicyType' in deploy_config:
                print(f"  ✅ 重启策略类型: {deploy_config['restartPolicyType']}")
            else:
                print("  ❌ 重启策略类型: 未设置")
            
            if 'restartPolicyMaxRetries' in deploy_config:
                print(f"  ✅ 最大重试次数: {deploy_config['restartPolicyMaxRetries']}")
            else:
                print("  ❌ 最大重试次数: 未设置")
        
        # 检查环境变量
        if 'deploy' in config and 'variables' in config['deploy']:
            print("📋 全局环境变量:")
            variables = config['deploy']['variables']
            for key, value in variables.items():
                print(f"  ✅ {key}: {value}")
        
        # 检查生产环境配置
        if 'deploy' in config and 'environments' in config['deploy']:
            if 'production' in config['deploy']['environments']:
                print("📋 生产环境配置:")
                prod_config = config['deploy']['environments']['production']
                
                if 'startCommand' in prod_config:
                    print(f"  ✅ 生产环境启动命令: {prod_config['startCommand']}")
                
                if 'variables' in prod_config:
                    print("  📋 生产环境变量:")
                    for key, value in prod_config['variables'].items():
                        print(f"    ✅ {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ 读取railway.toml失败: {e}")
        return False

def check_railway_json():
    """检查railway.json配置文件"""
    print_section("Railway.json配置检查")
    
    config_file = Path("railway.json")
    if not config_file.exists():
        print("❌ railway.json 文件不存在")
        return False
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print("✅ railway.json 文件存在且格式正确")
        
        # 检查build配置
        if 'build' in config:
            print("📋 Build配置:")
            build_config = config['build']
            if 'builder' in build_config:
                print(f"  ✅ Builder: {build_config['builder']}")
        
        # 检查deploy配置
        if 'deploy' in config:
            print("📋 Deploy配置:")
            deploy_config = config['deploy']
            
            if 'startCommand' in deploy_config:
                print(f"  ✅ 启动命令: {deploy_config['startCommand']}")
            
            if 'healthcheckPath' in deploy_config:
                print(f"  ✅ 健康检查路径: {deploy_config['healthcheckPath']}")
            
            if 'healthcheckTimeout' in deploy_config:
                print(f"  ✅ 健康检查超时: {deploy_config['healthcheckTimeout']}秒")
        
        # 检查环境配置
        if 'environments' in config:
            print("📋 环境配置:")
            for env_name, env_config in config['environments'].items():
                print(f"  📋 {env_name}环境:")
                if 'variables' in env_config:
                    for key, value in env_config['variables'].items():
                        print(f"    ✅ {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ 读取railway.json失败: {e}")
        return False

def check_nixpacks_toml():
    """检查nixpacks.toml配置文件"""
    print_section("Nixpacks.toml配置检查")
    
    if not TOML_AVAILABLE:
        print("❌ toml模块未安装，无法检查nixpacks.toml")
        return False
    
    config_file = Path("nixpacks.toml")
    if not config_file.exists():
        print("❌ nixpacks.toml 文件不存在")
        return False
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = toml.load(f)
        
        print("✅ nixpacks.toml 文件存在且格式正确")
        
        # 检查phases配置
        if 'phases' in config:
            print("📋 Phases配置:")
            phases = config['phases']
            
            if 'setup' in phases:
                setup = phases['setup']
                if 'nixPkgs' in setup:
                    print(f"  ✅ Nix包: {setup['nixPkgs']}")
                if 'aptPkgs' in setup:
                    print(f"  ✅ Apt包: {setup['aptPkgs']}")
            
            if 'install' in phases:
                install = phases['install']
                if 'cmds' in install:
                    print(f"  ✅ 安装命令: {install['cmds']}")
            
            if 'build' in phases:
                build = phases['build']
                if 'cmds' in build:
                    print(f"  ✅ 构建命令: {build['cmds']}")
        
        # 检查start配置
        if 'start' in config:
            print("📋 Start配置:")
            start_config = config['start']
            if 'cmd' in start_config:
                print(f"  ✅ 启动命令: {start_config['cmd']}")
        
        # 检查variables配置
        if 'variables' in config:
            print("📋 变量配置:")
            variables = config['variables']
            for key, value in variables.items():
                print(f"  ✅ {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ 读取nixpacks.toml失败: {e}")
        return False

def check_package_json():
    """检查package.json配置文件"""
    print_section("Package.json配置检查")
    
    config_file = Path("package.json")
    if not config_file.exists():
        print("❌ package.json 文件不存在")
        return False
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print("✅ package.json 文件存在且格式正确")
        
        # 检查基本信息
        if 'name' in config:
            print(f"📋 项目名称: {config['name']}")
        if 'version' in config:
            print(f"📋 版本: {config['version']}")
        if 'main' in config:
            print(f"📋 主文件: {config['main']}")
        
        # 检查scripts配置
        if 'scripts' in config:
            print("📋 Scripts配置:")
            scripts = config['scripts']
            for script_name, script_cmd in scripts.items():
                print(f"  ✅ {script_name}: {script_cmd}")
        
        # 检查engines配置
        if 'engines' in config:
            print("📋 Engines配置:")
            engines = config['engines']
            for engine_name, engine_version in engines.items():
                print(f"  ✅ {engine_name}: {engine_version}")
        
        return True
        
    except Exception as e:
        print(f"❌ 读取package.json失败: {e}")
        return False

def check_config_consistency():
    """检查配置文件一致性"""
    print_section("配置文件一致性检查")
    
    start_commands = []
    
    # 收集所有启动命令
    if Path("railway.toml").exists() and TOML_AVAILABLE:
        try:
            with open("railway.toml", 'r', encoding='utf-8') as f:
                config = toml.load(f)
                if 'deploy' in config and 'startCommand' in config['deploy']:
                    start_commands.append(("railway.toml", config['deploy']['startCommand']))
        except:
            pass
    
    if Path("railway.json").exists():
        try:
            with open("railway.json", 'r', encoding='utf-8') as f:
                config = json.load(f)
                if 'deploy' in config and 'startCommand' in config['deploy']:
                    start_commands.append(("railway.json", config['deploy']['startCommand']))
        except:
            pass
    
    if Path("nixpacks.toml").exists() and TOML_AVAILABLE:
        try:
            with open("nixpacks.toml", 'r', encoding='utf-8') as f:
                config = toml.load(f)
                if 'start' in config and 'cmd' in config['start']:
                    start_commands.append(("nixpacks.toml", config['start']['cmd']))
        except:
            pass
    
    if Path("package.json").exists():
        try:
            with open("package.json", 'r', encoding='utf-8') as f:
                config = json.load(f)
                if 'scripts' in config and 'start' in config['scripts']:
                    start_commands.append(("package.json", config['scripts']['start']))
        except:
            pass
    
    if start_commands:
        print("📋 启动命令检查:")
        for file_name, command in start_commands:
            print(f"  📄 {file_name}: {command}")
        
        # 检查是否一致
        commands = [cmd for _, cmd in start_commands]
        if len(set(commands)) == 1:
            print("  ✅ 所有配置文件中的启动命令一致")
        else:
            print("  ⚠️  配置文件中的启动命令不一致")
            print("  🔧 建议统一启动命令")
    else:
        print("  ❌ 未找到启动命令配置")

def main():
    """主函数"""
    print("🚀 Railway配置文件检查工具")
    print("=" * 60)
    
    # 检查各种配置文件
    railway_toml_ok = check_railway_toml()
    railway_json_ok = check_railway_json()
    nixpacks_toml_ok = check_nixpacks_toml()
    package_json_ok = check_package_json()
    
    # 检查配置一致性
    check_config_consistency()
    
    # 总结
    print_section("检查总结")
    
    config_files = [
        ("railway.toml", railway_toml_ok),
        ("railway.json", railway_json_ok),
        ("nixpacks.toml", nixpacks_toml_ok),
        ("package.json", package_json_ok)
    ]
    
    print("📋 配置文件状态:")
    for file_name, status in config_files:
        if status:
            print(f"  ✅ {file_name}: 正常")
        else:
            print(f"  ❌ {file_name}: 有问题")
    
    # 建议
    print("\n📋 建议:")
    if railway_toml_ok:
        print("1. railway.toml 配置正确，Railway将使用此配置")
    elif railway_json_ok:
        print("1. railway.json 配置正确，但建议迁移到 railway.toml")
    else:
        print("1. 建议创建 railway.toml 配置文件")
    
    print("2. 确保启动命令在所有配置文件中一致")
    print("3. 检查环境变量配置是否正确")
    print("4. 验证健康检查路径和超时设置")

if __name__ == "__main__":
    main()
