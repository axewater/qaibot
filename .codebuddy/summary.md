## Project Summary

### Overview
This project is a Discord bot called QAIBOT powered by OpenAI's GPT4. It includes various commands for interacting with the bot, such as asking questions to the AI, summarizing content from URLs, checking component prices, researching topics, and more.

### Languages, Frameworks, and Libraries Used
- Language: Python
- Framework: SQLAlchemy
- Libraries: discord.py, dotenv, urllib, json, logging

### Purpose
The purpose of the project is to provide a Discord bot with AI capabilities using OpenAI's GPT4. Users can interact with the bot to ask questions, summarize content, search for prices, and conduct research.

### Relevant Files
- `/app.py`: Main entry point for the application.
- `/bot/config.py`: Configuration file for storing API keys and settings.
- `/bot/database.py`: File for initializing the database and creating tables.
- `/bot/models.py`: Contains the database models for the bot.
- `/bot/commands/admin_settings.py`: Handles admin settings and interactions.
- `/bot/integrations/search_*.py`: Multiple search plugins that scrape sites or interface with APIs for data retrieval
- `/bot/command/*.py`: Handler files. These interface between the integrations and Discord. 
- `/bot/command/sectools/*.py`: Handler files for the security tools

### Source Files Directory
- Source files for the bot are located in the `/bot` directory.

### Documentation Files Location
- Documentation files such as `readme.md` can be found in the root directory of the project.