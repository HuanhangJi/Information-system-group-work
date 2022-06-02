import datetime
import math

from django.http import *
from .models import *
import os
import sys
sys.path.append(os.path.abspath('..'))
os.chdir(os.path.abspath(os.getcwd()))
from client_management.models import *
from django.db.models import Q
import shutil
from django.shortcuts import render
import json
import time
import zipfile
task_num = 0
flag = 0

## request初始化 FINISH
def get_res(request):
    data = request.body.decode('utf-8')
    res = json.loads(data)
    print(res)
    return res['info']


## TODO 补充ID池
def full_project_id(request):
    for ids in range(10000000,10005000):
        id = project_id_pool()
        id.project_id = ids
        id.save()
    return HttpResponse('成功添加')


## TODO 判断分数
def judge_score(star):
    stars = int(star)
    if stars == 1:
        score = 100
    elif stars == 2:
        score = 300
    elif stars == 3:
        score = 500
    elif stars == 4:
        score = 1000
    else:
        score = 2000
    return score

def judge_level(scores):
    if scores <= 1000:
        return 1
    elif scores <=3000:
        return 2
    elif scores <= 10000:
        return 3
    elif scores <= 20000:
        return 4
    else:
        return 5


## TODO 增加任务函数
def project_add(request):
    # try:
        res = get_res(request)
        publisher_id = res['publisher_id']
        project_name = res['project_name']
        project_type = res['project_type']
        global flag
        if project_type == 'image_block':
            flag = 0
            project_type = '图片识别标注'
        else:
            flag = 1
            project_type = '文本标注'
        description = res['description']
        due_time = res['due_time']
        pay_per_task = res['pay_per_task']
        global task_num
        task_num = res['task_num']
        project_star = res['project_star']
        text_tags = res['text_tags']
        p = Project()
        id = project_id_pool.objects.first()
        project_id = id.project_id
        p.project_id = project_id
        id.delete()
        dic = prepay(request,project_id)
        if dic['code'] == 200:
            if os.path.exists(f'./static/sample_document/{project_id}'):
                shutil.rmtree(f'./static/sample_document/{project_id}')
            os.mkdir(f'./static/sample_document/{project_id}')
            if flag == 1:
                with open(f'./static/sample_document/{project_id}/text_tags_{project_id}.txt','w',encoding='utf-8') as fp:
                    n = len(text_tags)
                    for i in range(n):
                        if text_tags[i] == '，':
                            text_tags=replace_char(text_tags,",",i)
                        if text_tags[i] == '；':
                            text_tags=replace_char(text_tags,";",i)
                    fp.write(text_tags)
            p.account_id = publisher_id
            p.project_type = project_type
            p.task_num = task_num
            p.project_status = 0
            p.payment_per_task = pay_per_task
            t = time.localtime(due_time/1000)
            due_time = time.strftime("%Y-%m-%d %H:%M:%S",t)
            p.due_time = str(due_time)
            p.completed_task_num = 0
            p.description = description
            p.project_name = project_name
            p.project_star = project_star
            # p.sample_document = sample_document
            p.save()
            for i in range(1,task_num+1):
                t = Task()
                t.project_id = project_id
                t.task_id = project_id+'_'+str(i)
                t.score = judge_score(project_star)
                # t.original_data = sample_document
                t.due_time = due_time
                t.task_status = 0
                t.save()
            data = {'code':200,'msg':'添加任务成功','project_id':project_id}
        else:
            data = {'code':404,'msg':'预付款余额不足'}
        # except BaseException:
        #     data = {'code':404,'msg':'添加任务失败'}
        return JsonResponse(data)

def replace_char(old_string, char, index):
    '''
    字符串按索引位置替换字符
    '''
    old_string = str(old_string)
    # 新的字符串 = 老字符串[:要替换的索引位置] + 替换成的目标字符 + 老字符串[要替换的索引位置+1:]
    new_string = old_string[:index] + char + old_string[index+1:]
    return new_string



## TODO 删除任务函数
def project_delete(request):
    # try:
        res = get_res(request)
        project_id = res['project_id']
        if Project.objects.filter(project_id=project_id).exist():
            Project.objects.get(project_id=project_id).delete()
            Task.objects.filter(project_id=project_id).delete()
            data = {'code':200,'msg':'删除成功'}
        else:
            data = {'code':402,'msg':'不存在删除对象'}
    # except BaseException:
    #     data = {'code':404,'msg':'删除失败'}
        return JsonResponse(data)


## TODO 编辑任务函数
def project_edit(request):
    # try:
        res = get_res(request)
        project_id = res['project_id']
        project_name = res['project_name']
        description = res['description']
        due_time = res['due_time']
        # pay_per_task = request.GET['pay_per_task']
        if Project.objects.filter(project_id=project_id).exist():
            p = Project.objects.get(project_id=project_id)
            p.project_name = project_name
            p.description = description
            p.due_time = due_time
            # p.payment_per_task = pay_per_task
            p.save()
            data = {'code': 200, 'msg': '修改成功'}
        else:
            data = {'code':404,'msg':'未找到该任务'}
    # except BaseException:
    #     data = {'code':404,'msg':'修改失败'}
        return JsonResponse(data)


## TODO 查询任务函数
def project_query(request):
    # try:
        res = get_res(request)
        keyword = res['keyword']
        t = Project.objects.get(project_id=keyword)
        info = t.to_dict()
        data = {'code': 200, 'msg': '查询成功', 'task_info':info}
    # except BaseException:
    #     data = {'code': 404, 'msg': '查询失败','task_info':''}
        return JsonResponse(data)


# def write_data(request, project_id):
#     project_id = project_id
#     sample_document = request.FILES['file']
#     destination = f'./static/sample_document/{project_id}/{sample_document.name}'
#     if os.path.exists(destination):
#         os.remove(destination)
#     z = zipfile.ZipFile(destination,'w',zipfile.ZIP_DEFLATED)
#     z.close()
#     try:
#         with open(destination,'wb') as f:
#             for chunk in sample_document.chunks():
#                 f.write(chunk)
#         Z = zipfile.ZipFile(destination,'r',zipfile.ZIP_DEFLATED)
#         path = f'./static/sample_document/{project_id}'
#         num = 0
#         for i in Z.namelist():
#             num += 1
#             try:
#                 new_name = i.encode('cp437').decode('gbk')
#             except:
#                 new_name = i.encode('cp437').decode('utf-8')
#             Z.extract(i,path=path)
#             os.rename(path+f'/{i}',path+f'/{new_name}')
#         data = {'code': 200, 'msg': '写入成功'}
#     except Exception:
#         os.remove(destination)
#         data = {'code': 404, 'msg': '写入失败'}
#     return JsonResponse(data)


def write_data(request, project_id):
    global task_num
    global flag
    sample_document = request.FILES['file']
    destination = f'./static/sample_document/{project_id}/{sample_document.name}'
    if os.path.exists(destination):
        os.remove(destination)
    z = zipfile.ZipFile(destination,'w',zipfile.ZIP_DEFLATED)
    z.close()
    with open(destination,'wb') as f:
        for chunk in sample_document.chunks():
            f.write(chunk)
    Z = zipfile.ZipFile(destination,'r',zipfile.ZIP_DEFLATED)
    path = f'./static/sample_document/{project_id}'
    num = 0
    for i in Z.namelist():
        try:
            new_name = i.encode('cp437').decode('gbk')
        except:
            new_name = i.encode('cp437').decode('utf-8')
        type = new_name.split('.')[-1]
        if flag == 0:
            if type not in ['jpg','jpeg','png']:
                continue
            num += 1
            Z.extract(i, path=path)
            os.rename(path + f'/{i}', path + f'/{num}.{type}')
        else:
            num += 1
            Z.extract(i,path=path)
            os.rename(path+f'/{i}',path+f'/{num}.{type}')
    Z.close()
    #图片画框任务
    if flag == 0:
        task_should = math.floor(num/task_num)
        if task_should < 10:
            p = Project.objects.get(project_id=project_id)
            p.project_status = 6
            data = {'code':404, 'msg':'无法分配任务','path':path}
            shutil.rmtree(path)
        else:
            for i in os.listdir(path):
                try:
                    type = i.split('.')[1]
                    if type not in ['jpg','jpeg','png']:
                        continue
                    num = int(i.split('.')[0])
                    id = math.ceil(num/task_should)
                    if id >task_num:
                        id = task_num
                    os.rename(path + f'/{i}', path + f'/{num}_{id}.{type}')
                except:
                    pass
            pic = ''
            for i in os.listdir(path):
                try:
                    type = i.split('.')[1]
                    if type not in ['jpg','jpeg','png']:
                        continue
                    pic = i
                    break
                except:
                    pass
            p = Project.objects.get(project_id=project_id)
            p.project_pic = (path+f'/{pic}')[1:]
            p.item_per_task = task_should
            p.save()
            data = {'code': 200, 'msg': '写入成功'}
    #文本任务
    if flag == 1:
        p = Project.objects.get(project_id=project_id)
        p.project_pic = f'/static/sample_document/txt_pic/txt_defalut_pic.png'
        task_num = p.task_num
        n = 0
        try:
            with open(f'{path}/total.txt','w',encoding='gb18030') as fp:
                for i in range(1,num+1):
                    with open(f'{path}/{i}.txt','r',encoding='gb18030') as f:
                        for line in f:
                            n += 1
                            fp.write(line)
        except:
            with open(f'{path}/total.txt','w',encoding='gb18030') as fp:
                for i in range(1,num+1):
                    with open(f'{path}/{i}.txt','r',encoding='gbk') as f:
                        for line in f:
                            n += 1
                            fp.write(line)
        task_should = math.floor(n/task_num)
        p.item_per_task = task_should
        p.save()
        data = {'code': 200, 'msg': '写入成功'}
    return JsonResponse(data)


## TODO 预付款
def prepay(request,project_id):
    res = get_res(request)
    pay_per_task = float(res['pay_per_task'])
    task_num = int(res['task_num'])
    account_id = res['publisher_id']
    total = pay_per_task * task_num
    w = Wallet.objects.get(account_id=account_id)
    if w.account_num >= total:
        w.account_num -= total
        w.save()
        p = Prepay()
        p.prepay_amount = total
        p.prepay_balance = total
        p.project_id = project_id
        p.account_id = account_id
        p.save()
        data = {'code': 200}
    else:
        data = {'code':404}
    return data


## TODO 标注者取消任务
def give_up_task(request):
    res = get_res(request)
    account_id = request.session['user']['account_id']
    task_id = res['task_id']
    ta = Task_association.objects.filter(Q(account_id=account_id)|Q(task_id=task_id))
    ta.delete()
    t = Task.objects.get(task_id=task_id)
    t.task_status = 0
    t.save()
    return JsonResponse({'code': 200})


## TODO 标注者提交任务
def commit_task(request):
    res = get_res(request)
    processed_data = request.FILES['processed_data']
    task_id = res['task_id']
    type = processed_data.name.split('.').pop()
    project_id = task_id.split('.')[0]
    write_data(processed_data,task_id+'.'+type,project_id)
    t = Task.objects.get(task_id=task_id)
    t.task_status = 2
    t.save()
    return JsonResponse({'code': 200})


## TODO task提交成功后付款与升级
def completed_task(request):
    res = get_res(request)
    task_id = res['task_id']
    project_id = task_id.split('_')[0]
    t = Task.objects.get(task_id=task_id)
    ta = Task_association.objects.get(task_id=task_id)
    account_id = ta.account_id
    c = Consumer.objects.get(account_id=account_id)
    p = Project.objects.get(project_id=project_id)
    pre = Prepay.objects.get(project_id=project_id)
    w = Wallet.objects.get(account_id=account_id)
    r = Reward_record()
    web = Web_account()
    web.task_id = task_id
    t.task_status = 3
    t.save()
    r.reward_amount = p.payment_per_task
    r.ta_id = ta.ta_id
    r.reward_time = datetime.datetime.now()
    r.save()
    pre.prepay_balance -= p.payment_per_task
    pre.save()
    t.completed_task_num += 1
    t.save()
    w.account_num += float(p.payment_per_task)*0.8
    web.PAF_time = datetime.datetime.now()
    web.PAF_amount = float(p.payment_per_task)*0.2
    web.PAF_type = p.project_type
    web.PAF_balance += web.PAF_amount
    web.save()
    w.save()
    c.experience += t.score
    c.level = judge_level(c.experience)
    c.save()
    if p.task_num == p.completed_task_num:
        p.project_status = 2
        p.save()