
data "azurerm_resource_group" "sentinelrag" {
  name = var.resource_group_name
}

data "azurerm_client_config" "current" {}

output "resource_group_name" {
  description = "Existing SentinelRAG resource group"
  value       = data.azurerm_resource_group.sentinelrag.name
}

output "resource_group_location" {
  description = "Azure region of the existing resource group"
  value       = data.azurerm_resource_group.sentinelrag.location
}

resource "azurerm_container_registry" "sentinelrag" {
  name                = "sentinelragacr"
  resource_group_name = data.azurerm_resource_group.sentinelrag.name
  location            = data.azurerm_resource_group.sentinelrag.location
  sku                 = "Basic"
  admin_enabled       = false
}

resource "azurerm_search_service" "sentinelrag" {
  name                        = "search-sentinelrag-dev"
  resource_group_name         = data.azurerm_resource_group.sentinelrag.name
  location                    = "Central India"
  sku                         = "free"
  authentication_failure_mode = "http401WithBearerChallenge"
  semantic_search_sku         = "free"
}

resource "azurerm_key_vault" "sentinelrag" {
  name                       = "kv-sentinelrag-dev-01"
  resource_group_name        = data.azurerm_resource_group.sentinelrag.name
  location                   = data.azurerm_resource_group.sentinelrag.location
  tenant_id                  = data.azurerm_client_config.current.tenant_id
  sku_name                   = "standard"
  rbac_authorization_enabled = true
  soft_delete_retention_days = 90
  purge_protection_enabled   = false
}
