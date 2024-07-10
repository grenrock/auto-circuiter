import sys

def input_panels(p_file):
    f = open(p_file)
    panels = f.readlines()
    panel_list = []
    for panel in panels:
        info_arr = panel.split(',')
        panel_list.append({
            'description': info_arr[0],
            'bus_amperage': int(info_arr[1]),
            'phase_voltage': int(info_arr[2]),
            'line_voltage': int(info_arr[3]),
            'phase': int(info_arr[4]),
            'wire': int(info_arr[5]),
            'num_breakers': int(info_arr[6]),
        })
    return panel_list

def input_equip(eq_file):
    f = open(eq_file)
    equips = f.readlines()
    equip_list = []
    for equip in equips:
        info_arr = equip.split(',')
        if len(info_arr) > 5:
            existing = info_arr[5].strip()
        else:
            existing = False
        equip_list.append({
            'circuits' : '',
            'item_num': info_arr[0],
            'description': info_arr[1],
            'voltage': int(info_arr[2]),
            'amperage': float(info_arr[3]),
            'phase': int(info_arr[4]),
            'existing': existing
        })
    return equip_list

def encode_breaker_size(breaker_size):
    sizes = {
        '20': 'A',
        '25': 'B',
        '30': 'C',
        '35': 'D',
        '40': 'E',
        '45': 'F',
        '50': 'G',
        '55': 'H',
        '60': 'H',
        '65': 'I',
        '70': 'I',
        '75': 'J',
        '80': 'J',
        '85': 'K',
        '90': 'K',
        '95': 'L',
        '100': 'L',
        '15': 'Z'
    }
    return sizes[str(breaker_size)]

def decode_breaker_size(breaker_size):
    sizes = {
        '-': '-',
        '2': '-',
        '3': '-',
        '0': '-',
        'A': 20,
        'B': 25,
        'C': 30,
        'D': 35,
        'E': 40,
        'F': 45,
        'G': 50,
        'H': 60,
        'I': 70,
        'J': 80,
        'K': 90,
        'L': 100,
        'Z': 15
    }
    return sizes[str(breaker_size)]

def format_circuit_number(index, side, required_breakers):
    if (side == 'left'):
        if required_breakers == 3:
            return "{},{},{}".format(index + 1, index + 3, index + 5)
        if required_breakers == 2:
            return "{},{}".format(index + 1, index + 3)
        return str(index + 1)
    if required_breakers == 3:
        return "{},{},{}".format(index + 2, index + 4, index + 6)
    if required_breakers == 2:
        return "{},{}".format(index + 2, index + 4)
    return str(index + 2)

def verify_available_amperage(panel, new_amperage):
    a = 0
    b = 0
    c = 0
    if(panel['phase'] == 3):
        for side in ['left', 'right']:
            wattage_arr = panel[side]['wattage'].strip(',').split(',')
            for i in range(len(wattage_arr)):
                if (i % 3 == 0):
                    a = a + int(float(wattage_arr[i]))
                if (i % 3 == 1):
                    b = b + int(float(wattage_arr[i]))
                if (i % 3 == 2):
                    c = c + int(float(wattage_arr[i]))
    else:
        for side in ['left', 'right']:
            wattage_arr = panel[side]['wattage'].strip(',').split(',')
            for i in range(len(wattage_arr)):
                if (i % 2 == 0):
                    a = a + int(float(wattage_arr[i]))
                if (i % 2 == 1):
                    b = b + int(float(wattage_arr[i]))
    if (a / panel['phase_voltage'] + new_amperage > panel['bus_amperage'] * 0.8):
        return False
    if (b / panel['phase_voltage'] + new_amperage > panel['bus_amperage'] * 0.8):
        return False
    if (c / panel['phase_voltage'] + new_amperage > panel['bus_amperage'] * 0.8):
        return False
    panel['phase_a'] = a
    panel['phase_b'] = b
    panel['phase_c'] = c
    panel['amps'] = max([a,b,c]) / panel['phase_voltage']
    return True

def find_available_circuits(assigned_circuits, required_breakers, breaker_size, voltage, amperage, description):
    circuits = ''
    for panel in assigned_circuits:
        for side in ['left', 'right']:
            if assigned_circuits[panel]['phase'] == 3 and required_breakers == 3 and ',0,0,0,' in assigned_circuits[panel][side]['breakers'] and verify_available_amperage(assigned_circuits[panel], amperage):
                circuits = format_circuit_number(assigned_circuits[panel][side]['breakers'].index(',0,0,0,'), side, required_breakers)
                wattage = int(voltage * amperage / 1.732)
                assigned_circuits[panel][side]['wattage'] = assigned_circuits[panel][side]['wattage'].replace(',0,0,0,', ',{},{},{},'.format(wattage, wattage, wattage), 1)
                assigned_circuits[panel][side]['breakers'] = assigned_circuits[panel][side]['breakers'].replace(',0,0,0,', ',{},-,3,'.format(encode_breaker_size(breaker_size)), 1)
                assigned_circuits[panel][side]['description'] = assigned_circuits[panel][side]['description'].replace(',0,0,0,', ',{},{},{},'.format(description, '-', '-'), 1)
                return (panel, circuits, wattage)
            elif required_breakers == 2 and ',0,0,' in assigned_circuits[panel][side]['breakers'] and verify_available_amperage(assigned_circuits[panel], amperage):
                circuits = format_circuit_number(assigned_circuits[panel][side]['breakers'].index(',0,0,'), side, required_breakers)
                wattage = int(voltage * amperage / 2)
                assigned_circuits[panel][side]['wattage'] = assigned_circuits[panel][side]['wattage'].replace(',0,0,', ',{},{},'.format(wattage, wattage), 1)
                assigned_circuits[panel][side]['breakers'] = assigned_circuits[panel][side]['breakers'].replace(',0,0,', ',{},2,'.format(encode_breaker_size(breaker_size)), 1)
                assigned_circuits[panel][side]['description'] = assigned_circuits[panel][side]['description'].replace(',0,0,', ',{},{},'.format(description, '-'), 1)
                return (panel, circuits, wattage)
            elif required_breakers == 1 and ',0,' in assigned_circuits[panel][side]['breakers'] and verify_available_amperage(assigned_circuits[panel], amperage):
                circuits = format_circuit_number(assigned_circuits[panel][side]['breakers'].index(',0,'), side, required_breakers)
                assigned_circuits[panel][side]['wattage'] = assigned_circuits[panel][side]['wattage'].replace(',0,', ',{},'.format(voltage * amperage), 1)
                assigned_circuits[panel][side]['breakers'] = assigned_circuits[panel][side]['breakers'].replace(',0,', ',{},'.format(encode_breaker_size(breaker_size)), 1)
                assigned_circuits[panel][side]['description'] = assigned_circuits[panel][side]['description'].replace(',0,', ',{},'.format(description), 1)                
                return (panel, circuits, int(voltage * amperage))

def assign_circuits(panel_list, equip_list):
    done = False
    updated = False
    assigned_circuits = {}
    for panel in panel_list:
        assigned_circuits[panel['description']] = {
            'left': {
                'breakers': ',' + '0,'*int((panel['num_breakers'] / 2)),
                'wattage': ',' +  '0,'*int((panel['num_breakers'] / 2)),
                'description': ',' +  '0,'*int((panel['num_breakers'] / 2)),
            },
            'right': {
                'breakers': ',' +  '0,'*int((panel['num_breakers'] / 2)),
                'wattage': ',' +  '0,'*int((panel['num_breakers'] / 2)),
                'description': ',' +  '0,'*int((panel['num_breakers'] / 2)),
            },
            'phase': panel['phase'],
            'phase_voltage': panel['phase_voltage'],
            'bus_amperage': panel['bus_amperage'],
            'phase_a': 0,
            'phase_b': 0,
            'phase_c': 0,
            'amps': 0
        }
        for equip in equip_list:
            if equip['existing']:
                p = equip['existing'].split(':')[0]
                existing_circuits = equip['existing'].split(':')[1].split(';')
                if p == panel['description']:
                    if (int(existing_circuits[0]) % 2 == 1):
                        side = 'left'
                        index = int(existing_circuits[0])
                    else:
                        side = 'right'
                        index = int(existing_circuits[1]) - 3
                    if len(existing_circuits) == 3:
                        wattage = int(equip['voltage'] * equip['amperage'] / 1.732)
                    elif len(existing_circuits) == 2:
                        wattage = int(equip['voltage'] * equip['amperage'] / 2)
                    else:
                        wattage = int(equip['voltage'] * equip['amperage'])
                    if equip['amperage'] > 16:
                        mba = encode_breaker_size(str(5 * round(equip['amperage'] * 1.1/5)))
                    else:
                        mba = 'A'
                    first = True
                    w_index = index
                    d_index = index
                    for i in range(len(existing_circuits)):
                        breaker_list = list(assigned_circuits[p][side]['breakers'])
                        if first:
                            breaker_list[index] = mba
                        else:
                            breaker_list[index] = '-'
                        assigned_circuits[p][side]['breakers'] = ''.join(breaker_list)
                        index += 2
                        first = False
                    for i in range(len(existing_circuits)):
                        wattage_list = list(assigned_circuits[p][side]['wattage'])
                        wattage_list[w_index] = str(wattage)
                        print(''.join(wattage_list))
                        assigned_circuits[p][side]['wattage'] = ''.join(wattage_list)
                        w_index += len(str(wattage)) + 1
                    first = True
                    for i in range(len(existing_circuits)):
                        description_list = list(assigned_circuits[p][side]['description'])
                        if first:
                            description_list[d_index] = equip['description']
                        else:
                            description_list[d_index] = '-'
                        assigned_circuits[p][side]['description'] = ''.join(description_list)
                        d_index += len(equip['description']) + 1
                        first = False
    while not done:
        for equip in equip_list:
            if not equip['circuits']:
                required_breakers = 1
                if equip['phase'] == 3:
                    required_breakers = 3
                elif equip['voltage'] > 120:
                    required_breakers = 2
                if equip['amperage'] > 16:
                    equip['mba'] = decode_breaker_size(encode_breaker_size(str(5 * round(equip['amperage'] * 1.1/5))))
                else:
                    equip['mba'] = 20
                circuits = find_available_circuits(assigned_circuits, required_breakers, equip['mba'], equip['voltage'], equip['amperage'], equip['item_num'] + ' - ' + equip['description'])
                if circuits:
                    equip['circuits'] = circuits
                    updated = True
                else:
                    updated = False
            else:
                updated = False
        if updated == False:
            done = True
    return assigned_circuits

def output_panels():
    return

if __name__ == "__main__":
    panel_list = input_panels(sys.argv[1])
    equip_list = input_equip(sys.argv[2])
    assigned_circuits = assign_circuits(panel_list, equip_list)
    for e in equip_list:
        print(e)

    print(assigned_circuits)
    