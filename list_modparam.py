#! /usr/bin/env drgn
# 
# drgn script to list module parameters
# sudo ./list_modparam.py [<module name>]

import argparse
from collections import defaultdict

import drgn
from drgn import Object
from drgn.helpers.linux import *
 
all_params = defaultdict(dict)

# iterate struct kernel_param to get module parameters
def iterate_kp(start_addr, stop_addr, mod_=""):
    kp = Object(prog, 'struct kernel_param', address=start_addr).address_of_()
    mod = mod_
    while True:
        name = kp.name.string_().split(b'.')
        # for bult-in module, retrieve module name from kp.name
        # usually parameter name is "<mod>.<param>" unless it is not a module
        if mod_ == "":
            if len(name) == 1:
                mod = 'core'
            else:
                mod = name[0].decode('utf-8')
    
        # get param string
        if kp.arg.value_() == 0:
            # It seems when module name is changed by module_param_named etc.,
            # kp.arg is NULL and kp.name holds original name
            param = name[1].decode('utf-8')
        else:
            sym = prog.symbol(kp.arg.value_())
            param = sym.name
    
        try:
            # use name string instead of address to read value
            # as drgn will handle type properly
            val = prog.variable(param)
            # ... but there may exist duplicates symbol...
            syms = prog.symbols(param)
            dup = True if len(syms) != 1 else 0
            # TODO: Resolve symbol duplicates
            # TODO: Also add handling when parameter is array

            all_params[mod][param] = (val, dup)
        except:
            # param not a variable (only has functions). skip it
            all_params[mod][param] = ('NaN', False)
            pass
    
        kp = kp + 1
        if kp.value_() == stop_addr:
            break

def fill_builtin_param():
    # built-in module's parameters info are packed in __start___param ~ __stop___param section
    _start_param_addr = prog.symbol('__start___param').address
    _stop_param_addr = prog.symbol('__stop___param').address
    iterate_kp(_start_param_addr, _stop_param_addr)

def fill_loadable_param():
    # loadable module's parameters info are stored in each module's 'struct module'
    for module in list_for_each_entry('struct module',
                                      prog['modules'].address_of_(), 'list'):
        mod = module.name.string_().decode('utf-8')
        if module.num_kp != 0:
            iterate_kp(module.kp.value_(), (module.kp + module.num_kp).value_(), mod)

def print_mod_param(target_mod):
    print(target_mod)
    if target_mod in all_params:
        for param, (val, dup) in all_params[target_mod].items():
            if dup:
                extra = " **symbol name duplicates, value might be incorrect**"
            else:
                extra =""
            print("\t{} = {}{}".format(param, val, extra))
    else:
        print("\tthere is no parameters or module is not loaded")

def print_all_param():
    for mod, params in all_params.items():
        print_mod_param(mod)

def main(target_mods):
    fill_builtin_param()
    fill_loadable_param()

    if target_mods:
        for target_mod in target_mods:
            print_mod_param(target_mod)
    else:
        print_all_param()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='List module parameters')
    parser.add_argument('module', help='module name(s)', type=str, nargs='*')
    args = parser.parse_args()
    main(args.module)

