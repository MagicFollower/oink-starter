---
title: "租户 Helm Charts"

weight: 40
---

<a id="helm-charts"></a>
<a id="minio-tenant-chart-values"></a>

已归档的 MinIO Operator 项目曾发布 [Operator Chart](https://github.com/minio/operator/tree/v7.1.1/helm/operator) 与 [Tenant Chart](https://github.com/minio/operator/tree/v7.1.1/helm/tenant)。本页记录其最终 `v7.1.1` Tenant Chart。

以下页面说明 MinIO 租户的 `values.yaml` Chart。 有关 MinIO Operator Chart 的文档，请参阅 [Operator Helm 图表](/docs/reference/operator-chart-values/#minio-operator-chart-values)

> [!WARNING]
> 上游 MinIO Operator 仓库已于 2026 年 3 月 20 日归档。本页是其最终 `v7.1.1` Chart 的保留参考快照，不代表上游仍在维护或提供支持。默认值已对照该标签核验；内部文档链接改为本站路由，并把上游陈旧的 `existingSecret` 注释校正为 Chart 实际使用的 `tenant.configSecret.name` 输入。下文的 `quay.io/minio/minio` 是上游 Chart 默认值，不是 Silo 品牌名称，也不是推荐的 Silo 镜像。要运行 Silo，请将 `tenant.image.repository` 覆盖为 `pgsty/silo`，并固定经过测试的 [已发布标签或镜像摘要](/zh/download/#server)。

<a id="minio-tenant-chart-operator-values"></a>

## MinIO 租户 Chart {#minio-chart}

{{< tabs group="tab1-yaml" >}}
{{< tab label="参考" value="tab1" >}}
**tenant**

> **name**
>
> > The Tenant name
> >
> > Change this to match your preferred MinIO Tenant name.
>
> **image**
>
> > Specify the Operator container image to use for the deployment. `image.tag` For example, the following sets the image to the `quay.io/minio/operator` repo and the v7.1.1 tag. The container pulls the image if not already present:
> >
> > ```yaml
> > image:
> >    repository: quay.io/minio/minio
> >    tag: RELEASE.2025-04-08T15-41-24Z
> >    pullPolicy: IfNotPresent
> > ```
> >
> > The chart also supports specifying an image based on digest value:
> >
> > ```yaml
> > image:
> >    repository: quay.io/minio/minio@sha256
> >    digest: 28c80b379c75242c6fe793dfbf212f43c602140a0de5ebe3d9c2a3a7b9f9f983
> >    pullPolicy: IfNotPresent
> > ```
>
> **imagePullSecret**
>
> > An array of Kubernetes secrets to use for pulling images from a private `image.repository`. Only one array element is supported at this time.
>
> **initContainers**
>
> > Specify [initContainers](https://kubernetes.io/docs/concepts/workloads/pods/init-containers/) to perform setup or configuration tasks before the main Tenant pods starts.
> >
> > Example of init container which waits for idenity provider to be reachable before starting MinIO Tenant:
> >
> > ```yaml
> > initContainers:
> >  - name: wait-for-idp
> >    image: busybox
> >    command:
> >      - sh
> >      - -c
> >      - |
> >        URL="https://idp-url"
> >        echo "Checking IdP reachability (${URL})"
> >        until $(wget -q -O "/dev/null" ${URL}) ; do
> >          echo "IdP (${URL}) not reachable. Waiting to be reachable..."
> >          sleep 5
> >        done
> >        echo "IdP (${URL}) reachable. Starting MinIO..."
> > ```
>
> **scheduler**
>
> > The Kubernetes [Scheduler](https://kubernetes.io/docs/concepts/scheduling-eviction/kube-scheduler/) to use for dispatching Tenant pods.
> >
> > Specify an empty dictionary `{}` to dispatch pods with the default scheduler.
>
> **configSecret**
>
> > Root key for dynamically creating a secret for use with configuring root MinIO User Specify the `name` and then a list of environment variables.
> > 若要复用包含 `config.env` 的现有 Secret，请将 `tenant.configSecret.name` 设为该 Secret，并把 `tenant.configSecret.existingSecret` 设为 `true`。
> >
> > > [!WARNING]
> > > **重要**
> > >
> > > Do not use this in production environments. This field is intended for use with rapid development or testing only.
> >
> > For example:
> >
> > ```yaml
> > name: myminio-env-configuration
> > accessKey: minio
> > secretKey: minio123
> > ```
>
> **poolsMetadata**
>
> > Metadata that will be added to the statefulset and pods of all pools
> >
> > **annotations**
> >
> > > Specify [annotations](https://kubernetes.io/docs/concepts/overview/working-with-objects/annotations/) to associate to Tenant pods.
> >
> > **labels**
> >
> > > Specify [labels](https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/) to associate to Tenant pods.
>
> **pools**
>
> > Top level key for configuring MinIO Pool(s) in this Tenant.
> >
> > See [Operator CRD: Pools](https://silo.pgsty.com/docs/reference/operator-crd/#pool) for more information on all subfields.
> >
> > **servers**
> >
> > > The number of MinIO Tenant Pods / Servers in this pool. For standalone mode, supply 1. For distributed mode, supply 4 or more. Note that the operator does not support upgrading from standalone to distributed mode.
> >
> > **name**
> >
> > > Custom name for the pool
> >
> > **volumesPerServer**
> >
> > > The number of volumes attached per MinIO Tenant Pod / Server.
> >
> > **size**
> >
> > > The capacity per volume requested per MinIO Tenant Pod.
> >
> > **storageAnnotations**
> >
> > > Specify [storageAnnotations](https://kubernetes.io/docs/concepts/overview/working-with-objects/annotations/) to associate to PVCs.
> >
> > **storageLabels**
> >
> > > Specify [storageLabels](https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/) to associate to PVCs.
> >
> > **annotations**
> >
> > > Specify [annotations](https://kubernetes.io/docs/concepts/overview/working-with-objects/annotations/) to associate to Tenant pods.
> >
> > **labels**
> >
> > > Specify [labels](https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/) to associate to Tenant pods.
> >
> > **tolerations**
> >
> > > An array of [Toleration labels](https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/) to associate to Tenant pods.
> > >
> > > These settings determine the distribution of pods across worker nodes.
> >
> > **nodeSelector**
> >
> > > Any [Node Selectors](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/) to apply to Tenant pods.
> > >
> > > The Kubernetes scheduler uses these selectors to determine which worker nodes onto which it can deploy Tenant pods.
> > >
> > > If no worker nodes match the specified selectors, the Tenant deployment will fail.
> >
> > **affinity**
> >
> > > The [affinity](https://kubernetes.io/docs/tasks/configure-pod-container/assign-pods-nodes-using-node-affinity/) or anti-affinity settings to apply to Tenant pods.
> > >
> > > These settings determine the distribution of pods across worker nodes and can help prevent or allow colocating pods onto the same worker nodes.
> >
> > **resources**
> >
> > > The [Requests or Limits](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/) for resources to associate to Tenant pods.
> > >
> > > These settings can control the minimum and maximum resources requested for each pod. If no worker nodes can meet the specified requests, the Operator may fail to deploy.
> >
> > **securityContext**
> >
> > > The Kubernetes [SecurityContext](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/) to use for deploying Tenant resources.
> > >
> > > You may need to modify these values to meet your cluster’s security and access settings.
> > >
> > > We recommend disabling recursive permission changes by setting `fsGroupChangePolicy` to `OnRootMismatch` as those operations can be expensive for certain workloads (e.g. large volumes with many small files).
> >
> > **containerSecurityContext**
> >
> > > The Kubernetes [SecurityContext](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/) to use for deploying Tenant containers. You may need to modify these values to meet your cluster’s security and access settings.
> >
> > **topologySpreadConstraints**
> >
> > > An array of [Topology Spread Constraints](https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/) to associate to Operator Console pods.
> > >
> > > These settings determine the distribution of pods across worker nodes.
>
> **mountPath**
>
> > The mount path where Persistent Volumes are mounted inside Tenant container(s).
>
> **subPath**
>
> > The Sub path inside Mount path where MinIO stores data.
> >
> > > [!CAUTION]
> > > **警告**
> > >
> > > Treat the `mountPath` and `subPath` values as immutable once you deploy the Tenant. If you change these values post-deployment, then you may have different paths for new and pre-existing data. This can vastly increase operational complexity and may result in unpredictable data states.
> >
>
> **metrics**
>
> > Configures a Prometheus-compatible scraping endpoint at the specified port.
>
> **certificate**
>
> > Configures external certificate settings for the Tenant.
> >
> > **externalCaCertSecret**
> >
> > > Specify an array of Kubernetes TLS secrets, where each entry corresponds to a secret the TLS private key and public certificate pair.
> > >
> > > This is used by MinIO to verify TLS connections from clients using those CAs If you omit this and have clients using TLS certificates minted by an external CA, those connections may fail with warnings around certificate verification. See [Operator CRD: TenantSpec](https://silo.pgsty.com/docs/reference/operator-crd/#tenantspec).
> >
> > **externalCertSecret**
> >
> > > Specify an array of Kubernetes secrets, where each entry corresponds to a secret contains the TLS private key and public certificate pair.
> > >
> > > Omit this to use only the MinIO Operator autogenerated certificates.
> > >
> > > If you omit this field *and* set `requestAutoCert` to false, the Tenant starts without TLS.
> > >
> > > See [Operator CRD: TenantSpec](https://silo.pgsty.com/docs/reference/operator-crd/#tenantspec).
> > >
> > > > [!WARNING]
> > > > **重要**
> > > >
> > > > The MinIO Operator may output TLS connectivity errors if it cannot trust the Certificate Authority (CA) which minted the custom certificates.
> > > >
> > > > You can pass the CA to the Operator to allow it to trust that cert. See [Self-Signed, Internal, and Private Certificates](https://silo.pgsty.com/docs/operations/network-encryption/#self-signed-internal-private-certificates-and-public-cas-with-intermediate-certificates) for more information. This step may also be necessary for globally trusted CAs where you must provide intermediate certificates to the Operator to help build the full chain of trust.
> > >
> >
> > **requestAutoCert**
> >
> > > Enable automatic Kubernetes based [certificate generation and signing](https://kubernetes.io/docs/tasks/tls/managing-tls-in-a-cluster)
> >
> > **certConfig**
> >
> > > This field is used only when `requestAutoCert: true`. Use this field to set CommonName for the auto-generated certificate. MinIO defaults to using the internal Kubernetes DNS name for the pod The default DNS name format is typically `*.minio.default.svc.cluster.local`.
> > >
> > > See [Operator CRD: CertificateConfig](https://silo.pgsty.com/docs/reference/operator-crd/#certificateconfig)
>
> **features**
>
> > MinIO features to enable or disable in the MinIO Tenant See [Operator CRD: Features](https://silo.pgsty.com/docs/reference/operator-crd/#features).
>
> **buckets**
>
> > Array of objects describing one or more buckets to create during tenant provisioning. Example:
> >
> > ```yaml
> > - name: my-minio-bucket
> >   objectLock: false        # optional
> >   region: us-east-1        # optional
> > ```
>
> **users**
>
> > Array of Kubernetes secrets from which the Operator generates MinIO users during tenant provisioning.
> >
> > Each secret should specify the `CONSOLE_ACCESS_KEY` and `CONSOLE_SECRET_KEY` as the access key and secret key for that user.
>
> **podManagementPolicy**
>
> > The [PodManagement](https://kubernetes.io/docs/tutorials/stateful-application/basic-stateful-set/#pod-management-policy) policy for MinIO Tenant Pods. Can be “OrderedReady” or “Parallel”
>
> **readiness**
>
> > [Readiness Probe](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/) for monitoring Tenant container readiness. Tenant pods will be removed from service endpoints if the probe fails.
>
> **startup**
>
> > [Startup Probe](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/) for monitoring container startup. Tenant pods will be restarted if the probe fails. Refer
>
> **lifecycle**
>
> > The [Lifecycle hooks](https://kubernetes.io/docs/concepts/containers/container-lifecycle-hooks/) for container.
>
> **exposeServices**
>
> > Directs the Operator to deploy the MinIO S3 API and Console services as LoadBalancer objects.
> >
> > If the Kubernetes cluster has a configured LoadBalancer, it can attempt to route traffic to those services automatically.
> >
> > - Specify `minio: true` to expose the MinIO S3 API.
> > - Specify `console: true` to expose the Console.
> >
> > Both fields default to `false`.
>
> **serviceAccountName**
>
> > The [Kubernetes Service Account](https://kubernetes.io/docs/tasks/configure-pod-container/configure-service-account/) associated with the Tenant.
>
> **prometheusOperator**
>
> > Directs the Operator to add the Tenant’s metric scrape configuration to an existing Kubernetes Prometheus deployment managed by the Prometheus Operator.
>
> **logging**
>
> > Configure pod logging configuration for the MinIO Tenant.
> >
> > - Specify `json` for JSON-formatted logs.
> > - Specify `anonymous` for anonymized logs.
> > - Specify `quiet` to supress logging.
> >
> > An example of JSON-formatted logs is as follows:
> >
> > ```shell
> > $ k logs myminio-pool-0-0 -n default
> > {"level":"INFO","errKind":"","time":"2022-04-07T21:49:33.740058549Z","message":"All MinIO sub-systems initialized successfully"}
> > ```
>
> **serviceMetadata**
>
> > serviceMetadata allows passing additional labels and annotations to MinIO and Console specific services created by the operator.
>
> **env**
>
> > Add environment variables to be set in MinIO container ([https://github.com/minio/minio/tree/master/docs/config](https://github.com/minio/minio/tree/master/docs/config))
>
> **priorityClassName**
>
> > PriorityClassName indicates the Pod priority and hence importance of a Pod relative to other Pods. This is applied to MinIO pods only. Refer Kubernetes documentation for details [https://kubernetes.io/docs/concepts/configuration/pod-priority-preemption/#priorityclass/](https://kubernetes.io/docs/concepts/configuration/pod-priority-preemption/#priorityclass/)
>
> **additionalVolumes**
>
> > An array of [Volumes](https://kubernetes.io/docs/concepts/storage/volumes/) which the Operator can mount to Tenant pods.
> >
> > The volumes must exist *and* be accessible to the Tenant pods.
>
> **additionalVolumeMounts**
>
> > An array of volume mount points associated to each Tenant container.
> >
> > Specify each item in the array as follows:
> >
> > ```yaml
> > volumeMounts:
> > - name: volumename
> >   mountPath: /path/to/mount
> > ```
> >
> > The `name` field must correspond to an entry in the `additionalVolumes` array.

**ingress**

> Configures [Ingress](https://kubernetes.io/docs/concepts/services-networking/ingress/) for the Tenant S3 API and Console.
>
> Set the keys to conform to the Ingress controller and configuration of your choice.
{{< /tab >}}
{{< tab label="YAML" value="yaml" >}}
```text
# Root key for MinIO Tenant Chart
tenant:
  ###
  # The Tenant name
  #
  # Change this to match your preferred MinIO Tenant name.
  name: myminio
  ###
  # Specify the Operator container image to use for the deployment.
  # ``image.tag`` 
  # For example, the following sets the image to the ``quay.io/minio/operator`` repo and the v7.1.1 tag.
  # The container pulls the image if not already present:
  #
  # .. code-block:: yaml
  # 
  #    image:
  #       repository: quay.io/minio/minio
  #       tag: RELEASE.2025-04-08T15-41-24Z
  #       pullPolicy: IfNotPresent
  #
  # The chart also supports specifying an image based on digest value:
  # 
  # .. code-block:: yaml
  # 
  #    image:
  #       repository: quay.io/minio/minio@sha256
  #       digest: 28c80b379c75242c6fe793dfbf212f43c602140a0de5ebe3d9c2a3a7b9f9f983
  #       pullPolicy: IfNotPresent
  #
  #
  image:
    repository: quay.io/minio/minio
    tag: RELEASE.2025-04-08T15-41-24Z
    pullPolicy: IfNotPresent
  ###
  #
  # An array of Kubernetes secrets to use for pulling images from a private ``image.repository``.
  # Only one array element is supported at this time.
  imagePullSecret: { }
  ###
  #
  # Specify `initContainers <https://kubernetes.io/docs/concepts/workloads/pods/init-containers/>`__ to perform setup or configuration tasks before the main Tenant pods starts.
  #
  # Example of init container which waits for idenity provider to be reachable before starting MinIO Tenant:
  # 
  # .. code-block:: yaml
  #
  #    initContainers:
  #     - name: wait-for-idp
  #       image: busybox
  #       command:
  #         - sh
  #         - -c
  #         - |
  #           URL="https://idp-url"
  #           echo "Checking IdP reachability (${URL})"
  #           until $(wget -q -O "/dev/null" ${URL}) ; do
  #             echo "IdP (${URL}) not reachable. Waiting to be reachable..."
  #             sleep 5
  #           done
  #           echo "IdP (${URL}) reachable. Starting MinIO..."
  #
  initContainers: [ ]
  ###
  # The Kubernetes `Scheduler <https://kubernetes.io/docs/concepts/scheduling-eviction/kube-scheduler/>`__ to use for dispatching Tenant pods.
  #
  # Specify an empty dictionary ``{}`` to dispatch pods with the default scheduler.
  scheduler: { }
  ###
  # Root key for dynamically creating a secret for use with configuring root MinIO User
  # Specify the ``name`` and then a list of environment variables.
  #
  # .. important::
  #
  #    Do not use this in production environments.
  #    This field is intended for use with rapid development or testing only.
  #
  # For example:
  #
  # .. code-block:: yaml
  #
  #    name: myminio-env-configuration
  #    accessKey: minio
  #    secretKey: minio123
  #
  configSecret:
    name: myminio-env-configuration
    accessKey: minio
    secretKey: minio123
    #existingSecret: true

  ###
  # Metadata that will be added to the statefulset and pods of all pools
  poolsMetadata:
    ###
    # Specify `annotations <https://kubernetes.io/docs/concepts/overview/working-with-objects/annotations/>`__ to associate to Tenant pods.
    annotations: { }
    ###
    # Specify `labels <https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/>`__ to associate to Tenant pods.
    labels: { }

  ###
  # If this variable is set to true, then enable the usage of an existing Kubernetes secret to set environment variables for the Tenant.
  # Set the existing Kubernetes secret name under .tenant.configSecret.name, for example existing-minio-env-configuration.
  # The secret must contain a key ``config.env``.
  # The values should be a series of export statements to set environment variables for the Tenant.
  # For example:
  #
  # .. code-block:: shell
  #
  #    stringData:
  #       config.env: |-
  #         export MINIO_ROOT_USER=ROOTUSERNAME
  #         export MINIO_ROOT_PASSWORD=ROOTUSERPASSWORD
  #
  #   existingSecret: false
  ###
  # Top level key for configuring MinIO Pool(s) in this Tenant.
  #
  # See `Operator CRD: Pools <https://silo.pgsty.com/docs/reference/operator-crd/#pool>`__ for more information on all subfields.
  pools:
    ###
    # The number of MinIO Tenant Pods / Servers in this pool.
    # For standalone mode, supply 1. For distributed mode, supply 4 or more.
    # Note that the operator does not support upgrading from standalone to distributed mode.
    - servers: 4
      ###
      # Custom name for the pool
      name: pool-0
      ###
      # The number of volumes attached per MinIO Tenant Pod / Server.
      volumesPerServer: 4
      ###
      # The capacity per volume requested per MinIO Tenant Pod.
      size: 10Gi
      ###
      # The `storageClass <https://kubernetes.io/docs/concepts/storage/storage-classes/>`__ to associate with volumes generated for this pool.
      #
      # If using Amazon Elastic Block Store (EBS) CSI driver
      # Please make sure to set xfs for "csi.storage.k8s.io/fstype" parameter under StorageClass.parameters.
      # Docs: https://github.com/kubernetes-sigs/aws-ebs-csi-driver/blob/master/docs/parameters.md
      # storageClassName: standard
      ###
      # Specify `storageAnnotations <https://kubernetes.io/docs/concepts/overview/working-with-objects/annotations/>`__ to associate to PVCs.
      storageAnnotations: { }
      ###
      # Specify `storageLabels <https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/>`__ to associate to PVCs.
      storageLabels: { }
      ###
      # Specify `annotations <https://kubernetes.io/docs/concepts/overview/working-with-objects/annotations/>`__ to associate to Tenant pods.
      annotations: { }
      ###
      # Specify `labels <https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/>`__ to associate to Tenant pods.
      labels: { }
      ###
      #
      # An array of `Toleration labels <https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/>`__ to associate to Tenant pods.
      #
      # These settings determine the distribution of pods across worker nodes.
      tolerations: [ ]
      ###
      # Any `Node Selectors <https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/>`__ to apply to Tenant pods.
      #
      # The Kubernetes scheduler uses these selectors to determine which worker nodes onto which it can deploy Tenant pods.
      #
      # If no worker nodes match the specified selectors, the Tenant deployment will fail.
      nodeSelector: { }
      ###
      #
      # The `affinity <https://kubernetes.io/docs/tasks/configure-pod-container/assign-pods-nodes-using-node-affinity/>`__ or anti-affinity settings to apply to Tenant pods.
      #
      # These settings determine the distribution of pods across worker nodes and can help prevent or allow colocating pods onto the same worker nodes.
      affinity: { }
      ###
      # 
      # The `Requests or Limits <https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/>`__ for resources to associate to Tenant pods.
      #
      # These settings can control the minimum and maximum resources requested for each pod.
      # If no worker nodes can meet the specified requests, the Operator may fail to deploy.
      resources: { }
      ###
      # The Kubernetes `SecurityContext <https://kubernetes.io/docs/tasks/configure-pod-container/security-context/>`__ to use for deploying Tenant resources.
      #
      # You may need to modify these values to meet your cluster's security and access settings.
      #
      # We recommend disabling recursive permission changes by setting ``fsGroupChangePolicy`` to ``OnRootMismatch`` as those operations can be expensive for certain workloads (e.g. large volumes with many small files).
      securityContext:
        runAsUser: 1000
        runAsGroup: 1000
        fsGroup: 1000
        fsGroupChangePolicy: "OnRootMismatch"
        runAsNonRoot: true
      ###
      # The Kubernetes `SecurityContext <https://kubernetes.io/docs/tasks/configure-pod-container/security-context/>`__ to use for deploying Tenant containers.
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
      #
      # An array of `Topology Spread Constraints <https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/>`__ to associate to Operator Console pods.
      #
      # These settings determine the distribution of pods across worker nodes.
      topologySpreadConstraints: [ ]
      ###
      #
      # The name of a custom `Container Runtime <https://kubernetes.io/docs/concepts/containers/runtime-class/>`__ to use for the Operator Console pods.
      # runtimeClassName: ""
  ###
  # The mount path where Persistent Volumes are mounted inside Tenant container(s).
  mountPath: /export
  ###
  # The Sub path inside Mount path where MinIO stores data.
  #
  # .. warning::
  #
  #    Treat the ``mountPath`` and ``subPath`` values as immutable once you deploy the Tenant.
  #    If you change these values post-deployment, then you may have different paths for new and pre-existing data.
  #    This can vastly increase operational complexity and may result in unpredictable data states.
  subPath: /data
  ###
  # Configures a Prometheus-compatible scraping endpoint at the specified port.
  metrics:
    enabled: false
    port: 9000
    protocol: http
  ###
  # Configures external certificate settings for the Tenant.
  certificate:
    ###
    # Specify an array of Kubernetes TLS secrets, where each entry corresponds to a secret the TLS private key and public certificate pair.
    #
    # This is used by MinIO to verify TLS connections from clients using those CAs
    # If you omit this and have clients using TLS certificates minted by an external CA, those connections may fail with warnings around certificate verification.
    # See `Operator CRD: TenantSpec <https://silo.pgsty.com/docs/reference/operator-crd/#tenantspec>`__.
    externalCaCertSecret: [ ]
    ###
    # Specify an array of Kubernetes secrets, where each entry corresponds to a secret contains the TLS private key and public certificate pair.
    #
    # Omit this to use only the MinIO Operator autogenerated certificates.
    # 
    # If you omit this field *and* set ``requestAutoCert`` to false, the Tenant starts without TLS.
    #
    # See `Operator CRD: TenantSpec <https://silo.pgsty.com/docs/reference/operator-crd/#tenantspec>`__.
    #
    # .. important::
    #
    #    The MinIO Operator may output TLS connectivity errors if it cannot trust the Certificate Authority (CA) which minted the custom certificates.
    #
    #    You can pass the CA to the Operator to allow it to trust that cert.
    #    See `Self-Signed, Internal, and Private Certificates <https://silo.pgsty.com/docs/operations/network-encryption/#self-signed-internal-private-certificates-and-public-cas-with-intermediate-certificates>`__ for more information.
    #    This step may also be necessary for globally trusted CAs where you must provide intermediate certificates to the Operator to help build the full chain of trust.
    externalCertSecret: [ ]
    ###
    # Enable automatic Kubernetes based `certificate generation and signing <https://kubernetes.io/docs/tasks/tls/managing-tls-in-a-cluster>`__
    requestAutoCert: true
    ###
    # The minimum number of days to expiry before an alert for an expiring certificate is fired.
    # In the below example, if a given certificate will expire in 7 days then expiration events will only be triggered 1 day before expiry
    # certExpiryAlertThreshold: 1
    ###
    # This field is used only when ``requestAutoCert: true``.
    # Use this field to set CommonName for the auto-generated certificate. 
    # MinIO defaults to using the internal Kubernetes DNS name for the pod
    # The default DNS name format is typically ``*.minio.default.svc.cluster.local``.
    #
    # See `Operator CRD: CertificateConfig <https://silo.pgsty.com/docs/reference/operator-crd/#certificateconfig>`__
    certConfig: { }
  ###
  # MinIO features to enable or disable in the MinIO Tenant
  # See `Operator CRD: Features <https://silo.pgsty.com/docs/reference/operator-crd/#features>`__.
  features:
    bucketDNS: false
    domains: { }
    enableSFTP: false
  ###
  # Array of objects describing one or more buckets to create during tenant provisioning.
  # Example:
  # 
  # .. code-block:: yaml
  #
  #    - name: my-minio-bucket
  #      objectLock: false        # optional
  #      region: us-east-1        # optional
  buckets: [ ]
  ###
  # Array of Kubernetes secrets from which the Operator generates MinIO users during tenant provisioning.
  #
  # Each secret should specify the ``CONSOLE_ACCESS_KEY`` and ``CONSOLE_SECRET_KEY`` as the access key and secret key for that user.
  users: [ ]
  ###
  # The `PodManagement <https://kubernetes.io/docs/tutorials/stateful-application/basic-stateful-set/#pod-management-policy>`__ policy for MinIO Tenant Pods. 
  # Can be "OrderedReady" or "Parallel"
  podManagementPolicy: Parallel
  # The `Liveness Probe <https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes>`__ for monitoring Tenant pod liveness. 
  # Tenant pods will be restarted if the probe fails.
  liveness: { }
  ###
  # `Readiness Probe <https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/>`__ for monitoring Tenant container readiness.
  # Tenant pods will be removed from service endpoints if the probe fails.
  readiness: { }
  ###
  # `Startup Probe <https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/>`__ for monitoring container startup. 
  # Tenant pods will be restarted if the probe fails.
  # Refer 
  startup: { }
  ###
  # The `Lifecycle hooks <https://kubernetes.io/docs/concepts/containers/container-lifecycle-hooks/>`__ for container.
  lifecycle: { }
  ###
  # Directs the Operator to deploy the MinIO S3 API and Console services as LoadBalancer objects.
  #
  # If the Kubernetes cluster has a configured LoadBalancer, it can attempt to route traffic to those services automatically.
  #
  # - Specify ``minio: true`` to expose the MinIO S3 API.
  # - Specify ``console: true`` to expose the Console.
  #
  # Both fields default to ``false``.
  exposeServices: { }
  ###
  # The `Kubernetes Service Account <https://kubernetes.io/docs/tasks/configure-pod-container/configure-service-account/>`__ associated with the Tenant.
  serviceAccountName: ""
  ###
  # Directs the Operator to add the Tenant's metric scrape configuration to an existing Kubernetes Prometheus deployment managed by the Prometheus Operator.
  prometheusOperator: false
  ###
  # Configure pod logging configuration for the MinIO Tenant.
  #
  # - Specify ``json`` for JSON-formatted logs.
  # - Specify ``anonymous`` for anonymized logs.
  # - Specify ``quiet`` to supress logging.
  #
  # An example of JSON-formatted logs is as follows:
  #
  # .. code-block:: shell
  #
  #    $ k logs myminio-pool-0-0 -n default
  #    {"level":"INFO","errKind":"","time":"2022-04-07T21:49:33.740058549Z","message":"All MinIO sub-systems initialized successfully"}
  logging: { }
  ###
  # serviceMetadata allows passing additional labels and annotations to MinIO and Console specific
  # services created by the operator.
  serviceMetadata: { }
  ###
  # Add environment variables to be set in MinIO container (https://github.com/minio/minio/tree/master/docs/config)
  env: [ ]
  ###
  # PriorityClassName indicates the Pod priority and hence importance of a Pod relative to other Pods.
  # This is applied to MinIO pods only.
  # Refer Kubernetes documentation for details https://kubernetes.io/docs/concepts/configuration/pod-priority-preemption/#priorityclass/
  priorityClassName: ""
  ###
  # An array of `Volumes <https://kubernetes.io/docs/concepts/storage/volumes/>`__ which the Operator can mount to Tenant pods.
  #
  # The volumes must exist *and* be accessible to the Tenant pods.
  additionalVolumes: [ ]
  ###
  # An array of volume mount points associated to each Tenant container.
  # 
  # Specify each item in the array as follows:
  #
  # .. code-block:: yaml
  #
  #    volumeMounts:
  #    - name: volumename
  #      mountPath: /path/to/mount
  #
  # The ``name`` field must correspond to an entry in the ``additionalVolumes`` array.
  additionalVolumeMounts: [ ]
  # Define configuration for KES (stateless and distributed key-management system)
  # Refer https://github.com/minio/kes
  #kes:
  #  ## Image field:
  #  # Image from tag (original behavior), for example:
  #  # image:
  #  #   repository: quay.io/minio/kes
  #  #   tag: 2025-03-12T09-35-18Z
  #  # Image from digest (added after original behavior), for example:
  #  # image:
  #  #   repository: quay.io/minio/kes@sha256
  #  #   digest: fb15af611149892f357a8a99d1bcd8bf5dae713bd64c15e6eb27fbdb88fc208b
  #  image:
  #    repository: quay.io/minio/kes
  #    tag: 2025-03-12T09-35-18Z
  #    pullPolicy: IfNotPresent
  #  env: [ ]
  #  replicas: 2
  #  configuration: |-
  #    address: :7373
  #    tls:
  #      key: /tmp/kes/server.key   # Path to the TLS private key
  #      cert: /tmp/kes/server.crt # Path to the TLS certificate
  #      proxy:
  #        identities: []
  #        header:
  #          cert: X-Tls-Client-Cert
  #    admin:
  #      identity: ${MINIO_KES_IDENTITY}
  #    cache:
  #      expiry:
  #        any: 5m0s
  #        unused: 20s
  #    log:
  #      error: on
  #      audit: off
  #    keystore:
  #      # KES configured with fs (File System mode) doesn't work in Kubernetes environments and is not recommended
  #      # use a real KMS
  #      # fs:
  #      #   path: "./keys" # Path to directory. Keys will be stored as files. Not Recommended for Production.
  #      vault:
  #        endpoint: "http://vault.default.svc.cluster.local:8200" # The Vault endpoint
  #        namespace: "" # An optional Vault namespace. See: https://www.vaultproject.io/docs/enterprise/namespaces/index.html
  #        prefix: "my-minio"    # An optional K/V prefix. The server will store keys under this prefix.
  #        approle:    # AppRole credentials. See: https://www.vaultproject.io/docs/auth/approle.html
  #          id: "<YOUR APPROLE ID HERE>"      # Your AppRole Role ID
  #          secret: "<YOUR APPROLE SECRET ID HERE>"  # Your AppRole Secret ID
  #          retry: 15s  # Duration until the server tries to re-authenticate after connection loss.
  #        tls:        # The Vault client TLS configuration for mTLS authentication and certificate verification
  #          key: ""     # Path to the TLS client private key for mTLS authentication to Vault
  #          cert: ""    # Path to the TLS client certificate for mTLS authentication to Vault
  #          ca: ""      # Path to one or multiple PEM root CA certificates
  #        status:     # Vault status configuration. The server will periodically reach out to Vault to check its status.
  #          ping: 10s   # Duration until the server checks Vault's status again.
  #      # aws:
  #      #   # The AWS SecretsManager key store. The server will store
  #      #   # secret keys at the AWS SecretsManager encrypted with
  #      #   # AWS-KMS. See: https://aws.amazon.com/secrets-manager
  #      #   secretsmanager:
  #      #     endpoint: ""   # The AWS SecretsManager endpoint      - e.g.: secretsmanager.us-east-2.amazonaws.com
  #      #     region: ""     # The AWS region of the SecretsManager - e.g.: us-east-2
  #      #     kmskey: ""     # The AWS-KMS key ID used to en/decrypt secrets at the SecretsManager. By default (if not set) the default AWS-KMS key will be used.
  #      #     credentials:   # The AWS credentials for accessing secrets at the AWS SecretsManager.
  #      #       accesskey: ""  # Your AWS Access Key
  #      #       secretkey: ""  # Your AWS Secret Key
  #      #       token: ""      # Your AWS session token (usually optional)
  #  imagePullPolicy: "IfNotPresent"
  #  externalCertSecret: null
  #  clientCertSecret: null
  #  # Key name to be created on the KMS, default is "my-minio-key"
  #  keyName: ""
  #  resources: { }
  #  nodeSelector: { }
  #  affinity:
  #    nodeAffinity: { }
  #    podAffinity: { }
  #    podAntiAffinity: { }
  #  tolerations: [ ]
  #  annotations: { }
  #  labels: { }
  #  serviceAccountName: ""
  #  securityContext:
  #    runAsUser: 1000
  #    runAsGroup: 1000
  #    runAsNonRoot: true
  #    fsGroup: 1000
  #  containerSecurityContext:
  #    runAsUser: 1000
  #    runAsGroup: 1000
  #    runAsNonRoot: true
  #    allowPrivilegeEscalation: false
  #    capabilities:
  #      drop:
  #        - ALL
  #    seccompProfile:
  #      type: RuntimeDefault

###
# Configures `Ingress <https://kubernetes.io/docs/concepts/services-networking/ingress/>`__ for the Tenant S3 API and Console.
#
# Set the keys to conform to the Ingress controller and configuration of your choice.
ingress:
  api:
    enabled: false
    ingressClassName: ""
    labels: { }
    annotations: { }
    tls: [ ]
    host: minio.local
    path: /
    pathType: Prefix
  console:
    enabled: false
    ingressClassName: ""
    labels: { }
    annotations: { }
    tls: [ ]
    host: minio-console.local
    path: /
    pathType: Prefix
# Use an extraResources template section to include additional Kubernetes resources
# with the Helm deployment.
#extraResources:
#  - |
#    apiVersion: v1
#    kind: Secret
#    type: Opaque
#    metadata:
#      name: {{ dig "tenant" "configSecret" "name" "" (.Values | merge (dict)) }}
#    stringData:
#      config.env: |-
#        export MINIO_ROOT_USER='minio'
#        export MINIO_ROOT_PASSWORD='minio123'

```
{{< /tab >}}
{{< /tabs >}}