#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess

# 提权
def is_admin():
    try:
        return os.geteuid() == 0
    except AttributeError:
        return False

if not is_admin():
    print("正在请求 root 权限...")
    try:
        os.execvp('pkexec', ['pkexec', sys.executable] + sys.argv)
    except Exception as e:
        print(f"无法自动提权，请手动使用 'sudo python3 {sys.argv[0]}' 运行。错误: {e}")
        sys.exit(1)

efivar_dir = "/sys/firmware/efi/efivars"
if not os.path.isdir(efivar_dir):
    print(f"错误: 找不到 efivarfs 路径 '{efivar_dir}'。")
    print("请确保系统是以 UEFI 模式启动，并且内核支持并挂载了 efivarfs。")
    sys.exit(1)

var_name = "OemMagicVariable"
# Linux 下 GUID 格式：小写，不带花括号 {}
guid = "9f33f85c-13ca-4fd1-9c4a-96217722c593"
filename = f"{var_name}-{guid}"
filepath = os.path.join(efivar_dir, filename)

# 区别: 10**1**0000000000871ff11400fffff
payload = bytes.fromhex("051d546000001a010001000000010affffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff02ffffff0000000000000000000000000000000018000000000000000000000000000000000000000000000000000100000001010000000000871ff11400ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff")

if len(payload) != 180:
    print("警告：Payload 长度不是 180 字节！")
    sys.exit(1)

# 构造写入数据
# Linux 的 efivarfs 要求写入文件的【前 4 个字节】必须是 UEFI 属性（32位无符号小端整数）
# 0x00000007 代表：
#   - EFI_VARIABLE_NON_VOLATILE (0x1)      (不挥发)
#   - EFI_VARIABLE_BOOTSERVICE_ACCESS (0x2) (启动服务可访问)
#   - EFI_VARIABLE_RUNTIME_ACCESS (0x4)     (运行时可访问)
attributes = b"\x07\x00\x00\x00"
full_data = attributes + payload

# 执行写入
try:
    # 如果该变量文件已存在，Linux 内核可能默认将其设为“不可修改”属性（immutable）以防误删。
    # 写入前我们需要先尝试清除该属性。
    if os.path.exists(filepath):
        try:
            subprocess.run(["chattr", "-i", filepath], capture_output=True)
        except FileNotFoundError:
            pass # 部分精简系统可能没有 chattr 命令，忽略即可

    # 直接向对应的 efivars 文件写入二进制数据
    with open(filepath, "wb") as f:
        f.write(full_data)
    print("设置成功！")

except PermissionError:
    print(f"设置失败！权限不足，或系统文件处于只读状态。")
    print(f"你可以尝试手动运行命令解锁：sudo chattr -i {filepath}")
except Exception as e:
    print(f"设置失败！错误信息: {e}")
