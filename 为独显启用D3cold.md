# 修复独显只能 D3hot 的 bug (不用独显时降低大约十几W的整机功耗)
# 查看独显状态
`cat /sys/bus/pci/devices/0000:01:00.0/power_state`
# 提取 SSDT
## 复制
`mkdir ~/acpi_tables && cd ~/acpi_tables`
## 反编译
```
sudo cp /sys/firmware/acpi/tables/SSDT* .
sudo cp /sys/firmware/acpi/tables/DSDT .
iasl -da DSDT SSDT*
```
# 修改 SSDT
`DefinitionBlock ("", "SSDT", 2, "AMD", "UPEPRPL ", 0x00000001)`
改为
`DefinitionBlock ("", "SSDT", 2, "AMD", "UPEPRPL ", 0x00000002)`(或者更高的版本号)
```
Case (0x04)
                        {
                            Local0 = \_SB.PCI0.SBRG.EC0.S0E1 /* External reference */
                            \_SB.PCI0.SBRG.EC0.S0E1 = Zero
                            If ((\_SB.ACDC.RTAC == 0x20))
                            {
                                \_SB.PCI0.SBRG.EC0.EYER = \_SB.ACDC.YARR /* External reference */
                                \_SB.PCI0.SBRG.EC0.EMON = \_SB.ACDC.MONR /* External reference */
                            }
                            Else
                            {
                                \_SB.PCI0.SBRG.EC0.EYER = Zero
                                \_SB.PCI0.SBRG.EC0.EMON = Zero
                            }

                            If (Local0)
```
改为
```
Case (0x04)
                        {
                            Local0 = \_SB.PCI0.SBRG.EC0.S0E1 /* External reference */
                            \_SB.PCI0.SBRG.EC0.S0E1 = Zero
                            
                            /* 加入 CondRefOf 安全检查 */
                            If (CondRefOf (\_SB.ACDC.RTAC))
                            {
                                If ((\_SB.ACDC.RTAC == 0x20))
                                {
                                    \_SB.PCI0.SBRG.EC0.EYER = \_SB.ACDC.YARR /* External reference */
                                    \_SB.PCI0.SBRG.EC0.EMON = \_SB.ACDC.MONR /* External reference */
                                }
                                Else
                                {
                                    \_SB.PCI0.SBRG.EC0.EYER = Zero
                                    \_SB.PCI0.SBRG.EC0.EMON = Zero
                                }
                            }
                            Else
                            {
                                /* 如果找不到该对象，直接赋值0，防止引发 AE_NOT_FOUND 崩溃 */
                                \_SB.PCI0.SBRG.EC0.EYER = Zero
                                \_SB.PCI0.SBRG.EC0.EMON = Zero
                            }

                            If (Local0)
```
# 重新编译
`iasl -tc SSDT21.dsl`
# 复制
`sudo cp SSDT21.aml /etc/initcpio/acpi_override/SSDT21.aml`
# 重新打包(以 Limine 为例)
`sudo limine-mkinitcpio`
