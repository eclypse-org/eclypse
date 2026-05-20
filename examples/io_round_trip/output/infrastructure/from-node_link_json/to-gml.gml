graph [
  directed 1
  id "cloud-edge-node-link"
  scenario "io-round-trip"
  source_format "node-link-json"
  node [
    id 0
    label "cloud"
    cpu 64
    ram 128
    storage 2048
    gpu 32
    availability 0.999
    processing_time 5
    tier "cloud"
  ]
  node [
    id 1
    label "edge-a"
    cpu 16
    ram 32
    storage 512
    gpu 128
    availability 0.995
    processing_time 3
    tier "edge"
  ]
  node [
    id 2
    label "edge-b"
    cpu 12
    ram 24
    storage 256
    gpu 2
    availability 0.99
    processing_time 23
    tier "edge"
  ]
  edge [
    source 1
    target 0
    latency 18
    bandwidth 500
    link_type "wan"
  ]
  edge [
    source 1
    target 2
    latency 4
    bandwidth 1000
    link_type "lan"
  ]
  edge [
    source 2
    target 0
    latency 22
    bandwidth 450
    link_type "wan"
  ]
]
