from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import base64
import asyncio
from constants import PAGE_LINK
from gemini import get_answer
from helpers import ascii_msg, get_phone_num, print_ascii_code, set_phone_num, shorten_num
from shared import stop_event, msg_queue

def setup_driver(width, height):
  driver_options = Options()
  driver_options.add_argument("--headless")
  driver_options.add_argument("--kiosk")
  driver_options.add_argument(f"--window-size={width},{height}")
  driver = webdriver.Chrome(options=driver_options)
  driver.set_page_load_timeout(5)

  return driver



def check_for_captcha(driver):
    print('searching for captcha...')
    try:
        captcha_image = driver.find_element(By.CLASS_NAME, "captcha")
        print("captcha found")

        img_name = save_captcha_img(captcha_image)
        solve_captcha(driver, img_name)
        
    except NoSuchElementException:
        print("captcha not found")

def solve_captcha(driver, img_name):
    print('solving captcha...')
    answer_str = get_answer(img_name)
    print(f'captcha answer:: {answer_str}')

    input_field = driver.find_element(By.NAME, "captcha")
    input_field.clear()
    input_field.send_keys(answer_str)
    input_field.send_keys(Keys.RETURN)

    print("captcha answer entered")
    time.sleep(1)

    check_for_captcha(driver)

def save_captcha_img(captcha_image):
    captcha_data = captcha_image.get_attribute("src")
    
    img_name = 'captcha.jpeg'
    save_base64_image(captcha_data, img_name)
    print(f"Captcha image saved")

    return img_name

def save_base64_image(base64_string, output_file):
    base64_data = base64_string.split(",")[1]
    
    image_data = base64.b64decode(base64_data)
    
    with open(output_file, "wb") as f:
        f.write(image_data)



def enter_phone_num(driver, phone_num):
    input_field = driver.find_element(By.NAME, "maskSelection_1")
    input_field.clear()
    input_field.send_keys(phone_num)
    input_field.send_keys(Keys.RETURN)

    print('phone num entered')

def expand_all_sections(driver):
    for i in range(30):
        try:
            expand_button = driver.find_element(By.CLASS_NAME, "PhoneNumbersBlock-module__loader--pc2Hc")            
            # expand_button.click()
            driver.execute_script("arguments[0].click();", expand_button)
            
            time.sleep(1)
            
            print("Section expanded")
        except NoSuchElementException:
            print("No more sections found")
            return
        except Exception as e:
            print(f"An exception occurred: {e}. Retrying...")
            print_ascii_code('error')
            time.sleep(1)
            continue
    
    print("exceeded_section_limit")
    raise Exception('exceeded_section_limit')

def get_all_numbers(driver):
    buttons = driver.find_elements(By.CLASS_NAME, "PhoneNumbersBlock-module__number--Fkfoh.PhoneNumbersBlock-module__numberHover--GntRY")
    
    numbers = [button.text for button in buttons]
    
    return numbers



def check_phone_num(target_num, loop=None):
    short_num = shorten_num(target_num)
    match_num = None
    numbers = None

    driver = setup_driver(1080, 1920)

    try:
        driver.get(PAGE_LINK)
        driver.quit()
        print('quit')
    except TimeoutException:
        try:
            check_for_captcha(driver)

            time.sleep(1)

            enter_phone_num(driver, short_num)

            time.sleep(10)

            expand_all_sections(driver)

            time.sleep(1)

            numbers = get_all_numbers(driver)

            time.sleep(1)

            print('NUBERS:')
            print(numbers)
            match_num = target_num in numbers

            if match_num:
                print('PHONE MATCH_FOUND')
                print_ascii_code('match_found')
            else:
                print('PHONE NO_MATCH')
                print_ascii_code('no_match')

            driver.quit()
            print('quit')
        except Exception as e:
            driver.quit()
            print('quit')
            print(f'An exception occurred: {e}.')
            print_ascii_code('error')
            loop and asyncio.run_coroutine_threadsafe(msg_queue.put({'result': 'error', 'msg': e}), loop)

    return match_num, numbers



def run_periodically(loop=None):
    cycle = 1
    
    while not stop_event.is_set():
        print(ascii_msg(f'Cycle {cycle}'))
        
        target_num = get_phone_num()
        result, numbers = run_until_long_enough(target_num, loop)

        to_put = {'result': result, 'cycle': cycle, 'target_num': target_num, 'numbers': numbers}
        loop and asyncio.run_coroutine_threadsafe(msg_queue.put(to_put), loop)
        print(f'Q PUT: {str(cycle)}, {str(result)}')

        if result is True:
            print("Function returned True. Stopping.")
            loop and asyncio.run_coroutine_threadsafe(msg_queue.put(None), loop)
            stop_event.set()
            return True
        elif result is None:
            print("Function returned None. Running again immediately...")
            if stop_event.is_set(): return
        elif result is False:
            print(f"Cycle {cycle}: Function returned False. Waiting until next minute...")
            cycle += 1
            if stop_event.is_set(): return
            time.sleep(60 - time.time() % 60)
        else:
            print("Function returned unexpected result.")
            print_ascii_code('error')
            loop and asyncio.run_coroutine_threadsafe(msg_queue.put(None), loop)
            stop_event.set()
            return 'error'
    
    loop and asyncio.run_coroutine_threadsafe(msg_queue.put(None), loop)
    stop_event.set()
    print("Bot checking routine has been stopped.")
    return 'bot_stopped'

def run_until_long_enough(target_num, loop=None, min_time=5):
    print(f'LOOP IS: {loop}')
    while True:
        try:
            start_time = time.time()
            
            match_num, numbers = check_phone_num(target_num, loop)
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            if execution_time < min_time:
                print(f"Execution time {execution_time:.2f} sec < {min_time} sec. Running again...")
            else:
                return match_num, numbers
        except Exception as e:
            print(f'An exception occurred: {e}.')
            print_ascii_code('error')
            loop and asyncio.run_coroutine_threadsafe(msg_queue.put({'result': 'error', 'msg': e}), loop)
            continue



if __name__ == "__main__":
    set_phone_num('+7 123 456 7890')
    run_periodically()