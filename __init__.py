from youtube_searcher import extract_videos
from ovos_utils.skills.templates.common_play import BetterCommonPlaySkill
from ovos_utils.playback import CPSMatchType, CPSPlayback, CPSMatchConfidence
from os.path import join, dirname


class EuroNewsSkill(BetterCommonPlaySkill):

    def __init__(self):
        super().__init__("Euronews")
        self.supported_media = [CPSMatchType.GENERIC,
                                CPSMatchType.AUDIO,
                                CPSMatchType.VIDEO,
                                CPSMatchType.TV,
                                CPSMatchType.NEWS]
        self.default_image = join(dirname(__file__), "ui", "logo.png")
        self.skill_logo = join(dirname(__file__), "ui", "euronews.png")
        self.skill_icon = join(dirname(__file__), "ui", "euronews.png")
        self.default_bg = join(dirname(__file__), "ui", "bg.jpeg")

    def get_intro_message(self):
        self.speak_dialog("intro")
        self.gui.show_image(join(dirname(__file__), "ui", "logo.png"))

    # common play
    def match_lang(self, phrase):
        lang = self.lang.split("-")[0]
        if self.voc_match(phrase, "pt"):
            lang = "pt"
        elif self.voc_match(phrase, "it"):
            lang = "it"
        elif self.voc_match(phrase, "fr"):
            lang = "fr"
        elif self.voc_match(phrase, "es"):
            lang = "es"
        elif self.voc_match(phrase, "de"):
            lang = "de"
        return lang

    def CPS_search(self, phrase, media_type):
        """Analyze phrase to see if it is a play-able phrase with this skill.

        Arguments:
            phrase (str): User phrase uttered after "Play", e.g. "some music"
            media_type (CPSMatchType): requested CPSMatchType to search for

        Returns:
            search_results (list): list of dictionaries with result entries
            {
                "match_confidence": CPSMatchConfidence.HIGH,
                "media_type":  CPSMatchType.MUSIC,
                "uri": "https://audioservice.or.gui.will.play.this",
                "playback": CPSPlayback.GUI,
                "image": "http://optional.audioservice.jpg",
                "bg_image": "http://optional.audioservice.background.jpg"
            }
        """
        lang = self.match_lang(phrase)
        url = EuroNewsLiveStream.get_stream(lang)
        score = 0
        if media_type == CPSMatchType.NEWS or self.voc_match(phrase, "news"):
            score = 60
            if self.voc_match(phrase, "euro"):
                score += 30

        if self.voc_match(phrase, "euronews"):
            score += 80
        if score >= CPSMatchConfidence.AVERAGE:
            if media_type not in [CPSMatchType.AUDIO, CPSMatchType.VIDEO,
                                  CPSMatchType.TV]:
                # audio + video results
                results = [
                    {
                        # video match
                        "match_confidence": min(100, score),
                        "media_type": CPSMatchType.NEWS,
                        "uri": url,
                        "playback": CPSPlayback.GUI,
                        "image": self.default_image,
                        "bg_image": self.default_bg,
                        "skill_icon": self.skill_icon,
                        "skill_logo": self.skill_logo,
                        "length": 0,
                        "title": "EuroNews",
                        "author": "EuroNews",
                        "album": "EuroNews"
                    },
                    {  # audio match
                        "match_confidence": min(100, score - 5),
                        "media_type": CPSMatchType.NEWS,
                        "uri": url,
                        "playback": CPSPlayback.AUDIO,
                        "image": self.default_image,
                        "bg_image": self.default_bg,
                        "skill_icon": self.skill_icon,
                        "skill_logo": self.skill_logo,
                        "length": 0,
                        "title": "EuroNews (Audio)",
                        "author": "EuroNews",
                        "album": "EuroNews"
                    }
                ]
            elif media_type == CPSMatchType.AUDIO:
                # audio only results
                results = [
                    {
                        # video match
                        "match_confidence": min(100, score),
                        "media_type": CPSMatchType.NEWS,
                        "uri": url,
                        "playback": CPSPlayback.AUDIO,
                        "image": self.default_image,
                        "bg_image": self.default_bg,
                        "skill_icon": self.skill_icon,
                        "skill_logo": self.skill_logo,
                        "length": 0,
                        "title": "EuroNews",
                        "author": "EuroNews",
                        "album": "EuroNews"
                    }]
            else:
                # gui only results
                results = [
                    {
                        # video match
                        "match_confidence": min(100, score),
                        "media_type": CPSMatchType.NEWS,
                        "uri": url,
                        "playback": CPSPlayback.GUI,
                        "image": self.default_image,
                        "bg_image": self.default_bg,
                        "skill_icon": self.skill_icon,
                        "skill_logo": self.skill_logo,
                        "length": 0,
                        "title": "EuroNews",
                        "author": "EuroNews",
                        "album": "EuroNews"
                    }]

            if lang != "en":
                pass
            return results
        return []


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
            return e["url"]


def create_skill():
    return EuroNewsSkill()
