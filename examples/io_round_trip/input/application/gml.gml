graph [
  directed 1
  id "vision-application-gml"
  scenario "io-round-trip"
  source_format "gml"
  node [
    id 0
    label "camera-gateway"
    cpu 1
    ram 1
    image "ghcr.io/eclypse/camera-gateway:latest"
  ]
  node [
    id 1
    label "inference"
    cpu 4
    ram 6
    image "ghcr.io/eclypse/inference:latest"
  ]
  node [
    id 2
    label "dashboard"
    cpu 1
    ram 1
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
