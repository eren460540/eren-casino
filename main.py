import json
import os
import random
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import discord
from discord import app_commands

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN environment variable is not set!")


# ==============================
# Data definitions
# ==============================


@dataclass(frozen=True)
class Animal:
    animal_id: str
    emoji: str
    rarity: str
    rarity_index: int
    role: str
    hp: int
    atk: int
    defense: int
    aliases: List[str]


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE_PATH = os.path.join(BASE_DIR, "users.json")


RARITY_ORDER = [
    ("COMMON", "⚪"),
    ("UNCOMMON", "🟢"),
    ("RARE", "🔵"),
    ("EPIC", "🟣"),
    ("LEGENDARY", "🟡"),
    ("SPECIAL", "🌈"),
    ("HIDDEN", "⚫"),
]

ROLE_EMOJI = {
    "TANK": "🛡️",
    "ATTACK": "⚔️",
    "SUPPORT": "🧪",
}


def build_animals() -> Dict[str, Animal]:
    animals: List[Animal] = []

    def add(
        rarity: str,
        rarity_index: int,
        role: str,
        animal_id: str,
        emoji: str,
        hp: int,
        atk: int,
        defense: int,
        aliases: List[str],
    ):
        animals.append(
            Animal(
                animal_id=animal_id,
                emoji=emoji,
                rarity=rarity,
                rarity_index=rarity_index,
                role=role,
                hp=hp,
                atk=atk,
                defense=defense,
                aliases=aliases,
            )
        )

    rarity_map = {name: idx for idx, (name, _) in enumerate(RARITY_ORDER)}

    # COMMON
    add("COMMON", rarity_map["COMMON"], "ATTACK", "mouse", "🐁", 7, 6, 1, ["mouse", "m"])
    add("COMMON", rarity_map["COMMON"], "ATTACK", "chicken", "🐔", 7, 5, 1, ["chicken", "chick"])
    add("COMMON", rarity_map["COMMON"], "ATTACK", "fish", "🐟", 7, 5, 1, ["fish"])
    add("COMMON", rarity_map["COMMON"], "TANK", "pig", "🐖", 10, 3, 3, ["pig"])
    add("COMMON", rarity_map["COMMON"], "TANK", "cow", "🐄", 11, 3, 3, ["cow"])
    add("COMMON", rarity_map["COMMON"], "TANK", "ram", "🐏", 9, 4, 3, ["ram"])
    add("COMMON", rarity_map["COMMON"], "TANK", "sheep", "🐑", 9, 3, 4, ["sheep"])
    add("COMMON", rarity_map["COMMON"], "TANK", "goat", "🐐", 8, 4, 3, ["goat"])
    add("COMMON", rarity_map["COMMON"], "SUPPORT", "bug", "🐛", 7, 3, 3, ["bug"])
    add("COMMON", rarity_map["COMMON"], "SUPPORT", "ant", "🐜", 6, 3, 3, ["ant"])
    add("COMMON", rarity_map["COMMON"], "SUPPORT", "bird", "🐦", 7, 3, 3, ["bird"])

    # UNCOMMON
    add("UNCOMMON", rarity_map["UNCOMMON"], "ATTACK", "dog", "🐕", 8, 7, 2, ["dog"])
    add("UNCOMMON", rarity_map["UNCOMMON"], "ATTACK", "cat", "🐈", 8, 7, 2, ["cat"])
    add("UNCOMMON", rarity_map["UNCOMMON"], "ATTACK", "snake", "🐍", 8, 8, 2, ["snake"])
    add("UNCOMMON", rarity_map["UNCOMMON"], "TANK", "horse", "🐎", 13, 4, 4, ["horse"])
    add("UNCOMMON", rarity_map["UNCOMMON"], "TANK", "boar", "🐗", 12, 5, 4, ["boar"])
    add("UNCOMMON", rarity_map["UNCOMMON"], "TANK", "deer", "🦌", 12, 4, 5, ["deer"])
    add("UNCOMMON", rarity_map["UNCOMMON"], "TANK", "turtle", "🐢", 14, 2, 5, ["turtle"])
    add("UNCOMMON", rarity_map["UNCOMMON"], "SUPPORT", "tropicalfish", "🐠", 8, 4, 4, ["tropicalfish", "tfish"])

    # RARE
    add("RARE", rarity_map["RARE"], "ATTACK", "wolf", "🐺", 9, 9, 3, ["wolf"])
    add("RARE", rarity_map["RARE"], "ATTACK", "fox", "🦊", 9, 9, 3, ["fox"])
    add("RARE", rarity_map["RARE"], "ATTACK", "dolphin", "🐬", 10, 8, 3, ["dolphin"])
    add("RARE", rarity_map["RARE"], "TANK", "crocodile", "🐊", 15, 5, 6, ["crocodile", "croc"])
    add("RARE", rarity_map["RARE"], "SUPPORT", "raccoon", "🦝", 9, 4, 5, ["raccoon"])
    add("RARE", rarity_map["RARE"], "SUPPORT", "owl", "🦉", 9, 3, 6, ["owl"])
    add("RARE", rarity_map["RARE"], "SUPPORT", "parrot", "🦜", 8, 4, 5, ["parrot"])

    # EPIC
    add("EPIC", rarity_map["EPIC"], "TANK", "elephant", "🐘", 18, 4, 8, ["elephant", "ele"])
    add("EPIC", rarity_map["EPIC"], "TANK", "hippo", "🦛", 19, 4, 8, ["hippo"])
    add("EPIC", rarity_map["EPIC"], "TANK", "llama", "🦙", 16, 5, 7, ["llama"])
    add("EPIC", rarity_map["EPIC"], "TANK", "giraffe", "🦒", 17, 5, 7, ["giraffe"])
    add("EPIC", rarity_map["EPIC"], "SUPPORT", "swan_epic", "🦢", 11, 4, 7, ["swan"])
    add("EPIC", rarity_map["EPIC"], "SUPPORT", "flamingo", "🦩", 10, 5, 6, ["flamingo"])

    # LEGENDARY
    add("LEGENDARY", rarity_map["LEGENDARY"], "ATTACK", "shark", "🦈", 14, 11, 4, ["shark"])
    add("LEGENDARY", rarity_map["LEGENDARY"], "TANK", "mammoth", "🦣", 22, 5, 9, ["mammoth"])
    add("LEGENDARY", rarity_map["LEGENDARY"], "TANK", "seal", "🦭", 20, 6, 8, ["seal"])
    add("LEGENDARY", rarity_map["LEGENDARY"], "TANK", "whale", "🐳", 24, 4, 10, ["whale"])

    # SPECIAL
    add("SPECIAL", rarity_map["SPECIAL"], "SUPPORT", "octopus", "🐙", 12, 5, 7, ["octopus"])
    add("SPECIAL", rarity_map["SPECIAL"], "SUPPORT", "butterfly", "🦋", 10, 4, 6, ["butterfly"])

    # HIDDEN
    add("HIDDEN", rarity_map["HIDDEN"], "ATTACK", "dragon", "🐉", 16, 13, 5, ["dragon"])
    add("HIDDEN", rarity_map["HIDDEN"], "TANK", "trex", "🦖", 25, 7, 10, ["trex", "t-rex"])
    add("HIDDEN", rarity_map["HIDDEN"], "SUPPORT", "unicorn", "🦄", 14, 6, 8, ["unicorn"])

    return {a.animal_id: a for a in animals}


ANIMALS = build_animals()
ALIASES: Dict[str, str] = {}
for animal in ANIMALS.values():
    for alias in animal.aliases + [animal.emoji]:
        ALIASES[alias] = animal.animal_id


DROP_TABLE: List[Tuple[float, str]] = [
    (62.0, "COMMON"),
    (24.0, "UNCOMMON"),
    (9.0, "RARE"),
    (3.0, "EPIC"),
    (1.2, "LEGENDARY"),
    (0.5, "SPECIAL"),
    (0.3, "HIDDEN"),
]

RARITY_SELL_VALUE = {
    "COMMON": 1,
    "UNCOMMON": 3,
    "RARE": 8,
    "EPIC": 20,
    "LEGENDARY": 60,
    "SPECIAL": 120,
    "HIDDEN": 250,
}


# ==============================
# Persistence
# ==============================


class DataStore:
    def __init__(self, path: str = DATA_FILE_PATH):
        self.path = path
        self.data = self._load_data()

    def _load_data(self) -> Dict:
        dir_name = os.path.dirname(self.path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        if not os.path.exists(self.path):
            initial_content = {"version": 1, "users": {}}
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(initial_content, f, indent=2)
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as exc:
            print(f"❌ Failed to parse users.json: {exc}")
            raise RuntimeError("users.json is invalid. Fix the file before running the bot.")

        if "version" not in data or "users" not in data:
            raise RuntimeError("users.json is missing required keys. Aborting startup.")
        return data

    def _default_profile(self, user_id: str) -> Dict:
        team = {"slot1": None, "slot2": None, "slot3": None}
        return {
            "user_id": user_id,
            "coins": 0,
            "energy": 0,
            "zoo": {},
            "team": team,
            "cooldowns": {"hunt": 0.0, "battle": 0.0},
            "last_enemy_signature": None,
        }

    def load_profile(self, user_id: str) -> Dict:
        if user_id not in self.data.get("users", {}):
            self.data["users"][user_id] = self._default_profile(user_id)
            self._write_data()
        profile = self.data["users"][user_id]
        profile.setdefault("cooldowns", {"hunt": 0.0, "battle": 0.0})
        profile.setdefault("team", {"slot1": None, "slot2": None, "slot3": None})
        profile.setdefault("zoo", {})
        profile.setdefault("last_enemy_signature", None)
        return profile

    def save_profile(self, profile: Dict) -> None:
        self.data.setdefault("users", {})[profile["user_id"]] = profile
        self._write_data()

    def _write_data(self) -> None:
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)


store = DataStore()
DAILY_COOLDOWNS: Dict[str, float] = {}


# ==============================
# Utility helpers
# ==============================


def resolve_animal(query: str) -> Optional[Animal]:
    key = query.strip().lower()
    animal_id = ALIASES.get(key)
    if animal_id:
        return ANIMALS[animal_id]
    return None


def now() -> float:
    return time.time()


def format_cooldown(seconds_left: float) -> str:
    seconds = int(max(0, seconds_left))
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    if hours:
        return f"{hours}h {minutes}m"
    if minutes:
        return f"{minutes}m {secs}s"
    return f"{secs}s"


def hp_bar(current: int, maximum: int) -> str:
    filled = max(0, min(10, round(10 * current / maximum))) if maximum else 0
    return "█" * filled + "░" * (10 - filled)


SUPERSCRIPT_MAP = {"0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴", "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹"}


def superscript_number(num: int) -> str:
    num_str = str(max(0, num))
    if len(num_str) == 1:
        return SUPERSCRIPT_MAP["0"] + SUPERSCRIPT_MAP[num_str]
    return "".join(SUPERSCRIPT_MAP[d] for d in num_str)


def reserved_count(team: Dict[str, Optional[str]], animal_id: str) -> int:
    return sum(1 for slot in team.values() if slot == animal_id)


def sellable_amount(profile: Dict, animal_id: str) -> int:
    return profile["zoo"].get(animal_id, 0) - reserved_count(profile["team"], animal_id)


def rarity_header(rarity: str) -> str:
    symbol = dict(RARITY_ORDER)[rarity]
    return f"{symbol} {rarity}"


def coins_reward(enemy_multiplier: float) -> int:
    base = 10
    scaled = round(base * enemy_multiplier)
    return max(5, scaled)


def enemy_signature(team: Dict[str, Animal]) -> str:
    return "|".join(team[f"slot{i}"].animal_id for i in range(1, 4))


def team_def_alive(team_hp: Dict[str, int], team_animals: Dict[str, Animal]) -> int:
    total = 0
    for i in range(1, 4):
        slot = f"slot{i}"
        if team_hp[slot] > 0:
            total += team_animals[slot].defense
    return total


def pick_rarity() -> str:
    roll = random.random() * 100
    cumulative = 0.0
    for chance, rarity in DROP_TABLE:
        cumulative += chance
        if roll <= cumulative:
            return rarity
    return DROP_TABLE[-1][1]


def random_animal_by_rarity_and_role(allowed_indices: List[int], role: str) -> Animal:
    candidates = [a for a in ANIMALS.values() if a.role == role and a.rarity_index in allowed_indices]
    return random.choice(candidates)


def power(animal: Animal) -> float:
    return animal.hp * 1.0 + animal.atk * 1.5 + animal.defense * 1.2


class MyClient(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()


client = MyClient()


@client.event
async def on_ready():
    desired_username = "ZyraZoo"
    if client.user and client.user.name != desired_username:
        await client.user.edit(username=desired_username)
    print(f"✅ Logged in as {client.user}")


def build_help_embed(page: int) -> Optional[discord.Embed]:
    if page == 1:
        embed = discord.Embed(
            title="📘 Emoji Zoo Battle Bot — Help (1/2)",
            description=(
                "Collect animals, build teams, and battle enemies with hidden difficulty."
            ),
            color=0x9B59B6,
        )
        embed.add_field(
            name="[🎯 Core Loop]",
            value=(
                "1️⃣ Claim daily rewards  \n"
                "2️⃣ Win battles to gain energy  \n"
                "3️⃣ Hunt animals using coins + energy  \n"
                "4️⃣ Build a Tank / Attack / Support team  \n"
                "5️⃣ Repeat and grow your zoo  "
            ),
            inline=False,
        )
        embed.add_field(
            name="[💰 Currencies]",
            value=(
                "💰 Coins  \n"
                "• Used for hunting animals  \n\n"
                "🔋 Energy  \n"
                "• Required for hunting  \n"
                "• Gained from battle wins  \n"
                "• NO LIMIT — stacks forever  "
            ),
            inline=False,
        )
        embed.add_field(
            name="[🧾 Commands]",
            value=(
                "!daily        → daily rewards  \n"
                "/balance      → show coins & energy  \n"
                "/zoo          → view animals (counts only)  \n"
                "/stats <x>    → view animal stats  \n"
                "/team add     → build your team  \n"
                "/team remove  → remove from team  \n"
                "/hunt <amt>   → hunt animals  \n"
                "/battle       → fight enemy teams  \n"
                "/sell <x> <n> → sell animals  "
            ),
            inline=False,
        )
        embed.add_field(
            name="[🐾 Animal Input]",
            value=(
                "Animals can be referenced by:\n"
                "• Emoji (🐘)\n"
                "• Alias (elephant)"
            ),
            inline=False,
        )
        embed.set_footer(text="Use !help 2 for battle rules")
        return embed

    if page == 2:
        embed = discord.Embed(
            title="📘 Emoji Zoo Battle Bot — Help (2/2)",
            color=0x3498DB,
        )
        embed.add_field(
            name="[🧑‍🤝‍🧑 Team Slots]",
            value=(
                "Slot 1 → 🛡️ Tank only  \n"
                "Slot 2 → ⚔️ Attack only  \n"
                "Slot 3 → 🧪 Support only  "
            ),
            inline=False,
        )
        embed.add_field(
            name="[🛡️ Team Defense Aura]",
            value=(
                "• Team DEF = sum of DEF of ALIVE units  \n"
                "• Defense reduces ALL incoming hits  \n"
                "• When a unit dies, its DEF is removed  "
            ),
            inline=False,
        )
        embed.add_field(
            name="[⚔️ Damage Formula]",
            value=(
                "damage = max(1, ATK - TEAM_DEF)\n\n"
                "Example:\n"
                "ATK 13 vs DEF 3 → 10 damage  \n"
                "Minimum damage is always 1  "
            ),
            inline=False,
        )
        embed.add_field(
            name="[🤝 Selling Rule]",
            value=(
                "Animals in your team are RESERVED:\n"
                "• Usable in battle  \n"
                "• NOT sellable  \n"
                "Even if zoo amount shows 0  "
            ),
            inline=False,
        )
        embed.add_field(
            name="[🎁 Battle Rewards]",
            value=(
                "Win:\n"
                "• +1 energy  \n"
                "• Coins (harder enemies give more)\n\n"
                "Lose:\n"
                "• No rewards"
            ),
            inline=False,
        )
        embed.set_footer(text="Build smart teams — roles matter")
        return embed

    return None


def parse_help_page(content: str) -> int:
    parts = content.strip().split()
    if len(parts) >= 2 and parts[1].isdigit():
        return int(parts[1])
    return 1


@client.tree.command(name="help", description="📘 View the Emoji Zoo help pages")
@app_commands.describe(page="Help page number (1 or 2)")
async def help_command(interaction: discord.Interaction, page: int = 1):
    embed = build_help_embed(page)
    if not embed:
        await interaction.response.send_message(
            "❌ Invalid page. Choose 1 or 2.", ephemeral=True
        )
        return
    await interaction.response.send_message(embed=embed)


HELP_ALIASES = {"!help", "!h", "!guide", "!commands"}


@client.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return
    content = message.content.strip()
    lowered = content.lower()
    if not lowered:
        return
    if any(lowered.startswith(alias) for alias in HELP_ALIASES):
        page = parse_help_page(lowered)
        embed = build_help_embed(page)
        if not embed:
            await message.channel.send("❌ Invalid page. Choose 1 or 2.")
            return
        await message.channel.send(embed=embed)
        return

    if lowered.startswith("-data"):
        store._write_data()
        await message.channel.send(
            "📂 Current users.json backup. Replace your local file with this copy.",
            file=discord.File(DATA_FILE_PATH, filename="users.json"),
        )


@client.tree.command(name="balance", description="💼 Check your coins and energy")
async def balance(interaction: discord.Interaction):
    profile = store.load_profile(str(interaction.user.id))
    embed = discord.Embed(title="💼 Your Balance", color=0xF1C40F)
    embed.add_field(name="💰 Coins", value=str(profile["coins"]), inline=False)
    embed.add_field(name="🔋 Energy", value=str(profile["energy"]), inline=False)
    await interaction.response.send_message(embed=embed)


@client.tree.command(name="daily", description="🎁 Claim your daily coins reward")
async def daily(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    profile = store.load_profile(user_id)
    now_ts = now()
    cooldown_until = DAILY_COOLDOWNS.get(user_id, 0.0)
    if cooldown_until > now_ts:
        wait = format_cooldown(cooldown_until - now_ts)
        embed = discord.Embed(
            title="⏳ Daily Cooldown",
            description=(
                "You already claimed your daily reward.\n"
                f"Try again in {wait}."
            ),
            color=0xE74C3C,
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    profile["coins"] += 100
    profile["energy"] += 40
    store.save_profile(profile)
    DAILY_COOLDOWNS[user_id] = now_ts + 24 * 3600
    embed = discord.Embed(title="🎁 Daily Reward", color=0x2ECC71)
    embed.add_field(name="💰 Coins", value="+100", inline=False)
    embed.add_field(name="🔋 Energy", value="+40", inline=False)
    embed.set_footer(text="Come back in 24 hours")
    await interaction.response.send_message(embed=embed)


@client.tree.command(name="zoo", description="🗂️ View your zoo inventory counts")
async def zoo(interaction: discord.Interaction):
    profile = store.load_profile(str(interaction.user.id))
    lines: List[str] = []
    for rarity, symbol in RARITY_ORDER:
        animals = [a for a in ANIMALS.values() if a.rarity == rarity]
        animals.sort(key=lambda a: a.animal_id)
        entries = []
        for animal in animals:
            amount = profile["zoo"].get(animal.animal_id, 0)
            if amount <= 0:
                continue
            entries.append(f"{animal.emoji} {superscript_number(amount)}")
        if entries:
            lines.append(f"{symbol} {rarity.capitalize()}\n" + "  ".join(entries))
    await interaction.response.send_message("\n\n".join(lines) if lines else "Your zoo is empty.")


@client.tree.command(name="stats", description="📊 Show stats for an animal (emoji or alias)")
@app_commands.describe(animal="Emoji or alias of the animal")
async def stats(interaction: discord.Interaction, animal: str):
    a = resolve_animal(animal)
    if not a:
        await interaction.response.send_message(
            "❌ Unknown animal\nTry an emoji or alias.", ephemeral=True
        )
        return
    rarity_symbol = dict(RARITY_ORDER)[a.rarity]
    msg = (
        f"{rarity_symbol} {a.emoji} {a.animal_id}\n"
        f"Role: {ROLE_EMOJI[a.role]} {a.role}\n\n"
        f"❤️ HP: {a.hp}\n"
        f"⚔️ ATK: {a.atk}\n"
        f"🛡️ DEF: {a.defense}\n\n"
        f"🛡️ Team DEF Aura: +{a.defense}"
    )
    await interaction.response.send_message(msg)


class TeamCommands(app_commands.Group):
    def __init__(self):
        super().__init__(name="team", description="🧭 Manage your battle team slots")

    @app_commands.command(name="view", description="🧑‍🤝‍🧑 View your current team")
    async def view(self, interaction: discord.Interaction):
        profile = store.load_profile(str(interaction.user.id))
        embed = discord.Embed(
            title="🧑‍🤝‍🧑 Your Team",
            description="Your active battle team.\nSlot order matters.",
            color=0x9B59B6,
        )
        slot_info = {
            1: ("slot1", "🛡️ Tank"),
            2: ("slot2", "⚔️ Attack"),
            3: ("slot3", "🧪 Support"),
        }
        total_hp = 0
        total_atk = 0
        total_def = 0
        for idx, (slot_key, label) in slot_info.items():
            animal_id = profile["team"].get(slot_key)
            if animal_id:
                animal = ANIMALS[animal_id]
                total_hp += animal.hp
                total_atk += animal.atk
                total_def += animal.defense
                animal_name = animal.animal_id.replace("_", " ").title()
                embed.add_field(
                    name=f"Slot {idx} — {label}",
                    value=(
                        f"{animal.emoji} {animal_name}\n"
                        f"❤️ HP: {animal.hp}\n"
                        f"⚔️ ATK: {animal.atk}\n"
                        f"🛡️ DEF: {animal.defense}"
                    ),
                    inline=False,
                )
            else:
                embed.add_field(
                    name=f"Slot {idx} — {label}",
                    value="❌ Empty Slot\nUse /team add <animal> <slot>",
                    inline=False,
                )

        embed.add_field(
            name="TEAM SUMMARY",
            value=(
                f"🛡️ Total Team DEF: {total_def}\n"
                f"❤️ Total Team HP: {total_hp}\n"
                f"⚔️ Total Team ATK: {total_atk}"
            ),
            inline=False,
        )
        embed.set_footer(text="Slot order: Tank → Attack → Support")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="add", description="➕ Assign an animal to a team slot")
    @app_commands.describe(animal="Emoji or alias", pos="Team slot (1=TANK, 2=ATTACK, 3=SUPPORT)")
    async def add(self, interaction: discord.Interaction, animal: str, pos: int):
        if pos not in (1, 2, 3):
            await interaction.response.send_message(
                "❌ Invalid slot\nSlot must be 1, 2, or 3.", ephemeral=True
            )
            return
        a = resolve_animal(animal)
        if not a:
            await interaction.response.send_message(
                "❌ Unknown animal\nTry an emoji or alias.", ephemeral=True
            )
            return
        role_requirement = {1: "TANK", 2: "ATTACK", 3: "SUPPORT"}
        if a.role != role_requirement[pos]:
            await interaction.response.send_message(
                f"❌ Invalid placement\nSlot {pos} requires a {role_requirement[pos]}.",
                ephemeral=True,
            )
            return

        profile = store.load_profile(str(interaction.user.id))
        owned = profile["zoo"].get(a.animal_id, 0)
        reserved = reserved_count(profile["team"], a.animal_id)
        if owned <= 0 and reserved == 0:
            await interaction.response.send_message(
                "❌ You don't own that animal yet.", ephemeral=True
            )
            return

        profile["team"][f"slot{pos}"] = a.animal_id
        store.save_profile(profile)
        await interaction.response.send_message(
            f"✅ TEAM UPDATED\nSlot {pos}: {ROLE_EMOJI[a.role]} {a.emoji} {a.animal_id}"
        )

    @app_commands.command(name="remove", description="➖ Clear a team slot")
    @app_commands.describe(pos="Team slot to clear (1-3)")
    async def remove(self, interaction: discord.Interaction, pos: int):
        if pos not in (1, 2, 3):
            await interaction.response.send_message(
                "❌ Invalid slot\nSlot must be 1, 2, or 3.", ephemeral=True
            )
            return
        profile = store.load_profile(str(interaction.user.id))
        profile["team"][f"slot{pos}"] = None
        store.save_profile(profile)
        await interaction.response.send_message(
            f"✅ TEAM UPDATED\nSlot {pos} cleared."
        )


client.tree.add_command(TeamCommands())


@client.tree.command(name="hunt", description="🌱 Spend coins and energy to roll animals")
@app_commands.describe(amount_coins="Coins to spend (divisible by 5)")
async def hunt(interaction: discord.Interaction, amount_coins: int):
    profile = store.load_profile(str(interaction.user.id))
    now_ts = now()
    if profile["cooldowns"]["hunt"] > now_ts:
        wait = format_cooldown(profile["cooldowns"]["hunt"] - now_ts)
        await interaction.response.send_message(
            f"⏳ Cooldown\nTry again in {wait}.", ephemeral=True
        )
        return
    if amount_coins <= 0 or amount_coins % 5 != 0:
        await interaction.response.send_message(
            "❌ Invalid amount\nUse a number divisible by 5 (e.g. 5, 25, 100).",
            ephemeral=True,
        )
        return

    rolls = amount_coins // 5
    if profile["coins"] < amount_coins:
        await interaction.response.send_message(
            "❌ Not enough coins", ephemeral=True
        )
        return
    if profile["energy"] < rolls:
        needed = rolls - profile["energy"]
        await interaction.response.send_message(
            f"❌ Not enough energy\nNeed {needed} more 🔋. Win battles to gain energy.",
            ephemeral=True,
        )
        return

    profile["coins"] -= amount_coins
    profile["energy"] -= rolls

    results: List[Animal] = []
    before_counts = dict(profile["zoo"])
    for _ in range(rolls):
        rarity = pick_rarity()
        pool = [a for a in ANIMALS.values() if a.rarity == rarity]
        animal = random.choice(pool)
        profile["zoo"][animal.animal_id] = profile["zoo"].get(animal.animal_id, 0) + 1
        results.append(animal)

    profile["cooldowns"]["hunt"] = now_ts + 10
    store.save_profile(profile)

    grouped: Dict[str, Dict[str, int]] = {rarity: {} for rarity, _ in RARITY_ORDER}
    for animal in results:
        grouped[animal.rarity][animal.animal_id] = grouped[animal.rarity].get(
            animal.animal_id, 0
        ) + 1

    lines = ["🌱 Hunt Results", "────────────────"]

    for rarity, symbol in RARITY_ORDER:
        animals = grouped[rarity]
        if not animals:
            continue
        entries = []
        for animal_id, count in sorted(animals.items()):
            animal = ANIMALS[animal_id]
            is_new = before_counts.get(animal_id, 0) == 0
            new_tag = " 🆕" if is_new else ""
            entries.append(f"{animal.emoji} {superscript_number(count)}{new_tag}")
        lines.append("")
        lines.append(f"{symbol} {rarity.capitalize()}")
        lines.append("  ".join(entries))

    lines.append("")
    lines.append("────────────────")
    lines.append(f"💰 Coins spent: {amount_coins}")
    lines.append(f"🔋 Energy used: {rolls}")

    await interaction.response.send_message("\n".join(lines))


class SellConfirmView(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=15)
        self.user_id = user_id
        self.confirmed = False

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("You cannot respond to this.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Yes ✅", style=discord.ButtonStyle.success, emoji="🟢")
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.confirmed = True
        await interaction.response.defer()
        self.stop()

    @discord.ui.button(label="Cancel ❌", style=discord.ButtonStyle.danger, emoji="🔴")
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.confirmed = False
        await interaction.response.defer()
        self.stop()


@client.tree.command(name="sell", description="💰 Sell animals for coins (reserves protected)")
@app_commands.describe(
    mode="Sell a single animal or all animals of a rarity",
    target="Emoji/alias when selling an animal, or rarity name",
    amount="Number to sell or 'all'",
)
@app_commands.choices(
    mode=[
        app_commands.Choice(name="Animal", value="animal"),
        app_commands.Choice(name="Rarity", value="rarity"),
    ]
)
async def sell(
    interaction: discord.Interaction, mode: app_commands.Choice[str], target: str, amount: str
):
    mode_value = mode.value if isinstance(mode, app_commands.Choice) else str(mode)
    amount_lower = amount.lower().strip()
    sell_all = amount_lower == "all"
    sell_count = None
    if not sell_all:
        if not amount_lower.isdigit() or int(amount_lower) <= 0:
            await interaction.response.send_message(
                "❌ Invalid amount\nUse a positive number or 'all'.", ephemeral=True
            )
            return
        sell_count = int(amount_lower)

    profile = store.load_profile(str(interaction.user.id))

    def finalize_sale(changes: List[Tuple[Animal, int]]) -> Tuple[int, int]:
        total_coins = 0
        total_sold = 0
        for animal_obj, qty in changes:
            current_amount = profile["zoo"].get(animal_obj.animal_id, 0)
            profile["zoo"][animal_obj.animal_id] = max(0, current_amount - qty)
            total_coins += qty * RARITY_SELL_VALUE[animal_obj.rarity]
            total_sold += qty
        profile["coins"] += total_coins
        store.save_profile(profile)
        return total_sold, total_coins

    if mode_value == "animal":
        a = resolve_animal(target)
        if not a:
            await interaction.response.send_message(
                "❌ Unknown animal\nTry an emoji or alias.", ephemeral=True
            )
            return
        reserved = reserved_count(profile["team"], a.animal_id)
        if reserved > 0:
            await interaction.response.send_message(
                "❌ Cannot sell\nThat animal is currently in your team.\nRemove it from the team first.",
                ephemeral=True,
            )
            return
        owned = profile["zoo"].get(a.animal_id, 0)
        if owned <= 0:
            await interaction.response.send_message(
                "❌ Cannot sell\nYou don't own that animal.", ephemeral=True
            )
            return
        sell_amount = owned if sell_all else sell_count or 0
        if sell_amount > owned:
            await interaction.response.send_message(
                f"❌ Cannot sell\nYou can sell up to {owned} of that animal.",
                ephemeral=True,
            )
            return

        plan = [(a, sell_amount)]
        needs_confirm = a.rarity in {"EPIC", "LEGENDARY", "SPECIAL", "HIDDEN"}

    else:
        rarity_key = target.strip().upper()
        if rarity_key not in RARITY_SELL_VALUE:
            await interaction.response.send_message(
                "❌ Invalid rarity\nUse common, uncommon, rare, epic, legendary, special, or hidden.",
                ephemeral=True,
            )
            return
        plan: List[Tuple[Animal, int]] = []
        for animal_obj in ANIMALS.values():
            if animal_obj.rarity != rarity_key:
                continue
            available = sellable_amount(profile, animal_obj.animal_id)
            if available <= 0:
                continue
            qty = available if sell_all else min(available, sell_count or 0)
            if qty > 0:
                plan.append((animal_obj, qty))
        if not plan:
            await interaction.response.send_message(
                "❌ Cannot sell\nNo animals of that rarity are available (team animals are excluded).",
                ephemeral=True,
            )
            return
        needs_confirm = True

    if needs_confirm:
        embed = discord.Embed(title="⚠️ Confirm Sale", description="You are about to sell the following:")
        embed.add_field(
            name="Items",
            value="\n".join(f"{animal.emoji} x{qty}" for animal, qty in plan),
            inline=False,
        )
        view = SellConfirmView(interaction.user.id)
        await interaction.response.send_message(embed=embed, view=view)
        message = await interaction.original_response()
        await view.wait()
        if not view.confirmed:
            await message.edit(content="Sale cancelled.", embed=None, view=None)
            return
        total_sold, total_coins = finalize_sale(plan)
        await message.edit(
            content=f"✅ SOLD\nItems: {total_sold}\n💰 Coins: +{total_coins}",
            embed=None,
            view=None,
        )
        return

    total_sold, total_coins = finalize_sale(plan)
    await interaction.response.send_message(
        f"✅ SOLD\n{plan[0][0].emoji} x{total_sold}\n💰 Coins: +{total_coins}"
    )


@client.tree.command(name="battle", description="⚔️ Battle an enemy bot for rewards")
async def battle(interaction: discord.Interaction):
    await interaction.response.defer()
    try:
        profile = store.load_profile(str(interaction.user.id))
        now_ts = now()
        if profile["cooldowns"]["battle"] > now_ts:
            wait = format_cooldown(profile["cooldowns"]["battle"] - now_ts)
            await interaction.edit_original_response(content=f"⏳ Cooldown\nTry again in {wait}.")
            return
        if not all(profile["team"][f"slot{i}"] for i in range(1, 4)):
            await interaction.edit_original_response(
                content="❌ Team incomplete\nSet slot 1 (TANK), slot 2 (ATTACK), slot 3 (SUPPORT)."
            )
            return

        player_animals: Dict[str, Animal] = {
            f"slot{i}": ANIMALS[profile["team"][f"slot{i}"]] for i in range(1, 4)
        }

        avg_index = round(
            sum(a.rarity_index for a in player_animals.values()) / 3
        )
        allowed = set()
        for idx in (avg_index - 1, avg_index, avg_index + 1):
            if 0 <= idx <= 5:
                allowed.add(idx)
        allowed_indices = sorted(allowed)

        player_power = sum(power(a) for a in player_animals.values())
        enemy_multiplier = random.uniform(0.85, 1.3)
        target_power = player_power * enemy_multiplier

        best_team: Optional[Dict[str, Animal]] = None
        best_delta = float("inf")
        last_signature = profile.get("last_enemy_signature")

        for attempt in range(50):
            enemy_team = {
                "slot1": random_animal_by_rarity_and_role(allowed_indices, "TANK"),
                "slot2": random_animal_by_rarity_and_role(allowed_indices, "ATTACK"),
                "slot3": random_animal_by_rarity_and_role(allowed_indices, "SUPPORT"),
            }
            signature = enemy_signature(enemy_team)
            if signature == last_signature:
                continue
            pwr = sum(power(a) for a in enemy_team.values())
            delta = abs(pwr - target_power)
            if delta < best_delta:
                best_delta = delta
                best_team = enemy_team
            if abs(pwr - target_power) <= target_power * 0.07:
                best_team = enemy_team
                break

        if not best_team:
            best_team = {
                "slot1": random_animal_by_rarity_and_role(allowed_indices, "TANK"),
                "slot2": random_animal_by_rarity_and_role(allowed_indices, "ATTACK"),
                "slot3": random_animal_by_rarity_and_role(allowed_indices, "SUPPORT"),
            }

        enemy_animals = best_team
        profile["last_enemy_signature"] = enemy_signature(enemy_animals)

        player_hp = {slot: animal.hp for slot, animal in player_animals.items()}
        enemy_hp = {slot: animal.hp for slot, animal in enemy_animals.items()}

        def first_alive(hp_map: Dict[str, int]) -> Optional[str]:
            for i in range(1, 4):
                slot = f"slot{i}"
                if hp_map[slot] > 0:
                    return slot
            return None

        def attack_phase(attacker_animals: Dict[str, Animal], attacker_hp: Dict[str, int], defender_animals: Dict[str, Animal], defender_hp: Dict[str, int]):
            for i in range(1, 4):
                slot = f"slot{i}"
                if attacker_hp[slot] <= 0:
                    continue
                target_slot = first_alive(defender_hp)
                if not target_slot:
                    break
                def_value = team_def_alive(defender_hp, defender_animals)
                dmg = max(1, attacker_animals[slot].atk - def_value)
                defender_hp[target_slot] = max(0, defender_hp[target_slot] - dmg)

        rounds = 0
        while first_alive(player_hp) and first_alive(enemy_hp) and rounds < 100:
            rounds += 1
            attack_phase(player_animals, player_hp, enemy_animals, enemy_hp)
            if not first_alive(enemy_hp):
                break
            attack_phase(enemy_animals, enemy_hp, player_animals, player_hp)

        player_alive = first_alive(player_hp) is not None
        enemy_alive = first_alive(enemy_hp) is not None
        cap_reached = rounds >= 100 and player_alive and enemy_alive
        if cap_reached:
            player_hp_total = sum(max(0, hp) for hp in player_hp.values())
            enemy_hp_total = sum(max(0, hp) for hp in enemy_hp.values())
            player_win = player_hp_total > enemy_hp_total
        else:
            player_win = player_alive and not enemy_alive

        energy_gain = 1 if player_win else 0
        coin_gain = coins_reward(enemy_multiplier) if player_win else 0

        profile["energy"] += energy_gain
        profile["coins"] += coin_gain
        profile["cooldowns"]["battle"] = now_ts + 10
        store.save_profile(profile)

        def format_row(role: str, slot: str, cur_hp: int, max_hp: int, animal: Animal) -> str:
            bar = hp_bar(cur_hp, max_hp)
            skull = " 💀" if cur_hp <= 0 else ""
            return f"{ROLE_EMOJI[role]} {animal.emoji} {animal.animal_id}\nHP [{bar}] {cur_hp}/{max_hp}{skull}"

        lines: List[str] = []
        result_title = "YOU WON" if player_win else "YOU LOST"
        lines.append(f"⚔️ BATTLE RESULT — {result_title}")
        lines.append("──────────────────────────────────────")
        lines.append("")
        lines.append("YOUR TEAM            ENEMY TEAM")
        lines.append("")

        for i in range(1, 4):
            slot = f"slot{i}"
            pa = player_animals[slot]
            ea = enemy_animals[slot]
            player_row = format_row(pa.role, slot, player_hp[slot], pa.hp, pa)
            enemy_row = format_row(ea.role, slot, enemy_hp[slot], ea.hp, ea)
            merged = "\n".join(
                [
                    f"{ROLE_EMOJI[pa.role]} {pa.emoji} {pa.animal_id}    {ROLE_EMOJI[ea.role]} {ea.emoji} {ea.animal_id}",
                    f"HP [{hp_bar(player_hp[slot], pa.hp)}] {player_hp[slot]}/{pa.hp}{' ' if player_hp[slot]>0 else ' 💀'}    "
                    f"HP [{hp_bar(enemy_hp[slot], ea.hp)}] {enemy_hp[slot]}/{ea.hp}{' ' if enemy_hp[slot]>0 else ' 💀'}",
                ]
            )
            lines.append(merged)
            lines.append("")

        your_def = team_def_alive(player_hp, player_animals)
        enemy_def = team_def_alive(enemy_hp, enemy_animals)

        sample_attacker = max(player_animals.values(), key=lambda a: a.atk)
        sample_def = enemy_def if enemy_def > 0 else 0
        sample_dmg = max(1, sample_attacker.atk - sample_def)

        lines.append("──────────────────────────────────────")
        lines.append(f"🛡️ Your Team DEF: −{your_def} DMG")
        lines.append(f"🛡️ Enemy Team DEF: −{enemy_def} DMG")
        lines.append(f"⚔️ Example Hit: {sample_attacker.atk} → {sample_dmg}")
        lines.append("──────────────────────────────────────")
        lines.append("")
        lines.append("🎁 Rewards")
        lines.append(f"💰 Coins: +{coin_gain}")
        lines.append(f"🔋 Energy: +{energy_gain}")

        await interaction.edit_original_response(content="\n".join(lines))
    except Exception as exc:
        print(f"❌ Battle error: {exc}")
        await interaction.edit_original_response(
            content=(
                "❌ Battle Failed\n"
                "Something went wrong during the fight.\n"
                "Please try again."
            )
        )


client.run(TOKEN)
