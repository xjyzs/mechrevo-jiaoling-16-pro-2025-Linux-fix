#!/bin/sh
# 扫描pciehp.sh
# 作用：找出独显根端口上绑定着 pciehp的服务设备名，
#       并打印出可以直接填进 systemd service 的那一行。
# 用法：
#   ./扫描pciehp.sh
#
# 背景见：修复独显直连时睡眠无法唤醒.md

DRV=/sys/bus/pci_express/drivers/pciehp

if [ ! -d "$DRV" ]; then
    echo "找不到 $DRV"
    echo "本内核没有把 pciehp 挂在 pci_express 总线上，本方案不适用。"
    exit 1
fi

found=0
hpsvc=""

for dev in /sys/bus/pci/devices/*; do
    [ -e "$dev/vendor" ] || continue
    [ "$(cat "$dev/vendor" 2>/dev/null)" = "0x10de" ] || continue

    case "$(cat "$dev/class" 2>/dev/null)" in
        0x0300*|0x0302*) ;;
        *) continue ;;
    esac

    real=$(readlink -f "$dev")
    bdf=${real##*/}
    portdir=${real%/*}
    port=${portdir##*/}

    echo "独显:        $bdf"
    echo "上游根端口:  $port"
    echo
    echo "该端口的 PCIe 服务设备："

    for s in "$portdir/$port":pcie*; do
        [ -e "$s" ] || continue
        svc=${s##*/}
        drv=""
        if [ -e "$s/driver" ]; then
            drv=$(basename "$(readlink -f "$s/driver" 2>/dev/null)" 2>/dev/null)
        fi
        if [ "$drv" = "pciehp" ]; then
            printf '  %-30s ->  pciehp     <== 要解绑的就是它\n' "$svc"
            hpsvc="$svc"
            found=1
        else
            printf '  %-30s ->  %s\n' "$svc" "${drv:-未绑定}"
        fi
    done
    echo
done

if [ "$found" = 1 ]; then
    echo "-------------------------------------------------------------"
    echo "请把下面这一行的设备名，填进 service 的 ExecStart："
    echo
    echo "  ExecStart=-/bin/sh -c \"echo $hpsvc > $DRV/unbind\""
    echo
    echo "（也就是：$hpsvc）"
    echo "-------------------------------------------------------------"
    exit 0
fi

echo "没有找到绑定着 pciehp 的独显根端口。可能原因："
echo "  1. 已经解绑过了 —— ls /sys/bus/pci/slots/ 会是空的"
echo "  2. _OSC 没有交出 PCIeHotplug（例如装过关掉 PEHP/SHPC 的 DSDT 补丁）"
echo "     —— 那样 pciehp 根本不会绑定，本方案不适用"
echo "  3. 这台机器的独显不在 HotPlug+ 端口后面 —— 那也不会有这个问题"
exit 1