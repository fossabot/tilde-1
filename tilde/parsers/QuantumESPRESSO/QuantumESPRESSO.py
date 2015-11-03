
# Quantum ESPRESSO basic parser
# Author: Evgeny Blokhin
# TODO: check ibrav settings, parsing might be wrong

import os, sys
import datetime, time

from numpy import array

from tilde.parsers import Output

from ase import Atoms
from ase.data import chemical_symbols
from ase.units import Bohr, Rydberg


class QuantumESPRESSO(Output):
    def __init__(self, filename, **kwargs):
        Output.__init__(self, filename)

        cur_folder = os.path.dirname(filename)
        self.related_files.append(filename)

        self.info['framework'] = 'Quantum ESPRESSO'
        self.info['finished'] = -1
        self.electrons['type'] = 'plane waves'

        # taken from trunk/Modules/funct.f90
        xc_internal_map = {
        "pw"           : {'name': "PW_LDA",                  'type': ['LDA'],              'setup': ["sla+pw+nogx+nogc"    ] },

        "pz"           : {'name': "PZ_LDA",                  'type': ['LDA'],              'setup': ["sla+pz+nogx+nogc"    ] },
        "bp"           : {'name': "Becke-Perdew grad.corr.", 'type': ['GGA'],              'setup': ["b88+p86+nogx+nogc"   ] },
        "pw91"         : {'name': "PW91",                    'type': ['GGA'],              'setup': ["sla+pw+ggx+ggc"      ] },
        "blyp"         : {'name': "BLYP",                    'type': ['GGA'],              'setup': ["sla+b88+lyp+blyp"    ] },
        "pbe"          : {'name': "PBE",                     'type': ['GGA'],              'setup': ["sla+pw+pbx+pbc", "sla+pw+pbe+pbe"] },
        "revpbe"       : {'name': "revPBE",                  'type': ['GGA'],              'setup': ["sla+pw+rpb+pbc", "sla+pw+rpb+pbe"] },
        "pw86pbe"      : {'name': "PW86+PBE",                'type': ['GGA'],              'setup': ["sla+pw+pw86+pbc", "sla+pw+pw86+pbe"] },
        "b86bpbe"      : {'name': "B86b+PBE",                'type': ['GGA'],              'setup': ["sla+pw+b86b+pbc", "sla+pw+b86b+pbe"] },
        "pbesol"       : {'name': "PBEsol",                  'type': ['GGA'],              'setup': ["sla+pw+psx+psc"      ] },
        "q2d"          : {'name': "PBEQ2D",                  'type': ['GGA'],              'setup': ["sla+pw+q2dx+q2dc"    ] },
        "hcth"         : {'name': "HCTH/120",                'type': ['GGA'],              'setup': ["nox+noc+hcth+hcth"   ] },
        "olyp"         : {'name': "OLYP",                    'type': ['GGA'],              'setup': ["nox+lyp+optx+blyp"   ] },
        "wc"           : {'name': "Wu-Cohen",                'type': ['GGA'],              'setup': ["sla+pw+wcx+pbc", "sla+pw+wcx+pbe"] },
        "sogga"        : {'name': "SOGGA",                   'type': ['GGA'],              'setup': ["sla+pw+sox+pbc", "sla+pw+sox+pbe"] },
        "optbk88"      : {'name': "optB88",                  'type': ['GGA'],              'setup': ["sla+pw+obk8+p86"     ] },
        "optb86b"      : {'name': "optB86",                  'type': ['GGA'],              'setup': ["sla+pw+ob86+p86"     ] },
        "ev93"         : {'name': "Engel-Vosko",             'type': ['GGA'],              'setup': ["sla+pw+evx+nogc"     ] },
        "tpss"         : {'name': "TPSS",                    'type': ['meta-GGA'],         'setup': ["sla+pw+tpss+tpss"    ] },
        "m06l"         : {'name': "M06L",                    'type': ['meta-GGA'],         'setup': ["nox+noc+m6lx+m6lc"   ] },
        "tb09"         : {'name': "TB09",                    'type': ['meta-GGA'],         'setup': ["sla+pw+tb09+tb09"    ] },
        "pbe0"         : {'name': "PBE0",                    'type': ['GGA', 'hybrid'],    'setup': ["pb0x+pw+pb0x+pbc", "pb0x+pw+pb0x+pbe"] },
        "hse"          : {'name': "HSE06",                   'type': ['GGA', 'hybrid'],    'setup': ["sla+pw+hse+pbc", "sla+pw+hse+pbe"] },
        "b3lyp"        : {'name': "B3LYP",                   'type': ['GGA', 'hybrid'],    'setup': ["b3lp+vwn+b3lp+b3lp"  ] },
        "gaupbe"       : {'name': "Gau-PBE",                 'type': ['GGA', 'hybrid'],    'setup': ["sla+pw+gaup+pbc", "sla+pw+gaup+pbe"] },
        "vdw-df"       : {'name': "vdW-DF",                  'type': ['GGA', 'vdW'],       'setup': ["sla+pw+rpb+vdw1"     ] },
        "vdw-df2"      : {'name': "vdW-DF2",                 'type': ['GGA', 'vdW'],       'setup': ["sla+pw+rw86+vdw2"    ] },
        "vdw-df-c09"   : {'name': "vdW-DF-C09",              'type': ['GGA', 'vdW'],       'setup': ["sla+pw+c09x+vdw1"    ] },
        "vdw-df2-c09"  : {'name': "vdW-DF2-C09",             'type': ['GGA', 'vdW'],       'setup': ["sla+pw+c09x+vdw2"    ] },
        "vdw-df-cx"    : {'name': "vdW-DF-cx",               'type': ['GGA', 'vdW'],       'setup': ["sla+pw+cx13+vdW1"    ] },
        "vdw-df-obk8"  : {'name': "vdW-DF-obk8",             'type': ['GGA', 'vdW'],       'setup': ["sla+pw+obk8+vdw1"    ] },
        "vdw-df-ob86"  : {'name': "vdW-DF-ob86",             'type': ['GGA', 'vdW'],       'setup': ["sla+pw+ob86+vdw1"    ] },
        "vdw-df2-b86r" : {'name': "vdW-DF2-B86R",            'type': ['GGA', 'vdW'],       'setup': ["sla+pw+b86r+vdw2"    ] },
        "rvv10"        : {'name': "rVV10",                   'type': ['GGA', 'vdW'],       'setup': ["sla+pw+rw86+pbc+vv10", "sla+pw+rw86+pbe+vv10"] },

        "hf"           : {'name': "Hartree-Fock",            'type': ['HF'],               'setup': ["hf+noc+nogx+nogc"    ] },
        "vdw-df3"      : {'name': "vdW-DF3",                 'type': ['GGA', 'vdW'],       'setup': ["sla+pw+rw86+vdw3"    ] },
        "vdw-df4"      : {'name': "vdW-DF4",                 'type': ['GGA', 'vdW'],       'setup': ["sla+pw+rw86+vdw4"    ] },
        "gaup"         : {'name': "Gau-PBE",                 'type': ['GGA', 'hybrid'],    'setup': ["sla+pw+gaup+pbc", "sla+pw+gaup+pbe"] },
        }

        self.data = open(filename).readlines()
        atomic_data, cell_data, pos_data, symbol_data, alat = None, [], [], [], 0

        for n in range(len(self.data)):
            cur_line = self.data[n]

            if "This run was terminated on" in cur_line:
                self.info['finished'] = 1

            elif "     Program PWSCF" in cur_line and " starts " in cur_line:
                ver_str = cur_line.strip().replace('Program PWSCF', '')
                ver_str = ver_str[ : ver_str.find(' starts ') ].strip()
                if ver_str.startswith("v."): ver_str = ver_str[2:]
                self.info['prog'] = self.info['framework'] + " " + ver_str

            elif cur_line.startswith("     celldm"):
                if not alat:
                    alat = float(cur_line.split()[1]) * Bohr
                    if not alat: alat = 1

            elif cur_line.startswith("     crystal axes:"):
                cell_data = [x.split()[3:6] for x in self.data[n + 1:n + 4]]
                cell_data = array([[float(col) for col in row] for row in cell_data])

            elif cur_line.startswith("     site n."):
                if len(pos_data): continue

                while True:
                    n += 1
                    next_line = self.data[n].split()
                    if not next_line: break
                    pos_data.append([float(x) for x in next_line[-4:-1]])
                    symbol = next_line[1].strip('0123456789').split('_')[0]
                    if not symbol in chemical_symbols and len(symbol) > 1: symbol = symbol[:-1]
                    symbol_data.append(symbol)
                pos_data = array(pos_data)*alat
                atomic_data = Atoms(symbol_data, pos_data, cell=cell_data*alat, pbc=(1,1,1))

            elif "CELL_PARAMETERS" in cur_line:
                for i in range(3):
                    n += 1
                    next_line = self.data[n].split()
                    if not next_line: break
                    cell_data[i][:] = map(float, next_line)
                else:
                    mult = 1
                    if "bohr" in cur_line: mult = Bohr
                    elif "alat" in cur_line: mult = alat
                    atomic_data.set_cell(cell_data*mult, scale_atoms=True)

            elif "ATOMIC_POSITIONS" in cur_line:
                coord_flag = cur_line.split('(')[-1].strip()
                for i in range(len(pos_data)):
                    n += 1
                    next_line = self.data[n].split()
                    pos_data[i][:] = map(float, next_line[1:4])
                if not atomic_data: continue

                if coord_flag=='alat)':
                    atomic_data.set_positions(pos_data*alat)
                elif coord_flag=='bohr)':
                    atomic_data.set_positions(pos_data*Bohr)
                elif coord_flag=='angstrom)':
                    atomic_data.set_positions(pos_data)
                else:
                    atomic_data.set_scaled_positions(pos_data)

            elif cur_line.startswith("!    total energy"):
                self.info['energy'] = float(cur_line.split()[-2]) * Rydberg

            elif "     Exchange-correlation" in cur_line:
                if self.info['H']: continue

                xc_str = cur_line.split('=')[-1].strip()
                xc_parts = xc_str[ : xc_str.find("(") ].split()
                if len(xc_parts) == 1: xc_parts = xc_parts[0].split('+')
                if len(xc_parts) < 4: xc_parts = [ '+'.join(xc_parts) ]
                xc_parts = map(lambda x: x.lower().strip("-'\""), xc_parts)

                if len(xc_parts) == 1:
                    try:
                        self.info['H'] = xc_internal_map[xc_parts[0]]['name']
                        self.info['H_types'].extend( xc_internal_map[xc_parts[0]]['type'] )
                    except KeyError:
                        self.info['H'] = xc_parts[0]
                else:
                    xc_parts = '+'.join(xc_parts)
                    match = [ i for i in xc_internal_map.values() if xc_parts in i['setup'] ]
                    if match:
                        self.info['H'] = match[0]['name']
                        self.info['H_types'].extend( match[0]['type'] )
                    else:
                        self.info['H'] = xc_parts

            elif "PWSCF        :" in cur_line:
                if "WALL" in cur_line or "wall" in cur_line:
                    fmt = "%S.%fs"
                    d = cur_line.split("CPU")[-1].replace("time", "").replace(",", "")
                    d = d[ : d.find("s") + 1 ].strip().replace(" ", "")
                    if 'm' in d: fmt = "%Mm" + fmt
                    if 'h' in d: fmt = "%Hh" + fmt
                    d = time.strptime(d, fmt)
                    # TODO: days?
                    self.info['duration'] = "%2.2f" % (  datetime.timedelta(hours=d.tm_hour, minutes=d.tm_min, seconds=d.tm_sec).total_seconds()/3600  )
                    self.info['finished'] = 1

        if atomic_data: self.structures.append(atomic_data)

        for check in [  filename.replace('.' + filename.split('.')[-1], '') + '.in'  ]: # NB no guarantee this file fits!
            if os.path.exists(os.path.join(cur_folder, check)): self.related_files.append(os.path.join(cur_folder, check))

    @staticmethod
    def fingerprints(test_string):
        if ("pwscf" in test_string or "PWSCF" in test_string) and "     Current dimensions of program " in test_string: return True
        else: return False
