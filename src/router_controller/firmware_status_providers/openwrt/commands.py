SYSTEM_RELEASE = "cat /etc/openwrt_release"
HOSTNAME = "cat /proc/sys/kernel/hostname"
KERNEL = "uname -r"
ARCHITECTURE = "uname -m"
UPTIME = "cat /proc/uptime"
LOAD_AVERAGE = "cat /proc/loadavg"

MEMORY = "cat /proc/meminfo"

STORAGE = "df -k"

TEMPERATURE = "cat /sys/class/thermal/thermal_zone0/temp"
