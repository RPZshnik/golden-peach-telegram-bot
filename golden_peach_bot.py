import io
import plotly.io as pio
import plotly.graph_objs as go
import requests
from datetime import datetime
import locale
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram import executor
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.dispatcher.filters import Text
from crypto_handlers import CRYPTO_HANDLERS
from coingecko import CoinGecko
import os
from dotenv import load_dotenv

load_dotenv()
locale.setlocale(locale.LC_ALL, '')

coingecko = CoinGecko()

inline_spot_kb = InlineKeyboardMarkup(row_width=3).insert(InlineKeyboardButton(text='USD', callback_data='usd')).insert(
    InlineKeyboardButton(text='BTC', callback_data='btc')) \
    .insert(InlineKeyboardButton(text='ETH', callback_data='eth'))

inline_usd_kb = InlineKeyboardMarkup(row_width=2).insert(InlineKeyboardButton(text='BTC', callback_data='btc_usd')). \
    insert(InlineKeyboardButton(text='ETH', callback_data='eth_usd')). \
    insert(InlineKeyboardButton(text='XRP', callback_data='xrp_usd')). \
    insert(InlineKeyboardButton(text='DOGE', callback_data='doge_usd')). \
    add(InlineKeyboardButton(text='Show all', callback_data='show_all_usd')). \
    add(InlineKeyboardButton(text='🔙 Back to menu', callback_data='back_to_menu'))

inline_btc_kb = InlineKeyboardMarkup(row_width=2).insert(InlineKeyboardButton(text='ETH', callback_data='eth_btc')). \
    insert(InlineKeyboardButton(text='LTC', callback_data='ltc_btc')). \
    insert(InlineKeyboardButton(text='XRP', callback_data='xrp_btc')). \
    insert(InlineKeyboardButton(text='DOGE', callback_data='doge_btc')). \
    add(InlineKeyboardButton(text='Show all', callback_data='show_all_btc')) \
    .add(InlineKeyboardButton(text='Coin full info', callback_data='btc_get_full_info')) \
    .add(InlineKeyboardButton(text='Coin chart', callback_data='btc_get_coin_chart')) \
    .add(InlineKeyboardButton(text='🔙 Back to menu', callback_data='back_to_menu'))

inline_eth_kb = InlineKeyboardMarkup(row_width=2).insert(InlineKeyboardButton(text='BTC', callback_data='btc_eth')). \
    insert(InlineKeyboardButton(text='XRP', callback_data='xrp_eth')). \
    insert(InlineKeyboardButton(text='DOGE', callback_data='doge_eth')). \
    insert(InlineKeyboardButton(text='LTC', callback_data='ltc_eth')). \
    add(InlineKeyboardButton(text='Show all', callback_data='show_all_btc')) \
    .add(InlineKeyboardButton(text='Coin full info', callback_data='eth_get_full_info')) \
    .add(InlineKeyboardButton(text='Coin chart', callback_data='eth_get_coin_chart')) \
    .add(InlineKeyboardButton(text='🔙 Back to menu', callback_data='back_to_menu'))

inline_back_kb = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton(text='🔙 Back to menu', callback_data='back_to_menu'))

static_kb = ReplyKeyboardMarkup(resize_keyboard=True)
static_kb.insert(KeyboardButton(text='🏠 Menu'))


class GoldenPeachBot:
    token = os.getenv('TG_TOKEN')
    bot = Bot(token)
    dp = Dispatcher(bot)

    def start(self):
        executor.start_polling(self.dp, skip_updates=True)
        print('Bot is Online')

    @dp.message_handler(commands=['start', 'help'])
    async def start_command(self, message: types.Message):
        await self.bot.send_message(message.from_user.id,
                                    '*Hello there!* 👋\n\n'
                                    'To start using *Golden Peach* type /menu or hit the corresponding button on the keyboard.',
                                    parse_mode='Markdown', reply_markup=static_kb)

    @staticmethod
    @dp.message_handler(commands=['menu'])
    async def load_menu(message: types.Message):
        await GoldenPeachBot.bot.send_message(message.from_user.id, 'Welcome to *CryptoAssist* menu!',
                                              parse_mode='Markdown', reply_markup=ReplyKeyboardRemove())
        await GoldenPeachBot.bot.send_message(message.from_user.id, 'Select one of the markets below. 👇',
                                              parse_mode='Markdown', reply_markup=inline_spot_kb)

    @staticmethod
    @dp.callback_query_handler(text='usd')
    async def usd_callback(callback: types.CallbackQuery):
        await callback.answer()
        await callback.message.edit_text("You have picked *USD*, nice!\nNow let's pick a crypto.",
                                         parse_mode='Markdown')
        await callback.message.edit_reply_markup(reply_markup=inline_usd_kb)

    @staticmethod
    @dp.callback_query_handler(text='btc')
    async def btc_callback(callback: types.CallbackQuery):
        await callback.answer()
        await callback.message.edit_text("You have picked *BTC*, nice!\nNow let's pick a crypto.",
                                         parse_mode='Markdown')
        await callback.message.edit_reply_markup(reply_markup=inline_btc_kb)

    @staticmethod
    @dp.callback_query_handler(text='eth')
    async def eth_callback(callback: types.CallbackQuery):
        await callback.answer()
        await callback.message.edit_text("You have picked *ETH*, nice!\nNow let's pick a crypto.",
                                         parse_mode='Markdown')
        await callback.message.edit_reply_markup(reply_markup=inline_eth_kb)

    @staticmethod
    @dp.callback_query_handler(text='back_to_menu')
    async def back_to_menu_command(callback: types.CallbackQuery):
        await callback.answer()
        await callback.message.edit_text('Select one of the markets below. 👇')
        await callback.message.edit_reply_markup(reply_markup=inline_spot_kb)

    @staticmethod
    @dp.callback_query_handler(Text(endswith='_get_full_info'))
    async def full_info_handler(callback: types.CallbackQuery):
        curr = callback.data.split('_')[0]
        res = GoldenPeachBot.get_full_info(curr)
        await callback.answer()
        await callback.message.edit_text(res)
        await GoldenPeachBot.bot.send_message(callback.message.chat.id,
                                              'You can now go back to */menu* and select another crypto.',
                                              parse_mode='Markdown', reply_markup=static_kb)

    @staticmethod
    @dp.callback_query_handler(Text(endswith='_get_coin_chart'))
    async def coin_chart_handler(callback: types.CallbackQuery):
        curr = callback.data.split('_')[0]
        fig = GoldenPeachBot.get_coin_chart(curr)
        await GoldenPeachBot.bot.send_photo(callback.message.chat.id,
                                            photo=io.BufferedReader(io.BytesIO(pio.to_image(fig, format="jpeg"))),
                                            parse_mode="Markdown")
        await GoldenPeachBot.bot.send_message(callback.message.chat.id,
                                              'You can now go back to */menu* and select another crypto.',
                                              parse_mode='Markdown', reply_markup=static_kb)

    @staticmethod
    @dp.callback_query_handler(Text(startswith='show_all_'))
    async def show_all_handler(callback: types.CallbackQuery):
        curr = callback.data.split('_')[2]
        arr = CRYPTO_HANDLERS
        if curr in arr:
            arr.remove(curr)
        res = ''
        for i in arr:
            res += GoldenPeachBot.get_price_data(f'{i}_{curr}') + '\n\n'
        await callback.answer()
        await callback.message.edit_text(res, parse_mode='Markdown')
        await GoldenPeachBot.bot.send_message(callback.message.chat.id,
                                              'You can now go back to */menu* and select another crypto.',
                                              parse_mode='Markdown', reply_markup=static_kb)

    @staticmethod
    @dp.callback_query_handler(Text(endswith='_usd'))
    async def usd_query_handler(callback: types.CallbackQuery):
        await callback.answer()
        await callback.message.edit_text(GoldenPeachBot.get_price_data(callback.data), parse_mode='Markdown')
        await GoldenPeachBot.bot.send_message(callback.message.chat.id,
                                              'You can now go back to */menu* and select another crypto.',
                                              parse_mode='Markdown', reply_markup=static_kb)

    @staticmethod
    @dp.callback_query_handler(Text(endswith='_btc'))
    async def btc_query_handler(callback: types.CallbackQuery):
        await callback.answer()
        await callback.message.edit_text(GoldenPeachBot.get_price_data(callback.data), parse_mode='Markdown')
        await GoldenPeachBot.bot.send_message(callback.message.chat.id,
                                              'You can now go back to */menu* and select another crypto.',
                                              parse_mode='Markdown', reply_markup=static_kb)

    @staticmethod
    @dp.callback_query_handler(Text(endswith='_eth'))
    async def eth_query_handler(callback: types.CallbackQuery):
        await callback.answer()
        await callback.message.edit_text(GoldenPeachBot.get_price_data(callback.data), parse_mode='Markdown')
        await GoldenPeachBot.bot.send_message(callback.message.chat.id,
                                              'You can now go back to */menu* and select another crypto.',
                                              parse_mode='Markdown', reply_markup=static_kb)

    @staticmethod
    @dp.message_handler()
    async def echo(message: types.Message):
        if message.text == '🏠 Menu':
            await GoldenPeachBot.bot.send_message(message.from_user.id, 'Welcome to *CryptoAssist* menu!',
                                                  parse_mode='Markdown', reply_markup=ReplyKeyboardRemove())
            await GoldenPeachBot.bot.send_message(message.from_user.id,
                                                  'Select one of the markets below. 👇',
                                                  parse_mode='Markdown', reply_markup=inline_spot_kb)
        else:
            await GoldenPeachBot.bot.send_message(message.from_user.id, "I don't understand you, bruh.\nType */help*.",
                                                  parse_mode='Markdown')

    @staticmethod
    def add_whitespaces(item, prev_word: str):
        string = " " * (20 - len(str(prev_word))) + str(item)
        return string

    @staticmethod
    def get_prices(coin_info):
        prices = {"usd": coin_info["market_data"]["current_price"]["usd"],
                  "eur": coin_info["market_data"]["current_price"]["eur"],
                  "uan": coin_info["market_data"]["current_price"]["uah"]}
        return prices

    @staticmethod
    def get_price_change_percentage(coin_info):
        price_changes = {"Year": coin_info["market_data"]["price_change_percentage_1y_in_currency"]["usd"],
                         "Month": coin_info["market_data"]["price_change_percentage_30d_in_currency"]["usd"],
                         "Week": coin_info["market_data"]["price_change_percentage_7d_in_currency"]["usd"],
                         "Day": coin_info["market_data"]["price_change_percentage_24h_in_currency"]["usd"],
                         "Hour": coin_info["market_data"]["price_change_percentage_1h_in_currency"]["usd"]}
        return price_changes

    @staticmethod
    def get_full_info(coin_symbol):
        coin_id = coingecko.get_id_by_symbol(coin_symbol)
        coin_info = coingecko.get_coin_by_id(coin_id)
        prices = GoldenPeachBot.get_prices(coin_info)
        price_change_percentage = GoldenPeachBot.get_price_change_percentage(coin_info)
        market_cap_rank = coin_info["market_cap_rank"]
        market_cap = coin_info["market_data"]["market_cap"]["usd"]
        message = f"" \
                  f"{coin_id.upper()} ({coin_symbol})\n\n" \
                  f"USD       {prices['usd']}\n" \
                  f"EUR       {prices['eur']}\n" \
                  f"UAN       {prices['uan']}\n\n" \
                  f"Hour      {price_change_percentage['Hour']}\n" \
                  f"Day       {price_change_percentage['Day']}\n" \
                  f"Week     {price_change_percentage['Week']}\n" \
                  f"Month   {price_change_percentage['Month']}\n" \
                  f"Year      {price_change_percentage['Year']}\n\n\n" \
                  f"Market Cap Rank:     {market_cap_rank}\n\n" \
                  f"Market Cap:     {market_cap} USD\n"
        return message

    @staticmethod
    def get_coin_chart(coin_symbol):
        coin_id = coingecko.get_id_by_symbol(coin_symbol)
        coin_chart_info = list(reversed(coingecko.get_coin_market_chart_by_id(coin_id, "usd", 30)["prices"]))

        data = {"x": [], "open": [], "high": [], "low": [], "close": []}
        for index in range(0, len(coin_chart_info), 24):
            d = coin_chart_info[index: index + 24]
            data["x"].append(datetime.utcfromtimestamp(d[0][0] / 1000).strftime('%Y-%m-%d %H:%M:%S'))
            data["open"].extend([d[-1][1]])
            data["high"].extend([max([dd[1] for dd in d])])
            data["low"].extend([min([dd[1] for dd in d])])
            data["close"].extend([d[0][1]])

        fig = go.Figure(data=[go.Candlestick(x=data['x'],
                                             open=data['open'],
                                             high=data['high'],
                                             low=data['low'],
                                             close=data['close'])])
        fig['layout'].update(
            paper_bgcolor='rgb(233,233,233)',
            plot_bgcolor='rgb(233,233,233)',
            autosize=False,
            width=800,
            height=600,
            margin=go.layout.Margin(
                r=50,
                b=85,
                t=100,
                pad=4
            ))

        return fig

    @staticmethod
    def get_price_data(values):
        first, second = values.split("_")
        if first == "usd":
            values = f"{second}_{first}"
        req_str = 'https://yobit.net/api/3/ticker/' + values
        req = requests.get(req_str)
        response = req.json()
        sell_price = response[f'{values}']['sell']
        return f'*{datetime.now().strftime("%Y-%m-%d %H:%M")}*\nSell *{values.split("_")[0].upper()}/{values.split("_")[1].upper()}* 1 / {sell_price}'
