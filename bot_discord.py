"""
bot_discord.py — discord.py v2 bot for Archive Scout.
Uses app_commands (slash commands), discord.ui.View with buttons,
and discord.ui.Modal for text input.

All Views and Modals are defined inside build_client() so they
close over the bot instance for cfg access.
"""

import logging

import discord
from discord import app_commands
from discord.ext import commands

import db
from bot_core import build_alert_embed_data, save_config

logger = logging.getLogger(__name__)


class ArchiveScoutBot(commands.Bot):
    def __init__(self, cfg: dict, alert_channel_id: int, **kwargs):
        intents = discord.Intents.default()
        super().__init__(command_prefix="!", intents=intents, **kwargs)
        self.cfg = cfg
        self.alert_channel_id = alert_channel_id

    async def setup_hook(self) -> None:
        await self.tree.sync()
        logger.info("Discord slash commands synced")

    async def on_ready(self) -> None:
        logger.info("Discord bot ready as %s", self.user)


async def send_deal_alert(bot: ArchiveScoutBot, scored) -> None:
    channel = bot.get_channel(bot.alert_channel_id)
    if channel is None:
        try:
            channel = await bot.fetch_channel(bot.alert_channel_id)
        except discord.DiscordException as exc:
            logger.error("Cannot fetch alert channel %s: %s", bot.alert_channel_id, exc)
            return

    data = build_alert_embed_data(scored)
    embed = discord.Embed(
        title=data["title"],
        url=data["url"],
        color=data["color"],
    )
    for field in data["fields"]:
        embed.add_field(name=field["name"], value=field["value"], inline=field["inline"])
    if data.get("thumbnail"):
        embed.set_thumbnail(url=data["thumbnail"])

    try:
        await channel.send(embed=embed)
    except discord.DiscordException as exc:
        logger.error("Failed to send Discord alert: %s", exc)


def build_client(cfg: dict) -> ArchiveScoutBot:
    alert_channel_id = int(cfg.get("discord_channel_id", 0))
    bot = ArchiveScoutBot(cfg=cfg, alert_channel_id=alert_channel_id)

    # ── Shared helpers ────────────────────────────────────────────────────────

    def _main_embed() -> discord.Embed:
        embed = discord.Embed(
            title="📦 Archive Scout Dashboard",
            color=0x5865F2,
        )
        return embed

    def _keywords_embed() -> discord.Embed:
        values = db.get_all_market_values()
        lines = []
        for row in values:
            lines.append(f"• **{row['keyword']}** — ~${row['estimated_usd']:.0f} USD")
        description = "\n".join(lines) if lines else "_No keywords configured yet._"
        embed = discord.Embed(
            title="📋 Keywords & Market Values",
            description=description,
            color=0x5865F2,
        )
        return embed

    def _settings_embed() -> discord.Embed:
        embed = discord.Embed(title="⚙️ Settings", color=0x5865F2)
        embed.add_field(name="💵 Max Price", value=f"${bot.cfg.get('max_price_usd', '—')} USD", inline=True)
        embed.add_field(name="📊 Deal Threshold", value=f"{bot.cfg.get('deal_threshold_pct', '—')}%", inline=True)
        embed.add_field(name="⏱ Check Interval", value=f"{bot.cfg.get('check_interval_minutes', '—')} min", inline=True)
        return embed

    def _stats_embed() -> discord.Embed:
        stats = db.get_recent_stats(60)
        embed = discord.Embed(title="📊 Stats (last 60 min)", color=0x5865F2)
        embed.add_field(name="Listings Checked", value=str(stats["checked"]), inline=True)
        embed.add_field(name="Alerts Sent", value=str(stats["alerted"]), inline=True)
        return embed

    # ── Modals ────────────────────────────────────────────────────────────────

    class AddKeywordModal(discord.ui.Modal, title="Add Keyword"):
        keyword_input = discord.ui.TextInput(
            label="Keyword",
            placeholder="e.g. undercover jacket",
            max_length=100,
        )
        price_input = discord.ui.TextInput(
            label="Market Value (USD)",
            placeholder="e.g. 480",
            max_length=20,
        )

        async def on_submit(self, interaction: discord.Interaction) -> None:
            keyword = self.keyword_input.value.strip().lower()
            try:
                price = float(self.price_input.value.strip())
            except ValueError:
                await interaction.response.send_message(
                    "⚠️ Market value must be a number.", ephemeral=True
                )
                return

            db.set_market_value(keyword, price)
            keywords = bot.cfg.get("keywords", [])
            if keyword not in [k.lower() for k in keywords]:
                bot.cfg.setdefault("keywords", []).append(keyword)
            bot.cfg.setdefault("market_values", {})[keyword] = price
            save_config(bot.cfg)

            embed = _keywords_embed()
            await interaction.response.edit_message(embed=embed, view=KeywordsView())

    class EditPriceModal(discord.ui.Modal, title="Edit Market Price"):
        def __init__(self, keyword: str, current_price: float):
            super().__init__()
            self._keyword = keyword
            self.price_input = discord.ui.TextInput(
                label=f"New price for: {keyword}",
                default=str(current_price),
                max_length=20,
            )
            self.add_item(self.price_input)

        async def on_submit(self, interaction: discord.Interaction) -> None:
            try:
                price = float(self.price_input.value.strip())
            except ValueError:
                await interaction.response.send_message(
                    "⚠️ Price must be a number.", ephemeral=True
                )
                return

            db.set_market_value(self._keyword, price)
            bot.cfg.setdefault("market_values", {})[self._keyword] = price
            save_config(bot.cfg)

            embed = _keywords_embed()
            await interaction.response.edit_message(embed=embed, view=KeywordsView())

    class EditSettingModal(discord.ui.Modal):
        def __init__(self, setting_key: str, label: str, current_value):
            super().__init__(title=f"Edit {label}")
            self._setting_key = setting_key
            self._int_keys = {"check_interval_minutes", "max_pages"}
            self.value_input = discord.ui.TextInput(
                label=label,
                default=str(current_value),
                max_length=20,
            )
            self.add_item(self.value_input)

        async def on_submit(self, interaction: discord.Interaction) -> None:
            raw = self.value_input.value.strip()
            try:
                value = int(raw) if self._setting_key in self._int_keys else float(raw)
            except ValueError:
                await interaction.response.send_message(
                    "⚠️ Value must be a number.", ephemeral=True
                )
                return

            bot.cfg[self._setting_key] = value
            save_config(bot.cfg)

            embed = _settings_embed()
            await interaction.response.edit_message(embed=embed, view=SettingsView())

    # ── Views ─────────────────────────────────────────────────────────────────

    class BackView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=300)

        @discord.ui.button(label="◀ Back", style=discord.ButtonStyle.secondary)
        async def back(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
            await interaction.response.edit_message(embed=_main_embed(), view=MainMenuView())

    class RemoveKeywordView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=300)
            values = db.get_all_market_values()
            options = [
                discord.SelectOption(label=row["keyword"], value=row["keyword"])
                for row in values
            ] or [discord.SelectOption(label="(none)", value="__none__")]

            select = discord.ui.Select(
                placeholder="Select keyword to remove…",
                options=options[:25],
            )
            select.callback = self._on_select
            self.add_item(select)

            back_btn = discord.ui.Button(label="◀ Back", style=discord.ButtonStyle.secondary)
            back_btn.callback = self._on_back
            self.add_item(back_btn)

        async def _on_select(self, interaction: discord.Interaction) -> None:
            keyword = interaction.data["values"][0]
            if keyword == "__none__":
                await interaction.response.defer()
                return
            with db.get_connection() as conn:
                conn.execute("DELETE FROM market_values WHERE keyword = ?", (keyword,))
            keywords = bot.cfg.get("keywords", [])
            bot.cfg["keywords"] = [k for k in keywords if k.lower() != keyword.lower()]
            bot.cfg.get("market_values", {}).pop(keyword, None)
            save_config(bot.cfg)
            embed = _keywords_embed()
            await interaction.response.edit_message(embed=embed, view=KeywordsView())

        async def _on_back(self, interaction: discord.Interaction) -> None:
            await interaction.response.edit_message(embed=_keywords_embed(), view=KeywordsView())

    class EditPriceSelectView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=300)
            values = db.get_all_market_values()
            options = [
                discord.SelectOption(label=row["keyword"], value=row["keyword"])
                for row in values
            ] or [discord.SelectOption(label="(none)", value="__none__")]

            select = discord.ui.Select(
                placeholder="Select keyword to edit…",
                options=options[:25],
            )
            select.callback = self._on_select
            self.add_item(select)

            back_btn = discord.ui.Button(label="◀ Back", style=discord.ButtonStyle.secondary)
            back_btn.callback = self._on_back
            self.add_item(back_btn)

        async def _on_select(self, interaction: discord.Interaction) -> None:
            keyword = interaction.data["values"][0]
            if keyword == "__none__":
                await interaction.response.defer()
                return
            current_price = db.get_market_value(keyword) or 0.0
            modal = EditPriceModal(keyword=keyword, current_price=current_price)
            await interaction.response.send_modal(modal)

        async def _on_back(self, interaction: discord.Interaction) -> None:
            await interaction.response.edit_message(embed=_keywords_embed(), view=KeywordsView())

    class KeywordsView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=300)

        @discord.ui.button(label="➕ Add", style=discord.ButtonStyle.success)
        async def add(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
            await interaction.response.send_modal(AddKeywordModal())

        @discord.ui.button(label="🗑 Remove", style=discord.ButtonStyle.danger)
        async def remove(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
            await interaction.response.edit_message(
                embed=discord.Embed(title="🗑 Remove Keyword", color=0x5865F2),
                view=RemoveKeywordView(),
            )

        @discord.ui.button(label="💰 Edit Price", style=discord.ButtonStyle.primary)
        async def edit_price(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
            await interaction.response.edit_message(
                embed=discord.Embed(title="💰 Edit Market Price", color=0x5865F2),
                view=EditPriceSelectView(),
            )

        @discord.ui.button(label="◀ Back", style=discord.ButtonStyle.secondary)
        async def back(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
            await interaction.response.edit_message(embed=_main_embed(), view=MainMenuView())

    class SettingsView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=300)

        @discord.ui.button(label="💵 Max Price", style=discord.ButtonStyle.primary)
        async def max_price(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
            modal = EditSettingModal(
                setting_key="max_price_usd",
                label="Max Price (USD)",
                current_value=bot.cfg.get("max_price_usd", 350),
            )
            await interaction.response.send_modal(modal)

        @discord.ui.button(label="📊 Deal Threshold %", style=discord.ButtonStyle.primary)
        async def deal_threshold(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
            modal = EditSettingModal(
                setting_key="deal_threshold_pct",
                label="Deal Threshold (%)",
                current_value=bot.cfg.get("deal_threshold_pct", 30),
            )
            await interaction.response.send_modal(modal)

        @discord.ui.button(label="⏱ Check Interval", style=discord.ButtonStyle.primary)
        async def check_interval(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
            modal = EditSettingModal(
                setting_key="check_interval_minutes",
                label="Check Interval (minutes)",
                current_value=bot.cfg.get("check_interval_minutes", 15),
            )
            await interaction.response.send_modal(modal)

        @discord.ui.button(label="◀ Back", style=discord.ButtonStyle.secondary)
        async def back(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
            await interaction.response.edit_message(embed=_main_embed(), view=MainMenuView())

    class MainMenuView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=300)

        @discord.ui.button(label="📋 Keywords & Prices", style=discord.ButtonStyle.primary)
        async def keywords(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
            await interaction.response.edit_message(embed=_keywords_embed(), view=KeywordsView())

        @discord.ui.button(label="⚙️ Settings", style=discord.ButtonStyle.primary)
        async def settings(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
            await interaction.response.edit_message(embed=_settings_embed(), view=SettingsView())

        @discord.ui.button(label="📊 Stats", style=discord.ButtonStyle.secondary)
        async def stats(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
            await interaction.response.edit_message(embed=_stats_embed(), view=BackView())

    # ── Slash commands ────────────────────────────────────────────────────────

    @bot.tree.command(name="manage", description="Open the Archive Scout dashboard")
    async def slash_manage(interaction: discord.Interaction) -> None:
        await interaction.response.send_message(
            embed=_main_embed(),
            view=MainMenuView(),
            ephemeral=True,
        )

    @bot.tree.command(name="status", description="Show recent stats")
    async def slash_status(interaction: discord.Interaction) -> None:
        await interaction.response.send_message(
            embed=_stats_embed(),
            ephemeral=True,
        )

    return bot
