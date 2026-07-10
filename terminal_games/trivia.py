import logging
import random
import time
from typing import Dict, List

from arcade_utils import (
    C_CYAN,
    C_GREEN,
    C_MAGENTA,
    C_RED,
    C_RESET,
    C_WHITE,
    C_YELLOW,
    beep,
    clear_screen,
    draw_retro_box,
    show_popup,
)
from base_game import BaseGame
from input_handler import get_safe_input_handler

logger = logging.getLogger(__name__)

QUESTIONS: Dict[str, List[Dict]] = {
    "Science": [
        {
            "q": "What is the chemical symbol for gold?",
            "options": ["Go", "Gd", "Au", "Ag"],
            "answer": 2, "difficulty": "easy",
        },
        {
            "q": "What planet is known as the Red Planet?",
            "options": ["Venus", "Mars", "Jupiter", "Saturn"],
            "answer": 1, "difficulty": "easy",
        },
        {
            "q": "What is the powerhouse of the cell?",
            "options": ["Nucleus", "Ribosome", "Mitochondria", "Golgi"],
            "answer": 2, "difficulty": "easy",
        },
        {
            "q": "How many bones are in the adult human body?",
            "options": ["106", "206", "306", "406"],
            "answer": 1, "difficulty": "medium",
        },
        {
            "q": "What is the speed of light in km/s (approx)?",
            "options": ["300,000", "150,000", "500,000", "1,000,000"],
            "answer": 0, "difficulty": "medium",
        },
        {
            "q": "What element has the highest melting point?",
            "options": ["Tungsten", "Carbon", "Iron", "Platinum"],
            "answer": 0, "difficulty": "hard",
        },
        {
            "q": "What is the half-life of Carbon-14 in years?",
            "options": ["2,730", "5,730", "11,460", "22,920"],
            "answer": 1, "difficulty": "hard",
        },
        {
            "q": "Which particle is responsible for carrying the strong nuclear force?",
            "options": ["Electron", "Photon", "Gluon", "Muon"],
            "answer": 2, "difficulty": "hard",
        },
    ],
    "History": [
        {
            "q": "In what year did World War II end?",
            "options": ["1943", "1944", "1945", "1946"],
            "answer": 2, "difficulty": "easy",
        },
        {
            "q": "Who was the first President of the United States?",
            "options": ["Adams", "Jefferson", "Washington", "Franklin"],
            "answer": 2, "difficulty": "easy",
        },
        {
            "q": "The ancient Mayans were primarily located in which region?",
            "options": ["South America", "Central America", "North Africa", "Southeast Asia"],
            "answer": 1, "difficulty": "medium",
        },
        {
            "q": "Which empire was ruled by Genghis Khan?",
            "options": ["Ottoman", "Roman", "Mongol", "Persian"],
            "answer": 2, "difficulty": "easy",
        },
        {
            "q": "What year did the Berlin Wall fall?",
            "options": ["1987", "1988", "1989", "1990"],
            "answer": 2, "difficulty": "medium",
        },
        {
            "q": "Who was the last pharaoh of ancient Egypt?",
            "options": ["Nefertiti", "Hatshepsut", "Cleopatra", "Ramesses"],
            "answer": 2, "difficulty": "medium",
        },
        {
            "q": "The Treaty of Westphalia ended which war?",
            "options": ["100 Years War", "30 Years War", "War of Roses", "7 Years War"],
            "answer": 1, "difficulty": "hard",
        },
        {
            "q": "What was the name of the first successful steamboat?",
            "options": ["Fulton's Folly", "The Clermont", "The Mayflower", "SS Great Western"],
            "answer": 1, "difficulty": "hard",
        },
    ],
    "Geography": [
        {
            "q": "What is the largest ocean on Earth?",
            "options": ["Atlantic", "Indian", "Arctic", "Pacific"],
            "answer": 3, "difficulty": "easy",
        },
        {
            "q": "What is the capital of Japan?",
            "options": ["Seoul", "Beijing", "Tokyo", "Bangkok"],
            "answer": 2, "difficulty": "easy",
        },
        {
            "q": "Which country has the most natural lakes?",
            "options": ["USA", "Russia", "Canada", "Finland"],
            "answer": 2, "difficulty": "medium",
        },
        {
            "q": "Mount Kilimanjaro is located in which country?",
            "options": ["Kenya", "Tanzania", "Uganda", "Ethiopia"],
            "answer": 1, "difficulty": "medium",
        },
        {
            "q": "What is the smallest country in the world by area?",
            "options": ["Monaco", "San Marino", "Vatican City", "Liechtenstein"],
            "answer": 2, "difficulty": "medium",
        },
        {
            "q": "Which desert is the largest hot desert on Earth?",
            "options": ["Gobi", "Kalahari", "Sahara", "Arabian"],
            "answer": 2, "difficulty": "easy",
        },
        {
            "q": "What is the capital of Mongolia?",
            "options": ["Ulaanbaatar", "Bishkek", "Astana", "Tashkent"],
            "answer": 0, "difficulty": "hard",
        },
        {
            "q": "Which river flows through London?",
            "options": ["Seine", "Danube", "Thames", "Rhine"],
            "answer": 2, "difficulty": "easy",
        },
    ],
    "Entertainment": [
        {
            "q": "Which film won the Oscar for Best Picture in 1994?",
            "options": ["Pulp Fiction", "Forrest Gump", "The Shawshank Redemption", "The Lion King"],
            "answer": 1, "difficulty": "medium",
        },
        {
            "q": "What is the highest-grossing film of all time (unadjusted)?",
            "options": ["Avatar", "Avengers: Endgame", "Titanic", "Star Wars"],
            "answer": 0, "difficulty": "medium",
        },
        {
            "q": "Which band performed \"Bohemian Rhapsody\"?",
            "options": ["Led Zeppelin", "Queen", "The Beatles", "Pink Floyd"],
            "answer": 1, "difficulty": "easy",
        },
        {
            "q": "What year was the first iPhone released?",
            "options": ["2005", "2006", "2007", "2008"],
            "answer": 2, "difficulty": "easy",
        },
        {
            "q": "Who played the Joker in \"The Dark Knight\"?",
            "options": ["Jack Nicholson", "Jared Leto", "Heath Ledger", "Joaquin Phoenix"],
            "answer": 2, "difficulty": "easy",
        },
        {
            "q": "What is the name of the fictional continent in Game of Thrones?",
            "options": ["Westeros", "Middle-earth", "Narnia", "Essos"],
            "answer": 0, "difficulty": "medium",
        },
        {
            "q": "Which video game franchise features a character named \"Master Chief\"?",
            "options": ["Call of Duty", "Halo", "Destiny", "Doom"],
            "answer": 1, "difficulty": "easy",
        },
    ],
    "Technology": [
        {
            "q": "What does \"HTTP\" stand for?",
            "options": ["HyperText Transfer Protocol", "High Transfer Text Protocol",
                         "HyperText Transmission Process", "Home Transfer Text Protocol"],
            "answer": 0, "difficulty": "easy",
        },
        {
            "q": "Who is considered the father of the World Wide Web?",
            "options": ["Vint Cerf", "Tim Berners-Lee", "Bill Gates", "Alan Turing"],
            "answer": 1, "difficulty": "easy",
        },
        {
            "q": "What programming language was created by Guido van Rossum?",
            "options": ["Java", "C++", "Python", "Ruby"],
            "answer": 2, "difficulty": "easy",
        },
        {
            "q": "What does \"SQL\" stand for?",
            "options": ["Simple Query Language", "Structured Query Language",
                         "Standard Query Logic", "Sequential Query Language"],
            "answer": 1, "difficulty": "medium",
        },
        {
            "q": "In what year was the first electronic general-purpose computer (ENIAC) completed?",
            "options": ["1943", "1945", "1947", "1950"],
            "answer": 1, "difficulty": "hard",
        },
        {
            "q": "What does the \"grep\" command do in Unix?",
            "options": ["Search files", "List files", "Delete files", "Copy files"],
            "answer": 0, "difficulty": "medium",
        },
        {
            "q": "Which company developed the Android operating system?",
            "options": ["Apple", "Microsoft", "Google", "IBM"],
            "answer": 2, "difficulty": "easy",
        },
        {
            "q": "What does \"API\" stand for?",
            "options": ["Application Program Interface", "Application Programming Interface",
                         "Automated Program Integration", "Applied Programming Interface"],
            "answer": 1, "difficulty": "easy",
        },
    ],
    "Sports": [
        {
            "q": "In which sport would you perform a \"slam dunk\"?",
            "options": ["Volleyball", "Basketball", "Tennis", "Football"],
            "answer": 1, "difficulty": "easy",
        },
        {
            "q": "How many players are on a standard soccer team?",
            "options": ["9", "10", "11", "12"],
            "answer": 2, "difficulty": "easy",
        },
        {
            "q": "Which country has won the most FIFA World Cups?",
            "options": ["Germany", "Argentina", "Italy", "Brazil"],
            "answer": 3, "difficulty": "easy",
        },
        {
            "q": "What sport is played at Wimbledon?",
            "options": ["Cricket", "Tennis", "Golf", "Badminton"],
            "answer": 1, "difficulty": "easy",
        },
        {
            "q": "In which year were the first modern Olympic Games held?",
            "options": ["1896", "1900", "1904", "1912"],
            "answer": 0, "difficulty": "medium",
        },
        {
            "q": "What is the maximum score in a single frame of bowling?",
            "options": ["10", "20", "30", "50"],
            "answer": 2, "difficulty": "medium",
        },
        {
            "q": "In chess, how many squares are on the board?",
            "options": ["32", "48", "64", "100"],
            "answer": 2, "difficulty": "easy",
        },
    ],
    "Literature": [
        {
            "q": "Who wrote \"Romeo and Juliet\"?",
            "options": ["Charles Dickens", "William Shakespeare", "Jane Austen", "Mark Twain"],
            "answer": 1, "difficulty": "easy",
        },
        {
            "q": "What is the first book of the Harry Potter series?",
            "options": ["Chamber of Secrets", "Prisoner of Azkaban", "Sorcerer's Stone", "Goblet of Fire"],
            "answer": 2, "difficulty": "easy",
        },
        {
            "q": "Who wrote \"1984\"?",
            "options": ["Aldous Huxley", "George Orwell", "Ray Bradbury", "H.G. Wells"],
            "answer": 1, "difficulty": "easy",
        },
        {
            "q": "In \"Moby Dick\", what is the name of the captain?",
            "options": ["Starbuck", "Ahab", "Ishmael", "Queequeg"],
            "answer": 1, "difficulty": "medium",
        },
        {
            "q": "Which Russian author wrote \"War and Peace\"?",
            "options": ["Dostoevsky", "Tolstoy", "Chekhov", "Gogol"],
            "answer": 1, "difficulty": "medium",
        },
        {
            "q": "Who wrote \"The Great Gatsby\"?",
            "options": ["Ernest Hemingway", "F. Scott Fitzgerald", "John Steinbeck", "William Faulkner"],
            "answer": 1, "difficulty": "easy",
        },
    ],
}

CATEGORY_NAMES = sorted(QUESTIONS.keys())

DIFFICULTY_POINTS = {"easy": 10, "medium": 25, "hard": 50}
QUESTIONS_PER_GAME = 10


class TriviaGame(BaseGame):
    def __init__(self, difficulty: str = 'normal') -> None:
        super().__init__('trivia', difficulty)
        self.category: str = ""
        self.questions: List[Dict] = []
        self.question_index = 0
        self.correct_count = 0
        self.total_questions = 0
        self.input_handler = get_safe_input_handler()

    def select_category(self) -> bool:
        """Let the player choose a category. Returns False if cancelled."""
        selection = 0
        num_cats = len(CATEGORY_NAMES)

        while True:
            clear_screen()
            print("\n" * 1)
            lines = [
                f"{C_CYAN}Choose a Category:{C_RESET}",
                "",
            ]
            for i, cat in enumerate(CATEGORY_NAMES):
                marker = f"{C_GREEN}> {C_RESET}" if i == selection else "  "
                lines.append(f"{marker}{C_WHITE}{cat}{C_RESET}")
            lines += [
                "",
                f"{C_YELLOW}↑↓ Navigate  ENTER Select  Q Back{C_RESET}",
            ]
            draw_retro_box(42, "TRIVIA", lines, color=C_MAGENTA)

            key = self.input_handler.get_safe_key()
            if key == 'up':
                selection = (selection - 1) % num_cats
                beep("move")
            elif key == 'down':
                selection = (selection + 1) % num_cats
                beep("move")
            elif key in ['\r', '\n', ' ']:
                self.category = CATEGORY_NAMES[selection]
                beep("correct")
                return True
            elif key and key.lower() == 'q':
                return False
            time.sleep(0.05)

    def build_question_pool(self) -> None:
        """Select questions from the chosen category, filtered by difficulty."""
        pool = [q for q in QUESTIONS[self.category]]
        random.shuffle(pool)

        diff_map = {"easy": 0, "normal": 1, "hard": 2}
        diff_level = diff_map.get(self.difficulty, 1)

        selected: List[Dict] = []
        for q in pool:
            q_diff = {"easy": 0, "medium": 1, "hard": 2}.get(q["difficulty"], 1)
            if q_diff <= diff_level:
                selected.append(q)
            if len(selected) >= QUESTIONS_PER_GAME:
                break

        if len(selected) < QUESTIONS_PER_GAME:
            remaining = [q for q in pool if q not in selected]
            selected.extend(remaining[:QUESTIONS_PER_GAME - len(selected)])

        self.questions = selected[:QUESTIONS_PER_GAME]
        self.total_questions = len(self.questions)

    def render_question(self) -> None:
        clear_screen()
        print("\n" * 1)
        q = self.questions[self.question_index]
        q_num = self.question_index + 1
        diff_icon = {"easy": "★", "medium": "★★", "hard": "★★★"}.get(q["difficulty"], "★")

        header = (
            f"{C_CYAN}{self.category}{C_RESET}  "
            f"Q{q_num}/{self.total_questions}  "
            f"Score: {C_YELLOW}{self.score}{C_RESET}  "
            f"Diff: {self.difficulty.upper()}"
        )
        lines = [
            header,
            "",
            f"{C_WHITE}{q['q']}{C_RESET}  {C_MAGENTA}({diff_icon}){C_RESET}",
            "",
        ]
        letters = ['A', 'B', 'C', 'D']
        for i, opt in enumerate(q["options"]):
            marker = f"{C_GREEN}{letters[i]}.{C_RESET}"
            lines.append(f"  {marker}  {opt}")

        lines += [
            "",
            f"{C_YELLOW}A-D or 1-4 select answer   Q Quit{C_RESET}",
        ]
        draw_retro_box(56, f"QUESTION {q_num}", lines, color=C_CYAN)

    def show_result_feedback(self, correct: bool, correct_idx: int) -> None:
        if correct:
            q = self.questions[self.question_index - 1]
            pts = DIFFICULTY_POINTS.get(q['difficulty'], 10)
            show_popup(f"{C_GREEN}CORRECT!{C_RESET}  +{pts} points", delay=0.8)
        else:
            correct_ans = self.questions[self.question_index - 1]["options"][correct_idx]
            show_popup(f"{C_RED}WRONG!{C_RESET}  Answer: {C_GREEN}{correct_ans}{C_RESET}",
                       delay=1.5)

    def show_summary(self) -> None:
        clear_screen()
        print("\n" * 2)
        pct = int((self.correct_count / self.total_questions) * 100) if self.total_questions else 0
        grade = "F"
        if pct >= 90:
            grade = "A"
        elif pct >= 80:
            grade = "B"
        elif pct >= 70:
            grade = "C"
        elif pct >= 60:
            grade = "D"

        grade_color = C_RED
        if grade in ('A', 'B'):
            grade_color = C_GREEN
        elif grade in ('C', 'D'):
            grade_color = C_YELLOW

        stats = [
            f"{C_WHITE}Category:{C_RESET}  {C_CYAN}{self.category}{C_RESET}",
            f"{C_WHITE}Correct:{C_RESET}   {C_GREEN}{self.correct_count}{C_RESET}/{self.total_questions}",
            f"{C_WHITE}Grade:{C_RESET}     {grade_color}{grade}{C_RESET}  ({pct}%)",
            f"{C_WHITE}Score:{C_RESET}     {C_YELLOW}{self.score}{C_RESET}",
            f"{C_WHITE}XP Earned:{C_RESET} {C_MAGENTA}{self.xp_earned}{C_RESET}",
        ]
        draw_retro_box(40, "QUIZ COMPLETE", stats, color=C_CYAN)
        print(f"\n{C_WHITE}Press any key to continue...{C_RESET}")
        self.input_handler.get_safe_key()

    def play(self) -> dict:
        self.start_timer()
        self.renderer.hide_cursor()

        try:
            if self.select_category():
                self.build_question_pool()

            while self.question_index < self.total_questions and not self.game_over:
                self.render_question()
                key = self.input_handler.get_safe_key()

                if key and self._save_and_quit(key.lower()):
                    break
                if key == '?':
                    self._show_help()
                    continue
                if key == 'p':
                    self._pause_game()
                    continue

                letters = {'a': 0, 'b': 1, 'c': 2, 'd': 3, '1': 0, '2': 1, '3': 2, '4': 3}
                if key and key.lower() in letters:
                    choice = letters[key.lower()]
                    q = self.questions[self.question_index]
                    correct = choice == q["answer"]

                    q_diff = q.get("difficulty", "medium")
                    base_pts = DIFFICULTY_POINTS.get(q_diff, 10)

                    if correct:
                        self.score += base_pts
                        self.correct_count += 1
                        self.award_xp_for_action(base_pts)
                        beep("correct")
                    else:
                        beep("wrong")

                    self.question_index += 1
                    self.show_result_feedback(correct, q["answer"])

                time.sleep(0.05)

            if not self.game_over:
                self.show_summary()

            final_stats = self.get_final_stats()
            final_stats['high_score'] = self.score
            self.save_stats(final_stats)
            return final_stats

        except KeyboardInterrupt:
            pass
        finally:
            self.end_timer()
            self.renderer.show_cursor()
            final_stats = self.get_final_stats()
            final_stats['high_score'] = self.score
            self.save_stats(final_stats)
            return final_stats

    def _show_help(self) -> None:
        lines = [
            "Answer multiple-choice trivia questions",
            "before time runs out.",
            "",
            f"{C_CYAN}Controls:{C_RESET}",
            "  A-D or 1-4   Select answer",
            "  Q            Quit (saves progress)",
            "  P            Pause",
            "  ?            Show this help",
            "",
            f"{C_CYAN}Scoring:{C_RESET}",
            "  Easy:   10 pts",
            "  Medium: 25 pts",
            "  Hard:   50 pts",
            "",
            f"{C_CYAN}Difficulty:{C_RESET}",
            "  Easy   - Easy questions only",
            "  Normal - Easy + Medium",
            "  Hard   - All difficulties",
        ]
        draw_retro_box(44, "TRIVIA HELP", lines, color=C_GREEN)
        print(f"\n{C_WHITE}Press any key to continue...{C_RESET}")
        self.input_handler.get_safe_key()


def play_trivia(difficulty: str = 'normal') -> dict:
    game = TriviaGame(difficulty)
    return game.play()
