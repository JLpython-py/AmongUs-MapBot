#! python3
# mapdatabase.py

"""
==============================================================================
MIT License

Copyright (c) 2020 Jacob Lee

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
==============================================================================
"""

import asyncio
import logging
import os
import re

import discord
from discord.ext import commands

logging.basicConfig(
    level=logging.INFO,
    format=" %(asctim)s - %(levelname)s - %(message)s"
)


class MapDatabase(commands.Cog):
    """ Allow member to explore available information in Among Us
"""
    def __init__(self, bot):
        self.bot = bot
        self.searches = {}

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """ Manage response to added reaction
"""
        if payload.member.bot:
            return
        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        embed = message.embeds[0]
        if payload.member.id == message.author.id:
            return
        if not any([m in embed.footer.text for m in [
            "Airship", "MIRAHQ", "Polus", "TheSkeld"
        ]]):
            return
        if payload.emoji.name in [
            u'\u23ee', u'\u23ea', u'\u25c0', u'\u25b6', u'\u23e9', u'\u23ed'
        ]:
            await self.scroll(payload)
        elif payload.emoji.name == u'\u2714':
            await self.retrieve_from_search(payload)
        elif payload.emoji.name == u'\u274c':
            await self.delete_search(payload)

    @commands.group(
        name="Airship", case_insensitive=True, pass_context=True,
        aliases=["A"]
    )
    async def airship(self, ctx):
        """ Command group to parse data/db/airship.sqlite
"""
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid Airship command passed")

    @airship.group(
        name="retrieve", case_insensitive=True, pass_context=True,
        aliases=["r"]
    )
    async def airship_retrieve(self, ctx, category, option):
        """ Retrieve option for category in Airship database
"""
        await self.retrieve(ctx, category, option)

    @airship.group(
        name="search", case_insensitive=True, pass_context=True,
        aliases=["s"]
    )
    async def airship_search(self, ctx, category):
        """ Search options for category in Airship database
"""
        await self.search(ctx, category)

    @airship.group(
        name="listopts", case_insensitive=True, pass_context=True,
        aliases=["ls"]
    )
    async def airship_listopts(self, ctx, category):
        """ List options for category in Airship database
"""
        await self.listopts(ctx, category)

    @commands.group(
        name="MIRAHQ", case_insensitive=True, pass_context=True,
        aliases=["MIRA", "MH"]
    )
    async def mira_hq(self, ctx):
        """ Command group to parse data/db/mira_hq.sqlite
"""
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid MIRA HQ command passed")

    @mira_hq.group(
        name="retrieve", case_insensitive=True, pass_context=True,
        aliases=["r"]
    )
    async def mirahq_retrieve(self, ctx, category, option):
        """ Retrieve option for category in MIRA HQ database
"""
        await self.retrieve(ctx, category, option)

    @mira_hq.group(
        name="search", case_insensitive=True, pass_context=True,
        aliases=["s"]
    )
    async def mirahq_search(self, ctx, category):
        """ Search options for category in MIRA HQ database
"""
        await self.search(ctx, category)

    @mira_hq.group(
        name="listopts", case_insensitive=True, pass_context=True,
        aliases=["ls"]
    )
    async def mirahq_listopts(self, ctx, category):
        """ List options for category in MIRA HQ database
"""
        await self.listopts(ctx, category)

    @commands.group(
        name="Polus", case_insensitive=True, pass_context=True,
        aliases=["P"]
    )
    async def polus(self, ctx):
        """ Command group to parse data/db/polus.sqlite
"""
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid Polus command passed")

    @polus.group(
        name="retrieve", case_insensitive=True, pass_context=True,
        aliases=["r"]
    )
    async def polus_retrieve(self, ctx, category, option):
        """ Retrieve option for category in Polus database
"""
        await self.retrieve(ctx, category, option)

    @polus.group(
        name="search", case_insensitive=True, pass_context=True,
        aliases=["s"]
    )
    async def polus_search(self, ctx, category):
        """ Search options for category in Polus database
"""
        await self.search(ctx, category)

    @polus.group(
        name="listopts", case_insensitive=True, pass_context=True,
        aliases=["ls"]
    )
    async def polus_listopts(self, ctx, category):
        """ List options for category in Polus database
"""
        await self.listopts(ctx, category)

    @commands.group(
        name="TheSkeld", case_insensitive=True, pass_context=True,
        aliases=["Skeld", "TS"]
    )
    async def the_skeld(self, ctx):
        """ Command group to parse data/db/theskeld.sqlite
"""
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid The Skeld command passed")

    @the_skeld.group(
        name="retrieve", case_insensitive=True, pass_context=True,
        aliases=["r"]
    )
    async def theskeld_retrieve(self, ctx, category, option):
        """ Retrieve option for category in The Skeld database
"""
        await self.retrieve(ctx, category, option)

    @the_skeld.group(
        name="search", case_insensitive=True, pass_context=True,
        aliases=["s"]
    )
    async def theskeld_search(self, ctx, category):
        """ Search options for category in The Skeld database
"""
        await self.search(ctx, category)

    @the_skeld.group(
        name="listopts", case_insensitive=True, pass_context=True,
        aliases=["ls"]
    )
    async def theskeld_listopts(self, ctx, category):
        """ List options for category in The Skeld database
"""
        await self.listopts(ctx, category)

    async def retrieve(self, ctx, category, option):
        """ Retrieve data for option for category of map
"""
        # Get appropriate database connection
        connections = {
            "airship": self.bot.airship, "mirahq": self.bot.mirahq,
            "polus": self.bot.polus, "theskeld": self.bot.theskeld
        }
        mapname = ctx.command.full_parent_name.lower()
        connection = connections.get(mapname)
        # Get data from database
        category, option = category.lower(), option.title()
        query = f"""
        SELECT *
        FROM {category}
        WHERE name=?
        """
        columns, content = connection.execute_query(
            query, "rr", option
        )
        data = dict(zip(columns, content[0]))
        if not data:
            await ctx.channel.send(
                f"No results found [`category`={category}, `option`={option}]"
            )
        # Send data in embed
        embed = discord.Embed(
            title=f"{category.title()}: {option}",
            color=0x0000ff
        )
        for item in data:
            embed.add_field(name=item, value=data[item])
        embed.set_footer(text=ctx.command.full_parent_name)
        image_name = f"{data['name']}.png"
        image_path = os.path.join(
            "data", mapname, category, image_name
        )
        image = discord.File(image_path, image_name)
        embed.set_image(url=f"attachment://{image_name}")
        await ctx.channel.send(file=image, embed=embed)

    async def search(self, ctx, category):
        """ Allow member to scroll through options for category of map
"""
        # Get appropriate database connection
        connections = {
            "airship": self.bot.airship, "mirahq": self.bot.mirahq,
            "polus": self.bot.polus, "theskeld": self.bot.theskeld
        }
        mapname = ctx.command.full_parent_name.lower()
        connection = connections.get(mapname)
        # Get data from database
        category = category.lower()
        query = f"""
        SELECT *
        FROM {category}
        """
        columns, content = connection.execute_query(
            query, "rr"
        )
        if not (columns or content):
            await ctx.send(
                f"No results found [`category`={category}]"
            )
            return
        data = {
            d["name"]: d for d in
            [dict(zip(columns, c)) for c in content]
        }
        # Create embed for member to scroll data with
        embed, image = scrolling_embed(
            ctx.author, ctx.command.full_parent_name, category, data
        )
        message = await send_with_reactions(ctx, embed, image)

        def check(pay):
            return pay.member.id == ctx.author.id

        while True:
            try:
                payload = await self.bot.wait_for(
                    "raw_reaction_add",
                    timeout=60.0,
                    check=check
                )
                if payload.emoji.name in [
                    u'\u23ee', u'\u23ea', u'\u25c0', u'\u25b6', u'\u23e9',
                    u'\u23ed'
                ]:
                    await self.scroll(payload, data)
                elif payload.emoji.name == u'\u2714':
                    await self.retrieve_from_search(payload)
                elif payload.emoji.name == u'\u274c':
                    await self.delete_search(payload)
            except asyncio.TimeoutError:
                break
        await message.clear_reactions()
        await message.delete()

    async def listopts(self, ctx, category):
        """ List all options for a category of map
"""
        # Get appropriate database connection
        connections = {
            "airship": self.bot.airship, "mirahq": self.bot.mirahq,
            "polus": self.bot.polus, "theskeld": self.bot.theskeld
        }
        mapname = ctx.command.full_parent_name.lower()
        connection = connections.get(mapname)
        # Get data from database
        category = category.lower()
        query = f"""
        SELECT *
        FROM {category}
        """
        content = connection.execute_query(
            query, "r"
        )
        if not content:
            await ctx.channel.send(
                f"No results found [`category`={category}]"
            )
            return
        # Send data in embed
        embed = discord.Embed(
            title=category.title(),
            color=0xff0000,
            description='\n'.join([f"-{r[0]}" for r in content])
        )
        embed.set_footer(text=ctx.command.full_parent_name)
        await ctx.channel.send(embed=embed)

    async def retrieve_from_search(self, payload):
        """ Retrieve data for current option of embed
"""
        # Process payload information
        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        # Get map and category from embed
        footer_regex = re.compile(
            fr"^({'|'.join([c.name for c in self.get_commands()])}):")
        mapname = footer_regex.search(
            message.embeds[0].footer.text).group(1)
        title_regex = re.compile(
            r"^(.*):")
        category = title_regex.search(
            message.embeds[0].title).group(1).lower()
        # Get data from embed from searches by payload
        option = self.searches.get(payload.member.id).option
        data = self.data[mapname.lower()][category][option]
        # Edit embed to mimic retrieve command
        embed = discord.Embed(
            title=f"{category.title()}: {option.title()}",
            color=0x0000ff)
        for item in data:
            embed.add_field(name=item, value=data[item])
        embed.set_footer(text=mapname)
        image_name = f"{data['Name']}.png"
        image_path = os.path.join(
            'data', mapname.lower(), category, image_name
        )
        image = discord.File(image_path, image_name)
        embed.set_image(url=f"attachment://{image_name}")
        await channel.send(file=image, embed=embed)
        await message.delete()
        del self.searches[payload.member.id]

    async def scroll(self, payload, data):
        """ Scroll embed from search command based on the emoji used
"""
        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        embed = message.embeds[0]
        # Validate member
        footer_regex = re.compile(
            r"^(.*): Page [0-9]+/[0-9]+ \| ([0-9]*)"
        )
        if payload.member.id != int(
                footer_regex.search(embed.footer.text).group(2)
        ):
            await message.remove_reaction(
                payload.emoji, payload.member
            )
            return
        mapname = footer_regex.search(embed.footer.text).group(1)
        # Get current index and scroll according to emoji
        title_regex = re.compile(
            r"^(.*): (.*)"
        )
        category = title_regex.search(embed.title).group(1)
        option = title_regex.search(embed.title).group(2)
        index = list(data).index(option)
        scroll = {
            u'\u23ee': 0, u'\u23ea': index - 5, u'\u25c0': index - 1,
            u'\u25b6': index + 1, u'\u23e9': index + 5, u'\u23ed': -1}
        index = scroll.get(payload.emoji.name) % len(data)
        embed, image = scrolling_embed(
            payload.member, mapname, category, data, index=index)
        await message.edit(embed=embed)
        await message.remove_reaction(payload.emoji, payload.member)

    async def delete_search(self, payload):
        """ Delete embed from search command
"""
        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        await message.delete()


def scrolling_embed(member, mapname, category, data, *, index=0):
    """ Create and embed to allow member to scroll data with
"""
    option = data[category].get(list(data)[index])
    embed = discord.Embed(
        title=f"{category.title()}: {option}",
        color=0x0000ff
    )
    embed.set_footer(
        text=f"{mapname}: Page {index+1}/{len(data)} | {member.id}"
    )
    for item in data:
        embed.add_field(name=item, value=data[item])
    image_name = f"{mapname.lower()}.png"
    image_path = os.path.join('data', image_name)
    image = discord.File(image_path, image_name)
    embed.set_image(url=f"attachment://{image_name}")
    return embed, image


async def send_with_reactions(ctx, embed, image):
    message = await ctx.channel.send(
        file=image, embed=embed
    )
    reactions = [
        u'\u23ee', u'\u23ea', u'\u25c0', u'\u25b6', u'\u23e9', u'\u23ed',
        u'\u2714', u'\u274c'
    ]
    for rxn in reactions:
        await message.add_reaction(rxn)
    return message


def setup(bot):
    """ Allow lib.bot.__init__.py to add MapDatabase cog
"""
    bot.add_cog(MapDatabase(bot))
