import datetime
import pytdx.hq as hq
from pytdx.config.hosts import hq_hosts as hosts
import format as F
import mongo
api = hq.TdxHq_API()

def log(log_info):
    """日志记录函数"""
    print(log_info)

def ping(ip, port):
    """测试ip连通时间"""
    tdx_api = hq.TdxHq_API()
    start = datetime.datetime.now()
    try:
        with tdx_api.connect(ip, port):
            log("F ping(): IP,%s port,%s" % (ip, port))
            if len(tdx_api.get_security_list(0, 1)) > 800:
                return datetime.datetime.now() - start
    except:
        log("F ping(): Bad response %s:%s" % (ip, port))
        return datetime.timedelta(9, 9, 0)


def select_best_server():
    """Select the best Server of TDX from pytdx.config.hosts"""
    log("Select the best Server of TDX from pytdx.config.hosts")
    time = [ping(x[1], x[-1]) for x in hosts[::]]
    log("===The best Server is : ")
    log(hosts[time.index(min(time))])
    return hosts[time.index(min(time))]


def get_companys(markets,server):
    """Get all company record from markets"""
    companys = []
    with api.connect(server[0],server[1]):
        for m in markets:
            for c in api.get_security_list(market=m,start=0):
                companys.append({'market':m,'code':c['code'],'name':c['name']})
    return companys

def get_companys_information(companys,server):
    """Get details for each company"""
    result = []
    with api.connect(server[0],server[1]):
        for cm in companys:
            for ct in api.get_company_info_category(cm['market'], cm['code']):
                result.append({'name':ct['name'],'length':ct['length'],
                    'info':api.get_company_info_content(cm['market'], cm['code'],ct['filename'],ct['start'],ct['length'])})
    return result

def select_function(name,info,tags):
    if name == '公司概况':
        return F.format_company_overview(info,tags)
    elif name == '财务分析':
        return F.format_financial_analysis(info,tags)
    elif name == '股本结构':
        return F.format_capital_structure(info,tags)
    elif name == '资本运作':
        return F.format_capital_operation(info,tags)
    elif name == '高层治理':
        return F.format_high_level_governance(info,tags)
    elif name == '关联个股':
        return F.format_associated_stocks(info,tags)

def test():
    name = {'公司概况': 'format_company_overview',
            '财务分析': 'format_financial_analysis',
            '股本结构': 'format_capital_structure',
            '资本运作': 'format_capital_operation',
            '高层治理': 'format_high_level_governance',
            '关联个股': 'format_associated_stocks'}
    market = 0
    code = '000002'
    tmp = []
    with api.connect('117.34.114.31',7709):
        for x in api.get_company_info_category(market,code):
            try:
                func = name[x['name']]
                info = api.get_company_info_content(market,code,x['filename'],x['start'],x['length'])
                tmp.append({x['name']:select_function(x['name'],info,F.table_tags)})
                # tmp.append([x['length'],info])
                # print(x)
                # if len(info) == x['length']:
                #     # print(function(function,info,F.table_tags))
                #     function_name(info,F.table_tags)
                # else:
                #     print("%s:未获取全部信息"%(x['name']))
            except KeyError:
                print("%s:不解析此文档"%(x['name']))
                continue
    for x in tmp:
        mongo.insert(x)
        # for x in api.get_company_info_category(0,'000001'):
        #     print(x)

test()

