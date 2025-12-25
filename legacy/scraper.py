import requests
from bs4 import BeautifulSoup
from collections import Counter
import random


def scrape_data(url, output_file="temp.txt"):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    with open(output_file, 'w') as f:
        for row in soup.select("table.large-only tbody tr"):
            numbers = row.select("td")[1].get_text().split(' - ')
            mega_ball = row.select("td")[2].get_text()
            megaplier = row.select("td")[3].get_text()
            f.write(",".join(numbers + [mega_ball, megaplier]) + "\n")


def count_occurrences(input_file="temp.txt", output_file="temp2.txt"):
    with open(input_file, 'r') as f:
        lines = f.readlines()
        all_numbers = []
        for line in lines:
            nums = line.strip().split(",")
            all_numbers.extend(["winning_number,"+n for n in nums[:5]])
            all_numbers.append("mega_ball,"+nums[5])
            all_numbers.append("megaplier,"+nums[6])

        counter = Counter(all_numbers)
    with open(output_file, 'w') as f:
        for num, count in counter.items():
            f.write(f"{num},{count}\n")


def display_probabilities(threshold, input_file="temp2.txt", output_file="final.txt"):  # noqa
    total_draws = sum(1 for _ in open(input_file)) // 7
    min_count = int(threshold * total_draws)

    print(f"Total Draws: {total_draws}")
    print(f"Minimum Count Threshold: {min_count}")

    winning_numbers = []
    mega_balls = []
    megapliers = []

    with open(input_file, 'r') as f:
        for line in f:
            category, num, count = line.strip().split(",")
            if int(count) >= min_count:
                if category == "winning_number":
                    winning_numbers.append(num)
                elif category == "mega_ball":
                    mega_balls.append(num)
                elif category == "megaplier":
                    megapliers.append(num)

    with open(output_file, 'w') as out:
        for _ in range(5):  # Generate 5 random sets.
            if len(winning_numbers) < 5 or not mega_balls or not megapliers:
                break
            random_win_nums = random.sample(winning_numbers, 5)
            random_mega_ball = random.choice(mega_balls)
            random_megaplier = random.choice(megapliers)
            out.write(f"{', '.join(random_win_nums)}, {random_mega_ball}, {random_megaplier}\n")  # noqa

# Scrape, Count and Display probabilities
url = 'https://www.texaslottery.com/export/sites/lottery/Games/Mega_Millions/Winning_Numbers/index.html_1894996477.html'  # noqa
scrape_data(url)
count_occurrences()
total_draws = sum(1 for _ in open("temp.txt")) // 7
dynamic_threshold = total_draws / 31
print(f"Dynamic Threshold: {dynamic_threshold:.2f}")
display_probabilities(dynamic_threshold)