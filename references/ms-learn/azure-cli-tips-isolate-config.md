Source: https://learn.microsoft.com/cli/azure/use-azure-cli-successfully-tips?view=azure-cli-latest
Fetched: 2026-10-13

# Tips for using the Azure CLI successfully

Table of contents 

Exit editor mode

---

Note

Access to this page requires authorization. You can try [signing in](#) or changing directories.

Access to this page requires authorization. You can try changing directories.

# Tips for using the Azure CLI successfully

Azure CLI is a command-line tool that allows you to configure and manage Azure resources from many
shell environments. After you [choose your preferred shell environment](choose-the-right-azure-command-line-tool?view=azure-cli-latest#different-shell-environments) and
[install the Azure CLI](install-azure-cli?view=azure-cli-latest), use this article to discover useful tips on how to avoid common
pitfalls and use the Azure CLI successfully.

To learn more about specific Azure CLI commands, see the [Azure CLI Reference list](reference-index?view=azure-cli-latest).

## Choose a scripting language

The Azure CLI is an open source *tool* that you can run in many *scripting languages*.

- It's the scripting language that determines the quoting, escape character, and line continuation
  rules for Azure CLI commands.
- It can be challenging to copy Azure CLI command syntax *containing single or double quotes, escape
  characters, or line continuation characters* between languages.
- **Most Microsoft documentation for the Azure CLI is written and tested in Bash.**
- If PowerShell is your scripting language of choice, consider using the tool,
  [Azure PowerShell](/en-us/powershell/azure/), which has native [PowerShell](/en-us/powershell/) scripting language functionality.

For more information on scripting language options for Azure CLI, see
[Choose the right command-line tool](choose-the-right-azure-command-line-tool?view=azure-cli-latest).

## FAQ

Here are some links to help you answer the most frequently asked Azure CLI questions:

| Subject area with article link | Tip |
| --- | --- |
| [Work behind a proxy](use-azure-cli-successfully-troubleshooting?view=azure-cli-latest#work-behind-a-proxy) | Information on how to work over a proxy server. |
| [Web Account Manager (WAM)](authenticate-azure-cli-interactively?view=azure-cli-latest#sign-in-with-web-account-manager-wam-on-windows) | Information on WAM and how to disable it. |
| [Configuration settings](azure-cli-configuration?view=azure-cli-latest) | List of available Azure CLI configuration settings, how to turn on/off Azure CLI features, and set default values. |
| [Output formats](format-output-azure-cli?view=azure-cli-latest) | Instructions on how to store Azure resource IDs in variables, and protect secrets returned by Azure CLI commands. |
| [Passing JSON values in a string](use-azure-cli-successfully-troubleshooting?view=azure-cli-latest#error-failed-to-parse-string-as-json) | Quoting examples for JSON parameter values. |
| [Support lifecycle](azure-cli-support-lifecycle?view=azure-cli-latest) | Information about supported operating systems, scripting languages and the end of service for Azure CLI versions and dependencies. |
| [REST API](/en-us/cli/azure/reference-index#az-rest) | Alternative [az rest](/en-us/cli/azure/reference-index) command to use when a specific Azure CLI command isn't available for an Azure resource. |
| [Azure CLI reference groups](reference-docs-index?view=azure-cli-latest) | A to Z list of Azure CLI reference groups with drill-down to subgroups and all Azure CLI commands. |
| [Azure CLI articles](/en-us/cli/azure/reference-index) | A to Z list of Quickstarts, How-to guides, and Tutorials that use Azure CLI reference commands. The list is grouped by reference group and subgroup for easy search. |
| [Azure CLI samples](samples-index?view=azure-cli-latest) | A to Z list of Samples, including those samples in the Azure-samples/azure-cli-samples GitHub repository. |
| [Troubleshooting](use-azure-cli-successfully-troubleshooting?view=azure-cli-latest) | Error cause and remediation tips. |
| [What's new](whats-new-overview?view=azure-cli-latest) | Short summary of new Azure CLI features. |

## Pass values to another command

If the value is used more than once, assign it to a variable. Variables allow you to use values more
than once or to create more general scripts. This example assigns an ID found by the
[az vm list](/en-us/cli/azure/vm#az-vm-list) command to a variable.

```
# assign the list of running VMs to a variable
running_vm_ids=$(az vm list --resource-group MyResourceGroup --show-details \
    --query "[?powerState=='VM running'].id" --output tsv)

# verify the value of the variable
echo $running_vm_ids
```

If the value is used only once, consider piping. (Piping passes the output of one command as input
to a second command.)

```
az vm list --query "[?powerState=='VM running'].name" --output tsv | grep my_vm
```

For multi-value lists, consider the following options:

1. If you need more controls on the result, use a "for" loop:

```
#!/usr/bin/env bash
for vmList in $(az vm list --resource-group MyResourceGroup --show-details --query "[?powerState=='VM running'].id"   -output tsv); do
    echo stopping $vmList
    az vm stop --ids $vmList
    if [ $? -ne 0 ]; then
        echo "Failed to stop $vmList"
        exit 1
    fi
    echo $vmList stopped
done
```

1. Alternatively, use `xargs` and consider using the `-P` flag to run the operations in parallel for
   improved performance:

```
az vm list --resource-group MyResourceGroup --show-details \
    --query "[?powerState=='VM stopped'].id" \
    --output tsv | xargs -I {} -P 10 az vm start --ids "{}"
```

1. Finally, Azure CLI has built-in support to process commands with multiple `--ids` in parallel to
   achieve the same effect of xargs. `@-` is used to get values from the pipe:

```
az vm list --resource-group MyResourceGroup --show-details \
    --query "[?powerState=='VM stopped'].id" \
    --output tsv | az vm start --ids @-
```

For more information on using Bash constructs with the Azure CLI including loops, case statements,
if..then..else, and error handling, see [Learn to use Bash with the Azure CLI](use-azure-cli-successfully-bash?view=azure-cli-latest).

## Common update parameters

Azure CLI command groups often feature an update command. For instance,
[Azure Virtual Machines](/en-us/cli/azure/vm) includes the [az vm update](/en-us/cli/azure/vm#az-vm-update) command. Most update commands offer the
three common parameters: `--add`, `--set`, and `--remove`.

The `--set` and `--add` parameters take a list of space-separated key-value pairs:
`key1=value1 key2=value2`. To see what properties you can update, use a show command, such as
[az vm show](/en-us/cli/azure/vm#az-vm-show).

```
az vm show --resource-group VMResources --name virtual-machine-01
```

To simplify the command, consider using a JSON string. For example, to attach a new data disk to a
virtual machine, use the following value:

```
az vm update --resource-group VMResources --name virtual-machine-01 \
--add storageProfile.dataDisks "{\"createOption\": \"Attach\", \"managedDisk\":
   {\"id\":
   \"/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/yg/providers/Microsoft.Compute/disks/yg-disk\"},
   \"lun\": 1}"
```

## Generic resource commands

A service you want to work with might not have Azure CLI support. You can use the [az resource](resource?view=azure-cli-latest)
or [az rest](use-azure-cli-rest-command?view=azure-cli-latest) commands to work with these resources.

## Concurrent execution

If you run Azure CLI commands concurrently on the same machine, write conflicts can happen if
multiple Azure CLI commands write to the same Microsoft Authentication Library (MSAL) token cache.

To avoid potential failures, isolate the Azure CLI configuration folder for each script by setting
environment variable `AZURE_CONFIG_DIR` for each script to a separate directory. Azure CLI commands
in that script save the configuration and token cache to the configured location instead of the
default `~/.azure` folder.

- [Bash](#tabpanel_1_bash)
- [PowerShell](#tabpanel_1_powershell)
- [Cmd](#tabpanel_1_cmd)

```
export AZURE_CONFIG_DIR=/my/config/dir
```

```
$env:AZURE_CONFIG_DIR='D:\my\config\dir'
```

```
set AZURE_CONFIG_DIR=D:\my\config\dir
```

## Asynchronous operations

Operations in Azure can take a noticeable amount of time. For instance, configuring a virtual
machine at a data center isn't instantaneous. Azure CLI waits until the command finishes to accept
other commands. Many commands therefore offer a `--no-wait` parameter as shown here:

```
az group delete --name MyResourceGroup --no-wait
```

When you delete a resource group, all the resources that belong to it are also removed. Removing
these resources can take a long time. When you run the command with the `--no-wait` parameter, the
console accepts new commands without interrupting the removal.

Many commands offer a wait option, pausing the console until some condition is met. The following
example uses the [az vm wait](/en-us/cli/azure/vm#az-vm-wait) command to support creating independent resources in parallel:

```
az vm create --resource-group VMResources --name virtual-machine-01 --image centos --no-wait
az vm create --resource-group VMResources --name virtual-machine-02 --image centos --no-wait

subscription=$(az account show --query "id" -o tsv)
vm1_id="/subscriptions/$subscription/resourceGroups/VMResources/providers/Microsoft.Compute/virtualMachines/virtual-machine-01"
vm2_id="/subscriptions/$subscription/resourceGroups/VMResources/providers/Microsoft.Compute/virtualMachines/virtual-machine-02"
az vm wait --created --ids $vm1_id $vm2_id
```

After both IDs are created, you can use the console again.

## Script examples

Here are examples for using variables and looping through a list when working with Azure Virtual
Machines. For in-depth examples on using Bash constructs with the Azure CLI including loops, case
statements, if..then..else, and error handling, see [Learn to use Bash with the Azure CLI](use-azure-cli-successfully-bash?view=azure-cli-latest).

Use these scripts to save IDs to variables:

- [Cmd](#tabpanel_2_cmd2)
- [PowerShell](#tabpanel_2_powershell2)

```
ECHO OFF
SETLOCAL
FOR /F "tokens=* USEBACKQ" %%F IN (
   `az vm list --resource-group VMResources --show-details --query "[?powerState=='VM running'].id" --output tsv`
) DO (
    SET "vm_ids=%%F %vm_ids%"  :: construct the id list
)
az vm stop --ids %vm_ids% :: CLI stops all VMs in parallel
```

```
$vm_ids=(az vm list --resource-group VMResources --show-details --query "[?powerState=='VM running'].id" --output tsv)
az vm stop --ids $vm_ids # CLI stops all VMs in parallel
```

Use these scripts to loop through a list:

- [Cmd](#tabpanel_3_cmd2)
- [PowerShell](#tabpanel_3_powershell2)

```
ECHO OFF
SETLOCAL
FOR /F "tokens=* USEBACKQ" %%F IN (
    `az vm list --resource-group VMResources --show-details --query "[?powerState=='VM running'].id" --output tsv`
) DO (
    ECHO Stopping %%F
    az vm stop --ids %%F
)
```

```
$vm_ids=(az vm list --resource-group VMResources --show-details --query "[?powerState=='VM running'].id" --output tsv)
foreach ($vm_id in $vm_ids) {
    Write-Output "Stopping $vm_id"
    az vm stop --ids $vm_id
}
```

## See also

- [Troubleshooting the Azure CLI](use-azure-cli-successfully-troubleshooting?view=azure-cli-latest)

---

- Last updated on 
  2026-09-01
