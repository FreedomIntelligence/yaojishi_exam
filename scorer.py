import re
import json

def process_json(file):
    with open(file, 'r') as f:
        data = f.read()
        data = data.replace('}{', '}\n{')
        for i in range(2,10):
            r = '}'+'\n'*i+'{'
            data = data.replace(r, '}\n{')
        return data

# 注意要让模型最后给出选项，采用的正则只匹配最后的选择
def match_choice(text):
    match = re.findall(r'.*?([A-E]+(?:[、, ]+[A-E]+)*)', text)
    if match:
        last_match = match[-1]
        return ''.join(re.split(r'[、, ]+', last_match))
    return ''

def score_result(finished_path):
    # process_json(finished_path)
    datas = []
    with open(finished_path) as f:
        for l in f:
            datas.append(json.loads(l))
    q_type = ['最佳选择题','配伍选择题','综合分析选择题','多项选择题']
    type2score = {k:[0,0] for k in q_type}
    wrong_data = []
    wrong_data_file_path = 'wrong_choice.json'
    for da in datas:
        ty = da['question_type']
        ans = da['answer']
        choice = match_choice(da['ChatGPT_response'])
        if len(choice) > 1 and ty != '多项选择题':
            choice = choice[0]
        if choice == ans:
            type2score[ty][0] += 1
        else:
            da['model_answer'] = choice
            wrong_data.append(da)
        type2score[ty][1] += 1
    
    for k,v in type2score.items():
        print(f'【{k}】准确率：{v[0]/v[1]:.3f}   题目总数：{v[1]}')

    print(f'总分：{sum([sc[0] for sc in type2score.values()])}  / 满分：{len(datas)}')

    print(f'错误题目：{len(wrong_data)}道，已输出到 {wrong_data_file_path}')
    with open(wrong_data_file_path,'w') as fw:
        json.dump(wrong_data,fw,ensure_ascii=False,indent=2)