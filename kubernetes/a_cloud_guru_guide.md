# A Cloud Guru EKS Guide

``` sh
eksctl create cluster --name dev-cluster --version 1.31 --region us-east-1 --nodegroup-name standard-workers --node-type t3.micro --nodes 3 --nodes-min 1 --nodes-max 4 --managed

aws eks update-kubeconfig --name dev-cluster --region us-east-1
# > Added new context arn:aws:eks:us-east-1:680048507123:cluster/dev-cluster to /home/jacob/.kube/config

kubectl apply -f kubernetes/guru/service.yaml

kubectl get service
# > nginx-svc    LoadBalancer   10.100.188.180   ac160ebb3190a4c2096b8456b3fd6584-1303533787.us-east-1.elb.amazonaws.com   80:31489/TCP   12s

kubectl apply -f kubernetes/guru/deployment.yaml
kubectl get deployment
kubectl get rs

eksctl delete cluster dev-cluster

# install a helm chart
helm install my-release oci://registry-1.docker.io/bitnamicharts/nginx

# install metrics api to view cpu + memory usage on your deployments
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
kubectl logs -n kube-system $(kubectl get pods -n kube-system -l k8s-app=metrics-server -o jsonpath='{.items[0].metadata.name}')
kubectl top nodes
kubectl api-resources | grep metrics

# After making any changes to the Metrics Server deployment, restart it to apply the changes:
kubectl rollout restart deployment metrics-server -n kube-system

kubectl apply -f kubernetes/guru/cron_job.yaml
kubectl get cronjobs
kubectl get jobs

kubectl get pods --show-labels

```