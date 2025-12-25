from bs4 import BeautifulSoup  # type: ignore

from .base import GameConfig, register_game, ParseResult


def parse_row(row: BeautifulSoup) -> ParseResult:
    cols = row.select("td")
    numbers = cols[1].get_text().split(" - ")
    mega_ball = cols[2].get_text()
    megaplier = cols[3].get_text()
    return numbers, [mega_ball, megaplier]


MEGA_MILLIONS = GameConfig(
    key="mega_millions",
    name="Mega Millions",
    url="https://www.texaslottery.com/export/sites/lottery/Games/Mega_Millions/Winning_Numbers/index.html_1894996477.html",  # noqa: E501
    numbers_per_draw=5,
    numbers_label="winning_number",
    special_labels=["mega_ball", "megaplier"],
    parse_row=parse_row,
)

register_game(MEGA_MILLIONS)
