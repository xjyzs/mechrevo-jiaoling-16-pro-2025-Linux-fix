# 修改 ACPI 表通用教程 (DSDT / SSDT 覆盖)

本机固件存在若干 ACPI 层面的 bug, 需要用打过补丁的表覆盖内核加载的固件表。
本文件只讲通用流程, 各表的具体改法见对应文档:

- [修复独显直连时睡眠无法唤醒](修复独显直连时睡眠无法唤醒.md) —— DSDT, `_OSC` 不再交出 `PCIeHotplug`
- [为独显启用D3cold](为独显启用D3cold.md) —— SSDT21 `UPEPRPL`, `\_SB.ACDC.RTAC` 缺失
- [修复睡眠唤醒后无声](修复睡眠唤醒后无声.md) —— SSDT23 `CPMACPV4`, AZAL/ACP 共享电源门控

## 原理
内核启动早期会扫描 initramfs 里的 `kernel/firmware/acpi/*.aml`, 用它们替换固件同名表。
替换成功时会打印:

    ACPI: Table Upgrade: override [SSDT-   AMD-CPMACPV4]

匹配依据是表头里的 **signature / OEM ID / OEM Table ID**, 并且 **新表的版本号必须高于原表**。
否则内核会**静默忽略**整张表 —— 既没有 `Table Upgrade`, 也没有任何报错, 非常容易误判成"补丁无效"。

## 1. 提取并反编译

    mkdir ~/acpi_tables && cd ~/acpi_tables
    sudo cp /sys/firmware/acpi/tables/DSDT .
    sudo cp /sys/firmware/acpi/tables/SSDT* .
    sudo chown $USER DSDT SSDT*
    iasl -da DSDT SSDT*

产出 `*.dsl`。用 `OEM Table ID` 找到目标表(反编译文件头部注释里就有)。

## 2. 版本号必须 +1
版本号在 `DefinitionBlock` 的最后一个参数:

    DefinitionBlock ("", "SSDT", 2, "AMD", "CPMACPV4", 0x00000001)
                                                      ^^^^^^^^^^ 版本号

改成更高的值(`+1` 即可, 如 `0x00000002`)。这一步漏掉, 整个补丁都不会生效。

## 3. 修改
### 方法一: 反编译改 ASL 再编译 (逻辑改动推荐)
改 `*.dsl` 后重新编译:

    iasl -tc SSDT23.dsl

注意: `iasl` 重编译会让表的体积明显变化(本机 DSDT 62124 → 48774 字节), 可能顺带改变其他行为。

### 方法二: 直接改 AML (只动几个字节, 最小改动)
不重新编译, 直接对固件 AML 做字节级修改, 除目标字节外与原表逐字节一致, 不存在重编译引入未知差异的风险。
以把 `Name (PEHP, One)` 改成 `Zero` 为例:

    # patch.py
    src = bytearray(open('DSDT.aml', 'rb').read())
    pat = bytes([0x08, 0x50, 0x45, 0x48, 0x50, 0x01])   # Name(PEHP, One)
    assert src.count(pat) == 1, "模式不唯一, 停下来人工确认"
    src[src.index(pat) + 5] = 0x00                       # One -> Zero
    rev = int.from_bytes(src[24:28], 'little') + 1       # 版本号 +1
    src[24:28] = rev.to_bytes(4, 'little')
    src[9] = 0
    src[9] = (-sum(src)) & 0xFF                          # 重算 ACPI 校验和
    open('DSDT.aml', 'wb').write(bytes(src))

两个关键点: 偏移 `9` 的校验和必须重算, 偏移 `24` 的版本号必须 +1。

## 4. 安装与重新打包
把 `.aml` 放进 initramfs 的 `kernel/firmware/acpi/` 目录(内核只扫这个固定路径), 然后重新生成 initramfs。
建议把改好的 `.aml` 在 `/etc/initcpio/acpi_override/` 里留一份备份。

## 5. 验证

    sudo dmesg | grep "Table Upgrade"
    # 期望出现你改的那张表, 例如:
    # ACPI: Table Upgrade: override [SSDT-   AMD-CPMACPV4]

    sudo dmesg | grep CPMACPV4
    # 期望长度/版本号是新表的, 例如:
    # ACPI: SSDT 0x... 001107 (v02 AMD CPMACPV4 00000002 INTL 20251212)

注意: 覆盖成功后 `/sys/firmware/acpi/tables/` 里的序号可能会变(例如原来叫 `SSDT23` 的表变成 `SSDT22`),
不要按序号去找, 用 `dmesg` 确认。

## 6. 回滚
删掉对应的 `.aml`, 重新生成 initramfs 即可。

## 注意事项
- 一次可以覆盖多张表(DSDT + 多张 SSDT), 每张表都要各自把版本号 +1。
- 改 DSDT 影响面最大(它的 `_OSC` 等会改变内核行为), 能只改 SSDT 就不要动 DSDT。
- 修改前先备份原始 AML, 并对每次改动记录"改了哪个字节/哪段 ASL", 便于回滚。