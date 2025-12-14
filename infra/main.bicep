param location string = resourceGroup().location
param environmentName string
param principalId string = ''

var abbrs = {
  appServicePlan: 'asp-'
  appService: 'app-'
  keyVault: 'kv-'
  mySqlServer: 'mysql-'
  mySqlDatabase: 'sqldb-'
  logAnalyticsWorkspace: 'log-'
  applicationInsights: 'appi-'
  userAssignedIdentity: 'uai-'
  storageAccount: 'st'
}

var resourceToken = uniqueString(subscription().id, resourceGroup().id, location)
var tags = {
  'az-cli-env': environmentName
  'app-name': 'smartquiz'
}

// User Assigned Identity for secure authentication
resource userAssignedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: '${abbrs.userAssignedIdentity}${resourceToken}'
  location: location
  tags: tags
}

// Log Analytics Workspace
resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2021-12-01-preview' = {
  name: '${abbrs.logAnalyticsWorkspace}${resourceToken}'
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
    workspaceCapping: {
      dailyQuotaGb: 1
    }
  }
  tags: tags
}

// Application Insights
resource applicationInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: '${abbrs.applicationInsights}${resourceToken}'
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    RetentionInDays: 30
    WorkspaceResourceId: logAnalyticsWorkspace.id
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
  }
  tags: tags
}

// Key Vault for storing secrets
resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: '${abbrs.keyVault}${resourceToken}'
  location: location
  properties: {
    enabledForDeployment: true
    enabledForTemplateDeployment: true
    enabledForDiskEncryption: false
    tenantId: subscription().tenantId
    sku: {
      family: 'A'
      name: 'standard'
    }
    accessPolicies: [
      {
        tenantId: subscription().tenantId
        objectId: userAssignedIdentity.properties.principalId
        permissions: {
          secrets: ['get', 'list']
        }
      }
    ]
  }
  tags: tags
}

// MySQL Server
resource mySqlServer 'Microsoft.DBforMySQL/flexibleServers@2023-12-30' = {
  name: '${abbrs.mySqlServer}${resourceToken}'
  location: location
  sku: {
    name: 'Standard_B2s'
    tier: 'Burstable'
  }
  properties: {
    administratorLogin: 'smartquizadmin'
    administratorLoginPassword: 'Admin@123!Temp'
    version: '8.0.21'
    storage: {
      storageSizeGB: 20
    }
    backup: {
      backupRetentionDays: 7
      geoRedundantBackup: 'Disabled'
    }
    network: {
      delegatedSubnetResourceId: ''
      privateDnsZoneResourceId: ''
    }
    highAvailability: {
      mode: 'Disabled'
    }
    maintenanceWindow: {
      customWindow: 'Disabled'
      startHour: 0
      startMinute: 0
      dayOfWeek: 0
    }
  }
  tags: tags
}

// MySQL Database
resource mySqlDatabase 'Microsoft.DBforMySQL/flexibleServers/databases@2023-12-30' = {
  parent: mySqlServer
  name: 'smartquiz'
  properties: {
    charset: 'utf8mb4'
    collation: 'utf8mb4_unicode_ci'
  }
}

// MySQL Firewall Rule - Allow all Azure services
resource mySqlFirewallRule 'Microsoft.DBforMySQL/flexibleServers/firewallRules@2023-12-30' = {
  parent: mySqlServer
  name: 'AllowAzureServices'
  properties: {
    startIpAddress: '0.0.0.0'
    endIpAddress: '0.0.0.0'
  }
}

// Store MySQL connection string in Key Vault
resource mysqlConnectionStringSecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  parent: keyVault
  name: 'DbConnectionString'
  properties: {
    value: 'Server=${mySqlServer.properties.fullyQualifiedDomainName};Database=smartquiz;User=smartquizadmin;Password=Admin@123!Temp;Port=3306;'
  }
}

// App Service Plan
resource appServicePlan 'Microsoft.Web/serverfarms@2023-01-01' = {
  name: '${abbrs.appServicePlan}${resourceToken}'
  location: location
  kind: 'linux'
  sku: {
    name: 'B2'
    capacity: 1
  }
  properties: {
    reserved: true
  }
  tags: tags
}

// App Service
resource appService 'Microsoft.Web/sites@2023-01-01' = {
  name: '${abbrs.appService}${resourceToken}'
  location: location
  kind: 'app,linux'
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${userAssignedIdentity.id}': {}
    }
  }
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.11'
      appCommandLine: 'gunicorn --workers 4 --worker-class sync --bind=0.0.0.0:${environment().appServiceAppSettings.PORT ?? 8000} --timeout 600 app:app'
      numberOfWorkers: 1
      defaultDocuments: []
      netFrameworkVersion: ''
      requestTracingEnabled: false
      remoteDebuggingEnabled: false
      httpLoggingEnabled: true
      logsDirectorySizeLimit: 35
      detailedErrorLoggingEnabled: true
      publishingUsername: ''
      scmType: 'None'
      use32BitWorkerProcess: false
      webSocketsEnabled: false
      managedPipelineMode: 'Integrated'
      virtualApplications: [
        {
          virtualPath: '/'
          physicalPath: 'site\\wwwroot'
          preloadEnabled: true
        }
      ]
      loadBalancing: 'LeastRequests'
      experiments: {
        rampUpRules: []
      }
      autoHealEnabled: false
      localMySqlEnabled: false
      ipSecurityRestrictions: [
        {
          ipAddress: 'Any'
          action: 'Allow'
          priority: 1
          name: 'Allow all'
          description: 'Allow all access'
        }
      ]
      scmIpSecurityRestrictions: [
        {
          ipAddress: 'Any'
          action: 'Allow'
          priority: 1
          name: 'Allow all'
          description: 'Allow all access'
        }
      ]
      scmIpSecurityRestrictionsUseMain: false
      http20Enabled: true
      minTlsVersion: '1.2'
      scmMinTlsVersion: '1.0'
      ftpsState: 'FtpsOnly'
      preWarmedInstanceCount: 0
      functionAppScaleLimit: 0
      healthCheckPath: ''
      fileChangeAuditEnabled: false
      functionsRuntimeScaleMonitoringEnabled: false
      websiteTimeZone: ''
      minimumElasticInstanceCount: 0
      azureStorageAccounts: {}
      allowedOrigins: [
        '*'
      ]
    }
    httpsOnly: true
    virtualNetworkSubnetId: ''
    publicNetworkAccess: 'Enabled'
  }
  tags: tags
}

// App Service Configuration - Environment Variables
resource appServiceSettings 'Microsoft.Web/sites/config@2023-01-01' = {
  parent: appService
  name: 'appsettings'
  properties: {
    FLASK_ENV: 'production'
    FLASK_APP: 'app.py'
    SCM_DO_BUILD_DURING_DEPLOYMENT: 'true'
    BUILD_FLAGS: 'noFile'
    XDG_CACHE_HOME: '/tmp/.cache'
    WEBSITE_MOUNT_ENABLED: '1'
    WEBSITE_HTTPLOGGING_RETENTION_DAYS: '3'
    ApplicationInsightsAgent_EXTENSION_VERSION: '~3'
    APPINSIGHTS_INSTRUMENTATION_KEY: applicationInsights.properties.InstrumentationKey
    APPLICATIONINSIGHTS_CONNECTION_STRING: 'InstrumentationKey=${applicationInsights.properties.InstrumentationKey}'
    ApplicationInsightsAgent_EXTENSION_VERSION: '~3'
    XDG_DATA_HOME: '/tmp/.local/share'
  }
}

// App Service Connection Strings - MySQL
resource appServiceConnectionStrings 'Microsoft.Web/sites/config@2023-01-01' = {
  parent: appService
  name: 'connectionstrings'
  properties: {
    DefaultConnection: {
      value: 'Server=${mySqlServer.properties.fullyQualifiedDomainName};Database=smartquiz;Uid=smartquizadmin;Pwd=Admin@123!Temp;'
      type: 'MySql'
    }
  }
}

// Diagnostic Settings - App Service to Log Analytics
resource appServiceDiagnostics 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
  name: 'app-service-diagnostics'
  scope: appService
  properties: {
    workspaceId: logAnalyticsWorkspace.id
    logs: [
      {
        category: 'AppServiceHTTPLogs'
        enabled: true
      }
      {
        category: 'AppServiceConsoleLogs'
        enabled: true
      }
      {
        category: 'AppServiceAppLogs'
        enabled: true
      }
      {
        category: 'AppServiceIPSecAuditLogs'
        enabled: false
      }
      {
        category: 'AppServicePlatformLogs'
        enabled: false
      }
    ]
    metrics: [
      {
        category: 'AllMetrics'
        enabled: true
      }
    ]
  }
}

// Outputs
output appServiceUrl string = 'https://${appService.properties.defaultHostName}'
output appServiceName string = appService.name
output mySqlServerName string = mySqlServer.name
output mySqlServerFqdn string = mySqlServer.properties.fullyQualifiedDomainName
output applicationInsightsKey string = applicationInsights.properties.InstrumentationKey
output keyVaultName string = keyVault.name
