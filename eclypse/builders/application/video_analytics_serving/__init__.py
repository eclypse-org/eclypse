"""The video analytics serving application models a containerised pipeline.

Frames are captured, analysed, tracked, and aggregated before returning a
result to the originating camera gateway. It captures a common edge AI
deployment pattern in which low-latency processing is split across multiple
services.

Source:
    `Intel Edge Video Analytics Microservice
    <https://docs.edgeplatform.intel.com/edge-video-analytics-microservice/2.2.0/user-guide/Overview.html>`_
"""
