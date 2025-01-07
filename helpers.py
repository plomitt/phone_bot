import re
import pyfiglet

notif_step = 1
notif_amnt = 10
trg_phone_num = '+7 123 456 7890'


def get_msg_repeat(res, cyc):
    global notif_step
    global notif_amnt
    return notif_amnt if res else (cyc % notif_step == 0) * 1



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
    global trg_phone_num

    if not check_num_format(num):
        print('Incorrect phone number format.')
        raise Exception('Incorrect phone number format.')

    trg_phone_num = num

def get_phone_num():
    global trg_phone_num

    if not check_num_format(trg_phone_num):
        print('Incorrect phone number format.')
        raise Exception('Incorrect phone number format.')
    
    return trg_phone_num


def set_notifs_step():
    global notif_step

    steps = get_step_list(5, 60, 5)
    notif_step = get_next_value(notif_step, steps)

    return notif_step

def set_notifs_amnt():
    global notif_amnt

    steps = get_step_list(5, 20, 5)
    notif_amnt = get_next_value(notif_amnt, steps)

    return notif_amnt

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