Source: https://learn.microsoft.com/fabric/enterprise/pause-resume
Fetched: 2026-10-24

# Pause and resume your Fabric capacity

Table of contents 

Exit editor mode

---

Note

Access to this page requires authorization. You can try [signing in](#) or changing directories.

Access to this page requires authorization. You can try changing directories.

# Pause and resume your Fabric capacity

Microsoft Fabric lets you pause and resume your capacity. When your capacity isn't operational, you can pause it to enable cost savings for your organization. Later, when you want to resume work on your capacity, you can reactivate it.

When you pause your capacity, the remaining [cumulative overages and smoothed operations](throttling#how-fabric-balances-performance-and-reliability) on your capacity are summed, and added to your Azure bill. You can [monitor a paused capacity](monitor-paused-capacity) by using the [Microsoft Fabric Capacity Metrics app](metrics-app).

If your capacity is being [throttled](throttling), pausing it stops the throttling and returns your capacity to a healthy state immediately. This behavior enables you to pause your capacity as a self-service mechanism that ends throttling.

Important

Pausing a capacity can prevent Microsoft Fabric content from being available. Before you pause your capacity, make sure the capacity is not being used.

## Prerequisites

To pause your capacity, you need:

- An [F SKU capacity](licenses#capacity)
- The following Azure RBAC actions on the Fabric capacity resource:

  - `Microsoft.Fabric/capacities/read`
  - `Microsoft.Fabric/capacities/write`
  - `Microsoft.Fabric/capacities/suspend/action`
  - `Microsoft.Fabric/capacities/resume/action`

  Create an [Azure custom role](/en-us/azure/role-based-access-control/custom-roles) scoped to these actions. These actions are also included in the [Azure privileged built-in roles](/en-us/azure/role-based-access-control/built-in-roles/privileged), but using those roles isn't recommended because they grant more permissions than necessary.

  For more information about Microsoft Fabric resource provider operations, see [Microsoft.Fabric](/en-us/azure/role-based-access-control/permissions/analytics#microsoftfabric). To assign the custom role to the Fabric capacity resource, see [Assign Azure roles using the Azure portal](/en-us/azure/role-based-access-control/role-assignments-portal).

## Pause your capacity

To pause your capacity:

1. Sign into the [Azure portal](https://portal.azure.com/).
2. Select the **Microsoft Fabric** service to see your capacities. You can search for *Microsoft Fabric* in the search menu.
3. Select the capacity you want to pause.
4. Select **Pause**.
5. Select **Yes** to confirm you want to pause the capacity.

## Resume your capacity

Restart usage by resuming your capacity. Resuming your capacity also resumes billing. Content assigned to this capacity becomes available once the capacity is resumed.

1. Sign into the [Azure portal](https://portal.azure.com/).
2. Select the **Microsoft Fabric** service to see your capacities. You can search for *Microsoft Fabric* in the search menu.
3. Select the capacity you want to resume.
4. Select **Resume**.
5. Select **Yes** to confirm you want to resume the capacity.

## Schedule your operation

With [Azure runbook](/en-us/azure/automation/automation-runbook-types) you can schedule your pause and resume operations.

1. [Import a module from the module gallery](/en-us/azure/automation/automation-runbook-gallery#import-a-module-from-the-modules-gallery-in-the-azure-portal).
2. In the runbook gallery, search for *Fabric*.
3. Select the notebook you want to schedule. The scheduling parameters are described in the description of the runbook.

## Use APIs

You can use these Fabric REST APIs to pause and resume your capacity:

- [Pause or suspend your capacity](/en-us/rest/api/microsoftfabric/fabric-capacities/suspend)
- [Resume your capacity](/en-us/rest/api/microsoftfabric/fabric-capacities/resume)

## Related content

- [Scale your capacity](scale-capacity)
- [Understand the metrics app compute page](metrics-app-compute-page)

---

- Last updated on 
  2026-04-20
