# -*- coding: utf-8 -*-
"""상품 3 문구 원본. 계획은 product3-content.md. Prod 3 방 소유.

디자인과 무관한 "무엇을 적는가"만 담는다. 와이어프레임(p3_wireframe.py)과
나중의 실제 빌드가 같은 데이터를 읽는다.

    python scripts/p3/p3_content.py          # 검사 + output/p3_content_<연도>.csv

원칙 (product3-content.md 1절): 한 칸 = 한 가지, 70자 이내, 죄책감 금지,
의학적 주장 금지(제안만), 미국 영어.
"""
import calendar
import csv
import datetime as dt
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))   # scripts/p3/ -> 저장소

# ------------------------------------------------------------ 4-1 intro --
HOW_IT_WORKS = {
    "title": "How this planner works",
    "sub": "Three ideas. Everything else is optional.",
    "ideas": [
        ("52 experiments",
         "Each week has one small strategy to try. On Friday, mark it: "
         "helped, sort of, or not for me. By December you have a playbook "
         "that was tested on your own brain."),
        ("Time links",
         "Tonight's \"Tomorrow starts with\" waits for you on tomorrow's page. "
         "A \"Note to future me\" arrives 30 days later. Tap the chips to travel."),
        ("Time you can see",
         "Every day shows how far into the year and the month you are, and "
         "asks you to guess how long things take. Guesses get better."),
    ],
    "rules": [
        "Tap the side tabs to jump anywhere. SOS is for when you are stuck.",
        "Month, then date, takes you to that day. The chips at the top bring you back.",
        "Skip days. Skip weeks. Nothing here counts streaks.",
        "A blank box is not a failure. It is a box.",
    ],
}

# ---------------------------------------------------------- 4-2 SOS hub --
# 증상 -> 상품 1 도구 키(build_planner GROUPS). NEW 는 이 상품에서 새로 만든 도구.
SOS = [
    ("I can't start", "Break it into silly-small steps", "tasks"),
    ("I can't decide", "Narrow it to two, then pick", "paralysis"),
    ("Too much in my head", "Empty it onto paper", "braindump"),
    ("I keep avoiding it", "Find the small reason", "avoiding"),
    ("The deadline is scary", "Work backwards from the date", "deadline"),
    ("I lost the whole day", "Where did the hours go?", "hyperfocus"),
    ("I'm overwhelmed", "Stop, think, then act", "sta"),
    ("Someone's words stung", "What else could it have meant?", "rsd"),
    ("My inner critic is loud", "Answer it like a friend would", "kind"),
    ("I can't stop worrying", "Break the loop", "worry"),
    ("I want to buy it right now", "The 10-minute check", "impulse"),
    ("Bored and restless", "Order from your dopamine menu", "dopamine"),
    ("Mess everywhere", "Triage one doom pile", "doompile"),
    ("I have an appointment later", "Beat waiting mode", "waiting"),
]

# ----------------------------------------------------- 4-3 month themes --
MONTHS = [
    ("Systems, not resolutions", "Build one small system you will still use in March.",
     "Which system actually stuck this month?"),
    ("Tiny routines", "Two minutes counts. Start smaller than you think.",
     "Which tiny routine is starting to feel automatic?"),
    ("Clear one zone", "One drawer, one shelf, one corner. No marathons.",
     "Which space feels lighter now?"),
    ("Move a little", "Any movement counts. Find the kind you enjoy.",
     "What kind of movement did you actually enjoy?"),
    ("Mind your mind", "May is Mental Health Awareness Month. Check in kindly.",
     "What helped your mind feel steadier?"),
    ("Midyear keep and drop", "Keep what works. Drop what doesn't. No guilt.",
     "What will you stop doing for the rest of the year?"),
    ("Rest without earning it", "Rest is part of the plan, not a prize for finishing.",
     "When did you truly rest this month?"),
    ("Get ready early", "Back-to-routine month. Prepare before the rush.",
     "What prep made the biggest difference?"),
    ("Fresh start", "A new season is a good time to begin again.",
     "What new start are you proud of?"),
    ("Know your brain", "October is ADHD Awareness Month. Learn one thing about how you work.",
     "What did you learn about how your brain works?"),
    ("Protect your energy", "Busy season ahead. Plan the rest before the rush.",
     "What are you glad you said yes, or no, to?"),
    ("Close the year gently", "Celebrate what you did. Keep it simple.",
     "What do you want to remember about this year?"),
]

MONTH_REVIEW = [  # 상품 1 review 4개 + 테마 질문(MONTHS[2]) 이 5번째
    ("What went well", ""),
    ("What was hard", ""),
    ("What I learned about how I work", ""),
    ("One thing to change next month", "just one"),
]

# ------------------------------------------------ 4-4 life admin radar --
ADMIN = [
    ["Set up this year's planner", "Review every subscription", "Book the yearly check-up", "Back up phone photos"],
    ["Start a tax paperwork folder", "Check insurance renewal dates", "Clean out the fridge", "Plan one friend night"],
    ["Clocks may change: test smoke alarms", "Declutter one zone", "Check car or license renewals", "Book a dental visit"],
    ["Tax deadline in many places: check yours", "Swap seasonal clothes", "Review last month's spending", "Clean one window"],
    ["Mental health check-in", "Check passport expiry before summer", "Replace your toothbrush", "Plan summer time off"],
    ["Midyear money check", "Renew anything expiring in summer", "Restock first-aid and sunscreen", "Clear the car"],
    ["Back up your devices", "Check refills and prescriptions", "Plan one real rest day", "Clean out one closet"],
    ["Back-to-routine prep", "Book a dental visit", "Update emergency contacts", "Restock supplies"],
    ["Fall reset of one room", "Check heating and filters", "Review every subscription", "Book seasonal appointments"],
    ["Learn one thing about ADHD", "Test smoke alarms", "Start the gift list", "Plan autumn budget"],
    ["Set a holiday budget", "Book holiday travel early", "Clocks may change: reset alarms", "Write three thank-yous"],
    ["Use-it-or-lose-it benefits", "Donate one bag", "Year-end review", "Set up next year's planner"],
]

# ------------------------------------------- 4-5 question of the day --
# 요일별 7갈래 x 53. 그 요일의 "그 해 n 번째"로 고른다 -> 계절이 맞는다
# (26 번째 = 7월 초 midyear, 50~53 번째 = 12월).
DAILY = {
    0: ("Plan", [  # Monday
        "What's the one thing that would make this week lighter?",
        "Which task have you been carrying in your head? Write it down.",
        "What can wait until next week, honestly?",
        "Put one deadline somewhere you will actually see it.",
        "What does \"good enough\" look like this week?",
        "Which task needs a first step smaller than you think?",
        "Who could help with one thing this week?",
        "What's one thing you can say no to this week?",
        "Your hardest task: morning, afternoon, or evening slot?",
        "What would future-you thank you for setting up today?",
        "Name one thing you are looking forward to this week.",
        "Which day looks heaviest? Plan something easy for it.",
        "What's the smallest version of your biggest goal?",
        "What keeps getting pushed? Give it a time, not a wish.",
        "What do you need to buy, book, or reply to this week?",
        "Which task could you do with a friend or a timer?",
        "What's already on your plate that you can delete?",
        "Set one reminder now for something you always forget.",
        "What would a calm Monday afternoon look like?",
        "Describe this week in three words.",
        "Which boring task can you pair with music or a podcast?",
        "Which message would take under two minutes?",
        "What deadline are you quietly worried about?",
        "How much free time do you really have? Guess, then check.",
        "What's one promise to yourself you can keep this week?",
        "Halfway through the year: what still matters?",
        "What would feel amazing to cross off by Friday?",
        "What can you prepare tonight to make tomorrow easier?",
        "Which errand can ride along with another one?",
        "What's the first thing you'll do when you sit down to work?",
        "What can you hand off, automate, or skip?",
        "What would make this week 10% easier?",
        "Who do you need to check in with this week?",
        "Pick one thing to finish instead of three to start.",
        "Energy forecast for the week: low, medium, or high?",
        "Leave one block this week completely open.",
        "What did you avoid last week? What's step one?",
        "Plan one break you will actually take.",
        "Which space needs five minutes of attention?",
        "What's the plan if the plan falls apart?",
        "What's one habit to try, just for this week?",
        "Which bill, form, or renewal is coming up?",
        "What will you do the moment you feel stuck?",
        "What can you drop to protect your sleep this week?",
        "Choose a stop time for work each day this week.",
        "What would you love to learn about this week?",
        "What's coming this month that needs a step this week?",
        "What's the kindest schedule you could give yourself?",
        "What would make this a good week, even if nothing else happens?",
        "Which gift, card, or plan needs a first step?",
        "What can you simplify for the busy weeks ahead?",
        "Which loose ends do you want to close before the year ends?",
        "What will you carry into next year, and what will you leave?",
    ]),
    1: ("Focus", [  # Tuesday
        "Which task deserves your best hour today?",
        "Set a 10-minute timer and start. Start what?",
        "Where do you focus best? Can you work there today?",
        "What pulls your attention most? Hide it for an hour.",
        "Break your task into steps so small they feel silly.",
        "What's the very first physical action? Open, find, write?",
        "Try body doubling: work beside someone, even on video.",
        "If you only had 20 minutes, what would you do first?",
        "Which tab, app, or alert can you close right now?",
        "Write the distraction down instead of following it.",
        "What does \"done\" look like for today's main task?",
        "Pick a reward for after your focus block.",
        "When is your brain sharpest? Guard that time.",
        "How many short sprints can you fit in today?",
        "Make a boring task a race against the timer.",
        "What noise do you need: silence, music, or café?",
        "What can you do standing up or walking around?",
        "Start with the easiest part to get moving.",
        "Name the task you are avoiding. Just name it.",
        "What's one thing you can finish before lunch?",
        "Park your phone in another room for one block.",
        "Guess how long your main task takes. Check later.",
        "What would make starting feel less scary?",
        "Try \"just five minutes\" on something today.",
        "Which small task can you knock out right now?",
        "Is today's hyperfocus aimed at the right thing?",
        "Set a noon alarm to check in with yourself.",
        "Write your next step on a sticky note in plain sight.",
        "Save half-attention tasks for low-energy time.",
        "Put your task list where you can't ignore it.",
        "Change your spot. Does a new place help you start?",
        "Make one decision now instead of later.",
        "Which task needs a deadline you invent yourself?",
        "If you get stuck, what's your unstick move?",
        "Tell someone what you are working on, out loud.",
        "What one thing, once done, makes the rest easier?",
        "Clear one surface before you begin.",
        "Plan one 25-minute focus block today.",
        "Which thought keeps interrupting? Park it in the brain dump.",
        "Work with a visible timer today.",
        "What's the task hiding behind the one you avoid?",
        "Finish one thing before opening something new.",
        "What's your plan for the afternoon slump?",
        "Write a three-step launch list for your work session.",
        "Give your next meeting a one-line goal.",
        "What can you delete from today's list without guilt?",
        "Pick a start time and treat it like an appointment.",
        "What's almost done? Finish it today.",
        "What's the 80% version of today's task?",
        "Where did your focus go yesterday? What would help today?",
        "One task for your best energy, one for your worst.",
        "What would make today's work a little bit fun?",
        "Close one open loop before the year closes.",
    ]),
    2: ("Body", [  # Wednesday
        "Have you had water yet today?",
        "What did you eat before noon? Anything with protein?",
        "How did you sleep, and what would help tonight?",
        "Take a 5-minute walk. Where to?",
        "Did you take what you need to take today? Check the box.",
        "Stretch for the length of one song. Which song?",
        "Pick a time for lunch today and write it here.",
        "When will you start winding down tonight?",
        "Step outside for a minute of daylight.",
        "Is your body asking for food, rest, or movement?",
        "Refill your water bottle now.",
        "Keep one easy snack within reach today.",
        "Energy check: 1 to 5?",
        "Move in any way for 10 minutes.",
        "When is your next appointment or refill due?",
        "Put your phone to bed before you go to bed.",
        "What's one meal you can make without thinking?",
        "Unclench your jaw. Drop your shoulders. Breathe out slowly.",
        "How much screen time before bed last night?",
        "Dance to one song. Seriously.",
        "Did you eat a real lunch yesterday? What about today?",
        "What helps you fall asleep? Did you do it last night?",
        "Go outside, even if it's just to the mailbox.",
        "Note any symptom or side effect to mention at your next visit.",
        "What gives you energy without caffeine?",
        "Take the stairs, stretch, or walk during a call.",
        "Set a last-coffee time for today.",
        "Plan or pack tomorrow's food tonight.",
        "Your body today, in one word?",
        "Drink a glass of water before your next task.",
        "Try a 3-minute stretch between tasks.",
        "One change that would make your bedroom better for sleep?",
        "Plan one active thing for the weekend.",
        "What does your body need more of this week?",
        "Did you move today? Anything counts.",
        "Eat something with color today.",
        "What time did you actually go to bed last night?",
        "Take a short walk after a meal.",
        "Check your posture. Adjust your chair or screen.",
        "Which comfort food also treats you well?",
        "Look at something far away for 20 seconds.",
        "Book the check-up you have been putting off.",
        "How many glasses of water so far?",
        "Tonight's wind-down in three steps?",
        "Get fresh air before the afternoon slump.",
        "Which habit is quietly helping your body?",
        "Cold days: how will you move indoors?",
        "Plan a proper meal for your busiest day.",
        "Tired or bored? Check before reaching for a snack.",
        "Rest counts too. When will you rest this week?",
        "Busy season: what's your plan to keep sleeping well?",
        "Water between the treats today?",
        "Your body carried you all year. Say thank you.",
    ]),
    3: ("Feelings", [  # Thursday
        "How are you feeling right now, in one word?",
        "What's weighing on you? Write it down to set it aside.",
        "What would you say to a friend who felt like you do?",
        "What went better than you expected this week?",
        "Which thought keeps looping? Fact or fear?",
        "Who makes you feel understood?",
        "What small thing can you forgive yourself for today?",
        "Where do you feel stress in your body right now?",
        "What are you proud of that nobody saw?",
        "What boundary would protect your energy?",
        "Did something sting this week? What else could it mean?",
        "Write one kind sentence to yourself.",
        "What's making you anxious, and what's in your control?",
        "When did you last laugh really hard?",
        "What's your first sign of overwhelm? Spot it early.",
        "What calms you down fastest? List three.",
        "Which conversation are you avoiding? Write the first line.",
        "One small thing you're grateful for today?",
        "Which emotion showed up most this week?",
        "What would make today feel 5% better?",
        "Who could you send a \"thinking of you\" message?",
        "What did you learn about yourself this month?",
        "Name a feeling without judging it. Just name it.",
        "What did you do this week that took courage?",
        "When you feel frustrated, what helps you reset?",
        "What are you tired of pretending about?",
        "What made you feel capable recently?",
        "Write one worry down and close it for today.",
        "What would you like more of right now?",
        "Which comment are you replaying? Does it deserve the space?",
        "What does rest look like for your mind?",
        "What are you looking forward to?",
        "What would \"gentle\" look like today?",
        "How did you handle something hard this week?",
        "Which mistake taught you something useful?",
        "Who do you feel safe being yourself around?",
        "Are you carrying a feeling from yesterday? Can you set it down?",
        "What made you smile today?",
        "What do you need to hear right now?",
        "How do you know you're getting close to burnout?",
        "What does your brain do that you actually like?",
        "Your emotional weather today: sunny, cloudy, or stormy?",
        "What did you handle better than last time?",
        "What would support look like for you this week?",
        "What can you let be not perfect?",
        "Write three things that are going okay.",
        "What are you thankful for this season?",
        "What drained you this week, and what refilled you?",
        "Which feeling would you like to feel more often?",
        "Who do you want to thank before the year ends?",
        "How will you protect your peace during the holidays?",
        "Which feeling do you want to bring into the new year?",
        "What would you tell the you from January?",
    ]),
    4: ("Wins", [  # Friday
        "What got done this week? Big or tiny, list it.",
        "Which win did you almost not count?",
        "What worked this week that you want to repeat?",
        "Which task did you finally start?",
        "Celebrate one thing today. How?",
        "What would past-you be impressed by this week?",
        "What's one thing you finished?",
        "Who helped you this week?",
        "What was the best part of this week?",
        "What did you handle calmly?",
        "Write this week's done list.",
        "What was harder than expected, and you did it anyway?",
        "Which habit did you keep, even once?",
        "Where did you show up for someone else?",
        "What small step moved a big goal forward?",
        "What did you stop doing that was good for you?",
        "What did you learn this week?",
        "What did you do on time?",
        "When did you feel most like yourself this week?",
        "Rate the week out of 10. Why that number?",
        "What did you say no to? Good.",
        "What problem did you solve?",
        "What surprised you in a good way?",
        "Which task took less time than you feared?",
        "What are you proud of this month so far?",
        "Halfway through the year: list five wins.",
        "What did you make, fix, or tidy?",
        "What kind thing did you do for yourself?",
        "What did you remember without a reminder?",
        "What did you do even though you didn't feel like it?",
        "Share one win with someone today.",
        "What went right today?",
        "What deserves a high-five from you to you?",
        "Which progress would you have missed without writing it down?",
        "Which routine is getting easier?",
        "What did you start that excites you?",
        "Which small win made the biggest difference?",
        "What did you do this week just for fun?",
        "What are you better at than last year?",
        "What did you do for future-you?",
        "Where did a strategy actually work?",
        "Best thing you ate, saw, or heard this week?",
        "Which deadline did you meet?",
        "What did you let go of this week?",
        "Who would be proud of you this week?",
        "Which win from this month do you want to remember?",
        "What are you most glad you did this year?",
        "What did you finish before the rush?",
        "Which moment or tradition did you enjoy?",
        "Write three wins from this season.",
        "What did you do for someone else this month?",
        "What made this year better than you expected?",
        "Your top three wins of the year. Write them big.",
    ]),
    5: ("Play", [  # Saturday
        "What would be fun today? No productivity allowed.",
        "Which hobby do you miss? Could you give it 15 minutes?",
        "Try something new today, however small.",
        "What's your favorite way to do nothing?",
        "Plan one thing just for joy this weekend.",
        "Which place nearby have you never visited?",
        "What music makes you want to move?",
        "Who do you want to see this weekend?",
        "What small treat can you enjoy today?",
        "Make something with your hands today.",
        "What are you curious about right now?",
        "Go somewhere with trees, water, or sky.",
        "Which game, show, or book is calling you?",
        "Cook or bake something just for fun.",
        "Which childhood hobby could you try again?",
        "Take a photo of something beautiful today.",
        "What's the most fun you've had this month?",
        "Unplug for one hour. What will you do instead?",
        "Plan a small adventure for next weekend.",
        "What would turn today into a mini holiday?",
        "Rearrange one corner just for fun.",
        "Which skill would you learn purely for fun?",
        "Call someone who makes you laugh.",
        "Describe your perfect lazy morning.",
        "Try a new podcast, album, or artist.",
        "Summer mode: what's on your fun list?",
        "Have a picnic, even if it's on the floor.",
        "Which hyperfocus hobby makes you happy?",
        "Say yes to something spontaneous (and safe).",
        "Watch the sunset or the sunrise.",
        "Which creative project could you start small?",
        "Play a game you haven't played in years.",
        "Visit a market, library, or bookstore.",
        "What made you feel like a kid lately?",
        "Doodle, build, or puzzle for a while.",
        "Plan a cozy night in.",
        "Which new recipe would you like to try?",
        "Take a different route on a walk.",
        "What would you do with a completely free day?",
        "Your favorite thing about fall?",
        "Make a playlist for today's mood.",
        "Spend time with an animal, a plant, or the outdoors.",
        "What silly thing made you laugh?",
        "Treat yourself to a slow breakfast.",
        "What would you do on a \"yes day\"?",
        "Try a new café, park, or shop.",
        "Which cozy ritual gets you through colder days?",
        "List the little things that make you happy.",
        "Plan something fun with a friend before the year ends.",
        "Which holiday tradition do you enjoy most?",
        "Wrap, craft, or decorate something today.",
        "How do you want to celebrate the end of the year?",
        "What's one new thing to try next year?",
    ]),
    6: ("Reset", [  # Sunday
        "What needs to be ready before Monday?",
        "Clear your bag, desk, or inbox. Pick one.",
        "Keys, wallet, and meds: one spot.",
        "Look at next week. Which surprise can you avoid?",
        "Five-minute tidy: which room?",
        "Lay out what you need for tomorrow morning.",
        "Which chore would make the week easier?",
        "Check your calendar for the next seven days.",
        "What's running low? Refill, restock, recharge.",
        "Quick brain dump of everything on your mind.",
        "Laundry, dishes, or trash: 15 minutes on one.",
        "Plan three simple meals for the week.",
        "Charge your devices and set your alarms.",
        "Which paperwork or bill needs attention this week?",
        "Reset your workspace for a fresh start.",
        "What will you do differently this week?",
        "Cross off anything that no longer matters.",
        "Prep one thing for your busiest weekday.",
        "Clean out one drawer or one fridge shelf.",
        "Write next week's top three.",
        "Which reminders do you need to set?",
        "Pick outfits for the first days of the week.",
        "Do one \"someday\" task today.",
        "Tidy your desktop, downloads, or photos.",
        "What needs to be returned, mailed, or picked up?",
        "Midyear reset: which system needs a tune-up?",
        "Water the plants, feed the pets, check the basics.",
        "Set up a launch pad by the door.",
        "Prepare one thing for an appointment this week.",
        "Last week in one sentence?",
        "Wipe one surface that makes you feel calmer.",
        "Plan this week's walks or workouts.",
        "Empty one bag, box, or pile.",
        "Any birthdays or events coming this month?",
        "Unsubscribe from three emails you never read.",
        "Which routine will you restart this week?",
        "Refill your water bottle and prep snacks.",
        "Clear your notes app or sticky notes.",
        "Choose one no-plans evening this week.",
        "Fall reset: swap seasonal clothes or gear.",
        "Back up your phone or computer.",
        "Prepare one thing tonight for Monday morning.",
        "Pay or schedule bills due soon.",
        "Declutter ten things.",
        "Check supplies. Anything to reorder?",
        "What's the plan for this week's busiest day?",
        "Holiday prep: what can you start early?",
        "Make a gift or shopping list.",
        "Rest is part of the reset. How will you rest today?",
        "Check the holiday calendar for clashes.",
        "Reset your space before guests or travel.",
        "Year-end tidy: what can you archive or toss?",
        "Set up your planner for the new year.",
    ]),
}

# ---------------------------------------------------- 4-7 experiments --
EXPERIMENTS = [
    ("Brain dump first", "Before planning, write every task on paper.", "Choosing is easier when it's all in front of you."),
    ("One must-do a day", "Pick one must-do each morning. The rest is bonus.", "One clear target beats a list of twelve."),
    ("Body doubling", "Do one task next to someone, in person or on video.", "Company makes starting less lonely."),
    ("Timer sprints", "Work 20 minutes, break 5. Repeat.", "A finish line you can see."),
    ("Launch pad", "One spot by the door for keys, wallet, bag, and meds.", "Fewer morning hunts."),
    ("Trip over it", "Put tomorrow's task where you will literally see it.", "Out of sight really is out of mind."),
    ("Two-minute rule", "Under two minutes? Do it now.", "Tiny tasks stop piling up."),
    ("Done list", "Write what you finished, not only what's left.", "Progress you can see is fuel."),
    ("Guess vs actual", "Guess how long tasks take, then time them.", "Your guesses improve with data."),
    ("Habit stacking", "Attach a new habit to one you already do.", "The old habit becomes the reminder."),
    ("Default meals", "Pick three no-think meals for busy days.", "Fewer decisions at 6 p.m."),
    ("Named alarms", "Label alarms with actions: \"Leave now\", \"Take meds\".", "A label says what to do, not just the time."),
    ("Decide once", "Make one standing rule, like gym on Tuesday and Thursday.", "No daily debate."),
    ("Walk between blocks", "Take a 3-minute walk between focus sessions.", "Movement resets restlessness."),
    ("Make it easy", "Set up the good choice in advance, like water on the desk.", "Less effort, more follow-through."),
    ("Buffer time", "Add 10 minutes between everything.", "Transitions take longer than they look."),
    ("Sunday setup", "Spend 30 minutes on Sunday prepping the week.", "Monday starts half done."),
    ("Next-step notes", "Stop each task by writing the very next step.", "Restarting is the hard part."),
    ("Phone in another room", "One focus block a day with the phone out of reach.", "Distance beats willpower."),
    ("Temptation pairing", "Pair a dull task with something you enjoy.", "The fun part pulls you in."),
    ("Batch it", "Group errands or calls into one block.", "One start instead of five."),
    ("Say it out loud", "Tell someone your plan for the day.", "A plan said out loud is easier to keep."),
    ("Energy map", "Rate your energy three times a day, all week.", "Find your best hours."),
    ("Good enough", "Define the 80% version before you start.", "Done beats perfect."),
    ("Shutdown ritual", "End work the same way every day.", "A clear stop protects the evening."),
    ("Midyear keep and drop", "List what worked this year. Drop one thing that didn't.", "Less, but better."),
    ("Hotspot clear", "Clear the one surface that fills up first, daily.", "Small, visible, doable."),
    ("Plan in sight", "Keep this week's plan open where you'll see it.", "A hidden plan is a forgotten plan."),
    ("Waiting-mode kit", "Before an appointment, pick one small task for the wait.", "The day stops disappearing."),
    ("Parking lot", "Write stray ideas down instead of chasing them.", "Keep the idea, skip the detour."),
    ("Five-minute start", "Commit to five minutes. You may stop after.", "Starting is most of the battle."),
    ("Body check first", "Water, snack, and stretch before a hard task.", "Hard things are harder on empty."),
    ("Single tab", "Keep only the tab you need open.", "Fewer doors, fewer detours."),
    ("Evening pre-decide", "Choose tonight's plan by 3 p.m.", "Evenings stop evaporating."),
    ("Pen and paper", "Write the day's plan by hand.", "For many people, writing it makes it stick."),
    ("Beat the clock", "Race a timer on one chore a day.", "Urgency without the panic."),
    ("Routine card", "Put your morning steps on one card, in order.", "Follow the card, not your memory."),
    ("Hand one off", "Delegate or drop one task this week.", "Not everything is yours to carry."),
    ("Same wake time", "Get up at the same time every day, weekends too.", "A steady anchor for sleep."),
    ("One in, one out", "Something new comes in, something old goes out.", "Clutter stops growing."),
    ("Message windows", "Answer messages at two set times a day.", "Fewer interruptions."),
    ("What could go wrong?", "Before a big day, list three snags and a fix for each.", "Surprises shrink."),
    ("Money day", "One day a month for all bills and admin.", "Fewer surprise late fees."),
    ("Change rooms", "When stuck, move to a different spot.", "New place, fresh start."),
    ("Friday look-ahead", "Every Friday, glance at next week.", "Monday has no ambushes."),
    ("Ready-made no", "Keep one polite \"no\" sentence ready.", "Saying no is easier with a script."),
    ("Gift list now", "Start a running list of gift ideas.", "December-you will be grateful."),
    ("Spending cap", "Set a holiday budget before you shop.", "A number decides for you."),
    ("Rest on the calendar", "Book rest around busy events.", "Recovery is part of the plan."),
    ("Recharge corner", "Pick a quiet spot to step away at gatherings.", "A short break keeps you going longer."),
    ("Simplest version", "Do the easy version of one tradition.", "Keep the joy, lose the stress."),
    ("Win review", "Reread your done lists before planning next year.", "Plan from strength."),
    ("Keep the best three", "Pick three experiments that worked for next year.", "Your own playbook, tested."),
]

PATTERN_QS = [
    "My best days this month came after...",
    "My rough days came after...",
    "Sleep and focus: do they move together for me?",
]

WEEKLY_RESET = [
    "Calendar: look at the next seven days",
    "Launch pad: keys, wallet, meds in one spot",
    "Food: three easy meals decided",
    "Clothes: first two days picked",
    "Money: anything due this week?",
    "Space: one surface cleared",
]

# ------------------------------------------------------ 4-9 new tools --
TOOLS = {
    "dopamine": ("Dopamine menu", "Order from here when you are bored, flat, or restless.", [
        ("Starters", "five minutes or less", "one song, cold water on your face, step outside"),
        ("Mains", "when you have real time", "a walk with a podcast, cooking, a creative project"),
        ("Sides", "to add to boring tasks", "music, a fidget, a nice drink, a timer race"),
        ("Desserts", "sometimes, on purpose", "a show, a game, scrolling with a timer set"),
        ("Specials", "rare and worth planning", "a day trip, a concert, a new hobby class"),
    ]),
    "doompile": ("Doom pile triage", "Didn't Organize, Only Moved. One pile, fifteen minutes.", [
        ("Keep", "it lives here now", ""),
        ("Toss or recycle", "no second thoughts", ""),
        ("Belongs elsewhere", "put it back later, in one trip", ""),
        ("Needs action", "copy to today's to-do", ""),
    ]),
    "graveyard": ("Hobby graveyard", "Every hobby you tried taught you something. No shame here.", [
        ("Hobby or project", "", ""), ("How long it lasted", "", ""),
        ("What I got from it", "", ""), ("Bring it back?", "yes / maybe / rest in peace", ""),
    ]),
    "waiting": ("Waiting-mode kit", "When one appointment eats the whole day.", [
        ("Appointment", "what and when", ""),
        ("Leave at", "work backwards: travel + parking + 10 minutes", ""),
        ("Before it, I can", "short tasks that end on time", ""),
        ("Bring", "what you need to have with you", ""),
    ]),
}

# --------------------------------------------------- 4-6 holidays --
# 아래 둘은 지금 인쇄에 쓰지 않는다. 나라별 공휴일 스티커(§5-2 ④)를 만들 때 쓴다.
def nth_weekday(y, m, wd, n):
    """n 번째(1..) 요일. n=-1 이면 마지막."""
    days = [d for d in calendar.Calendar().itermonthdates(y, m) if d.month == m and d.weekday() == wd]
    return days[n - 1] if n > 0 else days[-1]


def easter(y):
    a, b, c = y % 19, y // 100, y % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = (h + l - 7 * m + 114) % 31 + 1
    return dt.date(y, month, day)


def holidays(y):
    """전 세계 어디서도 틀리지 않는 날만 인쇄한다 (2026-09-25 사용자 결정, product3-content.md §5-2).

    나라별 공휴일은 날짜도 이름도 다르다 -- 미국 공휴일을 박으면 미국 밖 구매자에게는
    틀린 정보가 된다(첫 구매자가 브라질이었다). 자기 나라 날은 "My holidays" 페이지에
    적는다. 크리스마스는 예외로 넣는다(사용자: "크리스마스는 못 참지").
    어머니날·부활절·추수감사절처럼 나라마다 날짜가 다른 것은 넣지 않는다.
    """
    D = dt.date
    return {
        D(y, 1, 1): "New Year's Day",
        D(y, 10, 1): "ADHD Awareness Month",
        D(y, 10, 10): "World Mental Health Day",
        D(y, 12, 25): "Christmas Day",
        D(y, 12, 31): "New Year's Eve",
    }


MY_HOLIDAYS = ("My holidays",
               "Public holidays, school breaks, days off. Write the ones where you live.")


# ---------------------------------------------------------- accessors --
def nth_of_weekday(d):
    """d 가 그 해 같은 요일 중 몇 번째인가 (0-based)."""
    return (d.timetuple().tm_yday - 1) // 7


def question(d):
    cat, qs = DAILY[d.weekday()]
    return cat, qs[nth_of_weekday(d)]


def year_weeks(y, week_start=0):
    jan1, dec31 = dt.date(y, 1, 1), dt.date(y, 12, 31)
    first = jan1 - dt.timedelta((jan1.weekday() - week_start) % 7)
    out = []
    while first <= dec31:
        out.append(first)
        first += dt.timedelta(7)
    return out


def experiment(n):
    """주 번호(1..) -> 실험. 53주가 없는 해도 있으니 마지막은 언제나 'Keep the best three'."""
    return EXPERIMENTS[min(n, len(EXPERIMENTS)) - 1]


def future_note_target(d):
    t = d + dt.timedelta(30)
    return t if t.year == d.year else None     # None -> Year-end mailbox


# ------------------------------------------------------------- checks --
# "treat it like", "treats"(간식)는 의학이 아니다 -- 치료 주장만 잡는다
BANNED = re.compile(r"\b(cure[sd]?|treatment|diagnos\w*|dosage|dose|disorder|fix your)\b"
                    r"|\btreat\w*\s+(adhd|symptoms?|your brain)\b", re.I)


def check():
    fails = []
    def need(ok, msg):
        if not ok:
            fails.append(msg)
    for wd, (cat, qs) in DAILY.items():
        need(len(qs) == 53, f"DAILY {cat}: {len(qs)} != 53")
    allq = [q for _, qs in DAILY.values() for q in qs]
    dup = {q for q in allq if allq.count(q) > 1}
    need(not dup, f"DAILY 중복 {sorted(dup)[:3]}")
    need(len(EXPERIMENTS) == 53, f"EXPERIMENTS {len(EXPERIMENTS)} != 53")
    need(len({e[0] for e in EXPERIMENTS}) == 53, "EXPERIMENTS 이름 중복")
    need(len(MONTHS) == 12 and len(ADMIN) == 12, "MONTHS/ADMIN 12 아님")
    texts = (allq + [x for e in EXPERIMENTS for x in e] + [x for m in MONTHS for x in m]
             + [x for a in ADMIN for x in a] + [s[0] + s[1] for s in SOS] + WEEKLY_RESET)
    long = [t for t in texts if len(t) > 70]
    need(not long, f"70자 초과 {len(long)}: {long[:3]}")
    bad = [t for t in texts if BANNED.search(t)]
    need(not bad, f"금지어 {bad[:3]}")
    # 인쇄 공휴일은 나라를 타지 않는 것만 (2026-09-25 결정). 미국 것이 다시 들어오면 잡는다.
    local = re.compile(r"Thanksgiving|Memorial|Independence|Labor|Presidents|King|Juneteenth|Veterans|"
                       r"Mother|Father|Easter|Halloween|Valentine", re.I)
    for y in (2026, 2027):
        leak = [v for v in holidays(y).values() if local.search(v)]
        need(not leak, f"{y} 나라별 공휴일이 인쇄됨: {leak}")
        need(holidays(y).get(dt.date(y, 12, 25)) == "Christmas Day", f"{y} 크리스마스 없음")
    return fails


def export_csv(y, week_start=0):
    path = os.path.join(ROOT, "output", f"p3_content_{y}.csv")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    hol = holidays(y)
    weeks = year_weeks(y, week_start)
    week_of = {w + dt.timedelta(i): n for n, w in enumerate(weeks, 1) for i in range(7)}
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["date", "weekday", "day_of_year", "days_left", "holiday",
                    "category", "question_of_the_day", "week", "experiment",
                    "month_theme", "note_arrives"])
        d = dt.date(y, 1, 1)
        total = 366 if calendar.isleap(y) else 365
        while d.year == y:
            cat, q = question(d)
            doy = d.timetuple().tm_yday
            t = future_note_target(d)
            w.writerow([d.isoformat(), calendar.day_name[d.weekday()], doy, total - doy,
                        hol.get(d, ""), cat, q, week_of[d], experiment(week_of[d])[0],
                        MONTHS[d.month - 1][0], t.isoformat() if t else "Year-end mailbox"])
            d += dt.timedelta(1)
    return path


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    f = check()
    for m in f:
        print("FAIL", m)
    n = sum(len(q) for _, q in DAILY.values())
    print(f"질문 {n} / 실험 {len(EXPERIMENTS)} / 테마 {len(MONTHS)} / admin {sum(map(len, ADMIN))} "
          f"/ SOS {len(SOS)} / 도구 {len(TOOLS)}")
    for y in (2026, 2027):
        print(export_csv(y), "|", ", ".join(f"{k:%m-%d} {v}" for k, v in sorted(holidays(y).items())))
    print("전부 통과" if not f else f"FAIL {len(f)}")
    sys.exit(1 if f else 0)
