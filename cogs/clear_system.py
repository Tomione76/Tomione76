"""
Die Datenbankverbindung wird hergestellt, indem die Datei "clear.db" als Datenbank verwendet wird.
Die Tabelle "nachrichten" wird erstellt, wenn sie noch nicht existiert, und die erforderlichen Spalten werden definiert.

________________________________|| Struktur: ||________________________________
1. id: Eine automatisch generierte eindeutige ID für jede Zeile in der Tabelle.
2.guild_id: Die ID des Discord-Servers, zu dem die gelöschte Nachricht gehört.
3. channel_id: Die ID des Textkanals, in dem die Nachricht gelöscht wurde.
4. user_id: Die ID des Benutzers, der die Nachricht gelöscht hat.
5. user: Der Name des Benutzers, der die Nachricht gelöscht hat.
6. grund: Ein Textfeld, in dem der Grund für das Löschen der Nachricht gespeichert wird.
7. timestamp: Ein Zeitstempel, der angibt, wann die Nachricht gelöscht wurde.
image/Mülleimer: https://cdn.discordapp.com/attachments/1070102699334451230/1133866585795334184/Mulleimer.png
clear hab ich ersetzt auf löschen. Grund eine clear hab ich schon, gabs probleme :)
"""

import sqlite3
import discord
import asyncio
from discord.ext import commands
from discord.commands import slash_command
from datetime import datetime

# Verbindung zur Datenbank herstellen
db = sqlite3.connect('clear.db')
c = db.cursor()

# Tabelle für gelöschte Nachrichten anlegen, falls sie noch nicht existiert
c.execute(
    '''CREATE TABLE IF NOT EXISTS nachrichten (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id INTEGER,
    channel_id INTEGER,
    user_id INTEGER,
    user TEXT,
    grund TEXT,
    timestamp TEXT
    )'''
)
db.commit()


class ClearCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(description='Löschen von Nachrichten')
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def clear(self, interaction: discord.Interaction, zahl: int, grund: str):
        await interaction.response.defer()

        if zahl <= 0:
            await interaction.channel.send('Die Anzahl der zu löschenden Nachrichten muss größer als 0 sein.')
            return

        messages = await interaction.channel.history(limit=zahl + 1).flatten()
        await interaction.channel.delete_messages(messages)

        # Gelöschte Nachrichten in der Datenbank speichern
        guild_id = interaction.guild.id
        channel_id = interaction.channel.id
        user_id = interaction.user.id
        user = f"{interaction.user.name}#{interaction.user.discriminator}"
        timestamp = datetime.now().strftime('%d.%m.%Y %H:%M:%S')

        c.execute("INSERT INTO nachrichten (guild_id, channel_id, user_id, user, grund, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
                  (guild_id, channel_id, user_id, user, grund, timestamp))
        db.commit()

        # Embed-Nachricht erstellen. Habs geändert sowie color passt besser zum Mülleimer.
        embed = discord.Embed(
            title='Nachrichten gelöscht',
            description=f'Es wurden {zahl} Nachrichten von {interaction.user.mention} gelöscht.',
            color=0x57f287,
            timestamp=datetime.now()
        )
        embed.add_field(name='Grund', value=grund, inline=False)
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        embed.set_image(
            url='https://cdn.discordapp.com/attachments/1070102699334451230/1133866585795334184/Mulleimer.png')
        embed.set_footer(text=f'{interaction.guild.name}')  # icon_url=self.bot.user.avatar.url)

        msg = await interaction.channel.send(embed=embed)
        await asyncio.sleep(20)  # Erhöht auf 20 sekunden. Embed anzuschauen :)
        await msg.delete()

    @clear.error
    async def clear_error(self, interaction: discord.Interaction, error: commands.CommandError):
        if isinstance(error, commands.MissingPermissions):
            await interaction.response.send_message(
                'Du hast keine Rechte, um den Befehl zu benutzen', ephemeral=True
            )


def setup(bot):
    bot.add_cog(ClearCommand(bot))
