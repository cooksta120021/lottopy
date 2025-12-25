from bs4 import BeautifulSoup  # type: ignore

from .base import GameConfig, register_game, ParseResult


def parse_row(row: BeautifulSoup) -> ParseResult:
    cols = row.select("td")
    numbers = cols[1].get_text().split(" - ")
    bonus_ball = cols[2].get_text() if len(cols) > 2 else ""
    specials = [bonus_ball] if bonus_ball else []
    return numbers, specials


TEXAS_TWO_STEP = GameConfig(
    key="texas_two_step",
    name="Texas Two Step",
    url="https://www.texaslottery.com/export/sites/lottery/Games/Texas_Two_Step/Winning_Numbers/index.html",  # noqa: E501
    numbers_per_draw=4,
    numbers_label="winning_number",
    special_labels=["bonus_ball"],
    parse_row=parse_row,
)

register_game(TEXAS_TWO_STEP)
