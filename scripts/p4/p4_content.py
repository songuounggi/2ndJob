# -*- coding: utf-8 -*-
"""상품 4 The ADHD Home Reset -- 페이지에 미리 인쇄될 문구 원고 + 검사 (PROCESS.md 2단계).

기획: product4-content.md (3절 페이지 지도, 4절 문구 목록, 7절 문구 원칙). 이 파일이 문구의 원본이다.
빌드 스크립트는 여기서 읽는다 -- 페이지에 문구를 직접 쓰지 않는다(5-1 기획서 대조가 여기와 PDF 를 비교한다).

    python scripts/p4/p4_content.py          # 검사 + 검수용 CSV (output/prod4/content/<VERSION>/)

문구 원칙 (product4-content.md 7절):
  1 한 칸 = 한 가지 일. 할 일은 동사로 시작, 6단어 이내
  2 죄책감 금지 -- streak·fail·behind·lazy·should 없음. 놓친 날은 다음 칸으로 밀 뿐
  3 "Done enough" 가 기본값. 완벽 기준을 인쇄하지 않는다
  4 의학적 주장 금지  5 1인칭 당사자 표현 금지  6 남의 방법론 이름·고유 용어를 가져오지 않는다
  7 미국 영어
"""
import csv
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VERSION = "v0.5"   # v0.5 = 빌드 코드에 박혀 있던 문구 23개를 원고로(5-1 검수에서 찾음) -- 사용자 확인 전   # v0.4 v0.4 = 전체 빌드용 페이지 제목·부제·칸 이름(PAGE_TEXT) 추가 -- 사용자 확인 전   # v0.3 v0.3 = 2쪽 순서도(FLOW) 추가 (2026-09-30 사용자: 순서도 2쪽, Start here 3쪽)   # v0.2 v0.2 = 사용법 안내 70자 안으로, "behind" 금지어를 뜻(밀렸다)으로만   # v0.1 = 첫 원고 (2026-09-30)

# --------------------------------------------------------------- 표지·사용법 --
COVER = ("The ADHD Home Reset", "clean by energy, not by schedule")

START_HERE = {
    "title": "Start here",
    "sub": "Thirty seconds, then you're cleaning.",
    "steps": [
        ("Check your battery", "Low, medium, or full? Pick a task that fits.", "energy"),
        ("Pick one room", "Tap it on the house map. Ten minutes, then stop.", "house-map"),
        ("All too much?", "Tap SOS on any page. Rescue first, tidy later.", "rescue"),
    ],
    "note": "Blank boxes are normal. No streaks, no catching up.",
}

# 2쪽 순서도 (2026-09-30 사용자 제안). 칸마다 링크. 칸 문구는 Start here·페이지 이름에서 온다
FLOW = {
    "title": "How it flows", "sub": "Tap any box to go there.",
    "boxes": {   # key: (제목, 한 줄, 링크 대상)
        "open": ("Open the planner", "", "start"),
        "battery": ("Check your battery", "Low, medium, or full", "energy"),
        "sos": ("All too much?", "Tap SOS on any page", "rescue"),
        "energy": ("Energy menu", "Pick by minutes", "energy"),
        "rescue": ("Rescue mode", "Five steps, then stop", "rescue"),
        "room": ("Room card", "Ten-minute reset", "house-map"),
        "done": ("Done enough", "Stop there", "house-map"),
        "wins": ("Wins log", "It counts", "wins"),
        "weeks": ("Once a week", "Reset week: one room a day", "weeks"),
    },
}

# ------------------------------------------------------------------- 방 --
# key, 이름, 10분 리셋 순서 6단계, Done enough 한 줄, 필요한 도구, 깊은 청소 8개
ROOMS = [
    ("kitchen", "Kitchen",
     ["Take out trash and recycling", "Gather dishes into the sink", "Put food back in the fridge",
      "Clear one counter", "Wipe counters and stovetop", "Sweep the middle of the floor"],
     "Counters clear, sink not overflowing.",
     ["trash bags", "dish soap", "spray", "cloth", "broom"],
     ["Clean out the fridge", "Wipe inside the microwave", "Degrease the stovetop", "Clean the oven door",
      "Wipe cabinet fronts", "Clean the dishwasher filter", "Scrub the sink and drain", "Mop the whole floor"]),
    ("bathroom", "Bathroom",
     ["Empty the trash can", "Hang towels or hamper them", "Put products in one bin",
      "Wipe the sink and faucet", "Swish the toilet bowl", "Wipe the mirror if there's time"],
     "Sink wiped, toilet swished, floor clear.",
     ["toilet brush", "spray", "cloth", "trash bags"],
     ["Scrub the shower walls", "Wash the shower curtain", "Clean the grout lines", "Wipe behind the toilet",
      "Wash the bath mats", "Clear out old products", "Clean the exhaust fan cover", "Mop the floor"]),
    ("bedroom", "Bedroom",
     ["Open the curtains", "Clothes into one basket", "Cups and plates to the door",
      "Pull up the covers", "Clear the nightstand", "Clear a path to the door"],
     "Covers pulled up, path to the door clear.",
     ["laundry basket", "trash bag", "cloth"],
     ["Change and wash the sheets", "Vacuum under the bed", "Dust the headboard and lamps",
      "Sort one dresser drawer", "Clear the closet floor", "Wash the pillows", "Wipe the light switches",
      "Flip or rotate the mattress"]),
    ("living", "Living room",
     ["Cups and dishes to the kitchen", "Trash into one bag", "Fold the blankets",
      "Remotes and chargers in one spot", "Clear the coffee table", "Vacuum the middle of the room"],
     "You could sit down, and so could a guest.",
     ["trash bag", "basket", "vacuum", "cloth"],
     ["Vacuum under the couch cushions", "Dust shelves and frames", "Wash the throw blankets",
      "Wipe the TV and remotes", "Clean the windowsills", "Sort the magazine and mail pile",
      "Wash the cushion covers", "Vacuum along the baseboards"]),
    ("entry", "Entry & hallway",
     ["Pair the shoes by the door", "Hang up the coats", "Mail to the desk tray",
      "Bags off the floor", "Keys into their bowl", "Shake out the door mat"],
     "You can walk in without stepping over anything.",
     ["shoe rack", "key bowl", "broom"],
     ["Wipe the front door", "Sort the coat closet", "Donate shoes nobody wears",
      "Clean the light fixture", "Wipe the hallway walls", "Wash the door mat", "Sweep behind the door",
      "Restock the umbrella and bags"]),
    ("laundry", "Laundry",
     ["Move the wet load to the dryer", "Start the next load", "Fold only what is dry",
      "Hang what wrinkles", "Carry piles to their rooms", "Clear the lint trap"],
     "Nothing wet sitting in the washer.",
     ["baskets", "hangers", "detergent"],
     ["Run a washer cleaning cycle", "Wipe the washer door seal", "Clean the dryer vent",
      "Sort the odd socks", "Wipe the top of the machines", "Toss empty bottles", "Wash the laundry baskets",
      "Sweep behind the machines"]),
    ("desk", "Desk & office",
     ["Cups and trash off the desk", "Papers into one inbox pile", "Pens back in one cup",
      "Cables into one spot", "Wipe the desk surface", "Write tomorrow's first task"],
     "Room to open a laptop and a notebook.",
     ["inbox tray", "cloth", "trash bag"],
     ["Shred old papers", "Empty the desk drawers", "Wipe the keyboard and mouse", "Untangle the cables",
      "Dust the monitor", "Sort the inbox pile to zero", "Clear the desktop files", "Wipe the chair"]),
    ("car", "Car",
     ["Trash into one bag", "Cups and bottles out", "Returns and bags to the house",
      "Shake out the floor mats", "Wipe the wheel and cup holders", "Toss old receipts from the glove box"],
     "Front seat empty enough for a passenger.",
     ["trash bag", "wipes", "small bin"],
     ["Vacuum the seats and floor", "Clean the inside windows", "Wash the floor mats", "Empty the trunk",
      "Wipe the dashboard", "Clean the door pockets", "Restock the car kit", "Wash the outside"]),
]
MY_ROOM = ("myroom", "My room")     # 이름·순서를 구매자가 채운다 -- 미리 인쇄 없음

# ----------------------------------------------------------------- 에너지 --
BATTERIES = ["Low", "Medium", "Full"]
MINUTES = [2, 5, 10, 20]
# (배터리, 분) -> [(할 일, 링크 대상)]. 대상은 방 key 또는 loop key
ENERGY = {
    ("Low", 2):     [("Take out one bag of trash", "kitchen"), ("Wipe the bathroom sink", "bathroom"),
                     ("Line up the shoes by the door", "entry")],
    ("Low", 5):     [("Load five dishes", "dishes-loop"), ("Start one laundry load", "laundry-loop"),
                     ("Clear the nightstand", "bedroom")],
    ("Low", 10):    [("Fold one basket sitting down", "laundry-loop"), ("Empty the car door pockets", "car"),
                     ("Reset the couch and pillows", "living")],
    ("Low", 20):    [("Unload and reload the dishwasher", "dishes-loop"), ("Sort the mail pile", "desk")],
    ("Medium", 2):  [("Wipe the stovetop", "kitchen"), ("Wipe the bathroom mirror", "bathroom")],
    ("Medium", 5):  [("Clear the kitchen counter", "kitchen"), ("Pull up the covers", "bedroom"),
                     ("Sweep the entry", "entry")],
    ("Medium", 10): [("Clean the toilet", "bathroom"), ("Vacuum one room", "living"),
                     ("Put away one basket", "laundry-loop")],
    ("Medium", 20): [("Change the sheets", "bedroom"), ("Clean out the fridge", "kitchen")],
    ("Full", 2):    [("Take out the recycling", "kitchen"), ("Swap in fresh hand towels", "bathroom")],
    ("Full", 5):    [("Wipe down the desk", "desk"), ("Shake out the door mat", "entry")],
    ("Full", 10):   [("Mop the kitchen floor", "kitchen"), ("Scrub the shower walls", "bathroom"),
                     ("Clear the desk to empty", "desk")],
    ("Full", 20):   [("Vacuum the car", "car"), ("Deep clean one cabinet", "kitchen"),
                     ("Wash the towels and bath mats", "laundry-loop")],
}

DAY_PAGES = {   # Low / Medium / Full day 페이지 (product4-content.md 3-2)
    "Low": ("Low battery day", "Small is still a reset."),
    "Medium": ("Medium battery day", "Enough for one room, maybe two."),
    "Full": ("Full battery day", "Spend it on the thing that keeps nagging."),
}
DAY_PAGE_CARDS = [("Today I'll do", "pick three at most"), ("On in the background", "music, a podcast, a call"),
                  ("After, I get", "a small reward, chosen now"), ("That's enough for today", "check it and stop")]

# --------------------------------------------------------------- 루틴 --
DAILY_RESET = {
    "Morning (5 min)": ["Pull up the covers", "Open the curtains", "Dishes from last night to the sink"],
    "Evening (10 min)": ["Load or soak the dishes", "Wipe the kitchen counter", "Set tomorrow's bag by the door"],
}
MONTHLY = ["Clean out the fridge", "Wipe inside the microwave", "Clean the dishwasher filter",
           "Run a washer cleaning cycle", "Vacuum under the bed", "Wipe light switches and handles",
           "Wipe the baseboards", "Wash the shower curtain", "Check the freezer", "Dust fans and vents",
           "Wash the trash cans", "Clear out one drawer"]
SEASONAL = {
    "Spring": ["Wash the windows inside", "Put away winter coats", "Wash the curtains",
               "Clear out the entry closet", "Clean behind the fridge"],
    "Summer": ["Clean the fans", "Wash the outdoor cushions", "Test the smoke alarms",
               "Clear out the freezer", "Donate one bag"],
    "Fall": ["Wash bedding for winter", "Put away summer clothes", "Deep clean the oven",
             "Restock the car kit", "Clear the gutters or ask for help"],
    "Winter": ["Wipe salt off the entry floor", "Wash the throw blankets", "Clean the humidifier",
               "Sort the holiday decorations", "Donate one bag"],
}
# 루프: (단계, 여기서 멈추면 -> 대책)
LAUNDRY_LOOP = [("Wash", "Set a phone timer when you start it"),
                ("Dry", "Move it the moment the timer rings"),
                ("Fold", "Skip folding: hang it or use bins"),
                ("Put away", "Carry it to the room, even unfolded")]
DISHES_LOOP = [("Use", "Keep one cup per person out"),
               ("Soak", "Fill the sink with hot water first"),
               ("Wash", "Set a 10-minute timer, stop when it rings"),
               ("Put away", "Unload while the kettle boils")]
WEEKLY_ROTATION_SUB = "One room a day. Missed one? Slide it to the next."

# ----------------------------------------------------------------- 도구 --
RESCUE = {
    "title": "Rescue mode", "sub": "When it's all too much. Rescue, don't organize.",
    "steps": [("Trash first", "Walk the room with one bag. Only trash.", "kitchen"),
              ("Gather the dishes", "Everything to the sink. Washing can wait.", "dishes-loop"),
              ("One basket of clothes", "Clean or not, into one basket. Sort later.", "laundry-loop"),
              ("Clear a path", "Floor things into a box. Just the path.", "house-map"),
              ("One surface", "Clear one table or counter. Then stop.", "wins")],
    "after": "Log it in Wins. Rescue counts.",
}
SPRINT = ("15-minute sprint", "Three rounds of five minutes. Stop when the last ring is done.")
GUESTS = ("Guests in 2 hours", "Only what they'll see.",
          ["Entry: shoes and coats away", "Bathroom: swish, wipe, fresh towel", "Living room: cups out, blankets folded",
           "Kitchen: dishes in, counter wiped", "Everything else into one box", "Close the doors they won't use"])
DECLUTTER = ("Declutter decisions", "Stuck on keep or toss? Ask these.",
             ["When did I last use it?", "Would I buy it again today?", "Does it have a place here?",
              "Is it someone else's to return?", "Is it taking space I need?"])
DOOM_PILE = ("Doom pile triage", "One pile, fifteen minutes.",
             ["Keep here", "Toss", "Belongs elsewhere", "Needs action"])
DOPAMINE = ("Cleaning dopamine menu", "What makes the boring part easier?",
            [("Soundtrack", "playlists that get you moving"), ("Something to listen to", "podcasts, audiobooks"),
             ("Company", "a call, a friend, body doubling online"), ("Reward", "what you get when it's done"),
             ("Make it a game", "beat the timer, one song per task")])
TOOL_PAGES = {   # 제목, 부제 (칸만 있는 페이지)
    "body-doubling": ("Body doubling log", "Cleaning is easier with someone around."),
    "wins": ("Wins log", "What you did, not what's left."),
    "guess-actual": ("Time guess vs actual", "The dishes took eight minutes, not an hour."),
    "where-things-live": ("Where things live", "No home for it, no way to put it away."),
    "restock": ("Restock list", "Buy it before it runs out."),
    "projects": ("Projects list", "Too big for one day? Write the first step only."),
    "big-reset": ("Moving or big reset", "One checklist for the big days."),
    "kids-pets": ("Kids & pets tasks", "Jobs they can own."),
    "who-does-what": ("Who does what", "Split it on paper before it turns into an argument."),
    "house-map": ("House map", "Tap a room. Ten minutes, then stop."),
    "energy": ("Energy menu", "Pick by battery and time, not by day."),
    "monthly": ("Monthly deep clean", "One a month. Any order."),
    "seasonal": ("Seasonal reset", "Four times a year."),
    "daily": ("Daily reset", "Once a day, one small thing."),
}
WEEK_PAGE = ("Reset week {n}", "This week's rooms, one deep clean, and the wins.")


# ------------------------------------------------ 전체 빌드용 작은 문구 --
# 표본 뒤 전체 빌드에서 새로 생긴 제목·부제·칸 이름 (2026-09-30). 사용자 확인 전 -- 5단계 검수 때 목록으로 보인다
PAGE_TEXT = {
    "index": ("Index", "Everything in here, one tap away."),
    "rooms": ("Rooms", "Pick one. Ten minutes, then stop."),
    "deep": ("{room}: deep clean", "Once a month or once a season. Any order."),
    "myroom": ("My room", "Name it and write your own order."),
    "weeks": ("Weeks", "Fifty-two reset weeks. Start on any week."),
    "tools": ("Tools", "For the days that need a different way in."),
    "notes-ruled": ("Notes", "Lined"), "notes-dots": ("Notes", "Dot grid"), "notes-blank": ("Notes", "Blank"),
}
# 5-1 검수(2026-09-30)에서 찾은 것: 빌드 코드에 직접 박혀 있던 문구. 원고로 옮겼다 -- 사용자 확인 전
SECTION_NAMES = {"home": "Home", "energy": "Energy", "rooms": "Rooms", "routines": "Routines",
                 "weeks": "Weeks", "tools": "Tools"}
COVER_CHIP = "UNDATED · NO-GUILT"
COVER_SUB = "Clean by energy, not by schedule."
COVER_ITEMS = [("Energy menu", "pick by battery and time"), ("Rooms", "nine rooms, ten-minute resets"),
               ("Routines & weeks", "daily, weekly, the loops"), ("Tools", "rescue, sprint, declutter")]
SOS_LABEL = "SOS"
GO = "Go"
START_PROMPT = ("The room that bugs me most", "start there next time")
ROOM_SUB = "Ten minutes, top to bottom. Then stop."
ROTATION_TITLE = "Weekly rotation"
LOOP_PAGES = {"laundry-loop": ("Laundry loop", "Wash, dry, fold, put away. Where do you stop?"),
              "dishes-loop": ("Dishes loop", "Use, soak, wash, put away. Where do you stop?")}

LABELS = {
    # 방 카드
    "reset": "10-minute reset", "done": "Done enough", "need": "You'll need", "last": "Last reset",
    "hot": "Hotspots", "hot_hint": "where it always piles up", "deep_link": "Deep clean list",
    "card_link": "Back to the room card", "task": "Task", "last_done": "Last done", "room_name": "Room name",
    # 에너지·순환·주간
    "pick": "Today's pick", "pick_hint": "one is enough", "slid": "Slid to next week",
    "slid_hint": "no penalty, just the next slot", "week_rooms": "This week's rooms",
    "week_deep": "One deep clean", "week_loops": "Loops this week", "week_wins": "Wins",
    "prev": "Previous week", "next": "Next week", "room": "Room",
    # 루틴
    "stuck": "Stuck here?", "my_fix": "What works for me", "who": "Who", "how_often": "How often",
    "turn": "Whose turn", "kids": "Kids can do", "age": "Age", "pets": "Pet care", "month": "Month",
    "season_extra": "My own",
    # 도구
    "round": "Round", "did": "What I did", "hide": "Everything else goes in one box.",
    "item": "Item", "keep": "Keep", "toss": "Toss", "donate": "Donate", "give_back": "Give back",
    "thing": "Thing", "home": "Its home", "left": "How much is left", "buy": "Buy",
    "full": "Full", "half": "Half", "low": "Low", "with": "With", "how_long": "How long",
    "date": "Date", "minutes": "Minutes", "guess": "Guess", "actual": "Actual",
    "project": "Project", "first_step": "First step", "timer": "Timer set for",
    "deep_chip": "deep clean", "laundry": "Laundry", "dishes": "Dishes",
}

# ----------------------------------------------------------------- 검사 --
BANNED = re.compile(
    r"\b(fail\w*|lazy|should|must|streaks?|(?:fall\w*|fell|get\w*|got|are|you\'re|running) behind|catch(?:ing)? up|perfect\w*|"
    r"cure[sd]?|treat(?:s|ment)?|heal\w*|diagnos\w*|therap\w*|symptom\w*|disorder|"
    r"gross|filthy|disgusting)\b", re.I)
# "No streaks, no catching up" 은 원칙을 말하는 문장이라 허용 -- START_HERE note 만.
# "behind" 는 밀렸다는 뜻만 막는다 -- "Wipe behind the toilet" 같은 위치 표현이 v0.1 에서 잘못 걸렸다
ALLOWED_BANNED = {START_HERE["note"]}
FIRST_PERSON = re.compile(r"\b(I have ADHD|for myself|as someone with|my ADHD)\b", re.I)
UK = re.compile(r"\b(colour|organis\w*|favourite|tidy up|rubbish|bin bags?|hoover\w*|washing up|flat)\b", re.I)
# 남의 방법론 이름·고유 용어 (product4-content.md 7절 6)
BORROWED = re.compile(r"\b(5 things|five things|care tasks|morally neutral|Fly ?Lady|KonMari|spark joy)\b", re.I)


def all_texts():
    """(어디, 문구) 전부"""
    out = [("cover", t) for t in COVER]
    out += [("flow", FLOW["title"]), ("flow", FLOW["sub"])] + [("flow", f"{a} {b}".strip()) for a, b, _ in FLOW["boxes"].values()]
    out += [("start", START_HERE["title"]), ("start", START_HERE["sub"]), ("start", START_HERE["note"])]
    out += [("start", a + " " + b) for a, b, _ in START_HERE["steps"]]
    for key, name, steps, done, tools, deep in ROOMS:
        out += [(key, name), (key, done)] + [(key, s) for s in steps] + [(key, t) for t in tools] + [(key, d) for d in deep]
    out += [("energy", t) for v in ENERGY.values() for t, _ in v]
    out += [("day", t) for p in DAY_PAGES.values() for t in p] + [("day", a + " " + b) for a, b in DAY_PAGE_CARDS]
    out += [("daily", t) for v in DAILY_RESET.values() for t in v] + [("monthly", t) for t in MONTHLY]
    out += [("seasonal", t) for v in SEASONAL.values() for t in v]
    out += [("loop", a + " " + b) for a, b in LAUNDRY_LOOP + DISHES_LOOP] + [("rotation", WEEKLY_ROTATION_SUB)]
    out += [("rescue", RESCUE["title"]), ("rescue", RESCUE["sub"]), ("rescue", RESCUE["after"])]
    out += [("rescue", a + " " + b) for a, b, _ in RESCUE["steps"]]
    out += [("sprint", t) for t in SPRINT] + [("guests", t) for t in GUESTS[:2]] + [("guests", t) for t in GUESTS[2]]
    out += [("declutter", t) for t in DECLUTTER[:2]] + [("declutter", t) for t in DECLUTTER[2]]
    out += [("doom", t) for t in DOOM_PILE[:2]] + [("doom", t) for t in DOOM_PILE[2]]
    out += [("dopamine", t) for t in DOPAMINE[:2]] + [("dopamine", a + " " + b) for a, b in DOPAMINE[2]]
    out += [(k, t) for k, v in TOOL_PAGES.items() for t in v] + [("week", t) for t in WEEK_PAGE]
    out += [(k, t) for k, v in PAGE_TEXT.items() for t in v] + [("label", t) for t in LABELS.values()]
    out += [("section", t) for t in SECTION_NAMES.values()] + [("cover", COVER_CHIP), ("cover", COVER_SUB)]
    out += [("cover", t) for pair in COVER_ITEMS for t in pair] + [("ui", SOS_LABEL), ("ui", GO)]
    out += [("start", t) for t in START_PROMPT] + [("room", ROOM_SUB), ("rotation", ROTATION_TITLE)]
    out += [(k, t) for k, v in LOOP_PAGES.items() for t in v]
    out += [("daily", k) for k in DAILY_RESET] + [("seasonal", k) for k in SEASONAL]
    return out


def words(s):
    return len(s.split())


def check():
    fails = []

    def need(ok, msg):
        if not ok:
            fails.append(msg)

    # 개수 (product4-content.md 3절·4절)
    need(len(ROOMS) == 8, f"방 {len(ROOMS)} != 8 (+ My room)")
    for key, name, steps, done, tools, deep in ROOMS:
        need(len(steps) == 6, f"{name}: 리셋 순서 {len(steps)} != 6")
        need(len(deep) == 8, f"{name}: 깊은 청소 {len(deep)} != 8")
        need(len(done) <= 60, f"{name}: Done enough {len(done)}자 > 60")
    need(set(ENERGY) == {(b, m) for b in BATTERIES for m in MINUTES}, "Energy menu 칸이 3x4 가 아님")
    need(all(2 <= len(v) <= 3 for v in ENERGY.values()), "Energy menu 칸마다 2~3개")
    need(len(MONTHLY) == 12, f"Monthly {len(MONTHLY)} != 12")
    need(all(len(v) == 5 for v in SEASONAL.values()) and len(SEASONAL) == 4, "Seasonal 4 x 5 아님")
    need(len(RESCUE["steps"]) == 5 and len(DECLUTTER[2]) == 5, "Rescue·Declutter 5 아님")
    need(len(LAUNDRY_LOOP) == 4 and len(DISHES_LOOP) == 4, "루프 4단계 아님")

    # 링크 대상이 실제 페이지 key 인가
    pages = {r[0] for r in ROOMS} | {MY_ROOM[0], "dishes-loop", "laundry-loop", "rescue"} | set(TOOL_PAGES)
    pages |= {"start", "weeks"}
    targets = [t for *_, t in FLOW["boxes"].values()] + [t for v in ENERGY.values() for _, t in v] + [t for *_, t in START_HERE["steps"]] + [t for *_, t in RESCUE["steps"]]
    need(not [t for t in targets if t not in pages], f"없는 링크 대상 {[t for t in targets if t not in pages]}")

    # 문구 원칙 1: 할 일은 6단어 이내 (방 순서·Energy·Daily·Monthly·Seasonal·깊은 청소)
    tasks = ([s for r in ROOMS for s in r[2] + r[5]] + [t for v in ENERGY.values() for t, _ in v]
             + [t for v in DAILY_RESET.values() for t in v] + MONTHLY + [t for v in SEASONAL.values() for t in v])
    need(not [t for t in tasks if words(t) > 7], f"7단어 초과 {[t for t in tasks if words(t) > 7]}")
    dup_energy = [t for v in ENERGY.values() for t, _ in v]
    need(len(dup_energy) == len(set(dup_energy)), "Energy menu 중복")
    for key, name, steps, *_ in ROOMS:
        need(len(set(steps)) == 6, f"{name}: 순서 중복")

    texts = all_texts()
    need(not [t for _, t in texts if len(t) > 70], f"70자 초과 {[t for _, t in texts if len(t) > 70][:3]}")
    bad = [t for _, t in texts if BANNED.search(t) and t not in ALLOWED_BANNED]
    need(not bad, f"금지어(죄책감·의학) {bad[:3]}")
    need(not [t for _, t in texts if FIRST_PERSON.search(t)], "1인칭 당사자 표현")
    need(not [t for _, t in texts if UK.search(t)], f"영국식 표기 {[t for _, t in texts if UK.search(t)][:3]}")
    need(not [t for _, t in texts if BORROWED.search(t)], f"남의 방법론 용어 {[t for _, t in texts if BORROWED.search(t)]}")
    return fails


def export_csv():
    path = os.path.join(ROOT, "output", "prod4", "content", VERSION, "p4_content.csv")
    if os.path.exists(path):
        return path + " (이미 있다 -- 덮어쓰지 않음)"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["where", "text", "words", "chars"])
        for where, t in all_texts():
            w.writerow([where, t, words(t), len(t)])
    return path


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    f = check()
    print(f"문구 {len(all_texts())}개 · 방 {len(ROOMS)}+1 · Energy {sum(len(v) for v in ENERGY.values())}개")
    print("FAIL:\n  " + "\n  ".join(f) if f else "검사 통과 (FAIL 0)")
    print("CSV ->", export_csv())
