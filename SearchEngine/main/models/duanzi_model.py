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

class DuanziType(DocType):
    suggest = Completion(analyzer=ik_analyzer)

    text = Text(analyzer="ik_max_word")
    digg_count = Text()



    class Meta:
        index = "neihanduanzi"
        doc_type = "duanzi"


if __name__ == '__main__':
    # 直接运行看效果
    DuanziType.init()