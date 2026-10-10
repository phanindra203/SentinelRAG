# Terraform Remote State

Terraform uses a state file to track the infrastructure resources
managed by Terraform.

A remote backend stores the Terraform state outside the local
developer machine.

Azure Blob Storage can be used as a Terraform remote backend.
This allows multiple engineers and CI/CD pipelines to work with
the same Terraform state.

Remote state provides centralized state management and supports
state locking. The state file can contain sensitive infrastructure
information, so access to the storage account should be restricted
using appropriate Azure permissions.

A typical Terraform workflow is:

terraform init
terraform validate
terraform plan
terraform apply
