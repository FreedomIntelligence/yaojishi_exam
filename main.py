# -*- coding: utf-8 -*-
# %%
import jsonlines as jl
import os
import random
import json
import time
from tqdm import tqdm
import multiprocessing
import re
from request_gpt import get_response
from scorer import score_result

def write_piece_order_data(d):
    out_file = jl.open('chatgpt_output.json', 'a')
    failed_file = jl.open('chatgpt_failed.json', 'a')
    try:
        d['ChatGPT_query'] = generate_query(d)
        message = get_response(d)
        d['ChatGPT_response'] = message
        out_file.write(d)
    except Exception as e:
        failed_file.write(d)
        print(e)
    return d['id']

def generate_query(data):
    chatgpt_query = System_prompt
    question = data['question']
    option = '\n'.join([k+'. '+v for k,v in data['option'].items() if v != ''])
    chatgpt_query = chatgpt_query.format_map({'question':question,'option':option})
    return chatgpt_query

def init():
    _ = open('chatgpt_output.json', "w")
    _.close()
    _ = open('chatgpt_failed.json', "w")
    _.close()

# 在这里修改prompt，其中{question}表示问题、{option}表示选项
System_prompt = "下面是一道选择题，请先详细分析问题，最后给出选项。\n{question}\n{option}"

if __name__ == '__main__':
    init()
    #读取数据
    data_path = 'dataset/2021真题.json'
    data=[]
    with open(data_path, encoding='utf-8') as f:
        data = json.load(f)
    for id,da in enumerate(data):
        da['id'] = id
    print(f"total {len(data)} questions")

    # 进程数
    num_process = 50
    process_list = []

    with multiprocessing.Pool(processes=num_process) as pool:
        results = [
            pool.apply_async(write_piece_order_data, args=(sample,))
            for sample in data
        ]
        for r in tqdm(results, desc="Processing samples", unit="sample"):
            r.wait()
        result_list = [r.get() for r in results]
        pool.close()
        pool.join()

    print('ChatGPT生成结束，开始测分')
    score_result('chatgpt_output.json')