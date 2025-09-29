from js import document, alert
from pyodide.ffi import create_proxy  # <-- crucial for wiring Python -> JS events
import string
import random

MAX_WRONG = 6

WORDS = [
    "python","hangman","keyboard","function","variable","iterator","package","library",
    "notebook","algorithm","computer","program","teacher","student","network","database",
    "object","inheritance","composition","encapsulation","polymorphism","abstraction",
    "exception","module","tuple","string","integer","boolean","recursion","generator","comprehension"
]

# ---------------- UI helpers ----------------
def set_word_display(text: str):
    document.getElementById("word").innerText = text

def set_score(won: int, played: int):
    document.getElementById("score").innerText = f"Score: {won}/{played}"

def disable_letter(letter: str, value: bool = True):
    btn = document.getElementById(f"btn-{letter}")
    if btn:
        btn.disabled = value

def reveal_parts(count: int):
    parts = ["part1","part2a","part3","part4","part5","part6"]
    for i, pid in enumerate(parts, start=1):
        el = document.getElementById(pid)
        if not el:
            continue
        if i <= count:
            el.classList.remove("hidden")
        else:
            el.classList.add("hidden")

def reset_parts():
    reveal_parts(0)

def build_letters():
    """Build letter buttons in the <aside> area and attach proxied Python handlers."""
    letters_div = document.getElementById("letters")
    letters_div.innerHTML = ""
    for ch in string.ascii_uppercase:
        btn = document.createElement("button")
        btn.className = "letter"
        btn.id = f"btn-{ch}"
        btn.textContent = ch

        # Create a proxied Python function so JS can call it safely
        def handler(evt, ch=ch):
            guess(ch)
        btn.addEventListener("click", create_proxy(handler))

        letters_div.appendChild(btn)

# ---------------- Game state ----------------
played = 0
won = 0
target = ""
guessed = set()
wrong = 0

def pick_word():
    return random.choice(WORDS).upper()

def display_word():
    return " ".join([c if c in guessed else "_" for c in target])

def new_game():
    global target
    target = pick_word()
    restart_game()

def restart_game():
    global guessed, wrong
    guessed = set()
    wrong = 0
    set_word_display(display_word())
    reset_parts()
    # re-enable all letters
    for ch in string.ascii_uppercase:
        disable_letter(ch, False)

def is_over():
    return wrong >= MAX_WRONG or set(target) <= guessed

def check_winner():
    global played, won
    played += 1
    if wrong < MAX_WRONG:
        won += 1
        msg = f"You won! Word: {target}\nScore: {won}/{played}\n(Starting a new round…)"
    else:
        msg = f"You lost! Word was: {target}\nScore: {won}/{played}\n(Starting a new round…)"
    set_score(won, played)
    alert(msg)
    new_game()

def guess(letter: str):
    global wrong
    if letter in guessed or is_over():
        return
    guessed.add(letter)
    disable_letter(letter, True)
    if letter not in target:
        wrong += 1
    set_word_display(display_word())
    reveal_parts(wrong)
    if is_over():
        check_winner()

# ---------------- Actions ----------------
def setup_actions():
    document.getElementById("new").addEventListener("click", create_proxy(lambda e: new_game()))
    document.getElementById("restart").addEventListener("click", create_proxy(lambda e: restart_game()))
    document.getElementById("quit").addEventListener("click", create_proxy(lambda e: alert("Close the tab to quit 🙂")))

# ---------------- Boot ----------------
build_letters()
setup_actions()
set_score(won, played)
new_game()

