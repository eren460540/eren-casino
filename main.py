import json
import os
import random
import sqlite3
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
    def __init__(self, path: str = "zoo.db"):
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self._prepare()

    def _prepare(self) -> None:
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS profiles (
                user_id TEXT PRIMARY KEY,
                coins INTEGER NOT NULL,
                energy INTEGER NOT NULL,
                zoo TEXT NOT NULL,
                team TEXT NOT NULL,
                hunt_until REAL,
                battle_until REAL,
                daily_until REAL,
                last_enemy_signature TEXT
            )
            """
        )
        self.conn.commit()

    def _default_profile(self, user_id: str) -> Dict:
        zoo = {animal_id: 0 for animal_id in ANIMALS.keys()}
        team = {"slot1": None, "slot2": None, "slot3": None}
        return {
            "user_id": user_id,
            "coins": 0,
            "energy": 0,
            "zoo": zoo,
            "team": team,
            "hunt_until": 0.0,
            "battle_until": 0.0,
            "daily_until": 0.0,
            "last_enemy_signature": None,
        }

    def load_profile(self, user_id: str) -> Dict:
        cur = self.conn.cursor()
        row = cur.execute(
            "SELECT * FROM profiles WHERE user_id = ?", (user_id,)
        ).fetchone()
        if not row:
            profile = self._default_profile(user_id)
            self.save_profile(profile)
            return profile
        return {
            "user_id": row["user_id"],
            "coins": row["coins"],
            "energy": row["energy"],
            "zoo": json.loads(row["zoo"]),
            "team": json.loads(row["team"]),
            "hunt_until": row["hunt_until"] or 0.0,
            "battle_until": row["battle_until"] or 0.0,
            "daily_until": row["daily_until"] or 0.0,
            "last_enemy_signature": row["last_enemy_signature"],
        }

    def save_profile(self, profile: Dict) -> None:
        cur = self.conn.cursor()
        cur.execute(
            """
            INSERT INTO profiles (
                user_id, coins, energy, zoo, team, hunt_until, battle_until, daily_until, last_enemy_signature
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                coins=excluded.coins,
                energy=excluded.energy,
                zoo=excluded.zoo,
                team=excluded.team,
                hunt_until=excluded.hunt_until,
                battle_until=excluded.battle_until,
                daily_until=excluded.daily_until,
                last_enemy_signature=excluded.last_enemy_signature
            """,
            (
                profile["user_id"],
                profile["coins"],
                profile["energy"],
                json.dumps(profile["zoo"]),
                json.dumps(profile["team"]),
                profile["hunt_until"],
                profile["battle_until"],
                profile["daily_until"],
                profile["last_enemy_signature"],
            ),
        )
        self.conn.commit()


store = DataStore()


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
    return "|".join(team[f"slot{i}"] for i in range(1, 4))


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
    print(f"✅ Logged in as {client.user}")


@client.tree.command(name="balance", description="💼 Check your coins and energy")
async def balance(interaction: discord.Interaction):
    profile = store.load_profile(str(interaction.user.id))
    msg = (
        "💼 YOUR BALANCE\n"
        "────────────────\n"
        f"💰 Coins: {profile['coins']}\n"
        f"🔋 Energy: {profile['energy']}"
    )
    await interaction.response.send_message(msg)


@client.tree.command(name="daily", description="🎁 Claim your daily coins reward")
async def daily(interaction: discord.Interaction):
    profile = store.load_profile(str(interaction.user.id))
    now_ts = now()
    if profile["daily_until"] > now_ts:
        wait = format_cooldown(profile["daily_until"] - now_ts)
        await interaction.response.send_message(
            f"⏳ Cooldown\nTry again in {wait}.", ephemeral=True
        )
        return
    profile["coins"] += 100
    profile["daily_until"] = now_ts + 24 * 3600
    store.save_profile(profile)
    await interaction.response.send_message(
        "🎁 DAILY REWARD\n" "💰 Coins gained: +100\n" "⏳ Come back in 24h"
    )


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
            locked = " 🔒" if amount == 0 and reserved_count(profile["team"], animal.animal_id) else ""
            entries.append(f"{animal.emoji} {amount:02d}{locked}")
        lines.append(f"{symbol} {rarity}\n" + " ".join(entries))
    await interaction.response.send_message("\n\n".join(lines))


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
    if profile["hunt_until"] > now_ts:
        wait = format_cooldown(profile["hunt_until"] - now_ts)
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
    for _ in range(rolls):
        rarity = pick_rarity()
        pool = [a for a in ANIMALS.values() if a.rarity == rarity]
        animal = random.choice(pool)
        profile["zoo"][animal.animal_id] += 1
        results.append(animal)

    profile["hunt_until"] = now_ts + 10
    store.save_profile(profile)

    lines = ["🌱 {user}, hunt is empowered by luck".format(user=interaction.user.display_name)]
    lines.append("")
    lines.append(f"🎯 You spent: {amount_coins} coins")
    lines.append(f"🔋 Energy used: {rolls}")
    lines.append("")
    lines.append("🐾 You found:")
    emoji_line = ""
    count = 0
    for animal in results:
        emoji_line += animal.emoji + " "
        count += 1
        if count % 7 == 0:
            lines.append(emoji_line.strip())
            emoji_line = ""
    if emoji_line:
        lines.append(emoji_line.strip())

    await interaction.response.send_message("\n".join(lines))


@client.tree.command(name="sell", description="💰 Sell animals for coins (reserves protected)")
@app_commands.describe(animal="Emoji or alias", amount="Number to sell")
async def sell(interaction: discord.Interaction, animal: str, amount: int):
    a = resolve_animal(animal)
    if not a:
        await interaction.response.send_message(
            "❌ Unknown animal\nTry an emoji or alias.", ephemeral=True
        )
        return
    if amount < 1:
        await interaction.response.send_message(
            "❌ Invalid amount\nAmount must be at least 1.", ephemeral=True
        )
        return

    profile = store.load_profile(str(interaction.user.id))
    sellable = sellable_amount(profile, a.animal_id)
    if amount > sellable:
        await interaction.response.send_message(
            "❌ Cannot sell\nThat animal is currently in your team (reserved)."
            if sellable == 0
            else f"❌ Cannot sell\nYou can sell up to {sellable} of that animal.",
            ephemeral=True,
        )
        return

    profile["zoo"][a.animal_id] -= amount
    earned = amount * RARITY_SELL_VALUE[a.rarity]
    profile["coins"] += earned
    store.save_profile(profile)

    await interaction.response.send_message(
        f"✅ SOLD\n{a.emoji} x{amount}\n💰 Coins: +{earned}"
    )


@client.tree.command(name="battle", description="⚔️ Battle an enemy bot for rewards")
async def battle(interaction: discord.Interaction):
    profile = store.load_profile(str(interaction.user.id))
    now_ts = now()
    if profile["battle_until"] > now_ts:
        wait = format_cooldown(profile["battle_until"] - now_ts)
        await interaction.response.send_message(
            f"⏳ Cooldown\nTry again in {wait}.", ephemeral=True
        )
        return
    if not all(profile["team"][f"slot{i}"] for i in range(1, 4)):
        await interaction.response.send_message(
            "❌ Team incomplete\nSet slot 1 (TANK), slot 2 (ATTACK), slot 3 (SUPPORT).",
            ephemeral=True,
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
    enemy_multiplier = random.uniform(0.75, 1.25)
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
    player_win = player_alive and not enemy_alive

    energy_gain = 1 if player_win else 0
    coin_gain = coins_reward(enemy_multiplier) if player_win else 0

    profile["energy"] += energy_gain
    profile["coins"] += coin_gain
    profile["battle_until"] = now_ts + 10
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

    await interaction.response.send_message("\n".join(lines))


client.run(TOKEN)
