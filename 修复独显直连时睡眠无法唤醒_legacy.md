# 修复独显直连时睡眠无法唤醒(不推荐)
**不推荐, 有副作用**

**本方法可能使独显在混合输出时无法进入D3cold, 推荐优先尝试[修复独显直连时睡眠无法唤醒.md](修复独显直连时睡眠无法唤醒)**
## 方法一: 直接改 AML (推荐, 只动 4 个字节)
```shell
mkdir ~/acpi_tables && cd ~/acpi_tables
sudo cp /sys/firmware/acpi/tables/DSDT DSDT.aml
sudo chown $USER DSDT.aml
```
```python
src = bytearray(open('DSDT.aml', 'rb').read())
for name in (b'PEHP', b'SHPC'):
    pat = bytes([0x08]) + name                 # Name(<name>, <val>)
    assert src.count(pat) == 1, f"{name} 模式不唯一, 停下来人工确认"
    src[src.index(pat) + 5] = 0x00             # One -> Zero
rev = int.from_bytes(src[24:28], 'little') + 1 # 版本号 +1
src[24:28] = rev.to_bytes(4, 'little')
src[9] = 0
src[9] = (-sum(src)) & 0xFF                    # 重算 ACPI 校验和
open('DSDT.aml', 'wb').write(bytes(src))
```
```shell
python3 patch_dsdt.py
```
改完与固件原表应当只差 4 个字节(偏移 9 校验和、偏移 24 版本号、`PEHP` 与 `SHPC` 的值字节)。

## 方法二: 反编译改 ASL 再编译
```shell
mkdir ~/acpi_tables && cd ~/acpi_tables
sudo cp /sys/firmware/acpi/tables/DSDT .
iasl -d DSDT
```
把
```
DefinitionBlock ("", "DSDT", 2, "ALASKA", "A M I ", 0x01072009)
    ...
    Name (PEHP, One)
    Name (SHPC, One)
```
改为(版本号必须 +1)
```
DefinitionBlock ("", "DSDT", 2, "ALASKA", "A M I ", 0x0107200A)
    ...
    Name (PEHP, Zero)
    Name (SHPC, Zero)
```
```shell
iasl -tc DSDT.dsl
```
注意: `iasl` 重编译后表的体积会明显变化, 可能顺带改变其他行为
(实测会额外丢掉 `LTR` 和 `DPC` 两项控制权)。追求最小改动请用方法一。

## 安装与重新打包
以 Limine 为例:
```shell
sudo cp DSDT.aml /etc/initcpio/acpi_override/DSDT.aml
sudo limine-mkinitcpio
```

## 验证
```shell
sudo dmesg | grep "Table Upgrade"
# 期望: ACPI: Table Upgrade: override [DSDT-ALASKA-  A M I ]

sudo dmesg | grep "_OSC"
# 期望: _OSC: OS now controls [PME AER PCIeCapability LTR DPC]
#       对比修复前少了 PCIeHotplug 与 SHPCHotplug

ls /sys/bus/pci/slots/
# 期望: 空 —— 没有任何热插拔驱动接管该端口
```
之后 `systemctl suspend` 应当能正常唤醒, 且**关机 / 重启也应当正常**。

## 回滚
```shell
sudo rm /etc/initcpio/acpi_override/DSDT.aml
sudo limine-mkinitcpio
```