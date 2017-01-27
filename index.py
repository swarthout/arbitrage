# -*- coding: utf-8 -*-
import scrapy
from scrapy.crawler import CrawlerProcess
import logging

SPORTS_BOOKS = ["5Dimes", "BetDSI", "BookMaker", "Bovada", "SportBet", "Sportsbook", "William H.", "Pinnacle",
                "SportsInt.", "SBG Global", "TheGreek", "BetOnline", "BetUS"]


class FightOddsSpider(scrapy.Spider):
    name = "fight-odds"
    allowed_domains = ["https://www.bestfightodds.com/"]
    start_urls = ['https://www.bestfightodds.com/']

    def __init__(self, *args, **kwargs):
        logging.getLogger('scrapy').setLevel(logging.WARNING)
        super().__init__(*args, **kwargs)

    def parse(self, response):
        skewed_fights = []
        even_rows = response.css("tr.even")
        odd_rows = response.css("tr.odd")
        for fighter1_row, fighter2_row in zip(even_rows, odd_rows):
            fighter1 = get_fighter_info(fighter1_row)
            fighter2 = get_fighter_info(fighter2_row)
            if fighter1["odds"] and fighter2["odds"]:
                fighter1_odds = int(fighter1["odds"].replace("+", ""))
                fighter2_odds = int(fighter2["odds"].replace("+", ""))
                if fighter1_odds > fighter2_odds:
                    underdog, favorite = fighter1, fighter2
                else:
                    underdog, favorite = fighter2, fighter1

                if fighter1_odds + fighter2_odds > 0:
                    skewed_fights.append({"underdog": underdog, "favorite": favorite})
        logging.info(skewed_fights)


def get_fighter_info(row):
    fighter = {"name": row.css("th > a > span.tw::text").extract_first(),
               "odds": None}

    for bet, book in zip(row.css("td"), SPORTS_BOOKS):
        odds = bet.css("a > span.tw > span.bestbet::text").extract_first()
        if odds is not None:
            fighter["odds"] = odds
            fighter["book"] = book
    return fighter


process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
})

process.crawl(FightOddsSpider)
process.start()
