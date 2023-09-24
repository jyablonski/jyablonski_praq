# K8s Install
[Tutorial](https://www.youtube.com/watch?v=X48VuDVv0do)
Left off at 1:02:00

## Minikube

``` sh
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install minikube-linux-amd64 /usr/local/bin/minikube

kubectl version
```

Start the Cluster
```
minikube start
minikube status
```

## Kubectl

``` sh
kubectl get nodes
kubectl get services
kubectl create -h

kubectl create deployment nginx-depl --image=nginx
> deployment.apps/nginx-depl created

kubectl get pod
> NAME                          READY   STATUS    RESTARTS   AGE
> nginx-depl-6b7698588c-6vxjb   1/1     Running   0          6m29s

kubectl get replicaset
> NAME                    DESIRED   CURRENT   READY   AGE
> nginx-depl-6b7698588c   1         1         1       6m56s

# manually edit the deployment file
kubectl edit deployment nginx-depl

# get logs from a pod
kubectl logs nginx-depl-6b7698588c-6vxjb

kubectl get pod

# see metadata about a pod like when it was created, what container image it pulled, when it pulled it, when it started it etc.
kubectl describe pod nginx-depl-6b7698588c-6vxjb

kubectl exec -it nginx-depl-6b7698588c-6vxjb bash

kubectl get deployment

kubectl delete deployment nginx-depl

kubectl get secret

kubectl top

kubectl apply -f mongo-secret.yaml
kubectl apply -f mongo-configmap.yaml
kubectl apply -f mongo-express.yaml

kubectl describe service mongo-express-service

kubectl get pod -o wide

kubectl delete service mongo-express-service

kubectl delete pods --all --all-namespaces

kubectl delete deployment mongo-express
```