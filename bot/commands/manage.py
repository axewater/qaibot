# bot/commands/manage.py
from discord.ui import Button, View
import discord
import logging
from bot.models import User, UserSetting
from bot.database import SessionLocal


async def handle_manage(interaction):
    session = SessionLocal()
    try:
        logging.info(f"handle_manage: Handling settings for Discord user ID: {interaction.user.id}")

        user = session.query(User).filter(User.user_discord_id == interaction.user.id).first()
        if user:
            logging.info(f"handle_manage: Found existing user with ID: {user.id}")
        if not user:
            logging.info("handle_manage: No existing user found, creating a new user.")
            user = User(username=interaction.user.name, user_discord_id=interaction.user.id)
            session.add(user)
            session.commit()
            logging.info(f"handle_manage: New user created with ID: {user.id}")

            user_setting = UserSetting(user_id=user.id, learn_about_me=True)
            session.add(user_setting)
            session.commit()
            logging.info("handle_manage: User settings created for new user.")
        else:
            user_setting = session.query(UserSetting).filter(UserSetting.user_id == user.id).first()
            if not user_setting:
                logging.info("handle_manage: No user settings found, creating new settings.")
                user_setting = UserSetting(user_id=user.id, learn_about_me=True)
                session.add(user_setting)
                session.commit()
                logging.info("handle_manage: User settings created for existing user.")

        # Log the current value of 'learn_about_me' from the database
        logging.info(f"handle_manage: Current 'Learn About Me' setting is {user_setting.learn_about_me}")

        button_label = "Disable Learn About Me" if user_setting.learn_about_me else "Enable Learn About Me"
        button = Button(label=button_label, style=discord.ButtonStyle.primary)

        async def toggle_learn_about_me(interaction: discord.Interaction, session=session):
            try:
                new_setting = not user_setting.learn_about_me
                logging.info(f"handle_manage: User {user.id} toggled Learn About Me setting to {new_setting}.")
                user_setting.learn_about_me = new_setting
                session.commit()
                logging.info("handle_manage: User settings updated in database.")
                button.label = "Disable Learn About Me" if user_setting.learn_about_me else "Enable Learn About Me"
                await interaction.response.edit_message(view=view)
            except Exception as e:
                logging.error(f"Error during database commit: {str(e)}")
                await interaction.response.send_message(f"An error occurred during update: {str(e)}", ephemeral=True)

        button.callback = toggle_learn_about_me
        view = View()
        view.add_item(button)
        await interaction.response.send_message("Manage your settings:", view=view)

    except Exception as e:
        logging.error(f"An error occurred while managing settings: {str(e)}")
        await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)
    finally:
        # Keep the session open for the button callback
        logging.info("Session will remain open for button callback.")
