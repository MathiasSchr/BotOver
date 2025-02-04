from discord.ext import commands


class Utils(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def clear(self,ctx, amount: int):
        if amount <= 0:
            await ctx.send("Le nombre de messages doit être supérieur à 0.", delete_after=5)
            return

        print(f'{ctx.author} vient de supprimer {amount} messages')
        await ctx.channel.purge(limit=amount + 1)  # +1 pour inclure la commande elle-même
        await ctx.send(f"{amount} messages supprimés.", delete_after=5)

    @clear.error
    async def clear_error(self,ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Tu n'as pas la permission de supprimer des messages.", delete_after=5)
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Usage : `!clear <nombre de messages>`", delete_after=5)
        elif isinstance(error, commands.BadArgument):
            await ctx.send("Merci d'entrer un nombre valide.", delete_after=5)

async def setup(bot):

    await bot.add_cog(Utils(bot))