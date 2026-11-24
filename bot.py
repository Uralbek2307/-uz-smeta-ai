import os, math, logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters


logging.basicConfig(level=logging.INFO)
TOKEN=os.getenv('TELEGRAM_BOT_TOKEN')

MENU=ReplyKeyboardMarkup([
 ['🧱 G‘isht hisoblash', '🪨 Beton hisoblash'],
 ['🎨 Suvoq/bo‘yoq', '🧮 Smeta tuzish'],
 ['ℹ️ Yordam']
], resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        'UZ SMETA AI — qurilish hisob-kitob yordamchisi.\n\n'
        'Miqdorlar formula asosida hisoblanadi; narxlarni o‘zing kiritasan.\n'
        'Kerakli xizmatni menyudan tanla.', reply_markup=MENU)

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Hisoblash buyruqlari:\n'
        '/brick — g‘isht devor (uzunlik, balandlik, qalinlik, g‘isht o‘lchami)\n'
        '/concrete — beton hajmi (uzunlik × kenglik × qalinlik)\n'
        '/area — yuzani hisoblash (uzunlik × kenglik)\n'
        '/smeta — materiallar va ishlar ro‘yxatidan smeta\n\n'
        'Smeta format: Har qatorda nom;miqdor;birlik;narx.\n'
        'Masalan:\nBeton;5;m3;950000\nArmatura;300;kg;12000\nG‘isht terish;80;m2;45000\nTugatish: /done')

async def brick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['mode']='brick'
    await update.message.reply_text('Devor uzunligi (m), balandligi (m), qalinligi (m) ni vergul bilan yoz.\nMisol: 10,3,0.38')

async def concrete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['mode']='concrete'
    await update.message.reply_text('Beton uzunligi, kengligi, qalinligini metrda yoz.\nMisol: 12,0.4,0.6')

async def area_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['mode']='area'
    await update.message.reply_text('Uzunlik va kenglikni metrda yoz.\nMisol: 5,4')

async def smeta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['mode']='smeta'
    context.user_data['items']=[]
    await update.message.reply_text('Smeta qatorlarini yubor. Har qator format: nom;miqdor;birlik;narx\nMasalan: Beton;5;m3;950000\nTugatish uchun /done yoz.')

async def done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    items=context.user_data.get('items',[])
    if not items:
        await update.message.reply_text('Smetada qator yo‘q. /smeta orqali boshlang.')
        return
    total=sum(q*p for _,q,unit,p in items)
    lines=['📋 SMETA','']+[f'{name}: {q:g} {unit} × {price:,.0f} = {q*price:,.0f} so‘m' for name,q,unit,price in items]
    lines += ['',f'JAMI: {total:,.0f} so‘m']
    await update.message.reply_text('\n'.join(lines))
    context.user_data['mode']=None

async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text=update.message.text.strip()
    if text=='🧱 G‘isht hisoblash': return await brick(update,context)
    if text=='🪨 Beton hisoblash': return await concrete(update,context)
    if text=='🎨 Suvoq/bo‘yoq':
        context.user_data['mode']='finish'
        return await update.message.reply_text('Devor yuzasi m², suvoq qalinligi mm, sarf kg/m²/mm (odatda 1.5), narx so‘m/kg ni vergul bilan yoz.\nMisol: 120,15,1.5,2500')
    if text=='🧮 Smeta tuzish': return await smeta(update,context)
    if text=='ℹ️ Yordam': return await help_cmd(update,context)
    mode=context.user_data.get('mode')
    try:
        vals=[float(x.strip().replace(',','.')) for x in text.split(',')]
    except Exception:
        vals=[]
    if mode=='brick':
        if len(vals)!=3 or min(vals)<=0:
            return await update.message.reply_text('3 ta musbat son kerak: uzunlik, balandlik, qalinlik. Masalan: 10,3,0.38')
        length,height,thick=vals
        wall_vol=length*height*thick
        # nominal brick dimensions 250x120x65 mm, mortar-inclusive estimate 0.002 bricks/m3
        bricks=wall_vol*400
        await update.message.reply_text(f'📐 Devor hajmi: {wall_vol:.3f} m³\n🧱 Taxminiy g‘isht: {bricks:,.0f} dona (1 m³ ≈ 400 dona, qorishma va kesimlar hisobga olinmagan).\nZaxira bilan 5% qo‘shilsa: {bricks*1.05:,.0f} dona.\nBu taxmin; g‘isht turi va chok o‘lchamiga qarab tekshiriladi.')
        context.user_data['mode']=None
    elif mode=='concrete':
        if len(vals)!=3 or min(vals)<=0:
            return await update.message.reply_text('3 ta musbat son kerak: uzunlik, kenglik, qalinlik. Misol: 12,0.4,0.6')
        vol=vals[0]*vals[1]*vals[2]
        await update.message.reply_text(f'🪨 Beton hajmi: {vol:.3f} m³\n5% zaxira bilan: {vol*1.05:.3f} m³.\nBuyurtma hajmini konstruktiv loyiha va beton yo‘qotishlariga qarab tekshir.')
        context.user_data['mode']=None
    elif mode=='area':
        if len(vals)!=2 or min(vals)<=0:
            return await update.message.reply_text('Uzunlik va kenglik 2 ta musbat son bo‘lishi kerak. Misol: 5,4')
        await update.message.reply_text(f'📏 Maydon: {vals[0]*vals[1]:.3f} m²')
        context.user_data['mode']=None
    elif mode=='finish':
        if len(vals)!=4 or min(vals[:3])<=0 or vals[3]<0:
            return await update.message.reply_text('4 son: yuzasi, qalinlik (mm), sarf (kg/m²/mm), narx (so‘m/kg). Misol: 120,15,1.5,2500')
        surface,thickness,rate,price=vals
        kg=surface*thickness*rate
        await update.message.reply_text(f'🎨 Material sarfi: {kg:.1f} kg\n💰 Narxi: {kg*price:,.0f} so‘m\nHisob me’yoriy sarfga asoslangan; mahsulot yorlig‘idagi sarfni tekshir.')
        context.user_data['mode']=None
    elif mode=='smeta':
        if text.lower()=='/done': return await done(update,context)
        try:
            name,qty,unit,price=text.split(';')
            qty=float(qty); price=float(price)
            if qty<0 or price<0: raise ValueError()
            context.user_data.setdefault('items',[]).append((name.strip(),qty,unit.strip(),price))
            await update.message.reply_text(f'Qo‘shildi: {name.strip()} — {qty:g} {unit.strip()} × {price:,.0f} = {qty*price:,.0f} so‘m. Yana qator yubor yoki /done.')
        except Exception:
            await update.message.reply_text('Format noto‘g‘ri. To‘g‘ri format: nom;miqdor;birlik;narx\nMisol: Beton;5;m3;950000')
    else:
        await update.message.reply_text('Menyudan tanlang yoki /help buyrug‘ini yuboring.', reply_markup=MENU)

app=None
def main():
    if not TOKEN:
        raise RuntimeError('TELEGRAM_BOT_TOKEN env var is missing. Set your bot token in .env or hosting settings.')
    application=Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler('start',start))
    application.add_handler(CommandHandler('help',help_cmd))
    application.add_handler(CommandHandler('brick',brick))
    application.add_handler(CommandHandler('concrete',concrete))
    application.add_handler(CommandHandler('area',area_cmd))
    application.add_handler(CommandHandler('smeta',smeta))
    application.add_handler(CommandHandler('done',done))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,on_text))
    application.run_polling()
if __name__=='__main__': main()
