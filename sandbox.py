import discord

embed=discord.Embed()
embed.add_field(name="undefined", value="undefined", inline=False)

print(embed)


client = discord.Client()
print(client.get_user(435481585379180554))
