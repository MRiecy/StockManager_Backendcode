#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
XtQuant 环境诊断工具
用于检查迅投交易终端的运行状态和安装情况
"""

import os
import sys
import time
import subprocess
import psutil
import winreg

def check_process_running(process_name_contains):
    """
    检查包含特定名称的进程是否在运行
    """
    running_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
        try:
            if process_name_contains.lower() in proc.info['name'].lower():
                running_processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'exe': proc.info.get('exe', 'Unknown'),
                    'cmdline': ' '.join(proc.info.get('cmdline', [])) if proc.info.get('cmdline') else 'Unknown'
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return running_processes

def find_xtquant_registry_entries():
    """
    从注册表中查找迅投相关的安装信息
    """
    registry_entries = []
    
    try:
        # 查找安装目录信息
        registry_keys = [
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
            r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
        ]
        
        for key_path in registry_keys:
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                    subkey_count = winreg.QueryInfoKey(key)[0]
                    
                    for i in range(subkey_count):
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            with winreg.OpenKey(key, subkey_name) as subkey:
                                try:
                                    display_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                                    # 查找包含"迅投"或"XtQuant"的程序
                                    if "迅投" in display_name or "xtquant" in display_name.lower():
                                        install_location = winreg.QueryValueEx(subkey, "InstallLocation")[0]
                                        registry_entries.append({
                                            'display_name': display_name,
                                            'install_location': install_location,
                                            'registry_path': f"{key_path}\\{subkey_name}"
                                        })
                                except:
                                    pass
                        except:
                            pass
            except:
                pass
    except Exception as e:
        print(f"读取注册表时出错: {e}")
    
    return registry_entries

def check_common_install_paths():
    """
    检查常见的迅投安装路径
    """
    common_paths = [
        r"C:\迅投极速交易终端 睿智融科版",
        r"D:\迅投极速交易终端 睿智融科版",
        r"E:\迅投极速交易终端 睿智融科版",
        r"F:\迅投极速交易终端 睿智融科版",
        r"G:\迅投极速交易终端 睿智融科版",
        r"C:\迅投极速交易终端",
        r"D:\迅投极速交易终端",
        r"E:\迅投极速交易终端",
        r"F:\迅投极速交易终端",
        r"G:\迅投极速交易终端",
        r"C:\迅投极速交易终端睿智融科版",
        r"D:\迅投极速交易终端睿智融科版",
        r"E:\迅投极速交易终端睿智融科版",
        r"F:\迅投极速交易终端睿智融科版",
        r"G:\迅投极速交易终端睿智融科版",
    ]
    
    existing_paths = []
    for path in common_paths:
        if os.path.exists(path):
            userdata_path = os.path.join(path, "userdata")
            userdata_exists = os.path.exists(userdata_path)
            
            existing_paths.append({
                'path': path,
                'exists': True,
                'userdata_path': userdata_path,
                'userdata_exists': userdata_exists,
                'userdata_readable': os.access(userdata_path, os.R_OK) if userdata_exists else False,
                'userdata_writable': os.access(userdata_path, os.W_OK) if userdata_exists else False,
            })
    
    return existing_paths

def check_xtquant_library():
    """
    检查 xtquant 库是否正确安装
    """
    try:
        import xtquant
        return {
            'installed': True,
            'version': getattr(xtquant, '__version__', 'Unknown'),
            'path': getattr(xtquant, '__file__', 'Unknown')
        }
    except ImportError:
        return {
            'installed': False,
            'error': 'xtquant 库未安装，请使用 pip install xtquant 安装'
        }
    except Exception as e:
        return {
            'installed': False,
            'error': f'导入 xtquant 时出错: {e}'
        }

def main():
    """
    主函数，运行所有检查并输出结果
    """
    print("="*80)
    print(" 迅投 (XtQuant) 环境诊断工具 ")
    print("="*80)
    
    print("\n1. 检查迅投进程...\n")
    processes = check_process_running("迅投")
    
    if processes:
        print(f"找到 {len(processes)} 个迅投相关进程:")
        for proc in processes:
            print(f"  - PID: {proc['pid']}, 名称: {proc['name']}")
            print(f"    可执行文件: {proc['exe']}")
            print(f"    命令行: {proc['cmdline']}")
    else:
        print("❌ 未找到任何迅投相关进程。请确保迅投交易终端已启动并登录。")
    
    print("\n2. 检查迅投安装注册表信息...\n")
    registry_entries = find_xtquant_registry_entries()
    
    if registry_entries:
        print(f"找到 {len(registry_entries)} 条迅投相关注册表记录:")
        for entry in registry_entries:
            print(f"  - 名称: {entry['display_name']}")
            print(f"    安装位置: {entry['install_location']}")
            print(f"    注册表路径: {entry['registry_path']}")
    else:
        print("❌ 未找到迅投相关注册表记录。")
    
    print("\n3. 检查常见安装路径...\n")
    install_paths = check_common_install_paths()
    
    if install_paths:
        print(f"找到 {len(install_paths)} 个可能的迅投安装路径:")
        for path_info in install_paths:
            print(f"  - 路径: {path_info['path']}")
            print(f"    userdata: {path_info['userdata_path']}")
            print(f"    userdata存在: {'✓' if path_info['userdata_exists'] else '❌'}")
            if path_info['userdata_exists']:
                print(f"    userdata可读: {'✓' if path_info['userdata_readable'] else '❌'}")
                print(f"    userdata可写: {'✓' if path_info['userdata_writable'] else '❌'}")
    else:
        print("❌ 未找到任何常见迅投安装路径。")
    
    print("\n4. 检查xtquant Python库...\n")
    library_info = check_xtquant_library()
    
    if library_info.get('installed'):
        print(f"✓ xtquant库已安装")
        print(f"  - 版本: {library_info['version']}")
        print(f"  - 路径: {library_info['path']}")
    else:
        print(f"❌ {library_info['error']}")
    
    print("\n"+"="*80)
    print(" 诊断完成 ")
    print("="*80)
    
    # 如果找到了安装路径但没有运行进程，给出建议
    if install_paths and not processes:
        print("\n⚠️ 建议:")
        print("  迅投软件已安装但未运行。请手动启动迅投交易终端并登录。")
        
        # 显示可能的可执行文件路径
        for path_info in install_paths:
            exe_path = os.path.join(path_info['path'], "xtthbss.exe")
            if os.path.exists(exe_path):
                print(f"  您可以尝试运行: {exe_path}")
    
    # 如果找到了userdata目录，建议更新settings.py
    if install_paths:
        valid_userdata_paths = [p['userdata_path'] for p in install_paths if p['userdata_exists'] and p['userdata_readable']]
        if valid_userdata_paths:
            print("\n⚠️ 配置建议:")
            print("  更新Django settings.py中的XT_CONFIG['USERDATA_PATH']为以下值:")
            for path in valid_userdata_paths:
                print(f"  r'{path}'")

if __name__ == "__main__":
    main() 