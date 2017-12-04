# -*- coding:utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from elasticsearch_dsl import DocType, Date, Nested, Boolean, \
    analyzer, InnerObjectWrapper, Completion,Integer, Keyword, Text

from elasticsearch_dsl.connections import connections
connections.create_connection(hosts=["localhost"])

from elasticsearch_dsl.analysis import CustomAnalyzer
class CustomAnlz(CustomAnalyzer):
    def get_analysis_definition(self):
        return {}

ik_analyzer = CustomAnlz("ik_max_word", filter=['lowercase'])

class ImgsType(DocType):
    suggest = Completion(analyzer=ik_analyzer)

    big_cate_name = Text(analyzer="ik_max_word")
    small_cate_name = Text(analyzer="ik_max_word")
    img_title = Text(analyzer="ik_max_word")
    img_src = Keyword()
    path = Text()



    class Meta:
        index = "imgs"
        doc_type = "img"


if __name__ == '__main__':
    # 直接运行看效果
    ImgsType.init()