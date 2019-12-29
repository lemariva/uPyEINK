"""
 Copyright [2019] [Mauro Riva <info@lemariva.com> <lemariva.com>]

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

 http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.

 The above copyright notice and this permission notice shall be
 included in all copies or substantial portions of the Software.
"""

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
