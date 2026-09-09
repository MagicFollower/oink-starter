---
title: "Operator Helm 图表"

weight: 30
---

<a id="operator-helm"></a>
<a id="minio-operator-chart-values"></a>

已归档的 MinIO Operator 项目曾发布 [Operator Chart](https://github.com/minio/operator/tree/v7.1.1/helm/operator) 与 [Tenant Chart](https://github.com/minio/operator/tree/v7.1.1/helm/tenant)。本页记录其最终 `v7.1.1` Operator Chart。

本页说明 MinIO Operator 的 `values.yaml` 图表。 有关 MinIO 租户图表的文档，请参见 [租户 Helm Charts](/docs/reference/tenant-chart-values/#minio-tenant-chart-values)

> [!WARNING]
> 上游 MinIO Operator 仓库已于 2026 年 3 月 20 日归档。请将这些配置视为冻结的 `v7.1.1` 参考快照，而不是上游仍在维护或提供支持的依据。

<a id="minio-operator-chart-operator-values"></a>

## MinIO Operator 图表 {#minio-operator}

{{< tabs group="tab1-yaml" >}}
{{< tab label="参考" value="tab1" >}}
**operator**

> Root key for Operator Helm Chart
>
> **env**
>
> > An array of environment variables to pass to the Operator deployment. Pass an empty array to start Operator with defaults.
> >
> > For example:
> >
> > ```yaml
> > env:
> > - name: CLUSTER_DOMAIN
> >   value: "cluster.domain"
> > - name: WATCHED_NAMESPACE
> >   value: ""
> > - name: MINIO_OPERATOR_RUNTIME
> >   value: "OpenShift"
> > ```
> >
> > See [Operator environment variables](https://github.com/minio/operator/blob/v7.1.1/docs/env-variables.md) for a list of all supported values.
>
> **image**
>
> > Specify the Operator container image to use for the deployment. `image.tag` For example, the following sets the image to the `quay.io/minio/operator` repo and the v7.1.1 tag. The container pulls the image if not already present:
> >
> > ```yaml
> > image:
> >   repository: quay.io/minio/operator
> >   tag: v7.1.1
> >   pullPolicy: IfNotPresent
> > ```
> >
> > The chart also supports specifying an image based on digest value:
> >
> > ```yaml
> > image:
> >   repository: quay.io/minio/operator@sha256
> >   digest: 28c80b379c75242c6fe793dfbf212f43c602140a0de5ebe3d9c2a3a7b9f9f983
> >   pullPolicy: IfNotPresent
> > ```
>
> **sidecarImage**
>
> > Specify the sidecar container image to deploy on tenant pods for init container and sidecar. Only need to change this if want to use a different version that the default, or want to set a custom registry. `sidecarImage.tag` For example, the following sets the image to the `quay.io/minio/operator-sidecar` repo and the v7.1.1 tag. The container pulls the image if not already present:
> >
> > ```yaml
> > sidecarImage:
> >   repository: quay.io/minio/operator-sidecar
> >   tag: v7.1.1
> >   pullPolicy: IfNotPresent
> > ```
> >
> > The chart also supports specifying an image based on digest value:
> >
> > ```yaml
> > sidecarImage:
> >   repository: quay.io/minio/operator-sidecar@sha256
> >   digest: a11947a230b80fb1b0bffa97173147a505d4f1207958f722e348d11ab9e972c1
> >   pullPolicy: IfNotPresent
> > ```
>
> **imagePullSecrets**
>
> > An array of Kubernetes secrets to use for pulling images from a private `image.repository`. Only one array element is supported at this time.
>
> **runtimeClassName**
>
> > The name of a custom [Container Runtime](https://kubernetes.io/docs/concepts/containers/runtime-class/) to use for the Operator pods.
>
> **initContainers**
>
> > An array of [initContainers](https://kubernetes.io/docs/concepts/workloads/pods/init-containers/) to start up before the Operator pods. Exercise care as `initContainer` failures prevent Operator pods from starting. Pass an empty array to start the Operator normally.
>
> **replicaCount**
>
> > The number of Operator pods to deploy. Higher values increase availability in the event of worker node failures.
> >
> > The cluster must have sufficient number of available worker nodes to fulfill the request. Operator pods deploy with pod anti-affinity by default, preventing Kubernetes from scheduling multiple pods onto a single Worker node.
>
> **securityContext**
>
> > The Kubernetes [SecurityContext](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/) to use for deploying Operator resources.
> >
> > You may need to modify these values to meet your cluster’s security and access settings.
>
> **containerSecurityContext**
>
> > The Kubernetes [SecurityContext](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/) to use for deploying Operator containers. You may need to modify these values to meet your cluster’s security and access settings.
>
> **volumes**
>
> > An array of [Volumes](https://kubernetes.io/docs/concepts/storage/volumes/) which the Operator can mount to pods.
> >
> > The volumes must exist *and* be accessible to the Operator pods.
>
> **volumeMounts**
>
> > An array of volume mount points associated to each Operator container.
> >
> > Specify each item in the array as follows:
> >
> > ```yaml
> > volumeMounts:
> > - name: volumename
> >   mountPath: /path/to/mount
> > ```
> >
> > The `name` field must correspond to an entry in the `volumes` array.
>
> **nodeSelector**
>
> > Any [Node Selectors](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/) to apply to Operator pods.
> >
> > The Kubernetes scheduler uses these selectors to determine which worker nodes onto which it can deploy Operator pods.
> >
> > If no worker nodes match the specified selectors, the Operator deployment will fail.
>
> **priorityClassName**
>
> > The [Pod Priority](https://kubernetes.io/docs/concepts/scheduling-eviction/pod-priority-preemption/) to assign to Operator pods.
>
> **affinity**
>
> > The [affinity](https://kubernetes.io/docs/tasks/configure-pod-container/assign-pods-nodes-using-node-affinity/) or anti-affinity settings to apply to Operator pods.
> >
> > These settings determine the distribution of pods across worker nodes and can help prevent or allow colocating pods onto the same worker nodes.
>
> **tolerations**
>
> > An array of [Toleration labels](https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/) to associate to Operator pods.
> >
> > These settings determine the distribution of pods across worker nodes.
>
> **topologySpreadConstraints**
>
> > An array of [Topology Spread Constraints](https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/) to associate to Operator pods.
> >
> > These settings determine the distribution of pods across worker nodes.
>
> **resources**
>
> > The [Requests or Limits](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/) for resources to associate to Operator pods.
> >
> > These settings can control the minimum and maximum resources requested for each pod. If no worker nodes can meet the specified requests, the Operator may fail to deploy.
{{< /tab >}}
{{< tab label="YAML" value="yaml" >}}
```text
###
# Root key for Operator Helm Chart
operator:
  ###
  # An array of environment variables to pass to the Operator deployment.
  # Pass an empty array to start Operator with defaults.
  #
  # For example:
  #
  # .. code-block:: yaml
  #
  #    env:
  #    - name: CLUSTER_DOMAIN
  #      value: "cluster.domain"
  #    - name: WATCHED_NAMESPACE
  #      value: ""
  #    - name: MINIO_OPERATOR_RUNTIME
  #      value: "OpenShift"
  #
  # See `Operator environment variables <https://github.com/minio/operator/blob/v7.1.1/docs/env-variables.md>`__ for a list of all supported values.
  env:
    - name: OPERATOR_STS_ENABLED
      value: "on"
  # An array of additional annotations to be applied to the operator service account
  serviceAccountAnnotations: []
  # additional labels to be applied to operator resources
  additionalLabels: {}
  ###
  # Specify the Operator container image to use for the deployment.
  # ``image.tag``
  # For example, the following sets the image to the ``quay.io/minio/operator`` repo and the v7.1.1 tag.
  # The container pulls the image if not already present:
  #
  # .. code-block:: yaml
  #
  #    image:
  #      repository: quay.io/minio/operator
  #      tag: v7.1.1
  #      pullPolicy: IfNotPresent
  #
  # The chart also supports specifying an image based on digest value:
  #
  # .. code-block:: yaml
  #
  #    image:
  #      repository: quay.io/minio/operator@sha256
  #      digest: 28c80b379c75242c6fe793dfbf212f43c602140a0de5ebe3d9c2a3a7b9f9f983
  #      pullPolicy: IfNotPresent
  #
  image:
    repository: quay.io/minio/operator
    tag: v7.1.1
    pullPolicy: IfNotPresent
  ###
  # Specify the sidecar container image to deploy on tenant pods for init container and sidecar.
  # Only need to change this if want to use a different version that the default, or want to set a custom registry.
  # ``sidecarImage.tag``
  # For example, the following sets the image to the ``quay.io/minio/operator-sidecar`` repo and the v7.1.1 tag.
  # The container pulls the image if not already present:
  #
  # .. code-block:: yaml
  #
  #    sidecarImage:
  #      repository: quay.io/minio/operator-sidecar
  #      tag: v7.1.1
  #      pullPolicy: IfNotPresent
  #
  # The chart also supports specifying an image based on digest value:
  #
  # .. code-block:: yaml
  #
  #    sidecarImage:
  #      repository: quay.io/minio/operator-sidecar@sha256
  #      digest: a11947a230b80fb1b0bffa97173147a505d4f1207958f722e348d11ab9e972c1
  #      pullPolicy: IfNotPresent
  #
  sidecarImage: {}
  ###
  #
  # An array of Kubernetes secrets to use for pulling images from a private ``image.repository``.
  # Only one array element is supported at this time.
  imagePullSecrets: [ ]
  ###
  #
  # The name of a custom `Container Runtime <https://kubernetes.io/docs/concepts/containers/runtime-class/>`__ to use for the Operator pods.
  runtimeClassName: ~
  ###
  # An array of `initContainers <https://kubernetes.io/docs/concepts/workloads/pods/init-containers/>`__ to start up before the Operator pods.
  # Exercise care as ``initContainer`` failures prevent Operator pods from starting.
  # Pass an empty array to start the Operator normally.
  initContainers: [ ]
  ###
  # The number of Operator pods to deploy.
  # Higher values increase availability in the event of worker node failures.
  #
  # The cluster must have sufficient number of available worker nodes to fulfill the request.
  # Operator pods deploy with pod anti-affinity by default, preventing Kubernetes from scheduling multiple pods onto a single Worker node.
  replicaCount: 2
  ###
  # The Kubernetes `SecurityContext <https://kubernetes.io/docs/tasks/configure-pod-container/security-context/>`__ to use for deploying Operator resources.
  #
  # You may need to modify these values to meet your cluster's security and access settings.
  securityContext:
    runAsUser: 1000
    runAsGroup: 1000
    runAsNonRoot: true
    fsGroup: 1000
  ###
  # The Kubernetes `SecurityContext <https://kubernetes.io/docs/tasks/configure-pod-container/security-context/>`__ to use for deploying Operator containers.
  # You may need to modify these values to meet your cluster's security and access settings.
  containerSecurityContext:
    runAsUser: 1000
    runAsGroup: 1000
    runAsNonRoot: true
    allowPrivilegeEscalation: false
    capabilities:
      drop:
        - ALL
    seccompProfile:
      type: RuntimeDefault
  ###
  # An array of `Volumes <https://kubernetes.io/docs/concepts/storage/volumes/>`__ which the Operator can mount to pods.
  #
  # The volumes must exist *and* be accessible to the Operator pods.
  volumes: [ ]
  ###
  # An array of volume mount points associated to each Operator container.
  #
  # Specify each item in the array as follows:
  #
  # .. code-block:: yaml
  #
  #    volumeMounts:
  #    - name: volumename
  #      mountPath: /path/to/mount
  #
  # The ``name`` field must correspond to an entry in the ``volumes`` array.
  volumeMounts: [ ]
  ###
  # Any `Node Selectors <https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/>`__ to apply to Operator pods.
  #
  # The Kubernetes scheduler uses these selectors to determine which worker nodes onto which it can deploy Operator pods.
  #
  # If no worker nodes match the specified selectors, the Operator deployment will fail.
  nodeSelector: { }
  ###
  #
  # The `Pod Priority <https://kubernetes.io/docs/concepts/scheduling-eviction/pod-priority-preemption/>`__ to assign to Operator pods.
  priorityClassName: ""
  ###
  #
  # The `affinity <https://kubernetes.io/docs/tasks/configure-pod-container/assign-pods-nodes-using-node-affinity/>`__ or anti-affinity settings to apply to Operator pods.
  #
  # These settings determine the distribution of pods across worker nodes and can help prevent or allow colocating pods onto the same worker nodes.
  affinity:
    podAntiAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        - labelSelector:
            matchExpressions:
              - key: name
                operator: In
                values:
                  - minio-operator
          topologyKey: kubernetes.io/hostname
  ###
  #
  # An array of `Toleration labels <https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/>`__ to associate to Operator pods.
  #
  # These settings determine the distribution of pods across worker nodes.
  tolerations: [ ]
  ###
  #
  # An array of `Topology Spread Constraints <https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/>`__ to associate to Operator pods.
  #
  # These settings determine the distribution of pods across worker nodes.
  topologySpreadConstraints: [ ]
  ###
  #
  # The `Requests or Limits <https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/>`__ for resources to associate to Operator pods.
  #
  # These settings can control the minimum and maximum resources requested for each pod.
  # If no worker nodes can meet the specified requests, the Operator may fail to deploy.
  resources:
    requests:
      cpu: 200m
      memory: 256Mi
      ephemeral-storage: 500Mi

```
{{< /tab >}}
{{< /tabs >}}