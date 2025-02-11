"""این ماژول شامل کلاس‌ها و توابعی برای خواندن پیکرهٔ دِگَربیان است.

[پیکرهٔ
دگربیان](https://www.peykaregan.ir/dataset/%D9%BE%DB%8C%DA%A9%D8%B1%D9%87-
%D8%AF%DA%AF%D8%B1%D8%A8%DB%8C%D8%A7%D9%86) حاوی
۱۵۲۳ نمونه است که به عنوان نمونه‌های دگربیان نشانه‌گذاری شده‌اند. جملات و
عبارات
دگربیان، بیانی متفاوت از مفهومی یکسان هستند. داده‌های این پیکره از خبرگزاری‌ها
جمع‌آورده شده و در سه دسته‌بندی «دگربیان»، «تقریباً دگربیان» و «نامرتبط» ارائه
می‌شوند. این داده‌ها با استفاده از همکاری جمعی در پیام‌رسان تلگرام نشانه‌گذاری
شده است.

"""


import os
import sys
from typing import Any, Dict, Iterator, Tuple
from xml.dom import minidom


class DegarbayanReader:
    """این کلاس شامل توابعی برای خواندن پیکرهٔ دگربیان است.

    Args:
        root مسیر فولدر حاوی فایل‌های پیکره
        corpus_file: فایل اطلاعات پیکره.
            در صورتی که بخواهید از حالت استاندارد پیکره استفاده کنید نیازی به تغییرِ این فایل نیست.
        judge_type: این پارامتر دارای دو مقدار `three_class` و `two_class` است.
            در حالت `three_class` جملات سه برچسب می‌خورند: ۱. `Paraphrase`(دگربیان)
            ۲. `SemiParaphrase`(تقریباً دگربیان) ۳. `NotParaphrase`(غیر دگربیان). در حالت
            `two_class` حالت دوم یعنی `SemiParaphrase` هم برچسب `Paraphrase` می‌خورَد.
        version: شمارهٔ نسخهٔ پیکره

    """

    def __init__(
        self,
        root: str,
        corpus_file: str = "CorpusPair.xml",
        judge_type: str = "three_class",
        version: float = 1.0,
    ) -> None:
        self._root = root
        self._corpus_file = corpus_file
        self._judge_type = judge_type
        if judge_type != "three_class" and judge_type != "two_class":
            self._judge_type = "three_class"

    def docs(self) -> Iterator[Dict[str, Any]]:
        """اسناد موجود در پیکره را برمی‌گرداند.

        Yields:
            سند بعدی.

        """

        def judge_number_to_text(judge):
            if judge == "1" or (self._judge_type == "two_class" and judge == "0"):
                return "Paraphrase"
            elif judge == "0":
                return "SemiParaphrase"
            else:
                return "NotParaphrase"

        filename = os.path.join(self._root, self._corpus_file)
        if os.path.exists(filename):
            try:
                elements = minidom.parse(filename)
                for element in elements.getElementsByTagName("Pair"):
                    pair = {
                        "id": (
                            element.getElementsByTagName("PairId")[0]
                            .childNodes[0]
                            .data.strip()
                        ),
                        "news_source1": (
                            element.getElementsByTagName("NewsSource1")[0]
                            .childNodes[0]
                            .data.strip()
                        ),
                        "news_source2": (
                            element.getElementsByTagName("NewsSource2")[0]
                            .childNodes[0]
                            .data.strip()
                        ),
                        "news_id1": (
                            element.getElementsByTagName("NewsId1")[0]
                            .childNodes[0]
                            .data.strip()
                        ),
                        "news_id2": (
                            element.getElementsByTagName("NewsId2")[0]
                            .childNodes[0]
                            .data.strip()
                        ),
                        "sentence1": (
                            element.getElementsByTagName("Sentence1")[0]
                            .childNodes[0]
                            .data.strip()
                        ),
                        "sentence2": (
                            element.getElementsByTagName("Sentence2")[0]
                            .childNodes[0]
                            .data.strip()
                        ),
                        "method_type": (
                            element.getElementsByTagName("MethodType")[0]
                            .childNodes[0]
                            .data.strip()
                        ),
                        "judge": judge_number_to_text(
                            element.getElementsByTagName("judge")[0]
                            .childNodes[0]
                            .data.strip()
                        ),
                    }
                    yield pair

            except Exception as e:
                print("error in reading", filename, e, file=sys.stderr)
        else:
            print("error in reading file", filename, e, file=sys.stderr)
            raise FileNotFoundError("error in reading file", filename)

    def pairs(self) -> Iterator[Tuple[str, str, str]]:
        """متن‌های دگربیان را در قالب یک `(متن اصلی، شکل دگربیان، برچسب)` برمی‌گرداند.

        Examples:
            >>> degarbayan = DegarbayanReader(root='corpora/degarbayan')
            >>> next(degarbayan.pairs())
            ('24 نفر نهایی تیم ملی بدون تغییری خاص معرفی شد', 'کی روش 24 بازیکن را به تیم ملی فوتبال دعوت کرد', 'Paraphrase')

        Yields:
            `متن دگربیان بعدی در قالب یک `(متن اصلی، شکل دگربیان، برچسب).

        """
        for pair in self.docs():
            yield pair["sentence1"], pair["sentence2"], pair["judge"]
