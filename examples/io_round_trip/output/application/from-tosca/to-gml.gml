graph [
  directed 1
  id "vision-application-tosca"
  scenario "io-round-trip"
  source_format "tosca"
  node [
    id 0
    label "camera-gateway"
    cpu 1
    ram 1
    storage 4096
    gpu 32
    availability 0.9924489185380347
    processing_time 5
    image "ghcr.io/eclypse/camera-gateway:latest"
  ]
  node [
    id 1
    label "inference"
    cpu 4
    ram 6
    storage 4
    gpu 128
    availability 0.9903178267948178
    processing_time 3
    image "ghcr.io/eclypse/inference:latest"
  ]
  node [
    id 2
    label "dashboard"
    cpu 1
    ram 1
    storage 512
    gpu 2
    availability 0.9956124506293861
    processing_time 23
    build "./dashboard"
  ]
  edge [
    source 0
    target 1
    latency 8
    bandwidth 80
  ]
  edge [
    source 1
    target 2
    latency 5
    bandwidth 40
  ]
]
