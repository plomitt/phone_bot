import re
import pyfiglet

from constants import DATA_CYCLE_NUM_LINE_ID, DATA_FILE_PATH, DATA_PHONE_NUM_LINE_ID, FAIL_MSG_NOTIF_STEP_LINE_ID, SCS_MSG_REP_AMNT_LINE_ID

def get_msg_repeat(res, cyc):
    amnt = get_notif_amnt()
    step = get_notif_step()
    return amnt if res else (cyc % step == 0) * 1



def check_num_format(num):
    return re.match(r"^\+7 \d{3} \d{3} \d{4}$", num)



def shorten_num(phone_number):
    digits_only = re.sub(r'\D', '', phone_number)
    return digits_only[4:]



def print_ascii_code(code):
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    RESET = '\033[0m'

    messages = {
        'match_found': f"{GREEN}{ascii_msg('MATCH FOUND!')}{RESET}",
        'no_match': f"{YELLOW}{ascii_msg('NO MATCH.')}{RESET}",
        'error': f"{RED}{ascii_msg('ERROR!')}{RESET}",
    }

    print(messages[code])

def ascii_msg(msg):
    return pyfiglet.figlet_format(msg)


def set_phone_num(num):
    write_line_to_file(DATA_FILE_PATH, DATA_PHONE_NUM_LINE_ID, num)

def get_phone_num():
    num = get_line_from_file(DATA_FILE_PATH, DATA_PHONE_NUM_LINE_ID)

    if not check_num_format(num):
        print('Incorrect phone number format.')
        raise Exception('Incorrect phone number format.')
    
    return num

def set_cycle_num(num):
    write_line_to_file(DATA_FILE_PATH, DATA_CYCLE_NUM_LINE_ID, num)

def get_cycle_num():
    cycle = int(get_line_from_file(DATA_FILE_PATH, DATA_CYCLE_NUM_LINE_ID))

    if cycle == None:
        write_line_to_file(DATA_FILE_PATH, DATA_CYCLE_NUM_LINE_ID, 1)
        return 1
    
    return cycle

def get_notif_step():
    return get_int_from_file(FAIL_MSG_NOTIF_STEP_LINE_ID)

def set_notif_param(param):
    if param == 'amnt':
        return set_notif_param_value(SCS_MSG_REP_AMNT_LINE_ID, 5, 20, 5)
    if param == 'step':
        return set_notif_param_value(FAIL_MSG_NOTIF_STEP_LINE_ID, 5, 60, 5)

def set_notif_param_value(line_id, minv, maxv, step):
    steps = get_step_list(minv, maxv, step)
    old = get_int_from_file(line_id)
    new = get_next_value(old, steps)

    write_line_to_file(DATA_FILE_PATH, line_id, new)
    return new

def get_notif_amnt():
    return get_int_from_file(SCS_MSG_REP_AMNT_LINE_ID)

def set_notif_amnt(num):
    write_line_to_file(DATA_FILE_PATH, SCS_MSG_REP_AMNT_LINE_ID, num)

def get_int_from_file(line):
    return int(get_line_from_file(DATA_FILE_PATH, line))

def get_step_list(minv, maxv, step):
    return [1] + list(range(minv, maxv + 1, step))

def get_next_value(current_value, n_list):
    current_index = n_list.index(current_value)
    next_index = (current_index + 1) % len(n_list)
    next_value = n_list[next_index]
    return next_value


def write_line_to_file(file_path, line_number, new_line):
    new_line = str(new_line)

    try:
        with open(file_path, "r") as file:
            lines = file.readlines()

        while len(lines) < line_number:
            lines.append("\n")

        lines[line_number - 1] = new_line + "\n"

        with open(file_path, "w") as file:
            file.writelines(lines)

    except FileNotFoundError:
        lines = ["\n"] * (line_number - 1) + [new_line + "\n"]
        with open(file_path, "w") as file:
            file.writelines(lines)

def get_line_from_file(file_path, line_number):
    try:
        with open(file_path, "r") as file:
            lines = file.readlines()

        if 0 < line_number <= len(lines):
            return lines[line_number - 1].rstrip("\n")
        else:
            return None

    except FileNotFoundError:
        return None