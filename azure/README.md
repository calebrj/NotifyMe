# command lines  
docker buildx build -f dockerfile.forest --platform linux/amd64 -t capstonenotifyme.azurecr.io/model_forest_fastapi-image:latest . --push 
docker buildx build -f dockerfile.cnn --platform linux/amd64 -t capstonenotifyme.azurecr.io/model_cnn_fastapi-image:latest . --push 

docker buildx build -f dockerfile.route --platform linux/amd64 -t capstonenotifyme.azurecr.io/route_fastapi-image:latest . --push 

docker buildx build -f dockerfile.server --platform linux/amd64 -t capstonenotifyme.azurecr.io/server_fastapi-image:latest . --push 

docker buildx build -f dockerfile --platform linux/amd64 -t capstonenotifyme.azurecr.io/frontend-image:latest . --push 


kubectl create secret generic node-env-secret --from-env-file=.env

kubectl apply -f apiservers.yaml

az aks list -o table

az aks get-credentials --resource-group capstone --name capstoneBackend

kubectl get svc

kubectl rollout restart deployment node-gateway


Ingress
    - kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.9.4/deploy/static/provider/cloud/deploy.yaml
    - kubectl get svc -n ingress-nginx
Cert Manager 
    - kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.14.3/cert-manager.yaml
Cluster-Issuer
    - 


kubectl rollout restart deployment fastapi-model-deployment
