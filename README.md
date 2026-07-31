# 机械革命 蛟龙 16 Pro 2025 Linux 补全计划
<p align="center">
  <img src="https://img.shields.io/badge/Platform-Linux-blue?logo=linux" alt="Linux">
  <img src="https://img.shields.io/badge/Model-MECHREVO%20JIAOLONG%2016%20Pro-orange" alt="Model">
  <img src="https://img.shields.io/badge/License-MIT-green" alt="License">
</p>

>在 Linux 下让笔记本正常工作, 并实现Windows机械革命控制台相同的功能

本项目致力于解决 **机械革命 蛟龙 16 Pro 2025** 在 Linux 系统下的功能缺失问题，涵盖 EC 数据读写、性能模式切换、GPU 显示模式切换以及功耗优化（D3cold）等核心功能。
## 机型与环境测试
本工具链目前在以下环境下完成验证：

| 组件 | 规格 / 版本 |
| :--- | :--- |
| **型号** | 机械革命 蛟龙 16 Pro 2025 |
| **CPU** | AMD Ryzen 9 9955HX |
| **显卡** | NVIDIA GeForce RTX 5070 Ti Laptop |
| **BIOS 版本** | `N.1.12MRO13` |
| **系统** | CachyOS + KDE |
---

## 已实现功能与文档

按需求点击查看具体实现说明与脚本：

- [x] **在 Linux 下读取与写入 EC 数据**  
  实现与 EC 的通信。详情参阅：[EC 读写指南](在Linux读取和写入EC数据.md)

- [x] **切换笔记本性能模式**  
  支持在 办公/平衡/狂暴/自定义 模式间自由切换。详情参阅：[性能模式切换](切换性能模式.md)

- [x] **独显直连与混合模式切换**  
  * 切换为 **独显直连**（重启生效）：运行 `python3 独显直连.py`
  * 切换为 **混合输出**（重启生效）：运行 `python3 混合输出.py`

- [x] **为独显启用 D3cold 状态**  
  大大降低空闲/轻度办公时的整机功耗与发热(约 15W)。详情参阅：[D3cold 配置指南](为独显启用D3cold.md)

- [x] **强制卸载独显设备** *(备选方案)*  
  [强制卸载独显说明](强制卸载独显.md)（推荐优先使用上面的 D3cold 策略）

---
## 研究中
- [ ] 在独显直连时睡眠能够正常唤醒
- [ ] 键盘 RGB 灯效控制

## 免责声明
本项目涉及对 EC 的直接读写操作。虽然已在指定机型上验证，但作者不对因误操作、固件不兼容等原因导致的硬件损坏或数据丢失承担责任。请在了解风险前提下使用。