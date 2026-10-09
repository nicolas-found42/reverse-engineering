#!/usr/bin/env python3
"""Exercise PyGhidra/EE and rabbitizer using generated R5900 bytes in the isolated utility environment."""
import argparse
import json
import os
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project', type=Path)
    parser.add_argument('--settings-dir')
    args = parser.parse_args()
    # These libraries belong to the isolated toolchain, not repository dependencies.
    import pyghidra
    import rabbitizer
    from pyghidra.launcher import HeadlessPyGhidraLauncher
    launcher = HeadlessPyGhidraLauncher(install_dir=Path(os.environ['GHIDRA_INSTALL_DIR']))
    if args.settings_dir:
        launcher.add_vmargs('-Dapplication.settingsdir=' + args.settings_dir)
    launcher.start()
    probe = args.project / 'ee-probe.bin'
    probe.write_bytes(bytes.fromhex('0800e00300000000'))
    with pyghidra.open_program(probe, project_location=str(args.project), project_name='ee',
                              language='r5900:LE:32:default', analyze=False) as api:
        program = api.getCurrentProgram()
        address = program.getMinAddress()
        api.disassemble(address)
        instruction = program.getListing().getInstructionAt(address)
        if instruction is None or instruction.getMnemonicString().lower() != 'jr' or not instruction.getPcode():
            raise RuntimeError('EE synthetic instruction/P-code control failed')
    decoded = rabbitizer.Instruction(0x03e00008, 0, rabbitizer.InstrCategory.R5900).disassemble()
    if decoded.split() != ['jr', '$ra']:
        raise RuntimeError('Rabbitizer synthetic control failed')
    print(json.dumps({'successful': True, 'controls': ['pyghidra_ee_pcode', 'rabbitizer_r5900']}))


if __name__ == '__main__':
    main()
