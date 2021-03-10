from youtube_searcher import extract_videos
import pafy


class EuroNewsLiveStream:
    lang2url = {
        "en": "https://www.youtube.com/user/Euronews",
        "ru": "https://www.youtube.com/user/euronewsru",
        "pt": "https://www.youtube.com/user/euronewspt",
        "it": "https://www.youtube.com/user/euronewsit",
        "fr": "https://www.youtube.com/user/euronewsfr",
        "de": "https://www.youtube.com/user/euronewsde",
        "es": "https://www.youtube.com/user/euronewses"
    }

    def __init__(self, lang="en-us"):
        lang = lang.lower()
        if lang not in self.lang2url:
            lang = lang.lower()[:2]
        self.lang = lang
        if self.lang not in self.lang2url:
            raise ValueError("Unsupported language")
        self._stream = None

    @property
    def url(self):
        return EuroNewsLiveStream.lang2url[self.lang]

    @property
    def stream(self):
        if self._stream is None:
            self._stream = self.get_stream(self.lang)
        return self._stream

    @staticmethod
    def get_stream(lang):
        if lang not in EuroNewsLiveStream.lang2url:
            raise ValueError("Unsupported language")
        url = EuroNewsLiveStream.lang2url[lang]
        for e in extract_videos(url):
            if not e["is_live"]:
                continue
            return pafy.new(e["videoId"]).getbest().url



e = EuroNewsLiveStream()
print(e.lang)
print(e.url)
print(e.stream)