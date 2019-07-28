from __future__ import print_function

from datetime import datetime, timedelta

from airflow import models
from airflow.operators import bash_operator
from airflow.operators import python_operator
from airflow.contrib.kubernetes import pod
from airflow.contrib.kubernetes import secret
from airflow.models import Variable
from airflow.contrib.operators import kubernetes_pod_operator

affinity_values={
        'nodeAffinity': {
            # requiredDuringSchedulingIgnoredDuringExecution means in order
            # for a pod to be scheduled on a node, the node must have the
            # specified labels. However, if labels on a node change at
            # runtime such that the affinity rules on a pod are no longer
            # met, the pod will still continue to run on the node.
            'requiredDuringSchedulingIgnoredDuringExecution': {
                'nodeSelectorTerms': [{
                    'matchExpressions': [{
                        # When nodepools are created in Google Kubernetes
                        # Engine, the nodes inside of that nodepool are
                        # automatically assigned the label
                        # 'cloud.google.com/gke-nodepool' with the value of
                        # the nodepool's name.
                        'key': 'cloud.google.com/gke-nodepool',
                        'operator': 'In',
                        # The label key's value that pods can be scheduled
                        # on.
                        'values': [
                            'pool-1',
                        ]
                    }]
                }]
            }
        }
    }


secret_env = secret.Secret(
    # Expose the secret as environment variable.
    deploy_type='env',
    # The name of the environment variable, since deploy_type is `env` rather
    # than `volume`.
    deploy_target='SQL_CONN',
    # Name of the Kubernetes Secret
    secret='air-sec',
    # Key of a secret stored in this Secret object
    key='sql_alchemy_conn')


default_dag_args = {
    'start_date': datetime(2018, 1, 1),
    'depends_on_past': False,
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
    'project_id': Variable.get('gcp_project')
    # The start_date describes when a DAG is valid / can be run. Set this to a
    # fixed point in time rather than dynamically, since it is evaluated every
    # time a DAG is parsed. See:
    # https://airflow.apache.org/faq.html#what-s-the-deal-with-start-date

}

# Define a DAG (directed acyclic graph) of tasks.
# Any task you create within the context manager is automatically added to the
# DAG object.
with models.DAG(
        'node_scale_down_3',
        catchup=False,
        schedule_interval='*/1 * * * *',
        default_args=default_dag_args) as dag:

    pod_res = pod.Resources(request_memory='10Mi',request_cpu='10m',limit_memory='15Mi',limit_cpu='15m')
    # setattr(pod_res, 'request_memory', '1Mi')
    # setattr(pod_res, 'request_cpu', None)
    # setattr(pod_res, 'limit_cpu', None)
    # An instance of an operator is called a task. In this case, the
    # hello_python task calls the "greeting" Python function.
    scale_down = kubernetes_pod_operator.KubernetesPodOperator(
        # The ID specified for the task.
        task_id='node-scale_down',
        # Name of task you want to run, used to generate Pod ID.
        name='scale-down',
        # resources=pod_res,
        # Entrypoint of the container, if not specified the Docker container's
        # entrypoint is used. The cmds parameter is templated.
        cmds=["echo", "I am here to scale down"],
        resources=pod_res,
        # The namespace to run within Kubernetes, default namespace is
        # `default`. There is the potential for the resource starvation of
        # Airflow workers and scheduler within the Cloud Composer environment,
        # the recommended solution is to increase the amount of nodes in order
        # to satisfy the computing requirements. Alternatively, launching pods
        # into a custom namespace will stop fighting over resources.
        namespace='bs4-app',
        is_delete_operator_pod=True,
        affinity=affinity_values,
        config_file='/home/airflow/composer_kube_config',
        # Docker image specified. Defaults to hub.docker.com, but any fully
        # qualified URLs will point to a custom repository. Supports private
        # gcr.io images if the Composer Environment is under the same
        # project-id as the gcr.io images.
        image='alpine:latest')



    scale_down
