# infras. for keyword-imageurl-crawler

## Prequsites
- k8s cluster
- helm v3

## postgresql
### installation or upgrade
```bash
kubectl create ns postgresql
cd postgresql
kubectl apply -f pvc.yaml -n postgresql
cd helm
helm install postgres bitnami/postgresql -f values.yaml -n postgresql
# or upgrade
heml upgrade postgres bitnami/postgresql -f values.yaml -n postgresql
```
### connect?
- how to access to postgresql
    ```bash
    # under pgmlops-01 context, and do port-forwarding
    > kubectl port-forward --namespace postgresql svc/postgres-postgresql 5432:5432
    Forwarding from 127.0.0.1:5432 -> 5432
    Forwarding from [::1]:5432 -> 5432
    ```
- connection string : postgresql://smartagent:[비밀번호]@10.10.5.13:31655/smartagent
- FQDN in pgmlops-01 cluster : postgres-postgresql.postgresql.svc.cluster.local
- database: smartagent
- username: smartagent
- password: 
    ```bash
    echo $(kubectl get secret --namespace postgresql postgres-postgresql -o jsonpath="{.data.password}" | base64 -d)
    ```
- schema: public
