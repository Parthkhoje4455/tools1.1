from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import random


app = Flask(__name__)

# win code
def calculate(data):
    total = 0
    mess = ""

    data = data.splitlines()
    clean_data = [i.split(':')[-1].strip() if ":" in i else i.strip() for i in data]

    for i in clean_data:
        if '-' in i:
            spli = i.replace('*', '').split('-')
        else:
            spli = i.replace('*', '').split('=')

        if len(spli) < 3:
            if len(spli[0]) == 1:  # single
                ans = int(spli[1]) * 9.5
                total += ans
                mess += f'{i} = {ans}\n'
            elif len(spli[0]) == 2:  # jodi
                ans = int(spli[1]) * 95
                total += ans
                mess += f'{i} = {ans}\n'
            elif len(spli[0]) == 3:  # pana
                if len(set(str(spli[0]))) == 3:  # SP
                    ans = int(spli[1]) * 150
                elif len(set(str(spli[0]))) == 2:  # DP
                    ans = int(spli[1]) * 300
                elif len(set(str(spli[0]))) == 1:  # TP
                    ans = int(spli[1]) * 600
                else:
                    mess += 'Error\n'
                    continue
                total += ans
                mess += f'{i} = {ans}\n'
            else:
                mess += 'Error\n'
        else:
            if spli[0].lower() == "sp":
                ans = int(spli[2]) * 150
            elif spli[0].lower() == "dp":
                ans = int(spli[2]) * 300
            elif spli[0].lower() == "tp":
                ans = int(spli[2]) * 600
            else:
                mess += 'Error\n'
                continue
            total += ans
            mess += f'{i} = {ans}\n'

    return mess, total

# Message Slite
def generate_results(amount, m_name):
    teams = {
        "team_a": {"ank": [], "pairs": [], "final_result": ""},
        "team_b": {"ank": [], "pairs": [], "final_result": ""}
    }

    # Split digits 0-9 into two non-overlapping groups of three.
    numbers = list(range(10))
    teams["team_a"]["ank"] = random.sample(numbers, 3)
    numbers = [n for n in numbers if n not in teams["team_a"]["ank"]]

    teams["team_b"]["ank"] = random.sample(numbers, 3)
    numbers = [n for n in numbers if n not in teams["team_b"]["ank"]]

    # Create 40 pairs from the four remaining digits.
    pairs = [f"{n}{i}" for n in numbers for i in range(10)]

    # Randomly divide all 40 pairs between the two teams.
    rnd_numb = random.randint(15, 25)
    teams["team_a"]["pairs"] = random.sample(pairs, rnd_numb)
    pairs = [p for p in pairs if p not in teams["team_a"]["pairs"]]
    teams["team_b"]["pairs"] = random.sample(pairs, 40 - rnd_numb)

    for key, value in teams.items():
        lines = [m_name]
        for ank in value["ank"]:
            lines.append(f"{ank}={amount}")
        for pair in value["pairs"]:
            lines.append(f"{pair}={round(amount / 10)}")

        total = round((len(value["pairs"]) * amount / 10) + (amount * 3))
        lines.append(f"Total {total}")
        value["final_result"] = "\n".join(lines)

    return teams



@app.route('/')
def home():
    return render_template('index.html')

# Win Calculator
@app.route("/win", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_data = request.form.get("data", "")

        mess, total = calculate(user_data)

        return render_template(
            "win_result.html",
            mess=mess.splitlines(),
            total=total
        )

    return render_template("win_index.html")


@app.route("/win/result")
def result():
    # Optional backward compatibility for existing result URLs
    data = request.args.get("data", "")
    mess, total = calculate(data)

    return render_template(
        "win_result.html",
        mess=mess.split("\n"),
        total=total
    )





# Profit Loss
@app.route("/profit-loss", methods=["GET", "POST"])
def profit_loss():
    total = request.args.get("total", "")
    total = float(total)
    message = ""
    play = ""
    date = ""

    if request.method == "POST":
        play = request.form.get("play", "").strip()
        date = request.form.get("date", "").strip()

        try:
            play_amount = float(play)

            if date:
                formatted_date = datetime.strptime(date, "%Y-%m-%d").strftime("%d-%m-%Y")
                message += f"*{formatted_date}*\n"
            com = play_amount * 0.06
            pl = play_amount - total - com
            message += f"*Play====={play}*\n*Win====={round(total)}*\n*Com====={round(com)}*\n"
            if pl  >0:
                message += f"*Loss====={round(abs(pl))}--*"
            else:
                message += f"*Profit===={round(abs(pl))}++*"

        except ValueError:
            message = "Please enter a valid Play amount."

    return render_template(
        "profit_loss.html",
        message=message,
        play=play,
        date=date
    )

# Message gen
@app.route("/message", methods=["GET", "POST"])
def message():
    mess = ""
    if request.method == "POST":
        nums = list(request.form["nums"])
        amount = int(request.form["amount"])
        market = request.form["market"]

        ank = amount * 16
        dp = int(amount * 0.5)

        ank_str = ""
        dp_str = ""

        for i in nums:
            ank_str += f"{i}={ank}\n"
            dp_str += f"{i}={dp}\n"

        mess = (f"{market}\n"
                f"{ank_str}"
                f"Total {ank * len(nums)}\n\n"
                f"{market}\n"
                f"DP\n"
                f"{dp_str}"
                f"Total {int(len(nums) * amount * 4.5)}")


    return render_template("dp_index.html", message=mess)


# Message Split
@app.route("/split", methods=["GET", "POST"])
def split():
    error = None
    results = None
    market_name = ""
    amount = ""

    if request.method == "POST":
        market_name = request.form.get("market_name", "").strip()
        amount = request.form.get("amount", "").strip()

        if not market_name:
            error = "Please enter a market name."
        else:
            try:
                amount_value = int(amount)
                if amount_value <= 0:
                    raise ValueError
            except (ValueError, TypeError):
                error = "Please enter a whole number greater than 0 for the amount."
            else:
                results = generate_results(amount_value, market_name)

    return render_template(
        "split.html",
        error=error,
        results=results,
        market_name=market_name,
        amount=amount
    )

if __name__ == '__main__':
    app.run(debug=True)




