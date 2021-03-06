from django.db import models

# Create your models here.

class Task(models.Model):
    task_id = models.CharField(max_length=25,primary_key=True)
    project_id = models.CharField(max_length=25)
    task_status = models.CharField(max_length=20)#0表示未接收，1表示已接收，2表示提交审核，3表示任务通过，4表示审核未通过,10管理员审核中
    # original_data = models.FileField(upload_to='data')
    # processed_data = models.FileField(upload_to='data')
    score = models.IntegerField()
    due_time = models.DateTimeField()

    def to_dict(self):
        data = {'project_id':self.project_id,
                'task_id':self.task_id,
                'score':self.score,
                'due_time': self.due_time
                }
        return data


class Project(models.Model):
    project_id = models.CharField(max_length=25,primary_key=True)
    # prepay_id = models.CharField(max_length=25)
    account_id = models.CharField(max_length=25)
    project_name = models.CharField(max_length=64)
    project_type = models.CharField(max_length=20)
    description = models.CharField(max_length=1024)
    # sample_document = models.FileField(upload_to='sample_document')
    start_time = models.DateTimeField(null=True)
    due_time = models.DateTimeField()
    payment_per_task = models.FloatField()
    project_status = models.IntegerField()#0表示未开始,1表示已经开始,2代表完全领取,5表示已结束,6为发布失败,10是暂停
    item_per_task = models.IntegerField(null=True)
    task_num = models.IntegerField()
    completed_task_num = models.IntegerField()
    project_star = models.FloatField()
    project_pic = models.CharField(max_length=64,null=True)
    project_target = models.CharField(max_length=64, null=True)



    def to_dict(self):
        data = {'project_id':self.project_id,
                'description':self.description,
                'project_name':self.project_name,
                'project_type':self.project_type,
                'due_time':self.due_time,
                'payment_per_task':self.payment_per_task,
                'task_num':self.task_num,
                'project_star':self.project_star,
                'account_id':self.account_id,
                'completed_task_num':self.completed_task_num
                # 'sample_document':self.sample_document
                }
        return data


class Prepay(models.Model):#数据库修改
    project_id = models.CharField(max_length=25)
    prepay_amount = models.FloatField()
    prepay_balance = models.FloatField()
    account_id = models.CharField(max_length=25)




class Reward_record(models.Model):#数据库修改
    task_id = models.CharField(max_length=25)
    reward_amount = models.FloatField()
    reward_time = models.DateTimeField()



class Web_account(models.Model):
    task_id = models.CharField(max_length=25)
    PAF_type = models.CharField(max_length=10)
    PAF_amount = models.FloatField()
    PAF_balance = models.FloatField()
    PAF_time = models.DateTimeField()


class Task_association(models.Model):#数据库修改
    account_id = models.CharField(max_length=25)
    task_id = models.CharField(max_length=25)
    project_id = models.CharField(max_length=25)


# 项目id库
class project_id_pool(models.Model):
    project_id = models.CharField(max_length=20,primary_key=True)


class task_error(models.Model):
    task_id = models.CharField(max_length=20)
    error = models.CharField(max_length=200)
    error_value = models.CharField(max_length=200)