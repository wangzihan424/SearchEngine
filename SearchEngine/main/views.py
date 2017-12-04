# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render,HttpResponse,HttpResponseRedirect
import json
from models.blog_model import ArticleType,client
from models.duanzi_model import DuanziType
from models.img_model import ImgsType
from datetime import datetime
import math
from django.core.cache import cache
# Create your views here.


def get_navs():
    return  [{"title": u"博客", "type": "blog","count":100},
                 {"title": u"段子", "type": "duanzis","count":500},
                 {"title": u"图片", "type": "imgs","count":1030}
                 ]

def index(request):
    return render(request, "index.html", {
        "navs": get_navs()
    })

def suggest(request):
    key_words = request.GET.get('s', '')  # 获取到请求词
    re_datas = []
    if key_words:
        search_type = request.GET.get("s_type")
        if search_type == "blog":
            s = ArticleType.search()  # 实例化elasticsearch(搜索引擎)类的search查询
            s = s.suggest('my_suggest', key_words, completion={
                "field": "suggest", "fuzzy": {
                    "fuzziness": 2
                },
                "size": 5

            })
            suggestions = s.execute_suggest()
            for match in suggestions.my_suggest[0].options:
                source = match._source
                re_datas.append(source["title"])
        elif search_type == "duanzis":
            s = DuanziType.search()  # 实例化elasticsearch(搜索引擎)类的search查询
            s = s.suggest('my_suggest', key_words, completion={
                "field": "suggest", "fuzzy": {
                    "fuzziness": 2
                },
                "size": 5
            })
            suggestions = s.execute_suggest()
            for match in suggestions.my_suggest[0].options:
                source = match._source
                re_datas.append(source["text"][:15])
        elif search_type == "imgs":
            s = ImgsType.search()  # 实例化elasticsearch(搜索引擎)类的search查询
            s = s.suggest('my_suggest', key_words, completion={
                "field": "suggest", "fuzzy": {
                    "fuzziness": 2
                },
                "size": 5
            })
            suggestions = s.execute_suggest()
            for match in suggestions.my_suggest[0].options:
                source = match._source
                re_datas.append(source["img_title"])
    return HttpResponse(json.dumps(re_datas), content_type="application/json")

def search(request):
    keywords = request.GET.get("q","")

    if not cache.get("hot"):
        cache.set("hot",{})
    hot_info = cache.get("hot")
    if hot_info.has_key(keywords):
        keywords_count =hot_info[keywords]
        keywords_count+=1
        hot_info[keywords] = keywords_count
    else:
        hot_info[keywords] = 1
    cache.set("hot", hot_info)
    top5 = sorted(hot_info.iteritems(),key=lambda a:a[1],reverse=True)[:5]
    page = request.GET.get("p","1")
    try:
        page = int(page)
    except:
        page = 1
    search_type = request.GET.get("s_type","blog")
    if not keywords:
        return HttpResponseRedirect("/")
    if search_type == 'blog':
        index = "blog"
        doc_type = "article"
        fields = ["title","content"]
        hight_fields = {
            "title":{},
            "content":{}
        }
    elif search_type == 'img':
        index = "imgs"
        doc_type = "img"
        fields = ["img_title","img_src"]
        hight_fields = {
            "img_title": {},
            "img_src": {}
        }
    elif search_type == 'duanzi':
        index = "neihanduanzi"
        doc_type = "duanzi"
        fields = ["text"]
        hight_fields = {
            "text": {}
        }
    start_time = datetime.now()
    response = client.search(  # 原生的elasticsearch接口的search()方法，就是搜索，可以支持原生elasticsearch语句查询
        index=index,  # 设置索引名称
        doc_type=doc_type,  # 设置表名称
        body={  # 书写elasticsearch语句
            "query": {
                "multi_match": {  # multi_match查询
                    "query": keywords,  # 查询关键词
                    "fields": fields  # 查询字段
                }
            },
            "from": (page-1)*10,  # 从第几条开始获取
            "size": 10,  # 获取多少条数据
            "highlight": {  # 查询关键词高亮处理
                "pre_tags": ['<span class="keyWord">'],  # 高亮开始标签
                "post_tags": ['</span>'],  # 高亮结束标签
                "fields": hight_fields
            }
        }
    )
    end_time = datetime.now()
    last_time = (end_time - start_time).total_seconds()
    total_nums = response["hits"]["total"]  # 获取查询结果的总条数
    page_num = math.ceil(total_nums*1.0/10)
    hit_list = []
    for hit in response["hits"]["hits"]:  # 循环查询到的结果
        hit_dict = {}
        if search_type == "blog":
            if "title" in hit["highlight"]:  # 判断title字段，如果高亮字段有类容
                hit_dict["title"] = "".join(hit["highlight"]["title"])  # 获取高亮里的title
            else:
                hit_dict["title"] = hit["_source"]["title"]  # 否则获取不是高亮里的title

            if "content" in hit["highlight"]:  # 判断description字段，如果高亮字段有类容
                hit_dict["content"] = "".join(hit["highlight"]["content"])[:500]  # 获取高亮里的description
            else:
                hit_dict["content"] = hit["_source"]["content"]  # 否则获取不是高亮里的description

        hit_dict["url"] = hit["_source"]["detail_url"]  # 获取返回url

        hit_list.append(hit_dict)  # 将获取到内容的字典，添加到列表


    return render(request,"result.html",{
            "keywords":keywords,
            "navs": get_navs(),
            "search_type":search_type,
            "hit_list":hit_list,
            "total_nums":total_nums,
            "last_time":last_time,
            "page":page,
            "page_num":page_num,
            "top5":top5,
        })