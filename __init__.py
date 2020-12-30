from ovos_utils.waiting_for_mycroft.common_play import CommonPlaySkill, \
    CPSMatchLevel, CPSMatchType, CPSTrackStatus
import pafy
from os.path import join, dirname


class EuroNewsSkill(CommonPlaySkill):

    def __init__(self):
        super().__init__("Euronews")
        if "audio_only" not in self.settings:
            self.settings["audio_only"] = False

        self.supported_media = [CPSMatchType.GENERIC,
                                CPSMatchType.VIDEO,
                                CPSMatchType.NEWS]

        self.urls = {
            "pt": "https://www.youtube.com/watch?v=VOw7bts_rGQ",
            "es": "https://www.youtube.com/watch?v=JbKgQhFlMdU",
            "en": "https://www.youtube.com/watch?v=sPgqEHsONK8",
            "it": "https://www.youtube.com/watch?v=6Wbu_82PF2I",
            "fr": "https://www.youtube.com/watch?v=MsN0_WNXvh8",
            "de": "https://www.youtube.com/watch?v=gdyuPcnSDuY"
        }

    def initialize(self):
        self.add_event('skill-euronews.jarbasskills.home',
                       self.handle_homescreen)

    def get_intro_message(self):
        self.speak_dialog("intro")
        self.gui.show_image(join(dirname(__file__), "ui", "logo.png"))

    # homescreen
    def handle_homescreen(self, message):
        if self.settings.get("lang_override"):
            lang = self.settings["lang_override"]
        else:
            lang = self.lang

        lang = lang.split("-")[0].lower()
        if lang not in self.urls:
            lang = "en"

        self.CPS_start("euro news",
                       {"media_type": CPSMatchType.NEWS, "query": "euro news",
                        "url": self.urls[lang], "lang": lang, "score": 1.0})

    # common play
    def match_lang(self, phrase, lang="en"):
        score = 0
        if self.voc_match(phrase, "pt"):
            score += 0.4
            lang = "pt"
        if self.voc_match(phrase, "it"):
            score += 0.4
            lang = "it"
        if self.voc_match(phrase, "fr"):
            score += 0.4
            lang = "fr"
        if self.voc_match(phrase, "es"):
            score += 0.4
            lang = "es"
        if self.voc_match(phrase, "de"):
            score += 0.4
            lang = "de"
        return lang, score

    def CPS_match_query_phrase(self, phrase, media_type):

        if self.settings.get("lang_override"):
            lang = self.settings["lang_override"]
        else:
            lang = self.lang

        lang = lang.split("-")[0].lower()
        if lang not in self.urls:
            lang = "en"

        match = None
        score = 0

        if media_type == CPSMatchType.VIDEO or self.voc_match(phrase, "video"):
            score += 0.2
            match = CPSMatchLevel.GENERIC

        if media_type == CPSMatchType.NEWS or self.voc_match(phrase, "news"):
            score += 0.6
            match = CPSMatchLevel.CATEGORY

            if self.voc_match(phrase, "euro") or \
                    self.voc_match(phrase, "euronews"):
                score += 0.4
                match = CPSMatchLevel.TITLE

            lang, lang_score = self.match_lang(phrase, lang)
            score += lang_score

        elif self.voc_match(phrase, "euronews"):
            score += 0.6
            match = CPSMatchLevel.TITLE

            lang, lang_score = self.match_lang(phrase, lang)
            score += lang_score

        print(score, match, lang_score)
        if score >= 0.9:
            match = CPSMatchLevel.EXACT

        if match is not None:
            return (phrase, match,
                    {"media_type": CPSMatchType.NEWS, "query": phrase,
                     "url": self.urls[lang], "lang": lang,
                     "score": min(1, score)})
        return None

    def CPS_start(self, phrase, data):
        image = join(dirname(__file__), "ui", "logo.png")

        url = data["url"]

        if self.gui.connected and not self.settings["audio_only"]:
            url = self.get_video_stream(url)
            self.CPS_send_status(uri=url,
                                 image=image,
                                 playlist_position=0,
                                 status=CPSTrackStatus.PLAYING_GUI)
            self.gui.play_video(url)
        else:
            url = self.get_audio_stream(url)
            self.audioservice.play(url, utterance=self.play_service_string)
            self.CPS_send_status(uri=url,
                                 image=image,
                                 playlist_position=0,
                                 status=CPSTrackStatus.PLAYING_AUDIOSERVICE)

    def stop(self):
        self.gui.release()

    # youtube handling
    @staticmethod
    def get_audio_stream(url):
        vid = pafy.new(url)
        stream = vid.getbestaudio()
        if stream:
            return stream.url
        return vid.streams[0].url  # stream fallback

    @staticmethod
    def get_video_stream(url):
        return pafy.new(url).streams[0].url  # stream fallback


def create_skill():
    return EuroNewsSkill()
