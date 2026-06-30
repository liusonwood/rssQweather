import unittest
from unittest.mock import patch, MagicMock
import os
import xml.etree.ElementTree as ET

from fetch_weather import select_forecast_day, generate_rss, slugify

class TestFetchWeather(unittest.TestCase):
    def setUp(self):
        self.mock_forecast = [
            {
                "fxDate": "2026-06-30",
                "tempMax": "30",
                "tempMin": "22",
                "textDay": "Sunny",
                "iconDay": "100",
                "textNight": "Clear",
                "iconNight": "150"
            },
            {
                "fxDate": "2026-07-01",
                "tempMax": "31",
                "tempMin": "23",
                "textDay": "Cloudy",
                "iconDay": "101",
                "textNight": "Overcast",
                "iconNight": "151"
            },
            {
                "fxDate": "2026-07-02",
                "tempMax": "29",
                "tempMin": "21",
                "textDay": "Rainy",
                "iconDay": "300",
                "textNight": "Light Rain",
                "iconNight": "350"
            }
        ]

    def test_select_forecast_day_default(self):
        # Defaults to index 1 (tomorrow)
        selected = select_forecast_day(self.mock_forecast, None)
        self.assertEqual(selected["fxDate"], "2026-07-01")

    def test_select_forecast_day_today(self):
        selected_today = select_forecast_day(self.mock_forecast, "today")
        self.assertEqual(selected_today["fxDate"], "2026-06-30")
        
        selected_0 = select_forecast_day(self.mock_forecast, "0")
        self.assertEqual(selected_0["fxDate"], "2026-06-30")

    def test_select_forecast_day_tomorrow(self):
        selected_tomorrow = select_forecast_day(self.mock_forecast, "tomorrow")
        self.assertEqual(selected_tomorrow["fxDate"], "2026-07-01")
        
        selected_1 = select_forecast_day(self.mock_forecast, "1")
        self.assertEqual(selected_1["fxDate"], "2026-07-01")

    def test_select_forecast_day_after_tomorrow(self):
        selected_2 = select_forecast_day(self.mock_forecast, "2")
        self.assertEqual(selected_2["fxDate"], "2026-07-02")

    def test_select_forecast_day_date_string(self):
        selected_date = select_forecast_day(self.mock_forecast, "2026-07-02")
        self.assertEqual(selected_date["fxDate"], "2026-07-02")

    def test_select_forecast_day_not_found(self):
        with self.assertRaises(SystemExit):
            select_forecast_day(self.mock_forecast, "2026-07-05")

    @patch("fetch_weather.RSS_FILENAME", "test_weather.xml")
    def test_generate_rss_with_different_dates(self):
        # Ensure cleanup of test file if it exists
        if os.path.exists("test_weather.xml"):
            os.remove("test_weather.xml")
            
        try:
            # Test with tomorrow (default)
            generate_rss(self.mock_forecast, "Shanghai", "101020100", None)
            self.assertTrue(os.path.exists("test_weather.xml"))
            
            tree = ET.parse("test_weather.xml")
            root = tree.getroot()
            channel = root.find("channel")
            items = channel.findall("item")
            self.assertEqual(len(items), 1)
            self.assertIn("2026-07-01", items[0].find("title").text)
            
            # Test appending today
            generate_rss(self.mock_forecast, "Shanghai", "101020100", "today")
            tree = ET.parse("test_weather.xml")
            root = tree.getroot()
            channel = root.find("channel")
            items = channel.findall("item")
            # Should have 2 items now
            self.assertEqual(len(items), 2)
            # New items are inserted at the top, so "today" (2026-06-30) should be at index 0
            self.assertIn("2026-06-30", items[0].find("title").text)
        finally:
            if os.path.exists("test_weather.xml"):
                os.remove("test_weather.xml")

if __name__ == "__main__":
    unittest.main()
