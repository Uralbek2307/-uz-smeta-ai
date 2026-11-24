import os
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, ContextTypes, filters

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
BASE_URL = os.getenv('RENDER_EXTERNAL_URL', '').rstrip('/')
PORT = int(os.getenv('PORT', '10000'))

MENU = ReplyKeyboardMarkup(
    [[KeyboardButton('🧱 G‘isht hisoblash'), KeyboardButton('🧱 Beton hisoblash')],
     [KeyboardButton('📐 Maydon hisoblash'), KeyboardButton('🪣 Suvoq hisoblash')],
     [KeyboardButton('🧾 Smeta tuzish')]], resize_keyboard=True
)

WALL_LEN, WALL_HEIGHT, WALL_THICK, CON_L, CON_W, CON_D, AREA_L, AREA_W, PL_AREA, PL_THICK, PL_RATE, PL_PRICE, SMETA_NAME, SMETA_PRICE, SMETA_MORE = range(15)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('UZ SMETA AI\nQurilish hajmlarini taxminiy hisoblash yordamchisi. Menyudan bo‘lim tanlang.', reply_markup=MENU)


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Menyudan hisob turini tanlang. Bekor qilish: /cancel. Smeta uchun /done bilan yakunlang.', reply_markup=MENU)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text('Hisob bekor qilindi.', reply_markup=MENU)
    return ConversationHandler.END


async def wall_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Devor uzunligini metrda kiriting (masalan 12.5):')
    return WALL_LEN
async def wall_len(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try: context.user_data['wl'] = float(update.message.text.replace(',', '.'))
    except ValueError: await update.message.reply_text('Son kiriting.'); return WALL_LEN
    await update.message.reply_text('Devor balandligi (metr):')
    return WALL_HEIGHT
async def wall_height(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try: context.user_data['wh'] = float(update.message.text.replace(',', '.'))
    except ValueError: await update.message.reply_text('Son kiriting.'); return WALL_HEIGHT
    await update.message.reply_text('Devor qalinligi (metrda, masalan 0.25):')
    return WALL_THICK
async def wall_thick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try: t = float(update.message.text.replace(',', '.'))
    except ValueError: await update.message.reply_text('Son kiriting.'); return WALL_THICK
    if t <= 0: await update.message.reply_text('Qalinlik 0 dan katta bo‘lsin.'); return WALL_THICK
    volume = context.user_data['wl'] * context.user_data['wh'] * t
    bricks = volume * 400
    await update.message.reply_text(f'Devor hajmi: {volume:.3f} m³\nTaxminiy g‘isht: {bricks:.0f} dona (400 dona/m³ taxmin).', reply_markup=MENU)
    return ConversationHandler.END


async def concrete_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Beton uzunligi (metr):')
    return CON_L
async def concrete_l(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try: context.user_data['cl'] = float(update.message.text.replace(',', '.'))
    except ValueError: await update.message.reply_text('Son kiriting.'); return CON_L
    await update.message.reply_text('Beton eni (metr):')
    return CON_W
async def concrete_w(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try: context.user_data['cw'] = float(update.message.text.replace(',', '.'))
    except ValueError: await update.message.reply_text('Son kiriting.'); return CON_W
    await update.message.reply_text('Beton qalinligi/balandligi (metr):')
    return CON_D
async def concrete_d(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try: d = float(update.message.text.replace(',', '.'))
    except ValueError: await update.message.reply_text('Son kiriting.'); return CON_D
    v = context.user_data['cl'] * context.user_data['cw'] * d
    await update.message.reply_text(f'Beton hajmi: {v:.3f} m³\n5% zaxira bilan: {v*1.05:.3f} m³', reply_markup=MENU)
    return ConversationHandler.END

async def area_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Uzunlik (metr):')
    return AREA_L
async def area_l(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try: context.user_data['al'] = float(update.message.text.replace(',', '.'))
    except ValueError: await update.message.reply_text('Son kiriting.'); return AREA_L
    await update.message.reply_text('En (metr):')
    return AREA_W
async def area_w(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try: w = float(update.message.text.replace(',', '.'))
    except ValueError: await update.message.reply_text('Son kiriting.'); return AREA_W
    await update.message.reply_text(f'Maydon: {context.user_data["al"]*w:.3f} m²', reply_markup=MENU)
    return ConversationHandler.END

async def plaster_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Suvoq qilinadigan maydon (m²):')
    return PL_AREA
async def plaster_area(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try: context.user_data['pa'] = float(update.message.text.replace(',', '.'))
    except ValueError: await update.message.reply_text('Son kiriting.'); return PL_AREA
    await update.message.reply_text('Suvoq qalinligi (mm):')
    return PL_THICK
async def plaster_thick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try: context.user_data['pt'] = float(update.message.text.replace(',', '.'))
    except ValueError: await update.message.reply_text('Son kiriting.'); return PL_THICK
    await update.message.reply_text('1 m² uchun 1 mm qatlamda sarf (kg) — qopdagi ko‘rsatkichni kiriting:')
    return PL_RATE
async def plaster_rate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try: context.user_data['pr'] = float(update.message.text.replace(',', '.'))
    except ValueError: await update.message.reply_text('Son kiriting.'); return PL_RATE
    kg = context.user_data['pa'] * context.user_data['pt'] * context.user_data['pr']
    context.user_data['plaster_kg'] = kg
    await update.message.reply_text(f'Taxminiy material: {kg:.2f} kg\n1 kg narxini so‘mda kiriting (narxni o‘zingiz bilgan qop/mahsulot narxiga qarab):')
    return PL_PRICE
async def plaster_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try: price = float(update.message.text.replace(',', '.'))
    except ValueError: await update.message.reply_text('Son kiriting.'); return PL_PRICE
    kg = context.user_data['plaster_kg']
    await update.message.reply_text(f'Material: {kg:.2f} kg\nTaxminiy qiymat: {kg*price:,.0f} so‘m', reply_markup=MENU)
    return ConversationHandler.END

async def smeta_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['items'] = []
    await update.message.reply_text('Smeta bandi nomini kiriting (masalan: sement). /done — yakunlash')
    return SMETA_NAME
async def smeta_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['item_name'] = update.message.text.strip()
    await update.message.reply_text('Ushbu bandning jami narxini so‘mda kiriting:')
    return SMETA_PRICE
async def smeta_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try: amount = float(update.message.text.replace(',', '.'))
    except ValueError: await update.message.reply_text('Narxni raqamda kiriting.'); return SMETA_PRICE
    context.user_data['items'].append((context.user_data['item_name'], amount))
    total = sum(x[1] for x in context.user_data['items'])
    await update.message.reply_text(f'Band qo‘shildi. Hozirgi jami: {total:,.0f} so‘m\nYana band kiriting yoki /done bosing.')
    return SMETA_NAME
async def smeta_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    items = context.user_data.get('items', [])
    if not items:
        await update.message.reply_text('Smeta bo‘sh. Menyudan qayta boshlang.', reply_markup=MENU)
    else:
        lines = [f'{i}. {name}: {price:,.0f} so‘m' for i, (name, price) in enumerate(items, 1)]
        total = sum(p for _, p in items)
        await update.message.reply_text('🧾 SMETA\n' + '\n'.join(lines) + f'\n\nJAMI: {total:,.0f} so‘m', reply_markup=MENU)
    context.user_data.clear()
    return ConversationHandler.END

async def text_fallback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    routes = {'🧱 G‘isht hisoblash': wall_start, '🧱 Beton hisoblash': concrete_start, '📐 Maydon hisoblash': area_start, '🪣 Suvoq hisoblash': plaster_start, '🧾 Smeta tuzish': smeta_start}
    if text in routes: return await routes[text](update, context)
    await update.message.reply_text('Menyudan bo‘lim tanlang yoki /help yuboring.', reply_markup=MENU)


def main():
    if not TOKEN: raise RuntimeError('TELEGRAM_BOT_TOKEN env var is required')
    if not BASE_URL: raise RuntimeError('Render external URL missing; deploy as Render Web Service')
    app = Application.builder().token(TOKEN).build()
    conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^(🧱 G‘isht hisoblash)$'), wall_start), MessageHandler(filters.Regex('^(🧱 Beton hisoblash)$'), concrete_start), MessageHandler(filters.Regex('^(📐 Maydon hisoblash)$'), area_start), MessageHandler(filters.Regex('^(🪣 Suvoq hisoblash)$'), plaster_start), MessageHandler(filters.Regex('^(🧾 Smeta tuzish)$'), smeta_start)],
        states={
            WALL_LEN:[MessageHandler(filters.TEXT & ~filters.COMMAND, wall_len)], WALL_HEIGHT:[MessageHandler(filters.TEXT & ~filters.COMMAND, wall_height)], WALL_THICK:[MessageHandler(filters.TEXT & ~filters.COMMAND, wall_thick)],
            CON_L:[MessageHandler(filters.TEXT & ~filters.COMMAND, concrete_l)], CON_W:[MessageHandler(filters.TEXT & ~filters.COMMAND, concrete_w)], CON_D:[MessageHandler(filters.TEXT & ~filters.COMMAND, concrete_d)],
            AREA_L:[MessageHandler(filters.TEXT & ~filters.COMMAND, area_l)], AREA_W:[MessageHandler(filters.TEXT & ~filters.COMMAND, area_w)],
            PL_AREA:[MessageHandler(filters.TEXT & ~filters.COMMAND, plaster_area)], PL_THICK:[MessageHandler(filters.TEXT & ~filters.COMMAND, plaster_thick)], PL_RATE:[MessageHandler(filters.TEXT & ~filters.COMMAND, plaster_rate)], PL_PRICE:[MessageHandler(filters.TEXT & ~filters.COMMAND, plaster_price)],
            SMETA_NAME:[CommandHandler('done', smeta_done), MessageHandler(filters.TEXT & ~filters.COMMAND, smeta_name)], SMETA_PRICE:[MessageHandler(filters.TEXT & ~filters.COMMAND, smeta_price)],
        }, fallbacks=[CommandHandler('cancel', cancel), CommandHandler('start', start)], allow_reentry=True
    )
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help_cmd))
    app.add_handler(CommandHandler('cancel', cancel))
    app.add_handler(conv)
    app.add_handler(CommandHandler('done', smeta_done))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_fallback))
    log.info('Starting webhook on port %s with url %s', PORT, BASE_URL)
    app.run_webhook(listen='0.0.0.0', port=PORT, webhook_url=BASE_URL, url_path='', drop_pending_updates=True)

if __name__ == '__main__':
    main()
