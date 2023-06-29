from gpt import GPT
def get_response(data):
    chatgptmodel= GPT()
    flag = False
    try_time = 0
    while not flag and try_time < 8:
        try_time += 1
        try:
            flag,message =  chatgptmodel.call(data['ChatGPT_query'])
            # if not flag:
            #     print(f'error: {message}')
        except Exception as e:
            # print('报错：',e)
            pass
    if not flag:
        raise ValueError('ChatGPT请求失败')
    return message