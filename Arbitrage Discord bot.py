import discord
import json
import http.client
from binance import Client
from discord.ext import commands
from functools import cache



api_key = 'YOUR API KEY'
api_secret = 'YOUR SECRET KEY'

clientbi = Client(api_key, api_secret)

client = commands.Bot(command_prefix = '$')



#Turn on discord bot
@client.event  
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


# Binance api price check

def check_price(symbol):
    prices = clientbi.get_all_tickers()
    EUR = [float(p['price']) for p in prices if p['symbol'] == symbol.upper()]
    return  round(EUR[0], 4)
      


# Binance p2p price check
def get_p2p_search_result(trade_type,number):
    conn = http.client.HTTPSConnection("p2p.binance.com")
    payload = json.dumps({
    "page": 1,
    "rows": 10,
    "payTypes": [],
    "asset": "USDT",
    "tradeType": trade_type,
    "fiat": "THB",
    "publisherType": None
    })
    headers = {
    'Content-Type': 'application/json',
    'Cookie': 'cid=lZ3VdnGV'
    }
    conn.request("POST", "/bapi/c2c/v2/friendly/c2c/adv/search", payload, headers)
    res = conn.getresponse()
    data = res.read()
    return json.loads(data.decode("utf-8"))['data'][number]['adv']['price']

def get_p2p_vol(trade_type, number,title):
    conn = http.client.HTTPSConnection("p2p.binance.com")
    payload = json.dumps({
    "page": 1,
    "rows": 10,
    "payTypes": [],
    "asset": "USDT",
    "tradeType": trade_type,
    "fiat": "THB",
    "publisherType": None
    })
    headers = {
    'Content-Type': 'application/json',
    'Cookie': 'cid=lZ3VdnGV'
    }
    conn.request("POST", "/bapi/c2c/v2/friendly/c2c/adv/search", payload, headers)
    res = conn.getresponse()
    data = res.read()
    return json.loads(data.decode("utf-8"))['data'][number]['adv'][title]



#Three current price of p2p buy and sell

def p2p_price_sell():
    price_sell = [get_p2p_search_result('SELL', p) for  p in range(3)]
    output_sell = ("\n".join(map(str, price_sell)))
    return output_sell

def p2p_price_buy():
    price_buy = [get_p2p_search_result('BUY', p) for  p in range(3)]
    output_buy = ("\n".join(map(str, price_buy)))
    return output_buy






@client.command(name = 'price')
async def binance_price(ctx, arg):
    embed = discord.Embed(title = arg.upper() + " PRICE")
    if arg.upper() == 'EURUSDT':
        EUR_price = round(1 / check_price(arg) , 4)
        embed.add_field(name = f'Current Price: ', value = f'{check_price(arg)} USDT \n or \n {EUR_price} EURO')
    else:    
        embed.add_field(name = f'Current Price: ', value = f'{check_price(arg)} USDT')
    embed.colour = 0x03df03
    
    await ctx.message.channel.send(embed = embed)

@client.command(name = 'p2p')
async def p2p(ctx, arg):
    if arg == 'vol':
        for i in range(9):
            if float(get_p2p_vol('SELL', i , 'maxSingleTransAmount' )) >= 250000:
                embed = discord.Embed(title = 'Volume p2p')
                embed.add_field(name = "volume:", value = str(get_p2p_search_result('SELL', i)))
                embed.colour = 0xff1010

    if arg == 'p':
        embed = discord.Embed(title = 'P2P prices')
        embed.add_field(name = 'BUY: ', value = p2p_price_buy())
        embed.add_field(name = "SELL: ", value = p2p_price_sell())
        embed.colour = 0xff1010

    await ctx.message.channel.send(embed = embed)

@client.command(name = 'clear')
async def name(ctx, amount = 2 ):
    await ctx.channel.purge(limit = amount)

    


#Discord message bot

@client.event  
async def on_message(message):
    if message.author == client.user:
        return 

    
   
    if message.content == '$p2p':
        embed = discord.Embed(title = 'P2P prices')
        embed.add_field(name = 'BUY: ', value = p2p_price_buy())
        embed.add_field(name = "SELL: ", value = p2p_price_sell())
        embed.colour = 0xff1010
        await message.channel.send(content = None, embed = embed)
  

    await client.process_commands(message)
         

client.run('YOUR DISCORD BOT')