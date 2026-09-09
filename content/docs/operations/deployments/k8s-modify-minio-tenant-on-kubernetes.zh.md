---
title: "修改 Silo Tenant"

weight: 30
---

<a id="minio-tenant"></a>
<a id="minio-k8s-modify-minio-tenant-security"></a>
<a id="minio-k8s-modify-minio-tenant"></a>

部署完成后，你可以修改租户以调整可变配置项。 有关 MinIO Custom Resource Definition 中可用设置的完整说明，请参阅 [MinIO 自定义资源定义](/docs/reference/operator-crd/#minio-operator-crd)。

修改租户的方法取决于你最初如何部署该租户：

{{< tabs group="kustomize-helm" >}}
{{< tab label="Kustomize" value="kustomize" >}}
对于使用 Kustomize 部署的租户，你可以修改基础 Kustomization 资源，并在包含 `kustomization.yaml` 的目录上运行 `kubectl apply -k` 进行应用。

```shell
kubectl apply -k ~/kustomization/TENANT-NAME/
```

请根据本地配置修改 Kustomization 目录路径。
{{< /tab >}}
{{< tab label="Helm" value="helm" >}}
对于使用 Helm 部署的租户，你可以修改基础 `values.yaml`，并通过 chart 升级租户：

```shell
helm upgrade TENANT-NAME minio-operator/tenant -f values.yaml -n TENANT-NAMESPACE
```

上述命令默认使用的是 MinIO Operator Chart 仓库。 如果你是手动安装 Chart，或使用了不同的仓库名称，请在命令中指定相应的 chart 或名称。

分别将 `TENANT-NAME` 和 `TENANT-NAMESPACE` 替换为租户的名称和命名空间。 你可以使用 `helm list -n TENANT-NAMESPACE` 验证租户名称。
{{< /tab >}}
{{< /tabs >}}

**添加受信任的证书颁发机构**

> MinIO 租户会使用主机系统的受信任根证书存储，校验每个连接客户端提供的 TLS 证书。 MinIO Operator 可以为租户挂载额外的第三方 Certificate Authorities (CA)，以便校验由这些 CA 签发的客户端 TLS 证书。
>
> 若要自定义挂载到每个租户 MinIO pod 的受信任 CA，请启用 **Custom Certificates** 开关。 点击 **Add CA Certificate +** 按钮即可添加第三方 CA 证书。
>
> 如果 MinIO 租户无法在容器操作系统的信任库 *或* 显式挂载的 CA 中匹配到传入客户端 TLS 证书的签发者，MinIO 会将该连接视为无效并拒绝。

## 管理租户 Pool {#pool}

### 指定 Runtime Class {#runtime-class}

> [!NOTE]
> **新增: Console**
>
> 0.23.1

在为租户添加新 pool 或修改现有 pool 时，你可以为这些 pool 指定 [Runtime Class Name](https://kubernetes.io/docs/concepts/containers/runtime-class/)。

### 退役租户 服务器池 {#id2}

MinIO Operator 4.4.13 及更高版本支持退役租户中的 服务器池。 具体而言，你可以遵循 [Decommission a Server pool](https://silo.pgsty.com/docs/operations/deployments/baremetal-decommission-server-pool/) 步骤先从租户中移除该 pool，然后编辑租户 YAML，将该 pool 从 StatefulSet 中移除。 移除租户 pool 时，请确保所有剩余 pool 的 `spec.pools.[n].name` 字段都具有明确取值。

> [!NOTE]
> **先下线再新增时保持 pool 顺序**
>
> 如果你在多 pool 部署中下线了一个 pool，就不能在新 pool 中复用相同的节点编号序列。 例如，假设某个部署包含以下几个 pool：
>
> ```text
> https://minio-{1...4}.example.net/mnt/drive-{1...4}
> https://minio-{5...8}.example.net/mnt/drive-{1...4}
> https://minio-{9...12}.example.net/mnt/drive-{1...4}
> ```
>
> 如果你下线了 `minio-{5...8}` 这个 pool，就不能再用相同的节点编号新增一个 pool。你必须将新 pool 添加在 `minio-{9...12}` *之后*：
>
> ```text
> https://minio-{1...4}.example.net/mnt/drive-{1...4}
> https://minio-{9...12}.example.net/mnt/drive-{1...4}
> https://minio-{13...16}.example.net/mnt/drive-{1...4}
> ```