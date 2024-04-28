## QAIBOT Discord Bot powered by OpenAI

This is a Discord bot with AI features, powered by GPT4.

Qaibot supports the following commands:

/qai, Ask QAI any question... answered using GPT4.
/joinconvo, Let QAI join the conversation (reads last 15 messages).
/summarize, QAI will summarize the content of a given URL.
/imback, I was away for a while, what happened while I was gone? Summarize the last 200 messages.
/pricewatch, Search for component prices on Tweakers Pricewatch.
/research, Let QAI research a topic on the web for you.
research takes 2 parameters :
    TOPIC : the topic to research
    DEPTH : quick, normal, deep

Research is probably the coolest option. It searches the web, summarizes websites and uses them as context to answer the research question.

## Requirements:

You need to have 3 things:

- DISCORD TOKEN
Get this from Discord developers portal
https://discord.com/developers/applications

- OPENAI API KEY
Get this from OpenAI (this costs money)
https://platform.openai.com

- GOOGLE API KEY
Get this from Google 
https://console.cloud.google.com/apis

## Instructions:
You must configure an .env file with your API keys
use .env.example as an example

## Starting the app:

Linux command line:
```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```