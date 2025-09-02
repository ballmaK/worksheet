#!/usr/bin/env python3
"""
修复Vue文件中computed导入问题的脚本
"""

import os
import re
from pathlib import Path

def check_vue_file(file_path):
    """检查Vue文件中的computed导入问题"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否使用了computed
        if 'computed(' in content:
            # 检查是否已经导入了computed
            if 'import { computed }' in content or 'import { computed,' in content:
                return f"✅ {file_path.name}: computed已正确导入"
            else:
                # 检查是否有其他Vue导入
                vue_import_match = re.search(r'import\s*\{([^}]+)\}\s*from\s*[\'"]vue[\'"]', content)
                if vue_import_match:
                    imports = vue_import_match.group(1)
                    # 在现有导入中添加computed
                    new_imports = imports + ', computed'
                    new_content = content.replace(
                        f'import {{{imports}}} from \'vue\'',
                        f'import {{{new_imports}}} from \'vue\''
                    )
                    
                    # 写回文件
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    return f"🔧 {file_path.name}: 已添加computed导入"
                else:
                    # 没有Vue导入，需要添加
                    script_start = content.find('<script')
                    if script_start != -1:
                        script_tag_end = content.find('>', script_start)
                        if script_tag_end != -1:
                            new_import = 'import { computed } from \'vue\'\n'
                            new_content = content[:script_tag_end+1] + '\n' + new_import + content[script_tag_end+1:]
                            
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(new_content)
                            
                            return f"🔧 {file_path.name}: 已添加computed导入"
                    
                    return f"⚠️  {file_path.name}: 需要手动添加computed导入"
        
        return f"⏭️  {file_path.name}: 未使用computed"
        
    except Exception as e:
        return f"❌ {file_path.name}: 处理失败 - {e}"

def main():
    """主函数"""
    print("🔍 检查Vue文件中的computed导入问题")
    print("=" * 60)
    
    # 查找所有Vue文件
    vue_files = []
    src_dir = Path('src')
    
    for file_path in src_dir.rglob('*.vue'):
        vue_files.append(file_path)
    
    print(f"找到 {len(vue_files)} 个Vue文件")
    print()
    
    # 检查每个文件
    results = []
    for file_path in vue_files:
        result = check_vue_file(file_path)
        results.append(result)
        print(result)
    
    print()
    print("📊 检查结果总结:")
    fixed_count = len([r for r in results if '🔧' in r])
    already_ok_count = len([r for r in results if '✅' in r])
    skipped_count = len([r for r in results if '⏭️' in r])
    warning_count = len([r for r in results if '⚠️' in r])
    error_count = len([r for r in results if '❌' in r])
    
    print(f"✅ 已正确导入: {already_ok_count}")
    print(f"🔧 已修复: {fixed_count}")
    print(f"⏭️  跳过: {skipped_count}")
    print(f"⚠️  需要手动处理: {warning_count}")
    print(f"❌ 处理失败: {error_count}")
    
    if warning_count > 0:
        print("\n⚠️  以下文件需要手动检查:")
        for result in results:
            if '⚠️' in result:
                print(f"  {result}")

if __name__ == "__main__":
    main()
