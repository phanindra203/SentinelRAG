variable "subscription_id" {
  description = "Azure subscription ID"
  type        = string
}

variable "resource_group_name" {
  description = "Existing SentinelRAG resource group"
  type        = string
  default     = "rg-sentinelrag-dev"
}

variable "location" {
  description = "Azure region for SentinelRAG resources"
  type        = string
  default     = "centralindia"
}
