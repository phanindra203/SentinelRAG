# Azure Kubernetes Service (AKS)

Azure Kubernetes Service (AKS) is a managed Kubernetes service provided by Microsoft Azure. AKS simplifies the deployment, management, and scaling of Kubernetes clusters in Azure.

## AKS Architecture

An AKS cluster consists of a managed control plane and one or more node pools. The control plane manages Kubernetes resources and scheduling, while worker nodes provide the compute capacity for running application workloads.

## Node Pools

A node pool is a group of Kubernetes nodes with the same configuration. AKS clusters can use multiple node pools to run different types of workloads and can scale node pools according to application requirements.

## Pods

A Pod is the smallest deployable unit in Kubernetes. Applications running on AKS execute inside Pods, which run on nodes in the cluster.

## Deployments

A Kubernetes Deployment manages replicated Pods and maintains the desired number of running application instances. Deployments can also be used to perform controlled updates to applications.

## Services

A Kubernetes Service provides a stable network endpoint for applications running inside Pods. AKS supports different Kubernetes Service types, including ClusterIP, NodePort, and LoadBalancer.

## Azure LoadBalancer

When an AKS application uses a Service of type LoadBalancer, Azure can provision an Azure Load Balancer and provide an external IP address for accessing the application.

## Azure Container Registry Integration

AKS can integrate with Azure Container Registry (ACR) to pull container images used by Kubernetes workloads. The AKS cluster identity can be granted permission to access the ACR repository.

## Managed Identity

AKS can use Azure managed identities to authenticate to Azure resources without storing passwords or long-lived credentials in application configuration.

## Scaling

AKS supports scaling workloads by increasing or decreasing the number of Pod replicas. Node pools can also be scaled to provide additional compute capacity for workloads.

## Monitoring

AKS workloads can be monitored using Azure Monitor, Log Analytics, and other Kubernetes observability tools. Monitoring helps identify application failures, resource usage, and cluster health issues.

## Security

AKS security can include Azure role-based access control (RBAC), Kubernetes RBAC, managed identities, network security controls, and integration with Azure Key Vault for managing sensitive configuration.

## Common AKS Troubleshooting

Common AKS workload problems include ImagePullBackOff, ErrImagePull, CrashLoopBackOff, Pods remaining Pending, and application connectivity problems. Troubleshooting normally involves checking Pod status, Pod events, container logs, deployments, services, networking configuration, and container registry access.

## AKS and Kubernetes

AKS uses Kubernetes concepts such as Pods, Deployments, Services, namespaces, and node pools. The main advantage of AKS is that Azure manages significant portions of the Kubernetes control-plane infrastructure while users focus on deploying and operating workloads.
