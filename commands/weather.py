import requests
from random import choice
from datetime import time
import pytz

from telegram import Update
from telegram.ext import CallbackContext

from commands.decorators import member_exclusive
from config.logger import log_command
from utils import try_msg

def intro() -> str:
   """
   Generates a random "good morning" message
   """ 
   gm = [
            "BUENOS DÍAS OFIPAPITAS!!!",
            "Buenos días 🌞",
            "CÓMO ESTÁ EL GRUPO MÁS BUENO PAL web-EO?!",
            "HOLA",
            "bdo",
            "buenos días grupazo!!!",
            "monitos días,,,",
            "ola buebos días",
            "ooct",
            "beunos días",
            "cómo está el grupo más bueno pal lunes",
            "buenos dias amiguites",
            "ola buenos dias",
            "/buenosDiasOfipapitas",
            "buenos dias c:",
            "Buenos dias mi gente",
            "Buenos dias bbs",
            "/buenosDiasAmoTuSonrisa",
            "/buenosdias@ofipapinhos",
            "yoyoyo what's up GAMERS?👾?🎮?",
            "Bom dia",
            "La vida es más dulce si le sonries... Buenos días"
            "Comienza tu día declarando DIOS TIENE COSAS BUENAS PARA MI!!!",
            "bdoct",
            "saludos a todxs los valientes que ya se levantaron",
            "wakey, wakey, ofisalita",
            "good morning ofisaleet-a",
            "wake up samurai",
    ]
   presentation = [
            "les traigo el clima",
            "acá tengo el clima del día",
            "veamos como estará el climilla hoy",
            "le tenimos el clima pa stgo",
            "y ahora... _el clima_:",
            "lo vi en un sueño, el clima de hoy",
            "el clima según yo:",
            "hoy día...",
            "comparemos los climas de ayer y hoy!!!1!",
            "al que le sirva el clima:",
            "clima pal que lee:",
            "al que madruga el clima le ayuda" ,
            "cachen el clima",
    ]
   return choice(gm)+"\n"+choice(presentation)+"\n"

def weather_emoji(mnTemp,mxTemp,prec) -> str:
    """
    Calculates an apropiate emoji for the given weather
    """
    avg = (int(mnTemp)+int(mxTemp))/2
    
    if prec>10:
        return "🌧"
    elif avg<12:
        return "❄️"
    elif avg<15:
        return "🌤"
    elif avg<18:
        return "😎"
    else:
        return "☀️"

def prec_msg(yest,today) -> str:
    if yest == 0 and today == 0:
        return ""
    elif today == 0:
        ayer_si = [
                "parece que ya pasó la lluvia",
                "risk of rain: none",
                "abrigate que va a hacer frío wuaja",
        ]
        return choice(ayer_si)
    elif yest-20 > today:
        mucho_menos = [
                "no va a llover tanto como ayer",
                "ayer llovió harto, no será tanto hoy",
        ]
        return choice(mucho_menos)
    elif yest-10 > today:
        menos = [
                "hoy va a llover menos que ayer, pero no sé si me confiaría",
                "al ojo llueve menos",
        ]
        return choice(menos)
    elif yest > today or yest < today-10:
        igual = [
                "debería llover lo mismo hoy que ayer",
                "la lluvia se mantendrá como ayer",
        ]
        return choice(igual) 
    elif yest < today-20:
        mas = [
                "mañana llueve más, prepararse",
                "se viene lluvia, cuidadito",
        ]
        return choice(mas)
    elif yest < today:
        harto = [
                "si este bot está bien programado, mañana llueve harto",
                "WARNING: RISK OF RAIN",
        ]
        return choice(harto)
    else:
        "hubo un error en la predicción de lluvia :("


def forecast() -> None:
    """
    Calculates today's and yesterday's forecasts
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = dict(
            latitude="-33.4569",
            longitude="-70.6483",
            hourly="temperature_2m,precipitation",
            timezone="auto",
            past_days="1",
            forecast_days="1"
    )

    response = requests.get(url=url, params=params)

    data = response.json()
    temp = data["hourly"]["temperature_2m"]
    prec = data["hourly"]["precipitation"]

    i = 7
    f = 22

    mnYest = str(round(min(temp[i:f])))
    mxYest = str(round(max(temp[i:f])))
    precYest = sum(prec[i:f])/(f-i)
    emojiYest = weather_emoji(mnYest,mxYest,precYest)
    tempYest = "Ayer: "+emojiYest+" "+mnYest+"/"+mxYest+"°C"

    mnToday = str(round(min(temp[i+24:f+24])))
    mxToday = str(round(max(temp[i+24:f+24])))
    precToday = sum(prec[i+24:f+24])/(f-i)
    emojiToday = weather_emoji(mnToday,mxToday,precToday)
    tempToday = "Hoy: "+emojiToday+" "+mnToday+"/"+mxToday+"°C"

    return tempYest, tempToday, prec_msg(precYest,precToday)

def weather(context: CallbackContext) -> None:
    """
    Tells the weather forecast for the day
    """
    tempYest, tempToday, prec = forecast()
    message = intro()+tempYest+"\n"+tempToday+"\n"+prec

    try_msg(context.bot,
            chat_id=context.job.context,
            parse_mode="markdown",
            text=message)

def enable_weather(update: Update, context: CallbackContext) -> None:
    """
    Enables the weather forecast everyday
    """
    context.job_queue.run_daily(weather, time=time(hour=7, minute=0, tzinfo=pytz.timezone('America/Santiago')), context=update.message.chat_id)
