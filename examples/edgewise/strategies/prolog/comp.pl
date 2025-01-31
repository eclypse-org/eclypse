compComponentPlacement(F, N, P) :-
    functionInstance(F, FId, _), function(FId, SWPlat, (Arch,HWReqs)),
    node(N, SWCaps, (Arch,HWCaps), _, _), 
    requirements(FId, N), 
    member(SWPlat, SWCaps),
    hwOK(N, HWCaps, HWReqs, P).
compComponentPlacement(S, N, P) :-
    serviceInstance(S, SId), service(SId, SWReqs, (Arch,HWReqs)),
    node(N, SWCaps, (Arch,HWCaps), _, _), 
    requirements(SId, N), 
    subset(SWReqs, SWCaps),
    hwOK(N, HWCaps, HWReqs, P).


compQosOK(C, N, P) :- 
    findall(DF, compRelevant(C, N, P, DF), DataFlows), 
    compCheckDF(DataFlows, [(C,N)|P]).

compRelevant(C, N, P, (N, M, Lat, BW, Sec)):-
    dataFlow(C, C1, _, Sec, Size, Rate, Lat),
    (member((C1,M), P); node(M, _, _, _, IoTCaps), member(C1, IoTCaps)),
    BW is Size*Rate.
compRelevant(C, N, _, (M, N, Lat, BW, Sec)):-
    dataFlow(C1, C, _, Sec, Size, Rate, Lat),
    node(M, _, _, _, IoTCaps), member(C1, IoTCaps),
    BW is Size*Rate.

compCheckDF([(N1,N2, ReqLat, _, SecReqs)|DFs], [(C,N)|P]) :-
    secOK(N1, N2, SecReqs),
    link(N1, N2, FeatLat, FeatBW),
    FeatLat =< ReqLat,
    compBwOK(C, N, FeatBW, P),
    compCheckDF(DFs, [(C,N)|P]).
compCheckDF([], _).

compBwOK(C, N, FeatBW, P):-
    findall(BW, compRelevant(C, N, P, (_,_,_,BW,_)), BWs), sum_list(BWs, OkAllocBW), 
    bwTh(T), FeatBW >= OkAllocBW + T.