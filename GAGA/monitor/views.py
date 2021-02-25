from django.shortcuts import render
from rest_framework import views
from rest_framework.response import Response
from redis import Redis
from rq import Queue
from rq.registry import ScheduledJobRegistry
from rq.job import Job

# Create your views here.


class MonitorQueueAPIView(views.APIView):

  def __init__(self):
    self.redis = Redis()
    self.queue = Queue(connection=self.redis)
    self.registry = ScheduledJobRegistry(queue=self.queue)

  def get(self, request, format=None):
    job_ids = self.registry.get_job_ids()

    jobs_info = map(self.get_job_information, job_ids)

    return Response({
      "message": "Scheduled Comment Rounds",
      "scheduled_rounds_info": jobs_info,
    })

  def get_job_information(self, job_id):
    job = Job.fetch(job_id, connection=self.redis)
    job_scheduled_time = self.registry.get_scheduled_time(job_id)
    return {
      "comment_round_args": job.args,
      "function": job.func_name,
      "comment_round_is_scheduled": job.is_scheduled,
      "comment__scheduled_at": job_scheduled_time,
    }