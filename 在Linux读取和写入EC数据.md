# 安装依赖
**安装后可使用 /proc/acpi/call 读写 EC 数据**
```shell
sudo pacman -S acpi_call-dkms
```
# 读取
**0x075B为你想读取的地址, 取后 4 位, 比如0xFED5075B取0x075B**
```shell
echo '\_SB.INOU.ECRR 0x075B' | sudo tee /proc/acpi/call
sudo cat /proc/acpi/call
```
# 写入
**0x0751为你想写入的地址, 0x10 为你想写入的数据**
```shell
echo '\_SB.INOU.ECRW 0x0751 0x10' | sudo tee /proc/acpi/call
```