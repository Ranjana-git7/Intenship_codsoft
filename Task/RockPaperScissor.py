import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk, ImageSequence
import random
import json
import os

# ----------------- Config -----------------
SCOREFILE = "rps_scores.json"

# Optional images: place in same folder or edit paths below
ROCK_IMG = "rock.png"          # optional
PAPER_IMG = "paper.png"        # optional
SCISSORS_IMG = "scissors.png"  # optional

# Developer-provided uploaded file path (used as home background if present)
UPLOADED_BG = "/mnt/data/fa450121-4956-43b8-a0f0-35de8dd1a8c7.png"
# ------------------------------------------

class RPSApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SUPER Rock-Paper-Scissors")
        self.geometry("900x600")
        self.minsize(780, 520)
        self.configure(bg="#111")

        self.user_score = 0
        self.comp_score = 0
        self.load_scores()

        # image storage to avoid GC
        self._images = {}
        self._gif_frames = []

        # create container
        container = tk.Frame(self, bg="#111")
        container.pack(fill="both", expand=True)

        # pages dict
        self.frames = {}
        for F in (HomePage, GamePage, ResultPage):
            page = F(parent=container, controller=self)
            self.frames[F.__name__] = page
            page.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.show_frame("HomePage")

    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()

    def save_scores(self):
        try:
            with open(SCOREFILE, "w", encoding="utf-8") as f:
                json.dump({"user": self.user_score, "comp": self.comp_score}, f)
        except Exception as e:
            print("Save error:", e)

    def load_scores(self):
        if os.path.exists(SCOREFILE):
            try:
                with open(SCOREFILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.user_score = int(data.get("user", 0))
                    self.comp_score = int(data.get("comp", 0))
            except Exception:
                self.user_score = 0
                self.comp_score = 0

    def reset_scores(self):
        self.user_score = 0
        self.comp_score = 0
        self.save_scores()
        # refresh scoreboard on pages
        if "GamePage" in self.frames:
            self.frames["GamePage"].update_scoreboard()

# ---------- utility ----------
def load_image(path, size=None):
    if not os.path.exists(path):
        return None
    try:
        img = Image.open(path).convert("RGBA")
        if size:
            img = img.resize(size, Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception:
        return None

# ---------- Home Page ----------
class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#111")
        self.controller = controller

        # Attempt to use uploaded file as decorative background on home if available
        if os.path.exists(UPLOADED_BG):
            try:
                img = Image.open(UPLOADED_BG).convert("RGBA")
                img = img.resize((900, 600), Image.LANCZOS)
                controller._images["home_bg"] = ImageTk.PhotoImage(img)
                bg_label = tk.Label(self, image=controller._images["home_bg"])
                bg_label.place(relx=0.5, rely=0.5, anchor="center")
            except Exception:
                pass

        # overlay frame so text is readable
        overlay = tk.Frame(self, bg="#000000", bd=0)
        overlay.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.86, relheight=0.86)

        title = tk.Label(overlay, text="SUPER R O C K  •  P A P E R  •  S C I S S O R S",
                         font=("Segoe UI", 20, "bold"), fg="#ffd37f", bg="#111")
        title.pack(pady=(30, 8))

        subtitle = tk.Label(overlay, text="Click play and beat the computer! Best of luck.",
                            font=("Segoe UI", 12), fg="#ddd", bg="#111")
        subtitle.pack(pady=(0, 24))

        btn_frame = tk.Frame(overlay, bg="#111")
        btn_frame.pack()

        play_btn = ttk.Button(btn_frame, text="Play Game", command=lambda: controller.show_frame("GamePage"))
        play_btn.grid(row=0, column=0, padx=12, pady=12)

        scores_btn = ttk.Button(btn_frame, text="Reset Scores", command=self.confirm_reset)
        scores_btn.grid(row=0, column=1, padx=12, pady=12)

        quit_btn = ttk.Button(btn_frame, text="Quit", command=controller.quit)
        quit_btn.grid(row=0, column=2, padx=12, pady=12)

        # show current scoreboard
        self.score_label = tk.Label(overlay,
                                    text=self._score_text(),
                                    font=("Segoe UI", 12),
                                    fg="#aaf7c7", bg="#111")
        self.score_label.pack(pady=(20, 6))

    def _score_text(self):
        c = self.controller
        return f"High Scores — You: {c.user_score}    Computer: {c.comp_score}"

    def confirm_reset(self):
        if messagebox.askyesno("Reset Scores", "Are you sure you want to reset scores?"):
            self.controller.reset_scores()
            self.score_label.config(text=self._score_text())
            self.controller.show_frame("GamePage")

# ---------- Game Page ----------
class GamePage(tk.Frame):
    CHOICES = ["rock", "paper", "scissors"]
    EMOJI = {"rock":"🪨", "paper":"📄", "scissors":"✂️"}

    def __init__(self, parent, controller):
        super().__init__(parent, bg="#0f0f12")
        self.controller = controller

        header = tk.Frame(self, bg="#0f0f12")
        header.pack(fill="x", pady=(8,0))

        back = ttk.Button(header, text="← Home", command=lambda: controller.show_frame("HomePage"))
        back.pack(side="left", padx=8)

        reset = ttk.Button(header, text="Reset Scores", command=controller.reset_scores)
        reset.pack(side="right", padx=8)

        self.scoreboard = tk.Label(self, text="", font=("Segoe UI", 12, "bold"), fg="#b6f9d6", bg="#0f0f12")
        self.scoreboard.pack(pady=6)
        self.update_scoreboard()

        # area for big choice buttons and images
        main = tk.Frame(self, bg="#0f0f12")
        main.pack(expand=True, fill="both", padx=20, pady=10)

        # load images if available (fall back to emoji)
        img_size = (160, 160)
        rock_img = load_image(ROCK_IMG, img_size) or None
        paper_img = load_image(PAPER_IMG, img_size) or None
        scissor_img = load_image(SCISSORS_IMG, img_size) or None

        # three columns
        col_frame = tk.Frame(main, bg="#0f0f12")
        col_frame.pack(expand=True)

        self.btn_rock = self._make_choice_button(col_frame, "rock", rock_img)
        self.btn_paper = self._make_choice_button(col_frame, "paper", paper_img)
        self.btn_scissors = self._make_choice_button(col_frame, "scissors", scissor_img)

        # quick instructions
        instr = tk.Label(self, text="Choose your move — first click registers your selection.",
                         font=("Segoe UI", 11), fg="#ccc", bg="#0f0f12")
        instr.pack(pady=(8,12))

        # area to show round result (brief)
        self.round_label = tk.Label(self, text="", font=("Segoe UI", 14, "bold"), fg="#ffd37f", bg="#0f0f12")
        self.round_label.pack(pady=4)

    def _make_choice_button(self, parent, choice, img):
        frame = tk.Frame(parent, bg="#0f0f12", padx=20)
        frame.pack(side="left", padx=8)
        if img:
            btn = tk.Button(frame, image=img, text=choice.capitalize(), compound="top",
                            font=("Segoe UI", 10, "bold"), command=lambda c=choice: self.play_round(c),
                            bd=2, relief="ridge", bg="#121218", fg="white", activebackground="#2a2a33")
            # keep reference so not GC'd
            self.controller._images[f"{choice}_img"] = img
        else:
            # fallback big emoji
            btn = tk.Button(frame, text=f"{self.EMOJI[choice]}\n{choice.capitalize()}",
                            font=("Segoe UI", 18), width=8, height=4,
                            command=lambda c=choice: self.play_round(c),
                            bd=2, relief="ridge", bg="#121218", fg="white", activebackground="#2a2a33")
        btn.pack()
        return btn

    def update_scoreboard(self):
        c = self.controller
        self.scoreboard.config(text=f"Score — You: {c.user_score}    Computer: {c.comp_score}")

    def play_round(self, user_choice):
        comp_choice = random.choice(self.CHOICES)
        result = self.judge(user_choice, comp_choice)

        # update scores
        if result == "win":
            self.controller.user_score += 1
        elif result == "lose":
            self.controller.comp_score += 1
        self.controller.save_scores()
        self.update_scoreboard()

        # show brief result then go to ResultPage with details
        msg = f"You chose {user_choice.capitalize()} — Computer chose {comp_choice.capitalize()}."
        if result == "win":
            msg += " You win!"
        elif result == "lose":
            msg += " You lose!"
        else:
            msg += " It's a tie!"
        self.round_label.config(text=msg)
        # pass round data to result page and show it
        rp = self.controller.frames["ResultPage"]
        rp.set_round(user_choice, comp_choice, result)
        self.controller.show_frame("ResultPage")

    @staticmethod
    def judge(user, comp):
        if user == comp:
            return "tie"
        wins = {
            "rock": "scissors",
            "scissors": "paper",
            "paper": "rock"
        }
        return "win" if wins[user] == comp else "lose"

# ---------- Result Page ----------
class ResultPage(tk.Frame):
    EMOJI = {"rock":"🪨", "paper":"📄", "scissors":"✂️"}

    def __init__(self, parent, controller):
        super().__init__(parent, bg="#0e0e12")
        self.controller = controller

        header = tk.Frame(self, bg="#0e0e12")
        header.pack(fill="x", pady=6)
        back = ttk.Button(header, text="← Back", command=lambda: controller.show_frame("GamePage"))
        back.pack(side="left", padx=8)
        home = ttk.Button(header, text="Home", command=lambda: controller.show_frame("HomePage"))
        home.pack(side="right", padx=8)

        # result display area
        box = tk.Frame(self, bg="#0e0e12")
        box.pack(expand=True, fill="both", pady=10, padx=10)

        self.user_label = tk.Label(box, text="", font=("Segoe UI", 18, "bold"), fg="#a8ffd1", bg="#0e0e12")
        self.user_label.pack(pady=(20,6))

        self.comp_label = tk.Label(box, text="", font=("Segoe UI", 18, "bold"), fg="#ffd1a8", bg="#0e0e12")
        self.comp_label.pack(pady=(6,18))

        self.result_big = tk.Label(box, text="", font=("Segoe UI", 36, "bold"), fg="#ffd37f", bg="#0e0e12")
        self.result_big.pack(pady=6)

        # spark animation: simple pulsing rectangle behind result
        self.canvas = tk.Canvas(box, width=420, height=160, bd=0, highlightthickness=0, bg="#0e0e12")
        self.canvas.pack(pady=10)
        self.rect = self.canvas.create_rectangle(10, 10, 410, 140, fill="#1b1b1b", outline="#333")

        btns = tk.Frame(box, bg="#0e0e12")
        btns.pack(pady=12)
        again = ttk.Button(btns, text="Play Again", command=self.play_again)
        again.grid(row=0, column=0, padx=8)
        finish = ttk.Button(btns, text="Home", command=lambda: controller.show_frame("HomePage"))
        finish.grid(row=0, column=1, padx=8)

        # small summary scoreboard
        self.summary = tk.Label(box, text="", font=("Segoe UI", 12), fg="#cfe", bg="#0e0e12")
        self.summary.pack(pady=(8,20))

        # for animation
        self._pulse_dir = 1
        self._pulse_step = 0

    def set_round(self, user_choice, comp_choice, result):
        # show choices (use images if available)
        # if the GamePage used images, we can't easily reuse them here, so use emoji + text
        self.user_label.config(text=f"You: {user_choice.capitalize()} {self.EMOJI[user_choice]}")
        self.comp_label.config(text=f"Computer: {comp_choice.capitalize()} {self.EMOJI[comp_choice]}")

        # big result
        if result == "win":
            txt = "YOU WIN!"
            color = "#7ef0a0"
        elif result == "lose":
            txt = "YOU LOSE!"
            color = "#ff8a8a"
        else:
            txt = "IT'S A TIE!"
            color = "#ffd37f"
        self.result_big.config(text=txt, fg=color)

        # scoreboard summary
        c = self.controller
        self.summary.config(text=f"Scoreboard — You: {c.user_score}    Computer: {c.comp_score}")

        # start pulsing animation
        self._pulse_step = 0
        self._pulse_dir = 1
        self.animate_pulse()

    def animate_pulse(self):
        # simple pulsing by changing rectangle color intensity
        self._pulse_step += self._pulse_dir * 2
        if self._pulse_step > 40:
            self._pulse_dir = -1
        if self._pulse_step < 0:
            self._pulse_dir = 1
        # map step to color
        intensity = 30 + self._pulse_step
        color = f"#{intensity:02x}{intensity:02x}{intensity:02x}"
        try:
            self.canvas.itemconfig(self.rect, fill=color)
        except Exception:
            pass
        # continue animation for a while
        self.after(60, self.animate_pulse)

    def play_again(self):
        # go back to Game page for another round
        self.controller.show_frame("GamePage")


# ---------- Run App ----------
if __name__ == "__main__":
    app = RPSApp()
    app.mainloop()
