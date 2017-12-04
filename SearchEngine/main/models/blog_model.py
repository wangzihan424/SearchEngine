# -*- coding:utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from elasticsearch_dsl import DocType, Date, Nested, Boolean, \
    analyzer, InnerObjectWrapper, Completion,Integer, Keyword, Text

from elasticsearch_dsl.connections import connections
client = connections.create_connection(hosts=["localhost"])

from elasticsearch_dsl.analysis import CustomAnalyzer
class CustomAnlz(CustomAnalyzer):
    def get_analysis_definition(self):
        return {}

ik_analyzer = CustomAnlz("ik_max_word", filter=['lowercase'])

class ArticleType(DocType):
    suggest = Completion(analyzer=ik_analyzer)

    title = Text(analyzer="ik_max_word")
    content = Text(analyzer="ik_max_word")

    img_src = Keyword()
    date_time = Date()
    tags = Text()
    dian_zan = Integer()
    shou_cang = Integer()
    ping_lun = Integer()
    detail_url = Keyword()


    class Meta:
        index = "blog"
        doc_type = "article"


if __name__ == '__main__':
    # 直接运行看效果
    ArticleType.init()