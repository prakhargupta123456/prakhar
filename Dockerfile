ARG BASE_IMAGE=ubuntu:22.04

# -------------------------------------------------------------------
# BUILDER
# -------------------------------------------------------------------
FROM ${BASE_IMAGE} AS vpp-upf-builder
ENV DEBIAN_FRONTEND=noninteractive
ENV IS_DOCKERFILE=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    git sudo wget curl make cmake ninja-build pkg-config \
    build-essential python3 python3-pip \
    libhyperscan-dev \
    rdma-core libibverbs1 libibverbs-dev ibverbs-providers libmlx5-1 libmlx5-dev librdmacm1 \
    libnuma-dev libssl-dev libmnl-dev libelf-dev \
    libnl-3-dev libnl-route-3-dev \
    && rm -rf /var/lib/apt/lists/*

RUN git config --global https.postBuffer 123289600 && \
    git config --global http.sslverify false

WORKDIR /vpp-upf
COPY . .

# Apply vpp patches if present
RUN mv upg-vpp/vpp-patches/* scripts/patches/ && \
    mv upg-vpp/vpp.spec / && \
    ./scripts/apply_vpp_patches.sh || true

# Build VPP with UPF and kernel interface support
RUN yes | make -C vpp install-dep && \
    make -C vpp build-release && \
    ldd /vpp-upf/vpp/build-root/install-vpp-native/vpp/bin/vpp && \
    ldd /vpp-upf/vpp/build-root/install-vpp-native/vpp/bin/vppctl

# -------------------------------------------------------------------
# RUNTIME
# -------------------------------------------------------------------
FROM ${BASE_IMAGE} AS amantya-upf-vpp
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Paris
ENV LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu

RUN apt-get update && apt-get install -y --no-install-recommends \
    rdma-core libibverbs1 ibverbs-providers libmlx5-1 librdmacm1 \
    libnuma1 libhyperscan5 \
    libnl-3-200 libnl-route-3-200 \
    net-tools iproute2 iputils-ping curl tzdata ethtool \
    && rm -rf /var/lib/apt/lists/*

# Binaries
WORKDIR /5g-upf/bin
COPY --from=vpp-upf-builder /vpp-upf/scripts/entrypoint.sh ./
COPY --from=vpp-upf-builder /vpp-upf/vpp/build-root/install-vpp-native/vpp/bin/vpp ./
COPY --from=vpp-upf-builder /vpp-upf/vpp/build-root/install-vpp-native/vpp/bin/vppctl ./
COPY --from=vpp-upf-builder /vpp-upf/src/nrf_client.sh ./

# Config
WORKDIR /5g-upf/etc
COPY --from=vpp-upf-builder /vpp-upf/scripts/upf_conf/upf_profile.json ./
COPY --from=vpp-upf-builder /vpp-upf/scripts/upf_conf/create_configuration.py ./
COPY --from=vpp-upf-builder /vpp-upf/scripts/snap/upf_default_conf.sh ./
COPY vpp-startup.conf startup.conf

# Plugins
WORKDIR /usr/lib/x86_64-linux-gnu/vpp_plugins/
COPY --from=vpp-upf-builder /vpp-upf/vpp/build-root/build-vpp-native/vpp/lib/x86_64-linux-gnu/vpp_plugins/*.so* ./

# Shared libs
WORKDIR /usr/lib/x86_64-linux-gnu/
COPY --from=vpp-upf-builder /vpp-upf/vpp/build-root/build-vpp-native/vpp/lib/x86_64-linux-gnu/*.so* ./

RUN ldconfig && \
    ldd /5g-upf/bin/vpp && \
    ldd /5g-upf/bin/vppctl

RUN groupadd vpp

WORKDIR /5g-upf
COPY --from=vpp-upf-builder /vpp-upf/scripts/run.sh .

EXPOSE 8085/udp 2152/udp
ENTRYPOINT ["/5g-upf/run.sh"]