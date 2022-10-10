# Description

drgn script to list module parameters (both built-in and loadable modules)
by searching 'struct kernel_param' info in memory.
This scirpt will also show module parameters which are hidden in '/sys/module/\<module name\>/parameters'.

Note that this script searches a global variable corresponding to the parameter
and print its value. This is rather a PoC and not fully validated.

Limitations:
 - duplicate symbols are not resolved
 - array parameters are not handled properly

Example:
```sh
# built-in module
$ modinfo -n thermal
(builtin)
$ modinfo -p thermal
act:Disable or override all lowest active trip points. (int)
crt:Disable or lower all critical trip points. (int)
tzp:Thermal zone polling frequency, in 1/10 seconds. (int)
nocrt:Set to take no action upon ACPI thermal zone critical trips points. (int)
off:Set to disable ACPI thermal support. (int)
psv:Disable or override all passive trip points. (int)

# some parameters are hidden in sysfs
$ grep -r "" /sys/module/thermal/parameters/
/sys/module/thermal/parameters/act:1:0
/sys/module/thermal/parameters/tzp:1:0
/sys/module/thermal/parameters/psv:1:0
/sys/module/thermal/parameters/crt:1:0

$ sudo ./list_modparam.py thermal
thermal
        psv = (int)0
        off = (int)0 **symbol name duplicates, value might be incorrect**
        nocrt = (int)0
        tzp = (int)0
        crt = (int)0
        act = (int)0

# loadable module
$ modinfo -n orangefs
/lib/modules/5.19.14-200.fc36.x86_64/kernel/fs/orangefs/orangefs.ko.xz
$ modinfo -p orangefs
hash_table_size:size of hash table for operations in progress (int)
module_parm_debug_mask:debugging level (see orangefs-debug.h for values) (ulong)
op_timeout_secs:Operation timeout in seconds (int)
slot_timeout_secs:Slot timeout in seconds (int)
$ modprobe orangefs

$ grep -r "" /sys/module/orangefs/parameters/
/sys/module/orangefs/parameters/module_parm_debug_mask:1:0

$ sudo ./list_modparam.py orangefs
orangefs
        slot_timeout_secs = (int)900
        op_timeout_secs = (int)20
        module_parm_debug_mask = (ulong)0
        hash_table_size = (int)509
```

