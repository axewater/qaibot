# bot/commands/manage.py
from ..models import UserSetting, User
from discord.ui import Button, View
import discord, logging
from bot.models import User, UserSetting
from bot.database import SessionLocal


async def handle_manage(interaction):
    session = SessionLocal()
    try:
        logging.info(f"Handling settings for Discord user ID: {interaction.user.id}")

        user = session.query(User).filter(User.user_discord_id == interaction.user.id).first()
        if not user:
            logging.info("No existing user found, creating a new user.")
            user = User(username=interaction.user.name, user_discord_id=interaction.user.id)
            session.add(user)
            session.commit()
            logging.info(f"New user created with ID: {user.id}")

            user_setting = UserSetting(user_id=user.id, learn_about_me=True)
            session.add(user_setting)
            session.commit()
            logging.info("User settings created for new user.")
        else:
            user_setting = session.query(UserSetting).filter(UserSetting.user_id == user.id).first()
            if not user_setting:
                logging.info("No user settings found, creating new settings.")
                user_setting = UserSetting(user_id=user.id, learn_about_me=True)
                session.add(user_setting)
                session.commit()
                logging.info("User settings created for existing user.")

        button_label = "Disable Learn About Me" if user_setting.learn_about_me else "Enable Learn About Me"
        button = Button(label=button_label, style=discord.ButtonStyle.primary)

        async def toggle_learn_about_me(interaction: discord.Interaction):
            logging.info(f"User {user.id} toggled Learn About Me setting.")
            user_setting.learn_about_me = not user_setting.learn_about_me
            session.commit()
            button.label = "Disable Learn About Me" if user_setting.learn_about_me else "Enable Learn About Me"
            await interaction.response.edit_message(view=view)

        button.callback = toggle_learn_about_me
        view = View()
        view.add_item(button)
        await interaction.response.send_message("Manage your settings:", view=view)

    except Exception as e:
        logging.error(f"An error occurred while managing settings: {str(e)}")
        await interaction.response.send_message(f"An error occurred: {str(e)}")
    finally:
        session.close()
        logging.info("Database session closed.")
