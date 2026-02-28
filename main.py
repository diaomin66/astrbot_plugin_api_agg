from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import astrbot.api.message_components as Comp
import httpx
import os
import uuid
import re
from typing import Any, Generator

@register("api_agg", "Grok助手", "API聚合器 v1.6.9（雨云专用 - NapCat真实路径 + 模糊匹配）", "1.6.9")
class APIAggregator(Star):
    def __init__(self, context: Context, config):
        super().__init__(context)
        self.config = config
        self.apis: list = config.get("apis", []) or []
        logger.info(f"API聚合器 v1.6.9 雨云版 已加载 {len(self.apis)} 个API")

        # 你的雨云 NapCat 真实临时目录
        self.napcat_temp = "/napcat-main-zb1wco/qq/NapCat/temp"
        os.makedirs(self.napcat_temp, exist_ok=True)

    # ==================== 使用你完整提供的 api_pool_default.json 作为 DEFAULT_APIS ====================
    DEFAULT_APIS = [
        {"name": "安慕希", "base_url": "http://api.317ak.cn/api/sp/amxx", "ckey": "", "method": "GET", "media_type": "video", "keywords": "安慕希,amx,amxi,安慕西", "body_template": ""},
        {"name": "安慰", "base_url": "http://api.317ak.cn/api/wz/awyl", "ckey": "", "method": "GET", "media_type": "text", "keywords": "安慰,anwei,aw,安慰我,awyl", "body_template": "", "params": {"type": "text"}},
        {"name": "奥运会", "base_url": "https://api.lolimi.cn/API/ayh/i.php", "ckey": "", "method": "GET", "media_type": "image", "keywords": "奥运会,aoyunhui,ayh,奥运", "body_template": ""},
        {"name": "拜托前辈", "base_url": "http://api.317ak.cn/api/sp/btqb", "ckey": "", "method": "GET", "media_type": "video", "keywords": "拜托前辈,btqb,btq,baituoqianbei", "body_template": ""},
        {"name": "报时", "base_url": "https://api.yuafeng.cn/API/ly/baoshi.php", "ckey": "", "method": "GET", "media_type": "audio", "keywords": "报时,baoshi,bs，整点报时,整点时间", "body_template": "", "params": {"mode": "msw"}},
        {"name": "背影变装", "base_url": "http://api.317ak.cn/api/sp/bybz", "ckey": "", "method": "GET", "media_type": "video", "keywords": "背影变装,bybz,beiying,by变装", "body_template": ""},
        {"name": "擦玻璃", "base_url": "http://api.317ak.cn/api/sp/cblx", "ckey": "", "method": "GET", "media_type": "video", "keywords": "擦玻璃,cblx,cabi,caboli", "body_template": ""},
        {"name": "超甜辣妹", "base_url": "https://api.lolimi.cn/API/xjj/lt.php", "ckey": "", "method": "GET", "media_type": "image", "keywords": "超甜辣妹,ctlm,chaotianlamei,超甜", "body_template": ""},
        {"name": "嘲讽", "base_url": "http://api.317ak.cn/api/wz/cfyl", "ckey": "", "method": "GET", "media_type": "text", "keywords": "嘲讽,chaofeng,cf,cfyl", "body_template": "", "params": {"type": "text"}},
        {"name": "电脑壁纸", "base_url": "https://api.yuafeng.cn/API/dnbz/api.php", "ckey": "", "method": "GET", "media_type": "image", "keywords": "电脑壁纸,dnbz,diannao,dnbz", "body_template": ""},
        {"name": "电影票房", "base_url": "https://api.yuafeng.cn/API/dypf/api.php", "ckey": "", "method": "GET", "media_type": "text", "keywords": "电影票房,dypf,dianyingpiao fang,票房", "body_template": "", "params": {"mod": "电影详细数据"}},
        {"name": "动漫变装", "base_url": "http://api.317ak.cn/api/sp/dmbz", "ckey": "", "method": "GET", "media_type": "video", "keywords": "动漫变装,dmbz,dongman,dmbz", "body_template": ""},
        {"name": "动漫一言", "base_url": "https://api.lolimi.cn/API/dmyiyan/api.php", "ckey": "", "method": "GET", "media_type": "text", "keywords": "动漫一言,dmyy,dmyiyan,dongmanyiyan", "body_template": "", "parse": "text"},
        {"name": "斗图", "base_url": "https://api.lolimi.cn/API/dou/api.php", "ckey": "", "method": "GET", "media_type": "image", "keywords": "斗图,doutu,dt,dou", "body_template": "", "parse": "data.image"},
        {"name": "毒鸡汤", "base_url": "https://api.yuafeng.cn/API/ly/djt.php", "ckey": "", "method": "GET", "media_type": "text", "keywords": "毒鸡汤,dujitang,djt,毒汤", "body_template": "", "params": {"type": "json"}, "parse": "Msg"},
        {"name": "读世界", "base_url": "https://api.yuafeng.cn/API/60s/", "ckey": "", "method": "GET", "media_type": "image", "keywords": "读世界,dushijie,dsj,60s", "body_template": ""},
        {"name": "蹲下变装", "base_url": "http://api.317ak.cn/api/sp/dxbz", "ckey": "", "method": "GET", "media_type": "video", "keywords": "蹲下变装,dxbz,dunxia,dunxia", "body_template": ""},
        {"name": "二次元形象", "base_url": "https://api.lolimi.cn/API/Ser/api.php", "ckey": "", "method": "GET", "media_type": "text", "keywords": "二次元形象,ecyx,erciyuan,2cyx", "body_template": "", "params": {"name": ""}, "parse": "text"},
        {"name": "发病", "base_url": "https://api.tangdouz.com/beill.php", "ckey": "", "method": "GET", "media_type": "text", "keywords": "发病,fabing,fb", "body_template": "", "params": {"keywords": ""}},
        {"name": "高清壁纸", "base_url": "https://api.tangdouz.com/abz/bz.php", "ckey": "", "method": "GET", "media_type": "image", "keywords": "高清壁纸,gqbz,gaoqing,gaoqingbz", "body_template": ""},
        {"name": "高校查询", "base_url": "https://api.pearktrue.cn/api/college/", "ckey": "", "method": "GET", "media_type": "text", "keywords": "高校查询,gxchaxun,gaoxiao", "body_template": "", "params": {"keyword": "清华"}, "parse": "data"},
        {"name": "光遇日历", "base_url": "https://api.lolimi.cn/API/gy/ril.php", "ckey": "", "method": "GET", "media_type": "image", "keywords": "光遇日历,gyrl,guangyu,rili", "body_template": ""},
        {"name": "号码归属地", "base_url": "https://free.wqwlkj.cn/wqwlapi/phone_area.php", "ckey": "", "method": "GET", "media_type": "text", "keywords": "号码归属地,hmgsd,haoma,guishudi", "body_template": "", "params": {"phone": ""}, "parse": "data"},
        {"name": "黑白双煞", "base_url": "http://api.317ak.cn/api/sp/hbss", "ckey": "", "method": "GET", "media_type": "video", "keywords": "黑白双煞,hbss,heibaishuangsha", "body_template": ""},
        {"name": "黄金价格", "base_url": "https://api.pearktrue.cn/api/goldprice/", "ckey": "", "method": "GET", "media_type": "text", "keywords": "黄金价格,hjjg,huangjin", "body_template": "", "parse": "data[]"},
        {"name": "火车摇", "base_url": "http://api.317ak.cn/api/sp/hcyx", "ckey": "", "method": "GET", "media_type": "video", "keywords": "火车摇,hcyx,huoche", "body_template": ""},
        {"name": "鸡叫", "base_url": "https://api.yuafeng.cn/API/ly/kun.php", "ckey": "", "method": "GET", "media_type": "audio", "keywords": "鸡叫, jijiao,jj,小黑子,xhz", "body_template": ""},
        {"name": "讲个笑话", "base_url": "https://api.yuafeng.cn/API/ly/xiaohua.php", "ckey": "", "method": "GET", "media_type": "text", "keywords": "讲个笑话,jgxh,xiaohua,xh", "body_template": "", "params": {"type": "json"}, "parse": "Msg"},
        {"name": "讲讲爱情", "base_url": "https://api.yuafeng.cn/API/ly/aiqing.php", "ckey": "", "method": "GET", "media_type": "text", "keywords": "讲讲爱情,jjaiqing,aiqing,aq", "body_template": "", "params": {"type": "json"}, "parse": "Msg"},
        {"name": "讲讲摆烂", "base_url": "https://api.yuafeng.cn/API/ly/wzrjcs.php", "ckey": "", "method": "GET", "media_type": "text", "keywords": "讲讲摆烂,jjbl,bailan,bl", "body_template": "", "params": {"type": "json"}, "parse": "Msg"},
        {"name": "讲讲古诗", "base_url": "https://api.yuafeng.cn/API/ly/gushi.php", "ckey": "", "method": "GET", "media_type": "text", "keywords": "讲讲古诗,jjgs,gushi,gs", "body_template": "", "params": {"type": "json"}, "parse": "Msg"},
        {"name": "讲讲人生", "base_url": "https://api.yuafeng.cn/API/ly/rensheng.php", "ckey": "", "method": "GET", "media_type": "text", "keywords": "讲讲人生,jjrs,rensheng,rs", "body_template": "", "params": {"type": "json"}, "parse": "Msg"},
        {"name": "讲讲伤感", "base_url": "https://api.yuafeng.cn/API/ly/shanggan.php", "ckey": "", "method": "GET", "media_type": "text", "keywords": "讲讲伤感,jjsg,shanggan,sg", "body_template": "", "params": {"type": "json"}, "parse": "Msg"},
        {"name": "讲讲舔狗", "base_url": "https://api.yuafeng.cn/API/ly/tiangou.php", "ckey": "", "method": "GET", "media_type": "text", "keywords": "讲讲舔狗,jjtg,tiangou,tg", "body_template": "", "params": {"type": "json"}, "parse": "Msg"},
        {"name": "讲讲温柔", "base_url": "https://api.yuafeng.cn/API/ly/wenrou.php", "ckey": "", "method": "GET", "media_type": "text", "keywords": "讲讲温柔,jjwr,wenrou,wr", "body_template": "", "params": {"type": "json"}, "parse": "Msg"},
        {"name": "讲讲英汉", "base_url": "https://api.yuafeng.cn/API/ly/yhyl.php", "ckey": "", "method": "GET", "media_type": "text", "keywords": "讲讲英汉,jjyh,yinghan,yh", "body_template": "", "params": {"type": "json"}, "parse": "Msg"},
        {"name": "今日运势", "base_url": "https://api.tangdouz.com/wz/luck.php", "ckey": "", "method": "GET", "media_type": "image", "keywords": "今日运势,jrys,jinriyunsi,yunshi", "body_template": ""},
        {"name": "今天吃什么", "base_url": "https://api.pearktrue.cn/api/today/food.php", "ckey": "", "method": "GET", "media_type": "text", "keywords": "今天吃什么,jtcsm,吃什么,csm", "body_template": "", "parse": "food"},
        {"name": "鞠婧祎", "base_url": "http://api.317ak.cn/api/sp/jjyx", "ckey": "", "method": "GET", "media_type": "video", "keywords": "鞠婧祎,jjy,jujingyi", "body_template": ""},
        {"name": "看看穿搭", "base_url": "http://api.317ak.cn/api/sp/cdxl", "ckey": "", "method": "GET", "media_type": "video", "keywords": "看看穿搭,kkcd,chuanda,cd", "body_template": ""},
        {"name": "看看吊带", "base_url": "http://api.317ak.cn/api/sp/ddxl", "ckey": "", "method": "GET", "media_type": "video", "keywords": "看看吊带,kkdd,diandai,dd", "body_template": ""},
        {"name": "看看动漫", "base_url": "https://api.yuafeng.cn/API/ly/dmxl.php", "ckey": "", "method": "GET", "media_type": "video", "keywords": "看看动漫,kkdm,dongman,dm", "body_template": ""},
        {"name": "看看腹肌", "base_url": "http://api.317ak.cn/api/sp/fjbz", "ckey": "", "method": "GET", "media_type": "video", "keywords": "看看腹肌,kkfj,fuji,fj", "body_template": ""},
        {"name": "看看公主", "base_url": "http://api.317ak.cn/api/sp/gzhy", "ckey": "", "method": "GET", "media_type": "video", "keywords": "看看公主,kkgz,gongzhu,gz", "body_template": "", "params": {"type": "json"}, "parse": "data"},
        {"name": "看看光剑", "base_url": "http://api.317ak.cn/api/sp/gjbz", "ckey": "", "method": "GET", "media_type": "video", "keywords": "看看光剑,kkgj,guangjian,gj", "body_template": ""},
        {"name": "看看红鸾", "base_url": "http://api.317ak.cn/api/sp/hljj", "ckey": "", "method": "GET", "media_type": "video", "keywords": "看看红鸾,kkhl,hongluan,hl", "body_template": "", "params": {"type": "json"}, "parse": "data"},
        {"name": "看看黄历", "base_url": "https://api.lolimi.cn/API/huang/api.php", "ckey": "", "method": "GET", "media_type": "text", "keywords": "看看黄历,kkhl,huangli,hl", "body_template": "", "parse": "text"},
        {"name": "看看久喵", "base_url": "http://api.317ak.cn/api/sp/jmxl", "ckey": "", "method": "GET", "media_type": "video", "keywords": "看看久喵,kkjm,jiu miao,jm", "body_template": "", "params": {"type": "json"}, "parse": "data"},
        {"name": "看看狼宝", "base_url": "http://api.317ak.cn/api/sp/lbjj", "ckey": "", "method": "GET", "media_type": "video", "keywords": "看看狼宝,kklb,langbao,lb", "body_template": "", "params": {"type": "json"}, "parse": "data"},
        {"name": "看看萝莉", "base_url": "http://api.317ak.cn/api/sp/llxl", "ckey": "", "method": "GET", "media_type": "video", "keywords": "看看萝莉,kkll,luoli,ll", "body_template": ""},
        {"name": "看看慢摇", "base_url": "http://api.317ak.cn/api/sp/myxl", "ckey": "", "method": "GET", "media_type": "video", "keywords": "看看慢摇,kkmy,man yao,my", "body_template": ""},
        {"name": "看看漫画", "base_url": "https://api.yuafeng.cn/API/ly/mhy.php", "ckey": "", "method": "GET", "media_type": "video", "keywords": "看看漫画,kkmh,manhua,mh", "body_template": ""},
        {"name": "看看萌娃", "base_url": "http://api.317ak.cn/api/sp/mwxl", "ckey": "", "method": "GET", "media_type": "video", "keywords": "看看萌娃,kkmw,mengwa,mw", "body_template": ""},
        {"name": "看看妞", "base_url": "https://free.wqwlkj.cn/wqwlapi/ks_xjj.php?type=image", "ckey": "", "method": "GET", "media_type": "image", "keywords": "看看妞,kkn,niu,nvsheng", "body_template": ""},
        {"name": "看看女大", "base_url": "https://api.yuafeng.cn/API/ly/cqng.php", "ckey": "", "method": "GET", "media_type": "video", "keywords": "看看女大,kknvd,nvda,nd", "body_template": ""},
        {"name": "看看女仆", "base_url": "http://api.317ak.cn/api/sp/npxl", "ckey": "", "method": "GET", "media_type": "video", "keywords": "看看女仆,kknp,nvpu,np", "body_template": ""},
        {"name": "看看清纯", "base_url": "http://api.317ak.cn/api/sp/qcxl", "ckey": "", "method": "GET", "media_type": "video", "keywords": "看看清纯,kkqc,qingchun,qc", "body_template": ""},
        {"name": "看看晴天", "base_url": "http://api.317ak.cn/api/sp/qttj", "ckey": "", "method": "GET", "media_type": "video", "keywords": "看看晴天,kkqt,qingtian,qt", "body_template": ""},
        {"name": "看看骚的", "base_url": "https://api.yuafeng.cn/API/ly/sjxl.php", "ckey": "", "method": "GET", "media_type": "video", "keywords": "看看骚的,kk sd,sao de,sd", "body_template": ""},
        {"name": "看看色色", "base_url": "https://api.yuafeng.cn/API/ly/sp.php", "ckey": "", "method": "GET", "media_type": "video", "keywords": "看看色色,kkss,se se,ss", "body_template": ""},
        {"name": "看看甩裙", "base_url": "http://api.317ak.cn/api/sp/sqxl", "ckey": "", "method": "GET", "media_type": "video", "keywords": "看看甩裙,kk sq,shuai qun,sq", "body_template": ""},
        {"name": "看看帅哥", "base_url": "https://api.yuafeng.cn/API/ly/sgxl.php", "ckey": "", "method": "GET", "media_type": "video", "keywords": "看看帅哥,kk sg,shuaige,sg", "body_template": ""},
        {"name": "看看兔子", "base_url": "http://api.317ak.cn/api/sp/ttmn", "ckey": "", "method": "GET", "media_type": "video", "keywords": "看看兔子,kk tz,tuzi,tz", "body_template": "", "params": {"type": "json"}, "parse": "data"},
        {"name": "看看微胖", "base_url": "http://api.317ak.cn/api/sp/wpxl", "ckey": "", "method": "GET", "media_type": "video", "keywords": "看看微胖,kk wp,weipang,wp", "body_template": ""},
        {"name": "看看仙桃猫", "base_url": "http://api.317ak.cn/api/sp/xtmx", "ckey": "", "method": "GET", "media_type": "video", "keywords": "看看仙桃猫,kk xtm,xiantaomao,xtm", "body_template": "", "params": {"type": "json"}, "parse": "data"},
        {"name": "看看小雪", "base_url": "http://api.317ak.cn/api/sp/xxmm", "ckey": "", "method": "GET", "media_type": "video", "keywords": "看看小雪,kk xx,xiaoxue,xx", "body_template": "", "params": {"type": "json"}, "parse": "data"},
        {"name": "看看心情", "base_url": "http://api.317ak.cn/api/sp/xqhh", "ckey": "", "method": "GET", "media_type": "video", "keywords": "看看心情,kk xq,xinqing,xq", "body_template": "", "params": {"type": "json"}, "parse": "data"},
        {"name": "看看雪梨", "base_url": "http://api.317ak.cn/api/sp/xlmn", "ckey": "", "method": "GET", "media_type": "video", "keywords": "看看雪梨,kk xl,xueli,xl", "body_template": "", "params": {"type": "json"}, "parse": "data"},
        {"name": "看看余震", "base_url": "http://api.317ak.cn/api/sp/yzxl", "ckey": "", "method": "GET", "media_type": "video", "keywords": "看看余震,kk yz,yuzhen,yz", "body_template": ""},
        {"name": "看看玉足", "base_url": "https://api.yuafeng.cn/API/ly/yzxl.php", "ckey": "", "method": "GET", "media_type": "video", "keywords": "看看玉足,kk yz,yuzu,yz", "body_template": ""},
        {"name": "看看欲梦", "base_url": "http://api.317ak.cn/api/sp/ndym", "ckey": "", "method": "GET", "media_type": "video", "keywords": "看看欲梦,kk ym,yumeng,ym", "body_template": ""},
        {"name": "看看原神", "base_url": "http://api.317ak.cn/api/sp/yssp", "ckey": "", "method": "GET", "media_type": "video", "keywords": "看看原神,kk ys,yuanshen,ys", "body_template": ""},
        {"name": "看看治愈", "base_url": "https://api.yuafeng.cn/API/ly/zyxl.php", "ckey": "", "method": "GET", "media_type": "video", "keywords": "看看治愈,kk zy,zhiyu,zy", "body_template": ""},
        {"name": "看看COS", "base_url": "http://api.317ak.cn/api/sp/cosxl", "ckey": "", "method": "GET", "media_type": "video", "keywords": "看看COS,kk cos,cosplay,cos", "body_template": ""},
        {"name": "看看emo", "base_url": "https://api.yuafeng.cn/API/ly/emo.php", "ckey": "", "method": "GET", "media_type": "video", "keywords": "看看emo,kk emo,emo", "body_template": ""},
        {"name": "坤", "base_url": "https://free.wqwlkj.cn/wqwlapi/ikun.php", "ckey": "", "method": "GET", "media_type": "image", "keywords": "坤,kun,ikun,ik", "body_template": ""},
        {"name": "垃圾分类", "base_url": "https://api.tangdouz.com/a/garbage.php", "ckey": "", "method": "GET", "media_type": "text", "keywords": "垃圾分类,ljf,lajifenlei", "body_template": "", "params": {"nr": ""}},
        {"name": "来点段子", "base_url": "https://api.lolimi.cn/API/yiyan/dz.php", "ckey": "", "method": "GET", "media_type": "text", "keywords": "来点段子,lddz,duanzi,dz", "body_template": ""},
        {"name": "来点腹肌", "base_url": "http://api.317ak.cn/api/tp/fjtp", "ckey": "", "method": "GET", "media_type": "image", "keywords": "来点腹肌,ldfj,fuji,fj", "body_template": ""},
        {"name": "来点帅哥", "base_url": "https://api.lolimi.cn/API/boy/api.php", "ckey": "", "method": "GET", "media_type": "image", "keywords": "来点帅哥,ldsg,shuaige,sg", "body_template": ""},
        {"name": "来点文案", "base_url": "https://api.tangdouz.com/a/refuel.php", "ckey": "", "method": "GET", "media_type": "text", "keywords": "来点文案,ldwa,wenan,wa", "body_template": "", "params": {"f": "哲理"}},
        {"name": "来份早报", "base_url": "https://api.yuafeng.cn/API/60sn/", "ckey": "", "method": "GET", "media_type": "image", "keywords": "来份早报,lfzb,zaobao,zb", "body_template": ""},
        {"name": "来个头像", "base_url": "https://api.yuafeng.cn/API/ecr/api.php", "ckey": "", "method": "GET", "media_type": "image", "keywords": "来个头像,lgtx,touxiang,tx", "body_template": ""},
        {"name": "来句情话", "base_url": "https://api.yuafeng.cn/API/ly/twqh.php", "ckey": "", "method": "GET", "media_type": "text", "keywords": "来句情话,ljqh,qinghua,qh", "body_template": "", "params": {"type": "json"}, "parse": "Msg"},
        {"name": "来句骚话", "base_url": "https://api.yuafeng.cn/API/ly/saohua.php", "ckey": "", "method": "GET", "media_type": "text", "keywords": "来句骚话,ljsh,saohua,sh", "body_template": "", "params": {"type": "json"}, "parse": "Msg"},
        {"name": "来句诗", "base_url": "https://api.tangdouz.com/a/poetrand.php", "ckey": "", "method": "GET", "media_type": "text", "keywords": "来句诗,ljs,shi,shici", "body_template": ""},
        {"name": "来篇文章", "base_url": "https://api.tangdouz.com/a/jt.php", "ckey": "", "method": "GET", "media_type": "text", "keywords": "来篇文章,ljwz,wenzhang,wz", "body_template": ""},
        {"name": "来碗鸡汤", "base_url": "https://api.tangdouz.com/a/jt.php", "ckey": "", "method": "GET", "media_type": "text", "keywords": "来碗鸡汤,lwjt,jitang,jt", "body_template": ""},
        {"name": "猫系女友", "base_url": "http://api.317ak.cn/api/sp/mxny", "ckey": "", "method": "GET", "media_type": "video", "keywords": "猫系女友,mxny,maoxi,maonv", "body_template": ""},
        {"name": "每日日报", "base_url": "https://api.tangdouz.com/a/60/", "ckey": "", "method": "GET", "media_type": "image", "keywords": "每日日报,mrrb,ribao,rb", "body_template": ""},
        {"name": "每日听力", "base_url": "https://api.tangdouz.com/a/perday.php", "ckey": "", "method": "GET", "media_type": "audio", "keywords": "每日听力,mrtl,tingli,tl", "body_template": "", "params": {"return": "json"}, "parse": "tts"},
        {"name": "每日一签", "base_url": "https://api.lolimi.cn/API/riq/", "ckey": "", "method": "GET", "media_type": "image", "keywords": "每日一签,mryq,yiqian,yq", "body_template": ""},
        {"name": "逆天语音", "base_url": "https://api.yuafeng.cn/API/ly/sjyy.php", "ckey": "", "method": "GET", "media_type": "audio", "keywords": "逆天语音,nty,shijieyu yin,sjyy", "body_template": ""},
        {"name": "起个网名", "base_url": "https://free.wqwlkj.cn/wqwlapi/gxwm.php", "ckey": "", "method": "GET", "media_type": "text", "keywords": "起个网名,qgwm,wangming,wm", "body_template": "", "params": {"msg": "非主流"}},
        {"name": "人品运势", "base_url": "https://api.lolimi.cn/API/Ren/api.php", "ckey": "", "method": "GET", "media_type": "text", "keywords": "人品运势,rpys,renpin,yunshi", "body_template": "", "params": {"name": "", "type": "json"}, "parse": "text"},
        {"name": "日历", "base_url": "https://api.tangdouz.com/htmlimage/rl.php", "ckey": "", "method": "GET", "media_type": "image", "keywords": "日历,rili,rl", "body_template": "", "params": {"theme": "原神"}},
        {"name": "三坑少女", "base_url": "https://api.pearktrue.cn/api/beautifulgirl/?type=image", "ckey": "", "method": "GET", "media_type": "image", "keywords": "三坑少女,sksn,sankeng", "body_template": ""},
        {"name": "生成二维码", "base_url": "https://api.yuafeng.cn/API/ly/qrcode.php", "ckey": "", "method": "GET", "media_type": "image", "keywords": "生成二维码,scerweima,erweima,ewm", "body_template": "", "params": {"text": "https://space.bilibili.com/496733846"}},
        {"name": "竖屏动漫壁纸", "base_url": "https://api.lolimi.cn/API/dmtx/sp.php", "ckey": "", "method": "GET", "media_type": "image", "keywords": "竖屏动漫壁纸,spdmbz,shuping,dongmanbz", "body_template": ""},
        {"name": "搜表情", "base_url": "https://api.tangdouz.com/a/biaoq.php", "ckey": "", "method": "GET", "media_type": "image", "keywords": "搜表情,sbqb,biaoqing,bq", "body_template": "", "params": {"nr": "", "return": "text"}},
        {"name": "搜菜谱", "base_url": "https://api.tangdouz.com/dtss.php", "ckey": "", "method": "GET", "media_type": "image", "keywords": "搜菜谱,scpu,caipu,cp", "body_template": "", "params": {"nr": "", "f": "1", "return": "json"}},
        {"name": "搜图", "base_url": "https://api.tangdouz.com/sgst.php", "ckey": "", "method": "GET", "media_type": "image", "keywords": "搜图,st,soutu", "body_template": "", "params": {"nr": ""}},
        {"name": "随机上色", "base_url": "https://free.wqwlkj.cn/wqwlapi/zsytw.php", "ckey": "", "method": "GET", "media_type": "image", "keywords": "随机上色,sjs s,shangse,ss", "body_template": "", "params": {"msg": "", "font_size": "20", "type": "", "line": "/n"}},
        {"name": "挑战古诗词", "base_url": "https://free.wqwlkj.cn/wqwlapi/tzgsc.php", "ckey": "", "method": "GET", "media_type": "text", "keywords": "挑战古诗词,tz gsc,gushici,gsc", "body_template": "", "params": {"msg": "1"}},
        {"name": "王者语音", "base_url": "https://free.wqwlkj.cn/wqwlapi/wzheroyy.php", "ckey": "", "method": "GET", "media_type": "audio", "keywords": "王者语音,wzyy,wangzhe,yy", "body_template": "", "params": {"hero": "孙悟空"}, "parse": "data[].voice"},
        {"name": "显卡排行榜", "base_url": "https://api.tangdouz.com/a/gpu.php", "ckey": "", "method": "GET", "media_type": "text", "keywords": "显卡排行榜,xkphb,xianka,phb", "body_template": "", "params": {"f": "desktop"}},
        {"name": "香烟价格", "base_url": "https://api.lolimi.cn/API/xyan/api.php", "ckey": "", "method": "GET", "media_type": "text", "keywords": "香烟价格,xyjg,xiangyan,xy", "body_template": "", "params": {"msg": "雪莲"}},
        {"name": "潇潇", "base_url": "http://api.317ak.cn/api/sp/xxxl", "ckey": "", "method": "GET", "media_type": "video", "keywords": "潇潇,xxxl,xiaoxiao,xx", "body_template": ""},
        {"name": "刑法", "base_url": "https://api.tangdouz.com/xf.php", "ckey": "", "method": "GET", "media_type": "text", "keywords": "刑法,xf,xingfa", "body_template": "", "params": {"nr": ""}},
        {"name": "硬气卡点", "base_url": "http://api.317ak.cn/api/sp/yqkd", "ckey": "", "method": "GET", "media_type": "video", "keywords": "硬气卡点,yqkd,yingqi,kadian", "body_template": ""},
        {"name": "又纯又欲", "base_url": "http://api.317ak.cn/api/sp/ycyy", "ckey": "", "method": "GET", "media_type": "video", "keywords": "又纯又欲,ycyy,ycy,yucy,ycyyd,又纯欲,纯又欲,ycyuy,ycyy", "body_template": ""},
        {"name": "御姐撒娇", "base_url": "https://api.pearktrue.cn/api/yujie/?type=mp3", "ckey": "", "method": "GET", "media_type": "audio", "keywords": "御姐撒娇,yjsj,yujie,sajiao,sj", "body_template": "", "parse": "audiopath"},
        {"name": "原神", "base_url": "https://api.xingzhige.com/API/yshl/", "ckey": "", "method": "GET", "media_type": "image", "keywords": "原神,ys,yuanshen", "body_template": ""},
        {"name": "原神黄历", "base_url": "https://api.xingzhige.com/API/yshl/", "ckey": "", "method": "GET", "media_type": "image", "keywords": "原神黄历,yshl,yuanshenhuangli", "body_template": ""},
        {"name": "中草药", "base_url": "https://api.tangdouz.com/a/zcy.php", "ckey": "", "method": "GET", "media_type": "text", "keywords": "中草药,zcy,zhongcaoyao", "body_template": "", "params": {"nr": "当归"}},
        {"name": "周清欢", "base_url": "http://api.317ak.cn/api/sp/zqhx", "ckey": "", "method": "GET", "media_type": "video", "keywords": "周清欢,zqhx,zhouqinghuan", "body_template": ""},
        {"name": "周扬青", "base_url": "http://api.317ak.cn/api/sp/zyqx", "ckey": "", "method": "GET", "media_type": "video", "keywords": "周扬青,zyqx,zhouyangqing", "body_template": ""},
        {"name": "B站更新", "base_url": "https://api.lolimi.cn/API/B_Update_Days/api.php", "ckey": "", "method": "GET", "media_type": "text", "keywords": "B站更新,bz gengxin,bilibili,更新", "body_template": "", "params": {"num": 3}, "parse": "data"},
        {"name": "bing图", "base_url": "https://free.wqwlkj.cn/wqwlapi/bing.php", "ckey": "", "method": "GET", "media_type": "image", "keywords": "bing图,bingtu,bt", "body_template": "", "parse": "img"},
        {"name": "KFC", "base_url": "http://api.317ak.cn/api/wz/KFC", "ckey": "", "method": "GET", "media_type": "text", "keywords": "KFC,kfc,疯狂星期四,肯德基,v我50", "body_template": "", "params": {"type": "text"}},
        {"name": "Linux命令", "base_url": "https://api.pearktrue.cn/api/linux/", "ckey": "", "method": "GET", "media_type": "text", "keywords": "Linux命令,lx ling,linux,命令", "body_template": "", "params": {"keyword": ""}, "parse": "data.content"},
        {"name": "QQ签名", "base_url": "http://api.317ak.cn/api/wz/QQqm", "ckey": "", "method": "GET", "media_type": "text", "keywords": "QQ签名,qq qm,qianming,qm", "body_template": "", "params": {"type": "text"}}
    ]

    def _import_defaults(self):
        existing_names = {a.get("name") for a in self.apis}
        added = 0
        for d in self.DEFAULT_APIS:
            if d["name"] not in existing_names:
                self.apis.append(d.copy())
                added += 1
        self.config["apis"] = self.apis
        self.config.save_config()
        return added

    async def _handle_binary_media(self, event: AstrMessageEvent, resp: httpx.Response, api_name: str):
        content_type = resp.headers.get("content-type", "").lower()
        content_length = len(resp.content)

        logger.info(f"[{api_name}] 二进制响应 - Type: {content_type}, 大小: {content_length / 1024 / 1024:.2f} MB")

        if content_length < 1024 * 50:
            yield event.plain_result(f"[{api_name}] 响应太小，可能无效")
            return

        # 优先远程URL
        try:
            url = str(resp.url)
            chain = [Comp.Plain(f"[{api_name}] video 媒体（远程直链发送）")]
            chain.append(Comp.Video.fromURL(url=url))
            yield event.chain_result(chain)
            logger.info(f"[{api_name}] 远程URL发送成功")
            return
        except Exception as e:
            logger.warning(f"远程URL失败，保存到 NapCat temp: {e}")

        # 保存到你的 NapCat temp 目录
        filename = f"{uuid.uuid4().hex}.mp4"
        local_path = os.path.join(self.napcat_temp, filename)
        absolute_path = os.path.abspath(local_path)

        with open(local_path, "wb") as f:
            f.write(resp.content)

        logger.info(f"[{api_name}] 文件保存到 NapCat temp 成功: {absolute_path}")

        chain = [Comp.Plain(f"[{api_name}] video 媒体（NapCat本地发送）")]
        chain.append(Comp.Video.fromFileSystem(path=absolute_path))
        yield event.chain_result(chain)

    async def call_api(self, api: dict, prompt: str) -> Any:
        base_url = api["base_url"].rstrip("/")
        ckey = api.get("ckey", "").strip() or self.config.get("global_ckey", "").strip()
        method = api.get("method", "GET").upper()
        body_template = api.get("body_template", '{"prompt": "{prompt}"}')

        async with httpx.AsyncClient(timeout=120) as client:
            if method == "POST":
                body_str = body_template.replace('"{prompt}"', json.dumps(prompt))
                try: payload = json.loads(body_str)
                except: payload = {"prompt": prompt}
                if ckey: payload["ckey"] = ckey
                resp = await client.post(base_url, json=payload)
            else:
                params = {"prompt": prompt} if prompt else {}
                if ckey: params["ckey"] = ckey
                resp = await client.get(base_url, params=params)

            resp.raise_for_status()

            content_type = resp.headers.get("content-type", "").lower()
            if "json" in content_type:
                try:
                    return resp.json()
                except:
                    return resp.text
            else:
                return resp

    async def process_response(self, event: AstrMessageEvent, data: Any, api_name: str, force_type: str = "auto"):
        if isinstance(data, httpx.Response):
            async for msg in self._handle_binary_media(event, data, api_name):
                yield msg
        else:
            text = self._clean_text(str(data) if not isinstance(data, str) else data)
            yield event.plain_result(f"[{api_name}] 非二进制响应预览：\n{text[:1000]}...")

    def _clean_text(self, text: str) -> str:
        if not text: return ""
        text = re.sub(r'[\x00-\x1F\x7F-\x9F\u200B-\u200F\uFEFF]', '', text)
        text = re.sub(r'\\x[0-9a-fA-F]{2}', '', text)
        return text.strip()[:2000]

    @filter.command("call")
    async def handle_call(self, event: AstrMessageEvent, api_name: str, *, prompt: str = ""):
        if not prompt:
            parts = event.message_str.split(maxsplit=2)
            prompt = parts[2] if len(parts) > 2 else ""
        api = next((a for a in self.apis if a.get("name") == api_name), None)
        if not api:
            yield event.plain_result(f"❌ 未找到：{api_name}")
            return

        yield event.plain_result(f"🔄 调用 {api_name} 中...")
        try:
            data = await self.call_api(api, prompt)
            force_type = api.get("media_type", "auto")
            async for msg in self.process_response(event, data, api_name, force_type):
                yield msg
        except Exception as e:
            yield event.plain_result(f"❌ 异常：{str(e)[:300]}")

    @filter.regex(r".+", priority=80)
    async def keyword_trigger(self, event: AstrMessageEvent):
        msg = event.message_str.strip().lower()  # 转为小写，便于匹配
        if not msg or msg.startswith("/"): return

        for api in self.apis:
            # 获取关键词字符串，并拆分成列表
            kws_str = api.get("keywords", "").strip()
            if not kws_str: continue
            original_kws = [k.strip() for k in kws_str.split(",") if k.strip()]

            # 自动生成首字母缩写 + 常见错别字变体
            all_variants = set(original_kws)  # 先加入原始关键词

            for kw in original_kws:
                # 1. 首字母缩写（支持中文拼音首字母）
                acronym = ''.join([c[0] for c in kw if c.isalpha() or '\u4e00' <= c <= '\u9fff'])
                if acronym:
                    all_variants.add(acronym.lower())
                    all_variants.add(acronym)  # 大小写都加

            # 2. 常见错别字 / 简写变体（可继续扩展）
            variants_map = {
                "又纯又欲": ["ycyy", "ycy", "yucy", "ycyyd", "又纯欲", "纯又欲", "又纯", "ycyuy", "ycyyyd"],
                "看看腿": ["kt", "kkt", "kantu", "看腿", "kk腿", "kt腿", "看k腿"],
                "看看腹肌": ["fj", "kktfj", "kkanfuji", "看腹肌", "kkfj", "fjtp"],
                "看看黑丝": ["hs", "kkhs", "看黑丝", "khs"],
                "看看白丝": ["bs", "kkbs", "看白丝", "kbs"],
                "看看女大": ["nvd", "kknvd", "女大", "nd"],
                "看看清纯": ["qc", "kkqc", "清纯", "qingchun"],
                "看看萝莉": ["ll", "kkll", "萝莉", "luoli"],
                "看看帅哥": ["sg", "kk sg", "帅哥", "shuaige"],
                "来点腹肌": ["ldfj", "lai dian fuji", "腹肌"],
                "来点帅哥": ["ldsg", "lai dian shuaige", "帅哥"],
                # 你可以继续在这里添加其他高频词的变体
            }

            # 合并变体
            for kw in original_kws:
                if kw in variants_map:
                    for v in variants_map[kw]:
                        all_variants.add(v.lower())
                        all_variants.add(v)

            # 匹配逻辑：完全匹配 > 前缀匹配 > 包含匹配
            matched_variant = None
            matched_priority = 0  # 0: 包含, 1: 前缀, 2: 完全

            for variant in all_variants:
                if msg == variant:
                    matched_variant = variant
                    matched_priority = 2
                    break
                elif msg.startswith(variant):
                    matched_variant = variant
                    matched_priority = 1
                    break
                elif variant in msg:
                    matched_variant = variant
                    matched_priority = 0
                    break

            if matched_variant:
                # 提取 prompt（去掉匹配词后面的内容）
                prompt_start = msg.find(matched_variant) + len(matched_variant)
                prompt = msg[prompt_start:].strip()

                # 显示匹配提示（方便调试）
                yield event.plain_result(f"🔄 模糊匹配到 {api['name']} ({matched_variant})，正在获取...")

                try:
                    data = await self.call_api(api, prompt)
                    force_type = api.get("media_type", "auto")
                    async for msg_part in self.process_response(event, data, api["name"], force_type):
                        yield msg_part
                    return  # 匹配成功后退出
                except Exception as e:
                    yield event.plain_result(f"❌ 调用 {api['name']} 失败：{str(e)[:200]}")
                    continue  # 继续尝试下一个

        # 如果没有任何匹配，可以取消注释下面这行
        # yield event.plain_result("未匹配到任何API关键词")

    @filter.command("listapi")
    async def list_apis(self, event: AstrMessageEvent):
        gckey_status = "已设置" if self.config.get("global_ckey", "").strip() else "未设置"
        lines = [f"• {a['name']} | 关键词: {a.get('keywords','无')} | 类型:{a.get('media_type','auto')}" for a in self.apis]
        yield event.plain_result(f"API列表（{len(self.apis)}个）\n全局ckey：{gckey_status}\n" + "\n".join(lines))

    @filter.command("importdefault")
    async def import_defaults_cmd(self, event: AstrMessageEvent):
        added = self._import_defaults()
        yield event.plain_result(f"已导入 {added} 个默认API完成。全局ckey状态：{'已设置' if self.config.get('global_ckey') else '未设置，请立即设置！'}")

    @filter.command("call")
    async def handle_call(self, event: AstrMessageEvent, api_name: str, *, prompt: str = ""):
        if not prompt:
            parts = event.message_str.split(maxsplit=2)
            prompt = parts[2] if len(parts) > 2 else ""
        api = next((a for a in self.apis if a.get("name") == api_name), None)
        if not api:
            yield event.plain_result(f"❌ 未找到：{api_name}")
            return

        yield event.plain_result(f"🔄 调用 {api_name} 中...")
        try:
            data = await self.call_api(api, prompt)
            force_type = api.get("media_type", "auto")
            async for msg in self.process_response(event, data, api_name, force_type):
                yield msg
        except Exception as e:
            yield event.plain_result(f"❌ 异常：{str(e)[:300]}")