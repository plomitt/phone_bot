import os
import asyncio
import threading
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
from bot import run_periodically
from constants import PAGE_LINK
from helpers import check_num_format, get_msg_repeat, get_phone_num, set_phone_num, set_notifs_step, set_notifs_amnt
from shared import stop_event, msg_queue
from dotenv import load_dotenv

load_dotenv()

SET_NUM_STATE = 1
check_thread = None
loop = None

async def start(update, context):
    await update.message.reply_text("Hello! I am your bot. How can I help you?")

async def fallback(update, context):
    await update.message.reply_text("Invalid command. Please use /menu to see available options.")

async def set_notif_amount(update, context):
    num = set_notifs_amnt()
    await update.message.reply_text(f"Success notification amount set to: {num}")

async def set_notif_step(update, context):
    num = set_notifs_step()
    await update.message.reply_text(f"No-result notification interval set to: {num}")

async def get_num(update, context):
    try:
        num = get_phone_num()
        await update.message.reply_text(f"Current target num: {num}")
    except Exception as e:
        await update.message.reply_text(f"Error occured: {e}")

async def set_num_start(update, context):
    await update.message.reply_text("Please enter a number in the format +7 123 456 7890:")
    return SET_NUM_STATE

async def set_num_process(update, context):
    number = update.message.text

    if not check_num_format(number):
        await update.message.reply_text("Invalid number format. Please try again with +7 123 456 7890.")
        return SET_NUM_STATE
    
    set_phone_num(number)
    
    await update.message.reply_text(f"Num set to {number}")
    return ConversationHandler.END

async def cancel(update, context):
    await update.message.reply_text("Operation canceled.")
    return ConversationHandler.END

async def send_check_result(update, context):
    print('Sending thread started.')
    while not stop_event.is_set():
        item = await msg_queue.get()
        if item is None: break

        result = item['result']
        cycle = item['cycle']
        print(f'Q GET: {str(cycle)}, {str(result)}')

        chat_id = update.effective_chat.id

        if result != 'error':
            msg = f'MATCH_FOUND\n\nLink: {PAGE_LINK}' if result else 'NO_MATCH'
            msg += f'\nCycle: {str(cycle)}\nTarget: {str(item["target_num"])}\n\nNumbers: {str(item["numbers"])}'

            msg_repeat = get_msg_repeat(result, cycle)
        else:
            msg = f'ERROR!\n\n{item["msg"]}'
            msg_repeat = 1

        for i in range(msg_repeat):
            await context.bot.send_message(chat_id=chat_id, text=msg, disable_notification=not result)
            await asyncio.sleep(0.5)
    
    print('Sending thread stopped.')

async def start_check(update, context):
    global check_thread

    stop_event.clear()

    if check_thread and check_thread.is_alive():
        await update.message.reply_text("Checking is already running!")
        return

    await update.message.reply_text("Checking has started!")

    loop = asyncio.get_running_loop()

    check_thread = threading.Thread(target=run_periodically, args=[loop])
    check_thread.daemon = True
    check_thread.start()

    task2 = asyncio.create_task(send_check_result(update, context))

async def stop_check(update, context):
    if not stop_event.is_set():
        stop_event.set()
        await update.message.reply_text("Checking has stopped!")
    else:
        await update.message.reply_text("Checking is not running.")
        
    global check_thread
    global send_thread
    global loop
    if check_thread:
        check_thread.join()
        check_thread = None
        print('Checking thread stopped.')

async def post_init(application):   
    commands = [
        ("start", "Start the bot"),
        ("set_num", "Set a number"),
        ("get_num", "Get current target num"),
        ("start_check", "Start checking"),
        ("stop_check", "Stop checking"),
        ("set_notif_amount", "Set amount of notifications sent upon finding a match"),
        ("set_notif_step", "Set the interval between sending no-result notifications")
    ]
    await application.bot.set_my_commands(commands)

def main():
    application = Application.builder().token(os.getenv("TEL_BOT_TOKEN")).post_init(post_init).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("set_num", set_num_start)],
        states={
            SET_NUM_STATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_num_process)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("get_num", get_num))
    application.add_handler(CommandHandler("start_check", start_check))
    application.add_handler(CommandHandler("stop_check", stop_check))
    application.add_handler(CommandHandler("set_notif_amount", set_notif_amount))
    application.add_handler(CommandHandler("set_notif_step", set_notif_step))
    application.add_handler(MessageHandler(filters.ALL, fallback))

    application.run_polling()

if __name__ == "__main__":
    main()
