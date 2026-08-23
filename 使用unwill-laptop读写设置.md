# 使用 unwill-laptop 读写设置
**此内核模块需要 Linux 内核 6.19+**
## 如何加载
`sudo modprobe uniwill-laptop force=1`
## 键盘功能设置
### 位置
`/sys/bus/platform/devices/INOU0000:00/`
### 功能
**fn_lock**: Fn 锁
**super_key_enable**: Win 键开关
**touchpad_toggle_enable**: 触控板开关
### 读取示例
``` shell
cat /sys/bus/platform/devices/INOU0000:00/fn_lock # 读取 Fn 锁状态
0
```
### 写入示例
``` shell
echo "1" | sudo tee /sys/devices/platform/INOU0000:00/super_key_enable # 启用 Win 键
```

## 硬件监控(风扇、温度)
### 位置
`/sys/bus/platform/devices/INOU0000:00/hwmon/hwmon12/`(把12改成对应目录下存在的数字)
### 功能
风扇转速、转速挡位、温度(CPU/GPU)、风扇/温度标签
**加载 unwill-laptop 后，某些监控软件，比如 missioncenter ，也能显示相应数据**