import gc
import urequests
gc.collect()

WIDGET_WIDTH = 190
WIDGET_HEIGHT = 384

class NewsWidget:

    def __init__(self, language="en", api_key=None, country="de", query=None):
        if (api_key is None or ""):
            raise ValueError('API key is missing')

        self._language = language
        self._api_key = api_key
        self._query = query
        self._country = country

    def _refresh_news(self, lines_break):
        if self._query is None:
            url = "https://newsapi.org/v2/top-headlines?country={}&apiKey={}&pageSize={}".format(self._country, self._api_key, lines_break)
        else:
            url = "https://newsapi.org/v2/top-headlines?q={}&country={}&apiKey={}&pageSize={}".format(self._query, self._country, self._api_key, lines_break)

        #print(url)
        r = urequests.get(url)
        gc.collect()
        return r.json()

    def get_data(self, lines_break=4):
        news_raw = self._refresh_news(lines_break)
        gc.collect()
        return news_raw
