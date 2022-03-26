import requests
from time import sleep
import pandas as pd
import numpy as np
from lxml import etree
import re
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.54 Safari/537.36',
    'Cookie': '''SINAGLOBAL=3069125760710.469.1645333188599; _s_tentry=-; Apache=6422101283243.302.1648282381271; ULV=1648282381395:3:2:1:6422101283243.302.1648282381271:1646715272546; SUB=_2A25POr6LDeRhGeNI71cX8yzEzTyIHXVsMZdDrDV8PUNbmtB-LVflkW9NSC5ecWqpJCw751JADZ0MI0wuzhRt6FvE; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WhsmZfa_oCfnP89s1b017Ux5JpX5KzhUgL.Fo-cSh-ce0zRSo52dJLoI0qLxK-LBKBLBK.LxKqL1K.LBoBLxKBLBonL12BLxK-LBKqL1hzLxK-LBKBLBK.LxK.L1-zLBKnt; ALF=1679819354; SSOLoginState=1648283355'''
}
all_df = pd.DataFrame(columns=['排行', '热度', '标题', '评论时间', '用户名称', '转发次数', '评论次数', '点赞次数', '评论内容'])
def get_hot_list(url):
    '''
    微博热搜页面采集，获取详情页链接后，跳转进入详情页采集
    :param url: 微博热搜页链接
    :return: None
    '''
    page_text = requests.get(url=url, headers=headers).text
    tree = etree.HTML(page_text)
    tr_list = tree.xpath('//*[@id="pl_top_realtimehot"]/table/tbody/tr')
    for tr in tr_list:
        parse_url = tr.xpath('./td[2]/a/@href')[0]
        detail_url = 'https://s.weibo.com' + parse_url
        title = tr.xpath('./td[2]/a/text()')[0]
        try:
            rank = tr.xpath('./td[1]/text()')[0]
            hot = tr.xpath('./td[2]/span/text()')[0]
        except:
            rank = '置顶'
            hot = '置顶'
        get_detail_page(detail_url, title, rank, hot)
def get_detail_page(detail_url, title, rank, hot):
    '''
    根据详情页链接，解析所需页面数据，并保存到全局变量 all_df
    :param detail_url: 详情页链接
    :param title: 标题
    :param rank: 排名
    :param hot: 热度
    :return: None
    '''
    global all_df
    try:
        page_text = requests.get(url=detail_url, headers=headers).text
    except:
        return None
    tree = etree.HTML(page_text)
    result_df = pd.DataFrame(columns=np.array(all_df.columns))
    # 爬取3条热门评论信息
    for i in range(1, 4):
        try:
            comment_time = tree.xpath(f'//*[@id="pl_feedlist_index"]/div[4]/div[{i}]/div[2]/div[1]/div[2]/p[1]/a/text()')[0]
            comment_time = re.sub('\s','',comment_time)
            user_name = tree.xpath(f'//*[@id="pl_feedlist_index"]/div[4]/div[{i}]/div[2]/div[1]/div[2]/p[2]/@nick-name')[0]
            forward_count = tree.xpath(f'//*[@id="pl_feedlist_index"]/div[4]/div[{i}]/div[2]/div[2]/ul/li[1]/a/text()')[1]
            forward_count = forward_count.strip()
            comment_count = tree.xpath(f'//*[@id="pl_feedlist_index"]/div[4]/div[{i}]/div[2]/div[2]/ul/li[2]/a/text()')[0]
            comment_count = comment_count.strip()
            like_count = tree.xpath(f'//*[@id="pl_feedlist_index"]/div[4]/div[{i}]/div[2]/div[2]/ul/li[3]/a/button/span[2]/text()')[0]
            comment = tree.xpath(f'//*[@id="pl_feedlist_index"]/div[4]/div[{i}]/div[2]/div[1]/div[2]/p[2]//text()')
            comment = ' '.join(comment).strip()
            result_df.loc[len(result_df), :] = [rank, hot, title, comment_time, user_name, forward_count, comment_count, like_count, comment]
        except Exception as e:
            print(e)
            continue
    print(detail_url, title)
    all_df = all_df.append(result_df, ignore_index=True)
if __name__ == '__main__':
    url = 'https://s.weibo.com/top/summary?cate=realtimehot'
    get_hot_list(url)
    all_df.to_excel('工作文档.xlsx', index=False)