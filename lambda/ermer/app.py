import json
import os, sys, backoff, math
from datetime import datetime
from random import randint
from gremlin_python import statics
from gremlin_python.process.traversal import Pop
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.structure.graph import Graph
from gremlin_python.driver.protocol import GremlinServerError
from gremlin_python.driver import serializer
from gremlin_python.driver import client
from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.process.graph_traversal import __
from gremlin_python.process.strategies import *
from gremlin_python.process.traversal import *
from tornado.websocket import WebSocketClosedError
from tornado import httpclient 
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from botocore.credentials import ReadOnlyCredentials
from types import SimpleNamespace

from collections import defaultdict

# variables
attributes = ["id","Gene_Name","Swiss_Prot","Protein","Function","Description","name","bigg.metabolite","biocyc","kegg.compound","label",'source','target','attribute',"eid","linehoverdisplay","equation"]

visualize_attributes = ["id","name","Description","biocyc","kegg.compound"]
# envorinments
reconnectable_err_msgs = [ 
    'ReadOnlyViolationException',
    'Server disconnected',
    'Connection refused'
]

retriable_err_msgs = ['ConcurrentModificationException'] + reconnectable_err_msgs

network_errors = [WebSocketClosedError, OSError]

retriable_errors = [GremlinServerError] + network_errors  

def is_retriable_error(e):

    is_retriable = False
    err_msg = str(e)
    
    if isinstance(e, tuple(network_errors)):
        is_retriable = True
    else:
        is_retriable = any(retriable_err_msg in err_msg for retriable_err_msg in retriable_err_msgs)
  
    print('error: [{}] {}'.format(type(e), err_msg))
    print('is_retriable: {}'.format(is_retriable))
    
    return is_retriable

def is_non_retriable_error(e):    
    return not is_retriable_error(e)
    
def reset_connection_if_connection_issue(params):
  
    is_reconnectable = False

    e = sys.exc_info()[1]
    err_msg = str(e)
    
    if isinstance(e, tuple(network_errors)):
        is_reconnectable = True
    else:
        is_reconnectable = any(reconnectable_err_msg in err_msg for reconnectable_err_msg in reconnectable_err_msgs)
        
    print('is_reconnectable: {}'.format(is_reconnectable))
        
    if is_reconnectable:
        global conn
        global g
        conn.close()
        conn = create_remote_connection()
        g = create_graph_traversal_source(conn)

def create_graph_traversal_source(conn):
    return traversal().withRemote(conn)
  
def create_remote_connection():
    print('Creating remote connection')
    
    return DriverRemoteConnection(
        connection_string(),
        'g',
        pool_size=1,
        message_serializer=serializer.GraphSONSerializersV2d0())
    
def connection_string():
  
    database_url = 'wss://{}:{}/gremlin'.format(os.environ['neptuneEndpoint'], os.environ['neptunePort'])
        
    return database_url

@backoff.on_exception(backoff.constant,
    tuple(retriable_errors),
    max_tries=5,
    jitter=None,
    giveup=is_non_retriable_error,
    on_backoff=reset_connection_if_connection_issue,
    interval=1)
def regulation(source,target,step,stype,g):
    if stype == "metabolite":
        if step == 1:
            path = g.V(source).outE("CPI").inV().hasId(target).path().by(__.valueMap(*attributes).by(__.unfold())).toList()
            return path
        elif step < 5:
            path = g.V(source).outE("CPI").inV().repeat(__.outE('TFGI',"SFGI","sRGI","PPI").inV().simplePath()).emit().times(step -1).hasId(target).path().by(__.valueMap(*attributes).by(__.unfold())).toList()
            return path
        else:
            # path1 = g.V(source).outE("CPI").inV().hasId(target).path().by(__.valueMap(*attributes).by(__.unfold())).toList()
            path = g.V(source).store('x').outE("CPI").inV().where(without('x')).aggregate('x').repeat(__.outE('TFGI',"SFGI","sRGI","PPI").inV().where(without('x')).aggregate('x')).until(__.hasId(target).or_().loops().is_(step - 1)).hasId(target).path().by(__.valueMap(*attributes).by(__.unfold())).toList()
            # paths = path1 + path2
            # print(paths)
            return path
    elif stype == "gene":
        paths = g.V(source).store('x').repeat(__.outE('TFGI',"SFGI","sRGI","PPI").inV().where(without('x')).aggregate('x')).until(__.hasId(target).or_().loops().is_(step)).hasId(target).path().by(__.valueMap(*attributes).by(__.unfold())).toList()
        # print(paths)
        return paths

@backoff.on_exception(backoff.constant,
    tuple(retriable_errors),
    max_tries=5,
    jitter=None,
    giveup=is_non_retriable_error,
    on_backoff=reset_connection_if_connection_issue,
    interval=1)
def deep(vetex_ids,edges,client,g):
    sql_head = 'g.V(\"{}\")'.format(vetex_ids[0])
    for i in vetex_ids[1:]:
        tmp = '.bothE().otherV().hasId(\"{}\")'.format(i)
        sql_head += tmp
    sql_bothE = '"{}",' * len(edges)
    sql_bothE = sql_bothE.strip(",")
    sql_edge = '.bothE(%s).otherV().path().by(__.valueMap("id","Gene_Name","Swiss_Prot","Protein","Function","Description","name","bigg.metabolite","biocyc","kegg.compound","label","source","target","attribute","eid","linehoverdisplay","equation").by(__.unfold())).toList()' % sql_bothE
    sql_edge = sql_edge.format(*edges)
    sql = sql_head + sql_edge
    print("sql:",sql)
    result_set = client.submit(sql)
    future_results = result_set.all()
    paths = future_results.result()
    # print(paths)
    if len(paths):
        return paths
    else:
        sql = sql_head + '.path().by(__.valueMap("id","Gene_Name","Swiss_Prot","Protein","Function","Description","name","bigg.metabolite","biocyc","kegg.compound","label","source","target","attribute","eid","linehoverdisplay","equation").by(__.unfold())).toList()'
        print("sql:",sql)
        result_set = client.submit(sql)
        future_results = result_set.all()
        paths = future_results.result()
        # print(paths)
        return paths
    

@backoff.on_exception(backoff.constant,
    tuple(retriable_errors),
    max_tries=5,
    jitter=None,
    giveup=is_non_retriable_error,
    on_backoff=reset_connection_if_connection_issue,
    interval=1)
def simple_times(vetex_ids,edge_types,direction,times,g):
    """
    # use in beta version --- deep search
    vetex_id : entity id
    edge_types: ["sRGI","RMI","MRI","GRI","PPI","CPI","TFGI","RPI","SFGI"]
    direction: [in,out,both]
    times: '2' 
    """
    if direction == "both":
        if times > 2:
            paths = g.V(*vetex_ids).repeat(__.bothE(*edge_types).otherV().simplePath().limit(10)).emit().times(times).path().by(__.id()).toList()
        else:
            paths = g.V(*vetex_ids).repeat(__.bothE(*edge_types).otherV().simplePath()).emit().times(times).path().by(__.id()).toList()
    elif direction == "out":
        paths = g.V(*vetex_ids).repeat(__.outE(*edge_types).inV().simplePath()).emit().times(times).path().by(__.id()).toList()
    else:
        paths = g.V(*vetex_ids).repeat(__.inE(*edge_types).outV().simplePath()).emit().times(times).path().by(__.id()).toList()
    # print(paths)
    return paths


@backoff.on_exception(backoff.constant,
    tuple(retriable_errors),
    max_tries=5,
    jitter=None,
    giveup=is_non_retriable_error,
    on_backoff=reset_connection_if_connection_issue,
    interval=1)
def get_nodes_edges_attributes(nodes_ids,edges_ids,g):
    nodes = g.V(nodes_ids).valueMap(*attributes).by(__.unfold()).toList()
    if edges_ids:
        edges = g.E(edges_ids).valueMap(*attributes).by(__.unfold()).toList()
        return nodes,edges
    else:
        return nodes,[]



####################################
# neptune connection
####################################
print('Trying To Login')   
conn = create_remote_connection()
g = create_graph_traversal_source(conn)
print('Successfully Logged In')

######################################
# client
database_url = 'wss://{}:{}/gremlin'.format(os.environ['neptuneEndpoint'], os.environ['neptunePort'])
client = client.Client(database_url, 'g')

def response(statuscode,data):
    # lambda response to api gateway
    if "memory limitations" in data:
        data = "OOM: Two vertexs is far away, our machine performance is poor, please check the input and submit again"
    response_body = {
        "statusCode":statuscode,
        "data" : data
    }
    response = {
        "statusCode": statuscode,
        "headers":{
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        "body": json.dumps(response_body)
    }
    return response


def request_regulation(event):
    try:
        print("************ regulation  start************")
        body = event['body']
        print(body)
        source_id = json.loads(body)["source"]
        target_id = json.loads(body)["target"]
        step = json.loads(body)["step"]
        nodes = json.loads(body)["nodes"]
        number = json.loads(body)["number"]
        stype = json.loads(body)["type"]
        print("source_id:",source_id)
        print("target_id:",target_id)
        if number == "shortest":
            for s in range(1,int(step) + 1):
                paths = regulation(source_id,target_id,s,stype,g)
                if paths:
                    break
        else:
            paths = []
            for s in range(1,int(step) + 1):
                paths += regulation(source_id,target_id,s,stype,g) 
                    
        data = {}
        data["data"] = []
        # print(type(paths))
        filter_path = []
        if len(paths):
            # 过滤nodes
            for path in paths:
                strings=""
                tmp = [i for i in path]
                count_dict = {
                    "CPI":0,
                    "PPI":0,
                    "TFGI":0,
                    "SFGI":0,
                    "sRGI":0,
                }
                x = set()
                for i in tmp:
                    if "id" in i:
                        strings += i["id"]
                        if i["id"] in nodes:
                            x.add(i["id"])
                    elif 'source' in i and 'target' in i:
                        if i["label"] in count_dict:
                            count_dict[i["label"]] += 1
                if strings not in filter_path:
                    filter_path.append(strings)
                    # 满足必过的nodes，PPI默认小于3
                    # if len(x) == len(nodes) and count_dict["PPI"] < 3:
                    if len(x) == len(nodes):
                        tmp.append(count_dict)
                        data['data'].append(tmp)
            # 过滤number
            if number == "all":
                data = data
            else:
                if len(data["data"]) > 5:
                    data['data'] = data['data'][:5]
                else:
                    data = data
            # 返回选中的nodes和edges信息
            nodes_ids = []
            edges_ids = []
            data["nodes"] = []
            data["edges"] = []
            for path in data["data"]:
                for i in path:
                    if 'id' in i  and i["id"] not in nodes_ids:
                        data["nodes"].append(i)
                        nodes_ids.append(i["id"])
                    elif 'eid' in i and i['eid'] not in edges_ids:
                        i["linehoverdisplay"] = eval(i["linehoverdisplay"])
                        data["edges"].append(i)
                        edges_ids.append(i["eid"]) 
        response_message = response(200,data)
        print("************ regulation  end************")
        return response_message
    except Exception as e:
        print(e)
        response_message = response(500,str(e))
        return response_message
    
def request_deep(event):
    try:
        print("************ deep search ************")
        body = event['body']
        print(body)
        ids = json.loads(body)["ids"]
        edges = json.loads(body)["edges"]
        print("ids:",ids)
        print("edges:",edges)
        paths = deep(ids,edges,client,g)
        data = {}
        data["data"] = []
        for path in paths:
            tmp = [i for i in path]
            data['data'].append(tmp)
        # 返回选中的nodes和edges信息
        nodes_ids = []
        edges_ids = []
        data["nodes"] = []
        data["edges"] = []
        for path in data["data"]:
            for i in path:
                if 'id' in i  and i["id"] not in nodes_ids:
                    data["nodes"].append(i)
                    nodes_ids.append(i["id"])
                elif 'eid' in i and i['eid'] not in edges_ids:
                    i["linehoverdisplay"] = eval(i["linehoverdisplay"])
                    data["edges"].append(i)
                    edges_ids.append(i["eid"]) 
        response_message = response(200,data)
        print("************ deep end ************")
        return response_message
    except Exception as e:
        print(e)
        response_message = response(500,str(e))
        return response_message


def request_simple(event):
    try:
        print("************ simple times start************")
        body = event['body']
        print(body)
        vetex_ids = json.loads(body)["ids"]
        direction = json.loads(body)["direction"]
        edge_types = json.loads(body)["edge_types"]
        times = json.loads(body)["times"]
        print(vetex_ids)
        # 获取path
        print('gremlin query start:',datetime.now())
        paths = simple_times(vetex_ids,edge_types,direction,int(times),g)
        print('gremlin query end:',datetime.now())
        data = {}
        if paths:
            nodes_ids = []
            edges_ids = []
            for path in paths:
                for i in path:
                    if i.startswith('Edge_') and i not in edges_ids :
                        edges_ids.append(i)
                    elif  not i.startswith('Edge_') and i not in nodes_ids:
                        nodes_ids.append(i)
            nodes,edges = get_nodes_edges_attributes(nodes_ids,edges_ids,g)
            for edge in edges:
                edge['linehoverdisplay'] = eval(edge['linehoverdisplay'])
            data["nodes"] = nodes
            data["edges"] = edges
            # data["highlight_nodes"] = [vetex_id]
            data["highlight_nodes"] = vetex_ids
            data["highlight_edges"] = []
        else:
            pass
        response_message = response(200,data)
        print("************ simple times end************")
        return response_message
    except Exception as e:
        print(e)
        response_message = response(500,str(e))
        return response_message
    

def lambda_handler(event, context):
    print(event)
    if event["path"] == "/simple" and event["httpMethod"] == "POST":
        # Interactive Search  2nd Query
        return request_simple(event)
    elif event["path"] == "/deep" and event["httpMethod"] == "POST":
        # Interactive Search  1st Query
        return request_deep(event)
    elif event["path"] == "/regulation" and event["httpMethod"] == "POST":
        # Regulation Search
        return request_regulation(event)
    
    