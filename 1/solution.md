### Pod

Во всех командах `kubectl` опущен флаг `-n <namespace>`.
Используйте его, чтобы выполнить команду в своём namespace.

Можно задать неймспейс по умолчанию, выполнив команду (заменив `<namespace>` на свой namespace):
```bash
kubectl config set-context --current --namespace=<namespace>
```

**1. Создаем Pod**

Для этого выполним команду:
```bash
kubectl apply -f pod.yml
```
Проверим результат, для чего выполним команду:
```bash
kubectl get pod
```
Результат должен быть примерно следующим:
```bash
NAME      READY     STATUS              RESTARTS   AGE
my-pod    0/1       ContainerCreating   0          2s
```
Через какое-то время Pod должен перейти в состояние `Running`
и вывод команды `kubectl get po` станет таким:
```bash
NAME      READY     STATUS    RESTARTS   AGE
my-pod    1/1       Running   0          59s
```

*Результат:*

![alt text](<jpgs/1_Pod/1.png>)

**2. Скейлим приложение**

Открываем файл pod.yaml на редактирование:
```bash
vim pod.yml
```
И заменяем там строку:
```diff
-  name: my-pod
+  name: my-pod-1
```
Сохраняем и выходим. Для vim нужно нажать `:wq<Enter>`

Применяем изменения, для этого выполним команду:
```bash
kubectl apply -f pod.yml
```
Проверяем результат, для этого выполним команду:
```bash
kubectl get pod
```
Результат должен быть примерно следующим:
```bash
NAME      READY     STATUS    RESTARTS   AGE
my-pod    1/1       Running   0          10m
my-pod-1  1/1       Running   0          59s
```

*Результат:*

![alt text](<jpgs/1_Pod/2.png>)

**3. Обновляем версию Image**

Обновляем версию image в Pod `my-pod`, для этого выполним команду:
```bash
kubectl edit pod my-pod
```
И заменяем там строку:
```diff
-  - image: nginx:1.12
+  - image: nginx:1.13
```
Проверяем результат, для этого выполним команду:
```bash
kubectl describe pod my-pod
```

В результате должны присутствовать строки:
```bash
Containers:
  nginx:
    Container ID:
    Image:          nginx:1.13
```

*Результат:*

![alt text](<jpgs/1_Pod/3.png>)

**4. Удаляем все созданные поды**
```bash
kubectl delete pods --all
```

Проверяем, что все поды удалены
```bash
kubectl get pod
```

*Результат:*

![alt text](<jpgs/1_Pod/4.png>)

### ReplicaSet

**1. Создаем Replicaset**

Для этого выполним команду:
```bash
kubectl apply -f replicaset.yml
```
Проверим результат, для этого выполним команду:
```bash
kubectl get pod
```
Результат должен быть примерно следующим:
```bash
NAME                  READY     STATUS              RESTARTS   AGE
my-replicaset-pbtdm   0/1       ContainerCreating   0          2s
my-replicaset-z7rwm   0/1       ContainerCreating   0          2s
```

*Результат:*

![alt text](<jpgs/2_ReplicaSet/1.png>)

**2. Скейлим Replicaset**

Для этого выполним команду:
```bash
kubectl scale replicaset my-replicaset --replicas 3
```
Проверим результат, для этого выполним команду:
```bash
kubectl get pod
```
Результат должен быть примерно следующим:
```bash
NAME                  READY     STATUS              RESTARTS   AGE
my-replicaset-pbtdm   1/1       Running             0          2m
my-replicaset-szqgz   0/1       ContainerCreating   0          1s
my-replicaset-z7rwm   1/1       Running             0          2m
```

*Результат:*

![alt text](<jpgs/2_ReplicaSet/2.png>)

**3. Удаляем один из Pod**

Для этого выполним команду подставив имя своего Pod(``можно воспользоваться автоподстановкой по TAB``):
```bash
kubectl delete pod my-replicaset-pbtdm
```
Проверим результат, для этого выполним команду:
```bash
kubectl get pod
```
Результат должен быть примерно следующим:
```bash
NAME                  READY     STATUS              RESTARTS   AGE
my-replicaset-55qdj   0/1       ContainerCreating   0          1s
my-replicaset-pbtdm   1/1       Running             0          4m
my-replicaset-szqgz   1/1       Running             0          2m
my-replicaset-z7rwm   0/1       Terminating         0          4m
```

*Результат:*

![alt text](<jpgs/2_ReplicaSet/3.png>)

**4. Добавляем в Replicaset лишний Pod**

Открываем файл `pod.yml`
И в него после metadata: на следующей строке добавляем
```yaml
  labels:
    app: my-app
```
В итоге должно получиться:
```yaml
.............
kind: Pod
metadata:
  name: my-pod
  labels:
    app: my-app
spec:
.............
```
Создаем дополнительный Pod, для этого выполним команду:
```bash
kubectl apply -f pod.yml
```
Проверяем результат, для этого выполним команду:
```bash
kubectl get pod
```
Результат должен быть примерно следующим:
```bash
NAME                  READY     STATUS        RESTARTS   AGE
my-pod                0/1       Terminating   0          1s
my-replicaset-55qdj   1/1       Running       0          3m
my-replicaset-pbtdm   1/1       Running       0          8m
my-replicaset-szqgz   1/1       Running       0          6m
```

*Результат:*

![alt text](<jpgs/2_ReplicaSet/4.png>)

**5. Обновляем версию Image для container**

Для этого выполним команду:
```bash
kubectl set image replicaset my-replicaset nginx=nginx:1.13
```
Проверяем результат, для этого выполним команду:
```bash
kubectl get pod
```
Результат должен быть примерно следующим:
```bash
NAME                  READY     STATUS        RESTARTS   AGE
my-replicaset-55qdj   1/1       Running       0          3m
my-replicaset-pbtdm   1/1       Running       0          8m
my-replicaset-szqgz   1/1       Running       0          6m
```
И проверяем сам Replicaset, для чего выполним команду:
```bash
kubectl describe replicaset my-replicaset
```
В результате находим строку Image и видим:
```bash
  Containers:
   nginx:
    Image:        nginx:1.13
```

*Результат:*

![alt text](<jpgs/2_ReplicaSet/5.png>)

Проверяем версию image в pod. Для этого выполним команду, подставив имя своего Pod(``можно воспользоваться автоподстановкой по TAB``):
```bash
kubectl describe pod my-replicaset-55qdj
```
Видим что версия имаджа в поде не изменилась:
```bash
  Containers:
   nginx:
    Image:        nginx:1.12
```

*Результат:*

![alt text](<jpgs/2_ReplicaSet/6.png>)

Помогаем поду, для этого выполним команду, подставив имя своего Pod(``можно воспользоваться автоподстановкой по TAB``):
```bash
kubectl delete po my-replicaset-55qdj
```
Проверяем результат, для этого выполним команду:
```bash
kubectl get pod
```
Результат должен быть примерно следующим:
```bash
NAME                  READY     STATUS              RESTARTS   AGE
my-replicaset-55qdj   0/1       Terminating         0          11m
my-replicaset-cwjlf   0/1       ContainerCreating   0          1s
my-replicaset-pbtdm   1/1       Running             0          16m
my-replicaset-szqgz   1/1       Running             0          14m
```
Проверяем версию Image в новом Pod. Для этого выполним команду, подставив имя своего Pod:
```bash
kubectl describe pod my-replicaset-cwjlf
```
Результат должен быть примерно следующим:
```bash
    Image:          nginx:1.13
```

*Результат:*

![alt text](<jpgs/2_ReplicaSet/7.png>)

**6. Удаляем Replicaset**

```bash
kubectl delete replicaset my-replicaset
```

*Результат:*

![alt text](<jpgs/2_ReplicaSet/8.png>)

### Deployment

1) Создаем deployment

Для этого выполним команду:
```bash
kubectl apply -f deployment.yml
```

2) Проверка результата

Проверяем список pods, для этого выполним команду:
```bash
kubectl get pod
```
Результат должен быть примерно таким:
```bash
NAME                             READY     STATUS              RESTARTS   AGE
my-deployment-7c768c95c4-47jxz   0/1       ContainerCreating   0          2s
my-deployment-7c768c95c4-lx9bm   0/1       ContainerCreating   0          2s
```

Проверяем список replicaset, для этого выполним команду:
```bash
kubectl get replicaset
```
Результат должен быть примерно таким:
```bash
NAME                       DESIRED   CURRENT   READY     AGE
my-deployment-7c768c95c4   2         2         2         1m
```

*Результат:*

![alt text](<jpgs/3_Deployment/1.png>)

3) Обновляем версию image

Обновляем версию image для container в deployment my-deployment. Для этого выполним команду:

```bash
kubectl set image deployment my-deployment nginx=nginx:1.13
```
Проверяем результат, для этого выполним команду:
```bash
kubectl get pod
```
Результат должен быть примерно таким:
```bash
NAME                             READY     STATUS              RESTARTS   AGE
my-deployment-685879478f-7t6ws   0/1       ContainerCreating   0          1s
my-deployment-685879478f-gw7sq   0/1       ContainerCreating   0          1s
my-deployment-7c768c95c4-47jxz   0/1       Terminating         0          5m
my-deployment-7c768c95c4-lx9bm   1/1       Running             0          5m
```
И через какое-то время вывод этой команды станет:
```bash
NAME                             READY     STATUS    RESTARTS   AGE
my-deployment-685879478f-7t6ws   1/1       Running   0          33s
my-deployment-685879478f-gw7sq   1/1       Running   0          33s
```

*Результат:*

![alt text](<jpgs/3_Deployment/2.png>)

Проверяем что в новых pod новый image. Для этого выполним команду, заменив имя pod на имя вашего pod(``можно воспользоваться автоподстановкой по TAB``):
```bash
kubectl describe pod my-deployment-685879478f-7t6ws
```
Результат должен быть примерно таким:
```bash
    Image:          nginx:1.13
```

*Результат:*

![alt text](<jpgs/3_Deployment/3.png>)

Проверяем что стало с replicaset, для этого выполним команду:
```bash
kubectl get replicaset
```
Результат должен быть примерно таким:
```bash
NAME                       DESIRED   CURRENT   READY     AGE
my-deployment-685879478f   2         2         2         2m
my-deployment-7c768c95c4   0         0         0         7m
```

*Результат:*

![alt text](<jpgs/3_Deployment/4.png>)

4) Удаляем наш deployment
```bash
kubectl delete deployment my-deployment
```
Проверяем, что deployment, replicaset'ы и pod'ы удалились
```bash
kubectl get deployment,replicaset,pod
```

*Результат:*

![alt text](<jpgs/3_Deployment/5.png>)

# DaemonSet

1) Создаем демонсет

```bash
kubectl apply -f daemonset.yml
```

В ответ должны увидеть

```bash
daemonset.apps/node-exporter created
```

*Результат:*

![alt text](<jpgs/4_DaemonSet/1.png>)

2) Смотрим на поды

```bash
kubectl get pod -o wide
```

Видим
```bash
NAME                             READY   STATUS    RESTARTS   AGE   IP          NODE
node-exporter-2ch5q              1/1     Running   0          18s   10.128.0.6  node-1
node-exporter-r984x              1/1     Running   0          18s   10.128.0.38 node-2
node-exporter-t4x4s              1/1     Running   0          18s   10.128.0.9  node-3
```

3) Удаляем daemonset
```bash
kubectl delete -f daemonset.yml
```

*Результат:*

![alt text](<jpgs/4_DaemonSet/2.png>)

# Configmap

1) Создаем configmap

Для этого выполним команду:

```bash
kubectl apply -f .
```

*Результат:*

![alt text](<jpgs/5_ConfigMap/1.png>)

2) Проверяем

Проверим, что configmap попал в контейнер, для этого пробросим порт из пода и выполним curl.
Для этого выполним команду, заменив имя pod на имя вашего pod(``можно воспользоваться автоподстановкой по TAB``).

```bash
kubectl port-forward my-deployment-5b47d48b58-l4t67 8080:80 &
curl 127.0.0.1:8080
```

В результате выполнения curl увидим имя пода, который обработал запрос. Результат должен быть примерно таким:

```bash
my-deployment-5b47d48b58-l4t67
```

*Результат:*

![alt text](<jpgs/5_ConfigMap/2.png>)

3) Удаляем созданные ресурсы

*Результат:*

![alt text](<jpgs/5_ConfigMap/3.png>)

# Secret

1) Создаем секрет

Для этого выполним команду:

```bash
kubectl create secret generic test --from-literal=test1=asdf
kubectl get secret
kubectl get secret test -o yaml
```

*Результат:*

![alt text](<jpgs/6_Secret/1.png>)

2) Применим наш деплоймент

Для этого выполним команду:

```bash
kubectl apply -f .
```

*Результат:*

![alt text](<jpgs/6_Secret/2.png>)

3) Проверяем результат

Для этого выполним команду, подставив вместо < RANDOM > нужное значение(`автоподстановка по TAB`):

```bash
kubectl describe pod my-deployment-< RANDOM >
```

Результат должен содержать:

```bash
Environment:
      TEST:    foo
      TEST_1:  <set to the key 'test1' in secret 'test'>  Optional: false
```

*Результат:*

![alt text](<jpgs/6_Secret/3.png>)

# Job

### Запускаем простой job

1) Создаем job

```bash
kubectl apply -f job.yml
```

2) Проверяем

```bash
kubectl get job
```

Видим:

```bash
NAME    STATUS    COMPLETIONS   DURATION   AGE
hello   Running   0/1           2s         2s
```

3) Смотрим на поды

```bash
kubectl get pod
```

Видим под, созданный джобой:

```bash
NAME          READY   STATUS      RESTARTS   AGE
hello-6l9tv   0/1     Completed   0          8s
```

4) Смотрим его логи

```bash
kubectl logs hello-6l9tv
```

Видим что все отработало правильно:

```bash
Mon Mar 18 15:06:10 UTC 2019
Hello from the Kubernetes cluster
```

5) Удаляем джоб

```bash
kubectl delete job hello
```

*Результат:*

![alt text](<jpgs/7_Job/1.png>)

### Проверяем работу параметра backoffLimit

6) Открываем файл job.yml и находим командy выполняющуюся в поде

```yaml
args:
  - /bin/sh
  - -c
  - date; echo Hello from the Kubernetes cluster
```

И ломаем полностью:

```yaml
args:
  - /bin/sh
  - -c
  - date; echo Hello from the Kubernetes cluster; exit 1
```

7) Создаем джоб

```bash
kubectl apply -f job.yml
```

8) Проверяем

```bash
kubectl get job
```

Видим:

```bash
NAME    STATUS    COMPLETIONS   DURATION   AGE
hello   Failed    0/1           43s        43s
```

9) Смотрим на поды

```bash
kubectl get pod
```

Видим поды, созданные джобой:

```bash
NAME          READY   STATUS   RESTARTS   AGE
hello-5nvqf   0/1     Error    0          108s
hello-ks4ks   0/1     Error    0          96s
hello-rl984   0/1     Error    0          72s
```

Они в статусе Error

10) Смотрим в описание джобы

```bash
kubectl describe job hello
```

Видим, что backoffLimit сработал

```bash
  Warning  BackoffLimitExceeded  114s   job-controller  Job has reached the specified backoff limit
```

11) Удаляем джоб

```bash
kubectl delete job hello
```

*Результат:*

![alt text](<jpgs/7_Job/2.png>)
![alt text](<jpgs/7_Job/3.png>)


### Проверяем работу параметра activeDeadlineSeconds

12) Открываем файл job.yml и находим командy, выполняющуюся в поде

```yaml
args:
  - /bin/sh
  - -c
  - date; echo Hello from the Kubernetes cluster
```

И делаем ее бесконечной

```yaml
args:
  - /bin/sh
  - -c
  - while true; do date; echo Hello from the Kubernetes cluster; sleep 1; done
```

13) Создаем джоб

```bash
kubectl apply -f job.yml
```

14) Проверяем

```bash
kubectl get job
```

Видим:

```bash
NAME    STATUS    COMPLETIONS   DURATION   AGE
hello   Running   0/1           27s        27s
```

15) Смотрим на поды

```bash
kubectl get pod
```

Видим поды, созданный джобой

```bash
NAME          READY   STATUS   RESTARTS   AGE
hello-bt6g6   1/1     Running   0          5s
```

16) Ждем минуту и проверяем джоб

```bash
kubectl describe job hello
```

Видим, что activeDeadlineSeconds сработал
```bash
  Warning  DeadlineExceeded  35s  job-controller  Job was active longer than specified deadline
```

*Результат:*

![alt text](<jpgs/7_Job/4.png>)
![alt text](<jpgs/7_Job/5.png>)

17) Удаляем джоб

```bash
kubectl delete job hello
```

*Результат:*

![alt text](<jpgs/7_Job/6.png>)

# CronJob

1) Создаем крон джоб

```bash
kubectl apply -f cronjob.yml
```

2) Проверяем

```bash
kubectl get cronjob
```

Видим:

```bash
NAME    SCHEDULE      SUSPEND   ACTIVE   LAST SCHEDULE   AGE
hello   */1 * * * *   False     0        <none>          14s
```

3) Через минуту пробуем посмотреть на джобы

```bash
kubectl get job
```

Видим созданный джоб

```bash
NAME               STATUS       COMPLETIONS   DURATION   AGE
hello-1552924260   Complete     1/1           2s         49s
```

4) Смотрим на поды

```bash
kubectl get pod
```

Видим под

```bash
NAME                     READY   STATUS      RESTARTS   AGE
hello-1552924260-gp7pk   0/1     Completed   0          80s
```

*Результат:*

![alt text](<jpgs/8_CronJob/1.png>)

5) Если мы подождем 5-10 минут, то увидим что старые джобы и поды удаляются по мере появления новых

```bash
kubectl get job,pod
```

*Результат:*

![alt text](<jpgs/8_CronJob/2.png>)

6) Удаляем крон джоб

```bash
kubectl delete -f cronjob.yaml
```

*Результат:*

![alt text](<jpgs/8_CronJob/3.png>)

# Service

Если вы удалили ресурсы, созданные в задании 6.secret, то создайте их еще раз.

1) Проверяем что лэйблы на наших подах совпадают с тем, что у нас указано в labelSelector в service.yaml

Для этого выполним команду:

```bash
kubectl get po --show-labels
```

Результат должен быть примерно следующим:

```bash
NAME                             READY     STATUS    RESTARTS   AGE       LABELS
my-deployment-5b47d48b58-dr9kk   1/1       Running   0          15s       app=my-app,pod-template-hash=1603804614
my-deployment-5b47d48b58-r95lt   1/1       Running   0          15s       app=my-app,pod-template-hash=1603804614
```

2) Создаем сервис

Для этого выполним команду:

```bash
kubectl apply -f .
```

3) Проверяем что сервис есть

Для этого выполним команду:

```bash
kubectl get service
```

Результат должен быть примерно следующим:

```bash
NAME         TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)   AGE
my-service   ClusterIP   10.100.55.123   <none>        80/TCP    2s
```

4) Смотрим, что сервис действительно увидел наши поды и собирается проксировать на них трафик

Для этого выполним команду:

```bash
kubectl get endpoints
```

Результат должен быть примерно следующим:

```
NAME         ENDPOINTS                     AGE
my-service   10.99.1.3:80,10.99.2.163:80   1m
```

5) Смотрим, что IP эндпоинтов сервиса это действительно IP наших подов

Для этого выполним команду:

```
kubectl get pod -o wide
```

Результат должен быть примерно следующим:

```bash
NAME                             READY     STATUS    RESTARTS   AGE       IP           NODE
my-deployment-5b47d48b58-dr9kk   1/1       Running   0          3m        10.99.2.163   node-1
my-deployment-5b47d48b58-r95lt   1/1       Running   0          3m        10.99.1.3     node-2
```

6) Запускаем тестовый под для проверки сервиса

Для этого выполним команду:

```bash
kubectl run -t -i --rm --image centosadmin/utils test bash
```

7) Дальше уже из этого пода выполняем

Для этого выполним команду:

```bash
curl -i my-service
```

Результат должен быть примерно следующим:

```bash
HTTP/1.1 200 OK
Server: nginx/1.12.2
Date: Fri, 19 Sep 2025 10:12:35 GMT
Content-Type: text/plain
Content-Length: 31
Connection: keep-alive

my-deployment-5b47d48b58-r95lt

```

8) Выходим из тестового пода

Для этого выполним команду:

```bash
exit
```

*Результат:*

![alt text](<jpgs/9_Service/1.png>)

9) Удаляем все созданные ресурсы

*Результат:*

![alt text](<jpgs/9_Service/2.png>)