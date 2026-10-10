"""Seed dataset of physical games for Touch Grass: Play Outside.

Each game declares the equipment it *requires* (empty list = none), the
areas it works in, and a player range. `base_rules` is a short markdown
summary used as LLM context and as the offline fallback rules text.
"""

AREAS = ["hard_ground", "grass", "small_yard", "indoor"]
EQUIPMENT = ["Ball", "Chalk", "Jump Rope", "Frisbee", "Cones", "None"]

AREA_LABELS = {
    "hard_ground": "Hard Ground / Driveway",
    "grass": "Grassy Field",
    "small_yard": "Small Yard",
    "indoor": "Indoor / Porch",
}


def game_tags(game: dict) -> list[str]:
    """Derive display tags from a game's attributes."""
    tags: list[str] = []
    if game["equipment"]:
        tags += [f"{e} Games" for e in game["equipment"]]
    else:
        tags.append("No Equipment")
    if game["min_players"] <= 2:
        tags.append("Solo Games")
    elif game["min_players"] <= 5:
        tags.append("Small Group")
    if game["max_players"] >= 12:
        tags.append("Group Games")
    if "indoor" in game["areas"]:
        tags.append("Indoor")
    if any(a in game["areas"] for a in ("grass", "small_yard", "hard_ground")):
        tags.append("Outdoor")
    if game["energy"] == "high":
        tags.append("Active")
    return tags

GAMES = [
    {
        "id": "tag-classic",
        "name": "Tag",
        "min_players": 3,
        "max_players": 30,
        "equipment": [],
        "areas": ["grass", "small_yard", "hard_ground"],
        "energy": "high",
        "summary": "One player is 'it' and chases the others; tagged players become it.",
        "base_rules": """### Tag
- Pick one player to be **it**.
- **It** chases everyone else; a touch tags a player.
- The tagged player becomes the new **it**.
- Optional: agree on safe zones or freeze-tag variant for big groups.""",
    },
    {
        "id": "freeze-tag",
        "name": "Freeze Tag",
        "min_players": 5,
        "max_players": 30,
        "equipment": [],
        "areas": ["grass", "small_yard"],
        "energy": "high",
        "summary": "Tagged players freeze in place until a teammate unfreezes them.",
        "base_rules": """### Freeze Tag
- One or two players are **it**.
- Tagged players freeze where they stand.
- A free teammate can unfreeze them with a touch.
- Round ends when everyone is frozen or after a time limit — then swap who's it.""",
    },
    {
        "id": "hide-and-seek",
        "name": "Hide and Seek",
        "min_players": 3,
        "max_players": 15,
        "equipment": [],
        "areas": ["small_yard", "grass", "indoor"],
        "energy": "medium",
        "summary": "One seeker counts while everyone hides; last found wins.",
        "base_rules": """### Hide and Seek
- Choose a seeker and a home base.
- Seeker counts to 30 with eyes closed; everyone else hides.
- Seeker searches; first player found is the next seeker.
- Optional: hiders can race back to base to be safe.""",
    },
    {
        "id": "red-light-green-light",
        "name": "Red Light, Green Light",
        "min_players": 3,
        "max_players": 30,
        "equipment": [],
        "areas": ["grass", "hard_ground", "small_yard"],
        "energy": "medium",
        "summary": "Move on 'green light', freeze on 'red light' — get caught moving and you're out.",
        "base_rules": """### Red Light, Green Light
- One player is the **caller** at the finish line; others line up ~20m away.
- Caller turns away and says **green light** — players move.
- Caller spins around and says **red light** — everyone must freeze.
- Anyone caught moving goes back to start. First to tag the caller wins.""",
    },
    {
        "id": "simon-says",
        "name": "Simon Says",
        "min_players": 3,
        "max_players": 30,
        "equipment": [],
        "areas": ["indoor", "hard_ground", "grass", "small_yard"],
        "energy": "low",
        "summary": "Follow commands only when they start with 'Simon says'.",
        "base_rules": """### Simon Says
- One player is **Simon** and gives commands.
- Obey only commands starting with *"Simon says…"*.
- Anyone who moves on a command without it is out (or does 5 jumping jacks for a no-elimination game).
- Last player standing becomes Simon.""",
    },
    {
        "id": "duck-duck-goose",
        "name": "Duck, Duck, Goose",
        "min_players": 5,
        "max_players": 20,
        "equipment": [],
        "areas": ["grass", "indoor", "small_yard"],
        "energy": "medium",
        "summary": "Circle game: tap heads saying 'duck' until you pick a 'goose' to chase you.",
        "base_rules": """### Duck, Duck, Goose
- Everyone sits in a circle; one player walks outside tapping heads saying **duck**.
- When they say **goose**, that player jumps up and chases them around the circle.
- If the tapper sits in the goose's spot first, the goose is it; otherwise the tapper goes again.""",
    },
    {
        "id": "sharks-and-minnows",
        "name": "Sharks and Minnows",
        "min_players": 6,
        "max_players": 30,
        "equipment": ["Cones"],
        "areas": ["grass", "hard_ground"],
        "energy": "high",
        "summary": "Minnows run across a field past the sharks; tagged minnows become sharks.",
        "base_rules": """### Sharks and Minnows
- Mark two end zones with cones; one or two **sharks** start mid-field.
- **Minnows** line up at one end and try to run to the other side.
- Tagged minnows become sharks next round.
- Last minnow untagged wins.""",
    },
    {
        "id": "kickball",
        "name": "Kickball",
        "min_players": 8,
        "max_players": 30,
        "equipment": ["Ball"],
        "areas": ["grass", "hard_ground"],
        "energy": "high",
        "summary": "Baseball rules but you kick a big rubber ball.",
        "base_rules": """### Kickball
- Split into two teams; set up 4 bases like a baseball diamond.
- Pitcher rolls the ball; the kicker boots it and runs the bases.
- Fielders get outs by catching, tagging, or hitting a runner below the shoulders with the ball.
- 3 outs per half-inning; play 5 innings or a time limit.""",
    },
    {
        "id": "four-square",
        "name": "Four Square",
        "min_players": 4,
        "max_players": 8,
        "equipment": ["Ball", "Chalk"],
        "areas": ["hard_ground"],
        "energy": "medium",
        "summary": "Bounce a ball between four chalk squares; eliminate players to climb to the king square.",
        "base_rules": """### Four Square
- Draw a large square split into 4 smaller squares (A–D) with chalk.
- Players bounce the ball into another square after one bounce in theirs.
- Miss, hit out, or double-bounce and you're out — rotate to square D.
- Goal: reach and hold square A (the king).""",
    },
    {
        "id": "hopscotch",
        "name": "Hopscotch",
        "min_players": 2,
        "max_players": 6,
        "equipment": ["Chalk"],
        "areas": ["hard_ground"],
        "energy": "low",
        "summary": "Classic chalk court — toss a marker and hop the course.",
        "base_rules": """### Hopscotch
- Draw the numbered court (1–10) with chalk.
- Toss a small marker onto square 1; hop through, skipping that square.
- Single squares = one foot, doubles = two feet.
- Turn around at the top, come back, and pick up your marker. Lose your turn on a miss.""",
    },
    {
        "id": "jump-rope-rhymes",
        "name": "Jump Rope",
        "min_players": 2,
        "max_players": 6,
        "equipment": ["Jump Rope"],
        "areas": ["hard_ground", "grass", "small_yard", "indoor"],
        "energy": "medium",
        "summary": "Solo skipping tricks or two turners with rhymes for a jumper.",
        "base_rules": """### Jump Rope
- Solo: count consecutive jumps; try tricks (criss-cross, double-under).
- Group: two turners swing a long rope; jumpers enter on a rhyme and exit on a miss.
- Rotate roles every round.""",
    },
    {
        "id": "double-dutch",
        "name": "Double Dutch",
        "min_players": 3,
        "max_players": 8,
        "equipment": ["Jump Rope"],
        "areas": ["hard_ground"],
        "energy": "high",
        "summary": "Two ropes turned in opposite directions; jumpers take turns inside.",
        "base_rules": """### Double Dutch
- Two turners, each holding both rope ends, turn them in opposite directions (egg-beater).
- Jumper enters on the beat and jumps until a miss.
- Rotate: miss → take a turner spot.""",
    },
    {
        "id": "ultimate-frisbee-mini",
        "name": "Mini Ultimate Frisbee",
        "min_players": 6,
        "max_players": 14,
        "equipment": ["Frisbee", "Cones"],
        "areas": ["grass"],
        "energy": "high",
        "summary": "Pass the disc upfield; score by catching it in the end zone. No running with the disc.",
        "base_rules": """### Mini Ultimate
- Two teams; mark end zones with cones.
- Move the disc only by passing — thrower must stay planted.
- Turnover on drops, interceptions, or out of bounds.
- Score by catching in the opposing end zone; first to 5 or time limit.""",
    },
    {
        "id": "frisbee-golf",
        "name": "Frisbee Golf",
        "min_players": 2,
        "max_players": 8,
        "equipment": ["Frisbee", "Cones"],
        "areas": ["grass", "small_yard"],
        "energy": "low",
        "summary": "Set cone targets as 'holes'; fewest throws wins.",
        "base_rules": """### Frisbee Golf
- Place cones as holes around the field; set a par for each.
- Throw from the tee; next shot is from where the disc lands.
- Count throws per hole. Lowest total wins.""",
    },
    {
        "id": "frisbee-tag",
        "name": "Frisbee Tag",
        "min_players": 4,
        "max_players": 15,
        "equipment": ["Frisbee"],
        "areas": ["grass", "small_yard"],
        "energy": "high",
        "summary": "Tag where the thrower must complete a pass to freeze opponents.",
        "base_rules": """### Frisbee Tag
- One team holds the frisbee and can only move by passing.
- A completed pass lets the thrower tag a runner (soft touch with the disc below the neck).
- Everyone tagged swaps teams.""",
    },
    {
        "id": "capture-the-flag",
        "name": "Capture the Flag",
        "min_players": 8,
        "max_players": 30,
        "equipment": ["Cones"],
        "areas": ["grass"],
        "energy": "high",
        "summary": "Two teams, two flags, two halves of a field — steal theirs and get home safe.",
        "base_rules": """### Capture the Flag
- Split the field in half; each team hides a flag (cone/bandana) in its zone.
- Cross to grab their flag; tagged on enemy turf → jail.
- Teammates free jailed players with a touch (free walk back).
- Win by carrying the enemy flag back to your side.""",
    },
    {
        "id": "cone-relay",
        "name": "Cone Relay Races",
        "min_players": 4,
        "max_players": 30,
        "equipment": ["Cones"],
        "areas": ["grass", "hard_ground", "small_yard"],
        "energy": "high",
        "summary": "Teams sprint shuttle relays around cones — sprint, bear-crawl, skip, hop.",
        "base_rules": """### Cone Relays
- Even teams line up behind a start cone; one cone per team ~15m out.
- Round 1: sprint out and back, tag the next teammate.
- Add variety rounds: bear crawl, skipping, sideways shuffle, hopping.
- First team through all rounds wins.""",
    },
    {
        "id": "keep-away",
        "name": "Keep Away (Monkey in the Middle)",
        "min_players": 3,
        "max_players": 10,
        "equipment": ["Ball"],
        "areas": ["grass", "small_yard", "hard_ground"],
        "energy": "medium",
        "summary": "Pass the ball around the defender in the middle; intercepted? Swap.",
        "base_rules": """### Keep Away
- One player in the middle; everyone else circles up with a ball.
- Outer players pass; the middle player tries to intercept.
- Whoever throws an intercepted/bad pass swaps into the middle.""",
    },
    {
        "id": "soccer-mini",
        "name": "Small-Sided Soccer",
        "min_players": 4,
        "max_players": 14,
        "equipment": ["Ball", "Cones"],
        "areas": ["grass"],
        "energy": "high",
        "summary": "3v3 or 5v5 with cone goals — first to 3 wins.",
        "base_rules": """### Small-Sided Soccer
- Cone goals ~3m wide, no keepers.
- Everything else is normal soccer, shortened: first to 3 or 10 minutes.
- Rotate subs every goal.""",
    },
    {
        "id": "dodgeball-soft",
        "name": "Dodgeball (Soft Rules)",
        "min_players": 6,
        "max_players": 20,
        "equipment": ["Ball", "Cones"],
        "areas": ["grass", "hard_ground", "indoor"],
        "energy": "high",
        "summary": "Hit opponents below the shoulders with a soft ball; last team standing wins.",
        "base_rules": """### Dodgeball
- Two teams on their own halves; balls start on the center line.
- Hit a player below the shoulders → they're out. A caught throw → thrower out AND one teammate back in.
- No head shots. Win by eliminating the other team.""",
    },
    {
        "id": "mother-may-i",
        "name": "Mother, May I?",
        "min_players": 3,
        "max_players": 15,
        "equipment": [],
        "areas": ["grass", "hard_ground", "indoor", "small_yard"],
        "energy": "low",
        "summary": "Ask permission to take giant/scissor/baby steps — forget 'Mother may I?' and go back.",
        "base_rules": """### Mother, May I?
- One player is **Mother** at the far end.
- Players ask *"Mother, may I take 3 giant steps?"* — Mother says yes or offers a different step.
- Forget to ask → back to start. First to reach Mother wins.""",
    },
    {
        "id": "what-time-mr-wolf",
        "name": "What's the Time, Mr. Wolf?",
        "min_players": 4,
        "max_players": 20,
        "equipment": [],
        "areas": ["grass", "small_yard", "hard_ground"],
        "energy": "medium",
        "summary": "Step closer as the wolf calls times — when it's 'dinner time', run!",
        "base_rules": """### What's the Time, Mr. Wolf?
- One **wolf** stands away from the line of players.
- Players chant *"What's the time, Mr. Wolf?"* — wolf answers a time, players take that many steps.
- On *"Dinner time!"* the wolf chases; anyone tagged becomes a wolf.""",
    },
    {
        "id": "sardines",
        "name": "Sardines",
        "min_players": 4,
        "max_players": 15,
        "equipment": [],
        "areas": ["small_yard", "indoor", "grass"],
        "energy": "low",
        "summary": "Reverse hide-and-seek: one hides, everyone joins them in the hiding spot.",
        "base_rules": """### Sardines
- One player hides; everyone else counts and then searches alone.
- Find the hider → squeeze in and hide with them.
- Last person to find the group loses (and hides next).""",
    },
    {
        "id": "balloon-keep-up",
        "name": "Balloon Keep-Up",
        "min_players": 2,
        "max_players": 10,
        "equipment": ["Ball"],
        "areas": ["indoor", "small_yard"],
        "energy": "low",
        "summary": "Keep a balloon (or light ball) off the ground — team counts consecutive touches.",
        "base_rules": """### Balloon Keep-Up
- Use a balloon or very light ball.
- Everyone must keep it airborne; count consecutive touches.
- Add rules: no one touches twice in a row, or use only your feet/head for a harder round.""",
    },
    {
        "id": "horse",
        "name": "HORSE (Basketball)",
        "min_players": 2,
        "max_players": 6,
        "equipment": ["Ball"],
        "areas": ["hard_ground"],
        "energy": "medium",
        "summary": "Copy-shot basketball — miss the copy and take a letter.",
        "base_rules": """### HORSE
- Player 1 shoots from anywhere (declare trick shots).
- If they score, everyone must copy; miss → take a letter (H-O-R-S-E).
- Miss the opener and the next player chooses the shot.
- Spell HORSE and you're out.""",
    },
    {
        "id": "obstacle-course",
        "name": "Obstacle Course Challenge",
        "min_players": 2,
        "max_players": 20,
        "equipment": ["Cones", "Jump Rope", "Chalk", "Ball"],
        "areas": ["grass", "small_yard", "hard_ground"],
        "energy": "high",
        "summary": "Build a timed course from whatever you have — cones to weave, ropes to hop, chalk targets.",
        "base_rules": """### Obstacle Course
- Use everything on hand: cones to weave, a rope line to tightrope, chalk targets to land, a ball to dribble/carry.
- Time each runner; fastest clean run wins.
- Rebuild the course each round for variety.""",
    },
    {
        "id": "treasure-hunt",
        "name": "Chalk Treasure Hunt",
        "min_players": 2,
        "max_players": 10,
        "equipment": ["Chalk"],
        "areas": ["hard_ground", "small_yard"],
        "energy": "medium",
        "summary": "Draw a trail of chalk clues and arrows leading to a 'treasure'.",
        "base_rules": """### Chalk Treasure Hunt
- One player draws a winding trail: arrows, riddles, and mini-challenges ('do 10 hops here').
- Hunters follow it to the treasure (any fun object).
- Swap roles each round.""",
    },
    {
        "id": "shadow-tag",
        "name": "Shadow Tag",
        "min_players": 3,
        "max_players": 15,
        "equipment": [],
        "areas": ["grass", "hard_ground"],
        "energy": "medium",
        "summary": "Tag by stepping on shadows instead of touching people.",
        "base_rules": """### Shadow Tag
- Needs sunshine! One player is **it**.
- **It** tags by stepping on someone's shadow.
- Players can shrink their shadow by crouching — but only for 3 seconds.""",
    },
    {
        "id": "octopus",
        "name": "Octopus Tag",
        "min_players": 6,
        "max_players": 30,
        "equipment": ["Cones"],
        "areas": ["grass"],
        "energy": "high",
        "summary": "Like Sharks and Minnows, but tagged players become rooted seaweed helpers.",
        "base_rules": """### Octopus
- One **octopus** mid-field; fish run end to end.
- Tagged fish become **seaweed**: feet planted, arms waving to tag others.
- Last free fish wins.""",
    },
]
